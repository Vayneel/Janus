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


async def client_push(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    file_as_bytes = BytesIO()
    while 1:
        data = await asyncio.wait_for(reader.read(8192), timeout=8.0)
        file_as_bytes.write(data)
        if reader.at_eof():
            break


async def main():
    # program_data = get_program_data(False)  # todo
    program_data = get_program_data(True)
    if not program_data:
        return

    print("\nConnecting to the server...", end="")
    reader, writer = await asyncio.open_connection(host='localhost', port=23323)
    print("success")
    await print_write(writer, "\nClient is ready")

    command = await asyncio.wait_for(reader.read(16), timeout=4.0)
    print(f"\nCommand from server: <{command.decode()}>")
    print("\nExecuting command...")

    match command.decode():
        case "push":
            pass
        case "pull":
            pass
        case "create-backup":
            pass
        case "load-backup":
            pass

    print("\nCommand executed")


if __name__ == "__main__":
    asyncio.run(main())

