import requests
from general import *


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        local_ip = '127.0.0.1'
    return local_ip


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
        case "exit":
            raise KeyboardInterrupt

    print("\nCommand executed")


if __name__ == "__main__":
    global program_data
    program_data = get_program_data(True)
    ip = get_local_ip()
    print(f"Your IPv4 address: {ip}")
    # print(socket.gethostbyname_ex(socket.gethostname())[2])
    if program_data:
        s = socket_startup(ip, True)
        s.listen()
        try:
            handler(*s.accept())
        finally:
            s.close()
