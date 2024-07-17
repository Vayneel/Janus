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


# here are examples of asyncio usage
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
    print("\nClient connected")

    client_status = await asyncio.wait_for(reader.read(64), timeout=4.0)
    print(client_status.decode())

    while 1:
        command = input("\nEnter command (push, pull, create-backup, load-backup, exit): ").lower()
        if command == "exit":
            return
        elif command in ("push", "pull", "create-backup", "load-backup"):
            break
        print("Unknown command. Try again")

    await print_write(writer, command)


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
    global program_data
    program_data = get_program_data(True)
    if program_data:
        asyncio.run(main_server())
