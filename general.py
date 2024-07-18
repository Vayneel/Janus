import os
import socket
import json
import shutil
from io import BytesIO
from zipfile import ZipFile


def find_obsidian_dir(mode: bool) -> str | bool:  # todo normal
    print("please, wait, the searching process may take up to 10 minutes...", end="")
    if mode:
        for root, dirs, files in os.walk('C:\\'):
            if "Obsidian" in dirs:
                return os.path.join(root, "Obsidian")
        for root, dirs, files in os.walk('D:\\'):
            if "Obsidian" in dirs:
                return os.path.join(root, "Obsidian")
    else:
        for root, dirs, files in os.walk('/storage/emulated/0/Documents'):
            if "Obsidian" in dirs:
                return os.path.join(root, "Obsidian")
        for root, dirs, files in os.walk('/storage/emulated/0/'):
            if "Obsidian" in dirs:
                return os.path.join(root, "Obsidian")

    return False


def write_program_data(obsidian_dir, mode: bool):
    symbol = "\\" if mode else "/"
    obsidian_dir_split = obsidian_dir.split(symbol)

    janus_temp_dir = symbol.join(obsidian_dir_split[:-1]) + symbol + "Janus"

    zipfile_base = janus_temp_dir + symbol
    zipfile_loc = zipfile_base + "JanusObsidianArchive.zip"
    received_zipfile_loc = zipfile_base + "JanusReceivedArchive.zip"

    os.makedirs(janus_temp_dir, exist_ok=True)

    data_dict = {"obsidian_dir": obsidian_dir, "program_dir": janus_temp_dir, "zipfile_loc": zipfile_loc,
                 "received_zipfile_loc": received_zipfile_loc}

    with open('data.json', 'w') as data_file:
        json.dump(data_dict, data_file)

    return data_dict


def get_program_data(mode: bool = True) -> dict | None:
    print("Searching for Obsidian...", end="")

    if os.path.exists('data.json'):
        with open('data.json') as data_file:
            print("found")
            return json.load(data_file)

    obsidian_dir = find_obsidian_dir(mode)
    if obsidian_dir:
        data = write_program_data(obsidian_dir, mode)
        print("found")
        return data

    print("error")


def socket_startup(mode: bool) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if mode:
        s.bind(("localhost", 23323))
    else:
        s.connect(("localhost", 23323))

    return s


def print_send(connection, message: str):
    print(message)
    connection.send(message.encode())


def zip_obsidian(program_data) -> int:
    print("\nCreating zip archive...\n")
    current_dir = os.getcwd()
    os.chdir(program_data["obsidian_dir"])

    with ZipFile(program_data["zipfile_loc"], "w") as zipf:
        for root, dirs, files in os.walk("."):
            for file in files:
                path = os.path.join(root, file)
                zipf.write(path)
                print(f"file added to archive > {path}")

    os.chdir(current_dir)

    print("\nZip archive created")

    return os.path.getsize(program_data["zipfile_loc"])


def get_progress_bar(sent_quantity, file_size):
    percentage100 = round(sent_quantity / file_size * 100)
    percentage20 = round(sent_quantity / file_size * 20)
    return f"[{"#" * percentage20}{"-" * (20 - percentage20)}] {percentage100}%"


def gather_zipfile(connection):
    zipfile_size = int.from_bytes(connection.recv(64), "big")
    zipfile = BytesIO()
    bytes_to_recv = 16384
    i = 1

    while zipfile.getbuffer().nbytes < zipfile_size:
        byte_difference = zipfile_size - zipfile.getbuffer().nbytes
        if byte_difference > bytes_to_recv:
            data_slice = connection.recv(bytes_to_recv)
        else:
            data_slice = connection.recv(byte_difference)

        if not data_slice:
            raise Exception("Incomplete file received")

        if i == 31:
            print(get_progress_bar(zipfile.getbuffer().nbytes, zipfile_size))
            i = 0

        i += 1

        zipfile.write(data_slice)

    print(get_progress_bar(zipfile.getbuffer().nbytes, zipfile_size))
    return zipfile


def remove_obsidian_dir_content(program_data_dict):
    shutil.rmtree(program_data_dict['obsidian_dir'], ignore_errors=True)
