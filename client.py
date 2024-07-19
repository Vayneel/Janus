from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from general import *

# program_data = get_program_data(False)  # todo
program_data = get_program_data(True)
if not program_data:
    raise FileNotFoundError
connection: socket


class MainWindow(Screen):
    @staticmethod
    def push_button_pressed():
        global connection, program_data
        connection.send(b"push")
        command_push_pull(connection, program_data, "send")

    @staticmethod
    def pull_button_pressed():
        global connection, program_data
        connection.send(b"pull")
        command_push_pull(connection, program_data, "recv")

    @staticmethod
    def cb_button_pressed():
        global connection, program_data
        connection.send(b"create-backup")
        command_create_backup(program_data)

    @staticmethod
    def lb_button_pressed():
        global connection, program_data
        connection.send(b"load - backup")
        command_load_backup(program_data)


class ConnectToServerWindow(Screen):
    global program_data
    ip_input = ObjectProperty(None)
    try:
        last_ip = program_data["last_ip"]
    except KeyError:
        last_ip = ""

    def connect_button_pressed(self):
        global connection
        program_data["last_ip"] = self.ip_input.text
        with open("data.json", "w") as datafile:
            json.dump(program_data, datafile)
        connection = socket_startup(self.ip_input.text, False)


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("kivy.kv")


class ClientApp(App):
    def build(self):
        return kv


if __name__ == "__main__":
    ClientApp().run()
