from general import *


def server_push(connection, program_data_dict):
    remove_obsidian_dir_content(program_data_dict)
    # zipfile_bytes = gather_zipfile(connection)
    # with open(program_data_dict["received_zipfile_loc"], "wb") as zipfile:
    #     zipfile.write(zipfile_bytes)


def handler(connection, address):
    print(f"\nClient connected with {address[0]}:{address[1]}")

    command = connection.recv(16)
    print(f"\nCommand from client: <{command.decode()}>")
    print("\nExecuting command...")

    match command.decode():
        case "push":
            server_push(connection, program_data)
        case "pull":
            pass
        case "create-backup":
            pass
        case "load-backup":
            pass

    print("\nCommand executed")


if __name__ == "__main__":
    global program_data
    program_data = get_program_data(True)
    if program_data:
        s = socket_startup(True)
        s.listen()
        handler(*s.accept())
