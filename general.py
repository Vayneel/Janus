import os
import socket
import json
import shutil
import re
from io import BytesIO
from zipfile import ZipFile
from tkinter import filedialog
import subprocess


def find_obsidian_dir(mode: bool) -> str | bool:
    print("please, wait, the searching process may take up to 10 minutes...", end="")
    if mode:
        obsidian_directory = filedialog.askdirectory()
        if obsidian_directory.endswith("Obsidian"):
            return obsidian_directory
        drives = subprocess.check_output("fsutil fsinfo drives").strip().decode()
        drives = re.findall(r"\w+:\\", drives)
        for drive in drives:
            for root, dirs, files in os.walk(drive):
                if "Obsidian" in dirs:
                    return os.path.join(root, "Obsidian")
    else:
        for root, dirs, files in os.walk('/storage/emulated/0/'):
            if "Obsidian" in dirs:
                return os.path.join(root, "Obsidian")

    return False


def write_program_data(obsidian_dir, mode: bool):
    symbol = "\\" if mode else "/"

    obsidian_dir_split = obsidian_dir.split(symbol)
    janus_temp_dir = symbol.join(obsidian_dir_split[:-1]) + symbol + ".janus"

    # janus_temp_dir = obsidian_dir + symbol + ".janus"

    zipfile_base = janus_temp_dir + symbol
    zipfile_loc = zipfile_base + "janusObsidianArchive.zip"
    received_zipfile_loc = zipfile_base + "janusReceivedArchive.zip"
    backup_zipfile_loc = zipfile_base + "backup.zip"

    os.makedirs(janus_temp_dir, exist_ok=True)

    data_dict = {"obsidian_dir": obsidian_dir, "program_dir": janus_temp_dir, "zipfile_loc": zipfile_loc,
                 "received_zipfile_loc": received_zipfile_loc, "backup_zipfile_loc": backup_zipfile_loc}

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


def socket_startup(ip, mode: bool) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if mode:
        s.bind((ip, 23323))
    else:
        s.connect((ip, 23323))

    return s


def zip_obsidian(program_data_dict, mode: str) -> int:
    """
    :param mode: push / backup
    """
    print("\nCreating zip archive...\n")
    current_dir = os.getcwd()
    os.chdir(program_data_dict["obsidian_dir"])

    zipfile_loc = program_data_dict["zipfile_loc"] if mode == "push" else program_data_dict["backup_zipfile_loc"]

    with ZipFile(zipfile_loc, "w") as zipf:
        for root, dirs, files in os.walk("."):
            # if root.endswith(".janus"):
            #     continue
            for file in files:
                path = os.path.join(root, file)
                zipf.write(path)
                print(f"file added to archive > {path}")

    os.chdir(current_dir)

    print("\nZip archive created")

    return os.path.getsize(zipfile_loc)


def get_progress_bar(sent_quantity, file_size):
    percentage100 = round(sent_quantity / file_size * 100)
    percentage20 = round(sent_quantity / file_size * 20)
    return f"[{'#' * percentage20}{'-' * (20 - percentage20)}] {percentage100}%"


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


def command_push_pull(connection, program_data_dict, mode: str):
    """
    :param mode: recv/send
    """
    if mode == "send":
        zipfile_size = zip_obsidian(program_data_dict, "push")
        connection.send(zipfile_size.to_bytes(64, "big"))

        with open(program_data_dict["zipfile_loc"], "rb") as zipfile:
            connection.send(zipfile.read())

    elif mode == "recv":
        print("\nReceiving zip archive...\n")
        zipfile_bytes = gather_zipfile(connection)
        print("\nBytes received")
        with open(program_data_dict["received_zipfile_loc"], "wb") as zipfile:
            zipfile.write(zipfile_bytes.getvalue())
        print("Archive created")
        remove_obsidian_dir_content(program_data_dict)
        print("Obsidian content removed")
        with ZipFile(program_data_dict["received_zipfile_loc"], "r") as zipfile:
            zipfile.extractall(program_data_dict["obsidian_dir"])
        print("Archive extracted into obsidian directory")


def command_create_backup(program_data_dict):
    print("\nCreating backup...\n")
    zip_obsidian(program_data_dict, "backup")
    print("\nBackup created")


def command_load_backup(program_data_dict):
    print("\nLoading backup...\n")
    remove_obsidian_dir_content(program_data_dict)
    print("Obsidian content removed")
    with ZipFile(program_data_dict["backup_zipfile_loc"], "r") as zipfile:
        zipfile.extractall(program_data_dict["obsidian_dir"])
    print("Archive extracted into obsidian directory")
    print("\nBackup loaded")
