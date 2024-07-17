import socket
import os
import datetime
import threading
import json
import sys
import ctypes
from io import BytesIO
from general import *


def handler(connection, address):
    print(f"\nClient connected with {address[0]}:{address[1]}")
    client_status = connection.recv(64)
    print(client_status.decode())

    while 1:
        command = input("\nEnter command (push, pull, create-backup, load-backup, exit): ").lower()
        if command == "exit":
            return
        elif command in ("push", "pull", "create-backup", "load-backup"):
            break
        print("Unknown command. Try again")

    connection.send(command.encode())


if __name__ == "__main__":
    global program_data
    program_data = get_program_data(True)
    if program_data:
        s = socket_startup(True)
        s.listen()
        conn, addr = s.accept()
        handler(conn, addr)
