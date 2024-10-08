from general import *


def get_local_ip():
    try:
        get_local_ip_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        get_local_ip_socket.connect(('8.8.8.8', 80))
        local_ip = get_local_ip_socket.getsockname()[0]
        get_local_ip_socket.close()
    except Exception:
        local_ip = '127.0.0.1'
    return local_ip


def handler(connection, address, program_data_dict: dict):
    print(f"\nClient connected with {address[0]}:{address[1]}")

    while 1:
        command = connection.recv(16)
        print(f"\nCommand from client: <{command.decode()}>")
        print("\nExecuting command...")

        match command.decode():
            case "push":
                command_push_pull(connection, program_data_dict, "recv")
            case "pull":
                command_push_pull(connection, program_data_dict, "send")
            case "create-backup":
                command_create_backup(program_data_dict)
            case "load-backup":
                command_load_backup(program_data_dict)
            case _:
                raise KeyboardInterrupt

        print("\nCommand executed")


if __name__ == "__main__":
    program_data = get_program_data(True)
    ip = get_local_ip()
    print(f"Your IPv4 address: {ip}")
    if program_data:
        s = socket_startup(ip, True)
        s.listen()
        try:
            handler(*s.accept(), program_data_dict=program_data)
        finally:
            s.close()
