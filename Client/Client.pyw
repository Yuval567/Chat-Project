#########################
#     Chat Project      #
#       Client.pyw      #
#    By: Yuval Cohen    #
#    Date: 4.4.21       #
#########################

import json
import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from cryptography.fernet import Fernet
from Protocols import *


class Client:
    def __init__(self):
        """
        The builder function of the Client class.
        Setting the class variables and connecting to the server.
        :param IP: The ip of the Server.
        :param PORT: The port of the Server.
        """
        with open("config.json", 'r') as f:
            jsonObj = json.load(f)
            IP = jsonObj["server_address"]
            PORT = jsonObj["server_port"]

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((IP, PORT))
        except:
            exit()

        self.key = self.sock.recv(248)

        self.__set_nickname()
        self.gui_done = False
        self.running = True
        self.temp = []

        threading.Thread(target=self.__start_gui).start()
        threading.Thread(target=self.__receive).start()

    def __start_gui(self):
        """
        The function is building the graphic user interface and the gui loop.
        """

        # The root object of the Tkinter
        self.color = "DodgerBlue1"
        self.root = tkinter.Tk()
        self.root.title("Chat")
        self.root.geometry("1030x690")
        self.root.resizable(False, False)
        self.root.configure(bg=self.color)

        # The title label
        self.chat_label = tkinter.Label(self.root, text="Chat:", bg=self.color, font=("Arial", 8))
        self.chat_label.config(font=("bold", 15))
        self.chat_label.grid(padx=20, pady=5)

        # The text area that will show all the messages
        self.text_area = tkinter.scrolledtext.ScrolledText(self.root, font=("Arial", 15))
        self.text_area.grid(padx=20, ipadx=20, pady=5)
        self.text_area.config(state='disable')

        # The mini title label
        self.msg_label = tkinter.Label(self.root, text="Your Message:", bg=self.color)
        self.msg_label.config(font=("bold italic", 15))
        self.msg_label.grid(padx=3, pady=5)

        # The input area that will input the messages of the user
        self.input_area = tkinter.Text(self.root, height=1, font=("Arial", 15))
        self.input_area.grid(pady=5)
        self.input_area.bind('<Return>', lambda _: self.__send())

        # The button that will call the send function
        self.send_button = tkinter.Button(self.root, text="Send", command=self.__send)
        self.send_button.config(font=("bold", 14))
        self.send_button.place(x=950, y=640)

        self.gui_done = True
        self.__print_message(">>> You have connected to the chat <<<\n")
        self.__print_commands()

        for msg in self.temp:
            self.__print_message(msg)

        self.root.protocol("WM_DELETE_WINDOW", self.__stop)
        self.root.mainloop()

    def __set_nickname(self):
        """
        The function is setting the nickname of the client and communicate with the
        server about the nickname.
        """
        msg = tkinter.Tk()
        msg.withdraw()
        nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)

        while not nickname.lower().islower():  # Checks if the nickname has letters.
            nickname = simpledialog.askstring("Nickname", "The nickname must contain any letters.", parent=msg)

        Send_Message(nickname, self.sock, self.key)
        Check = Receive_Message(self.sock, self.key)
        while Check == "already in use":
            nickname = simpledialog.askstring("Nickname",
                                              "This nickname is already in use. Please choose a different nickname:",
                                              parent=msg)

            while not nickname.lower().islower():  # Checks if the nickname has letters.
                nickname = simpledialog.askstring("Nickname", "The nickname must contain any letters.", parent=msg)

            Send_Message(nickname, self.sock, self.key)
            Check = Receive_Message(self.sock, self.key)

    def __receive(self):
        """
        The function is working on Thread, and receiving the messages that coming
        from the Server and prints them on the chat interface.
        """
        while self.running:
            try:
                message = Receive_Message(self.sock, self.key)
                if self.gui_done:
                    self.__print_message(message)
                else:
                    self.temp.append(message)

            except:
                self.sock.close()
                self.__print_message("\n\n>>> Error! Connection with the server lost! <<<\n")
                break

    def __print_message(self, message):
        """
        The function prints a message to the user on the Text area.
        """
        self.text_area.config(state='normal')
        self.text_area.insert('end', message)
        self.text_area.yview('end')
        self.text_area.config(state='disabled')

    def __print_commands(self):
        """
        The function prints to the user the available commands in the chat.
        """
        self.__print_message("-----------------------------------------------------------------------------------------------------\n"
                             "Special Commands are:\n"
                             "'/createroom ROOM_NUMBER'  - Will create a private room for you and your friends.\n"
                             "The ROOM_NUMBER need to be in range of 1000 - 9999!\nYou don't have to enter a room "
                             "number, we will generate in randomly one for you.\n\n"
                             "'/joinroom ROOM_NUMBER' - Will move you to the selected room if it's exist.\n"
                             "Enter '0' as the ROOM_NUMBER if you wanna return to the main room.\n\n"
                             "'/users' - Will you show the room's online users\n"
                             "'/help' - Will you show all the commands again.\n"
                             "Enjoy :)\n"
                             "-----------------------------------------------------------------------------------------------------\n")

    def __send(self):
        """
        The function is working on reading the input area and sending the message
        from the input area to the server.
        """
        message = str(self.input_area.get('1.0', 'end')).replace('\n', '')
        self.input_area.delete('1.0', 'end')

        if message.lower() == "/help":
            self.__print_commands()

        elif message != '':
            Send_Message(message, self.sock, self.key)

    def __stop(self):
        """
        The function is stopping the program, closing the socket connection
        and the closing the gui.
        """
        self.running = False
        self.sock.close()
        try:
            self.root.destroy()
        except:
            pass


if __name__ == '__main__':
    Client()
