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
            command_push(connection, program_data, "send")
        case "pull":
            command_push(connection, program_data, "recv")
        case "create-backup":
            pass  # todo
        case "load-backup":
            pass


if __name__ == "__main__":
    main()

