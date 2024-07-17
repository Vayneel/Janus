import os
import socket
import asyncio


def find_obsidian_dir(mode: bool) -> str | bool:  # todo normal
    print("Please, wait. The searching process may take up to 10 minutes")
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
    print("Searching for Obsidian...", end="")

    if os.path.exists('obsidian_dir.md'):
        with open('obsidian_dir.md') as obsidian_dir_file:
            print("found")
            return obsidian_dir_file.readline()

    obsidian_dir = find_obsidian_dir(mode)
    if obsidian_dir:
        write_obsidian_dir(obsidian_dir)
        print("found")
        return obsidian_dir

    print("error")


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


async def print_write(writer: asyncio.StreamWriter, message: str):
    print(message)
    writer.write(message.encode())
    await writer.drain()
