import socket

from general import *


def handler(connection, address):
    print(f"\nClient connected with {address[0]}:{address[1]}")

    command = connection.recv(16)
    print(f"\nCommand from client: <{command.decode()}>")
    print("\nExecuting command...")

    match command.decode():
        case "push":
            command_push_pull(connection, program_data, "recv")
        case "pull":
            command_push_pull(connection, program_data, "send")
        case "create-backup":
            command_create_backup(program_data)
        case "load-backup":
            command_load_backup(program_data)

    print("\nCommand executed")


if __name__ == "__main__":
    global program_data
    program_data = get_program_data(True)
    # print(socket.gethostbyname_ex(socket.gethostname())[2])
    if not program_data:
        s = socket_startup(True)
        s.listen()
        handler(*s.accept())
        s.close()
