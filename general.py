import os
import socket
import asyncio


def find_obsidian_dir(mode: bool) -> str | bool:  # todo normal
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


def write_obsidian_dir(obsidian_dir):
    with open('obsidian_dir.md', 'w') as file:
        file.write(obsidian_dir)


def get_obsidian_dir(mode: bool):
    if os.path.exists('obsidian_dir.md'):
        with open('obsidian_dir.md') as obsidian_dir_file:
            return obsidian_dir_file.readline()
    obsidian_dir = find_obsidian_dir(mode)
    if obsidian_dir:
        write_obsidian_dir(obsidian_dir)
        return obsidian_dir
    return "Obsidian not found"


def socket_startup(mode: bool):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = ('127.0.0.1', 23323)
    if mode:
        sock.bind(address)
        print('Starting up on 127.0.0.1:23323')
    else:
        sock.connect(address)
        print('Trying to connect to 127.0.0.1:23323')

    return sock


async def get_command(sock: socket.socket):
    await sock.recv(16)


async def send_command(sock: socket.socket):
    while 1:
        command = input("Enter command (push, pull, createbackup, loadbackup, exit):")
        if command in ('push', 'pull', 'createbackup', 'loadbackup'):
            sock.send(command.encode())
            break
        elif command == 'exit':
            break


async def async_command_action(sock):
    async with asyncio.TaskGroup() as tg:
        tg.create_task(get_command(sock))
        tg.create_task(send_command(sock))


def print_write(writer: asyncio.StreamWriter, message: str):
    print(message)
    writer.write(message.encode())
    writer.drain()
