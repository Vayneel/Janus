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
#
# async def main():
#     try:
#         obsidian_dir = get_obsidian_dir(True)
#         sock = socket_startup(True)
#
#         sock.listen()
#         conn, addr = await sock.accept()
#         print(f'Connected')
#         conn.send(b"ok")
#
#
#
#     except Exception as e:
#         print(e)
#
#
# if __name__ == "__main__":
#     main()


async def example(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    all_data = BytesIO()

    all_data.write(b"FROM SERVER:\n")

    while 1:
        try:
            data = await asyncio.wait_for(reader.read(8192), timeout=4.0)
            all_data.write(data)
            if reader.at_eof():
                print(f"Received data: \n{all_data.getvalue().decode()}")
                break
        except (asyncio.CancelledError, asyncio.TimeoutError):
            print("Too slow connection aborted")
            break

    writer.write(all_data.getvalue())
    await writer.drain()

    if writer.can_write_eof():
        writer.write_eof()

    writer.close()


async def handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    print("Client connected")

    client_status = asyncio.wait_for(reader.read(64), timeout=4.0)
    print(client_status)


async def main_server():
    server = await asyncio.start_server(
        client_connected_cb=handler,
        host='localhost',
        port=23323,
        family=socket.AF_INET
    )

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    obsidian_dir = get_obsidian_dir(True)
    if not obsidian_dir:
        print(obsidian_dir)
    else:
        print("Obsidian found")
        asyncio.run(main_server())
