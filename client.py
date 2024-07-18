import socket
import os
import datetime
import threading
import json
import sys
import ctypes
import asyncio
from io import BytesIO
from general import *


async def example(reader, writer):
    for i in range(10):
        writer.write(f"test {i}".encode())
        await writer.drain()

    if writer.can_write_eof():
        writer.write_eof()

    data_from_server = BytesIO()

    try:
        while 1:
            data = await asyncio.wait_for(reader.read(8192), timeout=4.0)
            data_from_server.write(data)
            if reader.at_eof():
                break
            print(data_from_server.getvalue().decode())
    except ConnectionAbortedError:
        print("Server timed out connection")
        writer.close()
    except (asyncio.CancelledError, asyncio.TimeoutError):
        print("Server timed out connection")
        writer.close()


def client_push(connection, program_data):
    # zip_obsidian(False)  # todo
    zipfile_size = zip_obsidian(program_data)
    connection.send(zipfile_size.to_bytes(64, "big"))

    with open(program_data["zipfile_loc"], "rb") as zipfile:
        connection.send(zipfile.read())


def main():
    # program_data = get_program_data(False)  # todo
    program_data = get_program_data(True)
    if not program_data:
        return

    print("\nConnecting to the server...", end="")
    connection = socket_startup(False)
    print("success")

    while 1:
        command = input("\nEnter command (push, pull, create-backup, load-backup, exit): ").lower()
        if command == "exit":
            connection.close()
            return
        elif command in ("push", "pull", "create-backup", "load-backup"):
            break
        print("Unknown command. Try again")

    connection.send(command.encode())

    match command:
        case "push":
            # client_push(connection, program_data)
            pass
        case "pull":
            pass
        case "create-backup":
            pass
        case "load-backup":
            pass


if __name__ == "__main__":
    main()

