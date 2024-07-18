from general import *


def server_push(connection, program_data_dict):
    print("\nReceiving zip archive...\n")
    zipfile_bytes = gather_zipfile(connection)
    print("\nBytes received")
    with open(program_data_dict["received_zipfile_loc"], "wb") as zipfile:
        zipfile.write(zipfile_bytes.getvalue())
    print("Archive created")
    remove_obsidian_dir_content(program_data_dict)
    print("Obsidian content removed")
    with ZipFile(program_data_dict["received_zipfile_loc"], "r") as zipfile:
        zipfile.extractall(program_data_dict["obsidian_dir"])
    print("Archive extracted into obsidian directory")


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
