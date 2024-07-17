"""
Desktop part
"""

import socket
import json
import os
import shutil
from random import choices
from zipfile import ZipFile

with open('data/settings.json') as settings_file:
    settings = json.load(settings_file)


def create_dir_for_zipfile() -> str:
    directory = settings['zip_loc'].split('/')
    directory[-2] = ''.join(choices('!@#$%^&1234567890qwertyuiopasdfghjklzxcvbnm', k=16))
    os.mkdir('/'.join(directory[:-1]))
    directory = '/'.join(directory)
    return directory


def remove_zip_with_dir(zipfile) -> None:
    """
    Remove zip from client's machine
    :return: None
    """
    print('Removing zip and it\'s directory...', end='')
    directory = '/'.join(zipfile.split('/')[:-1])
    if os.path.exists(zipfile):
        os.remove(zipfile)
    if os.path.exists(directory):
        os.rmdir(directory)
    print('done.')


def zip_dir(path: str, ziph: ZipFile) -> None:
    """
    Zip a directory
    :param path: path to the directory you want to zip
    :param ziph: zipfile object
    :return: None
    """
    default_dir = os.getcwd()
    os.chdir('/'.join(path.split('/')[0:-1]) + '/')
    for root, dirs, files in os.walk(path.split('/')[-1]):
        for file in files:
            ziph.write(os.path.join(root, file))
    os.chdir(default_dir)


def gather_data(connection: socket.socket) -> bytes:
    """
    Gather data (zip file) by slices
    :param connection: connection to the server or the client
    :return: packet of bytes
    """
    file_size = int.from_bytes(connection.recv(16), 'big')
    packet = b""

    while len(packet) < file_size:
        if file_size - len(packet) > 8192:
            buffer = connection.recv(8192)
        else:
            buffer = connection.recv(file_size - len(packet))

        if not buffer:
            raise Exception("Incomplete file received")

        packet += buffer

    return packet


def unpack_data(directory: str) -> None:
    """
    Delete your previous obsidian dir and replace it with extracted dir
    :param directory: directory with zipped files
    :return: None
    """
    print('Extracting...', end='')
    shutil.rmtree(settings['obsidian_dir'], ignore_errors=True)
    with ZipFile(directory, 'r') as zip_file:
        zip_file.extractall('/'.join(settings['obsidian_dir'].split('/')[:-1]))
    print('done')


def client_downloading(serv_connection: socket.socket) -> None:
    print("Downloading...", end='')
    directory = create_dir_for_zipfile()
    with open(directory, 'wb') as zip_file:
        zip_file.write(gather_data(serv_connection))
    print('done')
    serv_connection.send(b'done')
    unpack_data(directory)
    remove_zip_with_dir(directory)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(eval(settings['address']))

zip_directory = "C:/!@#$!@#$!@#$!@#$/!@#$.zip"

try:
    while 1:
        sock.recv(2)  # just to check if connected
        username = settings['username'][:16]
        sock.send(username.encode())
        query = input("Enter query (upload/download/rollback/exit): ").lower()
        if query not in ("upload", "download", "rollback", "exit"):
            sock.send(query[:8].encode())
            if query == '/exit' and username == 'Vayneel':
                break
            print("Incorrect query. Try again")
            continue

        sock.send(query.encode())  # if query is correct, sending it to server

        if query == 'upload':
            print("Uploading...", end='')

            zip_directory = create_dir_for_zipfile()
            with ZipFile(zip_directory, 'w') as zipf:
                zip_dir(settings['obsidian_dir'], zipf)

            sock.send(os.path.getsize(zip_directory).to_bytes(16, 'big'))

            with open(zip_directory, "rb") as zipf:
                sock.send(zipf.read())

            print(sock.recv(4).decode())  # answer if uploaded (done)

            remove_zip_with_dir(zip_directory)

        elif query == 'download':
            client_downloading(sock)

        elif query == 'rollback':
            print(sock.recv(512).decode())
            answer = 0
            count = int.from_bytes(sock.recv(2), 'big')
            while answer <= 0 or answer > count:
                try:
                    answer = input("Your choice (exit to leave): ")
                    if answer == 'exit':
                        break
                    answer = int(answer)
                except ValueError:
                    continue
            sock.send(str(answer).encode())
            if answer != 'exit':
                client_downloading(sock)

        elif query == 'exit':
            print("Exiting...")
            sock.close()
            remove_zip_with_dir(zip_directory)
            break

except socket.error as e:
    print('Unable to connect to server')
    print(e)
    remove_zip_with_dir(zip_directory)
