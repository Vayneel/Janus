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


def main():
    program_data = get_program_data(False)
    if not program_data:
        return

    print(get_local_ip())
    ip = input("Enter IPv4 address, you see on your server: ")

    print("\nConnecting to the server...", end="")
    connection = socket_startup(ip, False)
    print("success")

    while 1:
        command = input("\nEnter command (push, pull, create-backup, load-backup, exit): ").lower()
        if command in ("push", "pull", "create-backup", "load-backup", "exit"):
            break
        print("Unknown command. Try again")

    connection.send(command.encode())

    match command:
        case "push":
            command_push_pull(connection, program_data, "send")
        case "pull":
            command_push_pull(connection, program_data, "recv")
        case "create-backup":
            command_create_backup(program_data)
        case "load-backup":
            command_load_backup(program_data)
        case "exit":
            connection.close()


if __name__ == "__main__":
    main()

