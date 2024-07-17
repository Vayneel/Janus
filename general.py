import os
import socket
import json
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

    os.makedirs(janus_temp_dir, exist_ok=True)

    data_dict = {"obsidian_dir": obsidian_dir, "program_dir": janus_temp_dir}

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


def zip_obsidian(mode):
    print("\nCreating zip archive...\n")

    if not os.path.exists('data.json'):
        raise FileNotFoundError

    with open('data.json') as data_file:
        program_data = json.load(data_file)
    zipfile_dir = program_data["program_dir"] + ("\\" if mode else "/") + "JanusObsidianArchive.zip"

    current_dir = os.getcwd()
    os.chdir(program_data["obsidian_dir"])

    with ZipFile(zipfile_dir, "w") as zipf:
        for root, dirs, files in os.walk("."):
            for file in files:
                path = os.path.join(root, file)
                zipf.write(path)
                print(f"file added to archive > {path}")

    os.chdir(current_dir)

    print("\nZip archive created")
