#########################
#     Chat Project      #
#       Server.py       #
#    By: Yuval Cohen    #
#    Date: 4.4.21       #
#########################

import socket
from Protocols import *
import select
from cryptography.fernet import Fernet
from User import User
from Room import Room
import threading
import random


class Server:
    def __init__(self, HOST="0.0.0.0", PORT=6868):
        """
        Builder method to the Server class.
        :param HOST: The Host of the server.
        :param PORT: The Port of the server.
        """
        self.soc = socket.socket()
        self.address = (HOST, PORT)
        self.socks = [self.soc]
        self.users = []
        self.rooms = [Room(0)]

    def Start_Server(self):
        """
        The function is doing the server job, handling with the clients and transferring the messages between them.
        """
        self.soc.bind(self.address)
        self.soc.listen(5)
        print("Server Running...")

        while True:

            readables, _, _ = select.select(self.socks, [], [], 0)

            for soc in readables:
                if soc is self.soc:
                    threading.Thread(target=self.__receive_client).start()

                else:
                    user = self.__Find_User(soc)
                    try:
                        message = Receive_Message(soc, user.get_key())
                        if not self.__Check_Special_Commands(message, user):
                            self.__broadcast(f"{user.get_name()}: {message}",
                                             self.__Get_RoomIndByNumber(user.get_room()))

                    except:  # Client disconnected
                        print(f"\n>>> {user.get_name()} has been disconnected from the chat <<<\n")
                        soc.close()
                        self.socks.remove(soc)
                        self.users.remove(user)
                        room_number = user.get_room()
                        room_ind = self.__Get_RoomIndByNumber(room_number)

                        self.rooms[room_ind].remove_user(user, -1)
                        self.__broadcast(f">>> {user.get_name()} has been disconnected from the chat <<<", room_ind)

    def __broadcast(self, message, room_ind):
        """
        The function is sending a broadcast message that the user sent.
        :param message: The message of the user.
        :param room_number: The room number of the user.
        """
        self.rooms[room_ind].write_to_logs(message)
        clients = self.rooms[room_ind].get_users()
        for client in clients:
            Send_Message(f"\n{message}\n", client.get_soc(), client.get_key())

    def __receive_client(self):
        """
        The function is handling with receiving clients, adding them to the main room and setting for them a nickname"
        """
        client_soc, address = self.soc.accept()
        try:
            print(f"New User Connected: {str(address)}")
            key = Fernet.generate_key()
            client_soc.send(key)

            # Handle Nickname Process
            client_nickname = Receive_Message(client_soc, key)
            while self.__Check_Nickname(client_nickname):
                Send_Message("already in use", client_soc, key)
                client_nickname = Receive_Message(client_soc, key)
            Send_Message("agreed", client_soc, key)

            # Room number 0 is the main room
            user = User(client_soc, address, client_nickname, 0, key)
            self.__broadcast(f">>> {client_nickname} has been connected to the server !<<<", 0)
            self.users.append(user)
            self.socks.append(client_soc)
            self.rooms[0].add_user(user)
            print(f"\n>>> {client_nickname} has been connected to the server !<<<\n")

        except:
            client_soc.close()

    def __Get_RoomIndByNumber(self, room_number):
        """
        The function is searching for the room index in the room list.
        :param room_number: integer | The room number.
        :return: integer | The room index.
        """
        for ind in range(len(self.rooms)):
            if self.rooms[ind].get_room_number() == room_number:
                return ind
        return -1

    def __Check_Special_Commands(self, message, user):
        """
        The function is checking if the user message is a special command.
        Handling with the command.
        :param message: The message of the user.
        :param user: The User object of the user.
        :return: True if the message was Special command, else False.
        """
        if message.lower()[:11] == "/createroom":
            message = message.replace(" ", '')
            try:
                room_number = int(message[11:])
                if room_number in range(1000, 10000):
                    if self.__Get_RoomIndByNumber(room_number) == -1:
                        self.rooms.append(Room(room_number))
                        self.__move_user_room(user, room_number)

                    else:
                        Send_Message("\n>>> This room number is already in use please try other one. <<<\n",
                                     user.get_soc(), user.get_key())
                else:
                    raise
            except:
                if len(message) > 11:
                    Send_Message("\n>>> Command Failed! Try: '/createroom ROOM_NUMBER' <<<\n",
                                 user.get_soc(), user.get_key())
                else:
                    room_number = random.randint(1000, 10000)
                    while self.__Get_RoomIndByNumber(room_number) != -1:
                        room_number = random.randint(1000, 10000)
                    self.rooms.append(Room(room_number))
                    self.__move_user_room(user, room_number)

            return True

        elif message.lower()[:9] == "/joinroom":
            message = message.replace(" ", '')

            try:
                room_number = int(message[9:])
                if self.__Get_RoomIndByNumber(room_number) != -1:
                    self.__move_user_room(user, room_number)
                else:
                    raise
            except:
                if len(message) > 9:
                    Send_Message("\n>>> This room number doesn't exist. <<<\n", user.get_soc(), user.get_key())
                else:
                    Send_Message("\n>>> You need to write a room number! <<<\n", user.get_soc(), user.get_key())

            return True

        elif message.lower() == "/users":
            room_users = self.rooms[self.__Get_RoomIndByNumber(user.get_room())].get_users()
            names = []
            for usr in room_users:
                if usr.get_name() != user.get_name():
                    names.append(usr.get_name())
            if names:
                Send_Message(f"\n>>> {names} <<<\n", user.get_soc(), user.get_key())
            else:
                Send_Message(f"\n>>> The room is currently empty ! <<<\n", user.get_soc(), user.get_key())
            return True

        return False

    def __move_user_room(self, user, room_number):
        """
        The function is moving the user room by removing him from the previous room, adding
        him to the new one and sending notifications in accordance.
        :param user: The User object of the user.
        :param room_number: The room number that the user will join to.
        """
        previous_room = user.get_room()

        prev_room_ind = self.__Get_RoomIndByNumber(previous_room)
        self.rooms[prev_room_ind].remove_user(user, room_number)
        self.__broadcast(f">>> {user.get_name()} has been disconnected from the room ! <<<", prev_room_ind)

        room_ind = self.__Get_RoomIndByNumber(room_number)
        self.__broadcast(f">>> {user.get_name()} has been connected to the room ! <<<", room_ind)

        self.rooms[room_ind].add_user(user)

        if room_number != 0:
            Send_Message(f"\n>>> You have connected to room number {room_number} ! <<<\n", user.get_soc(),
                         user.get_key())
        else:
            Send_Message(f"\n>>> You have connected to the main room! <<<\n", user.get_soc(),
                         user.get_key())

        if previous_room != 0 and len(self.rooms[prev_room_ind].get_users()) == 0:  # Deletes the room if it's empty
            del self.rooms[prev_room_ind]

    # Simple Help Functions

    def __Check_Nickname(self, nickname):
        """
        Help Function. That checking if the nickname the client choose is already in use.
        :param nickname: the nickname that the client choose.
        :return: True if the nickname is already in use, else False.
        """
        for user in self.users:
            if user.get_name().lower() == nickname.lower():
                return True
        return False

    def __Find_User(self, soc):
        """
        Help Function. That searching the User object by his socket object.
        :param soc: The socket object of the client.
        :return: The User object of the client.
        """
        for user in self.users:
            if user.get_soc() == soc:
                return user


def main():
    server = Server()
    server.Start_Server()



if __name__ == '__main__':
    main()
