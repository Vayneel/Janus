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

#
# try:
#     obsidian_dir = get_obsidian_dir(False)
#     sock = socket_startup(False)
#
#     sock.recv(2)
#     print(f'Connected')
#
#
#
# except Exception as e:
#     print(e)


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


async def main():
    # obsidian_dir = get_obsidian_dir(False)  # todo
    obsidian_dir = get_obsidian_dir(True)
    if not obsidian_dir:
        return print(obsidian_dir)
    print("Obsidian found")

    reader, writer = await asyncio.open_connection(host='localhost', port=23323)

    print("Connected")
    print_write(writer, "Client is ready\n")
    print("-" * 30 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

