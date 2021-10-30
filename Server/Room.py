#########################
#     Chat Project      #
#       Room.py         #
#    By: Yuval Cohen    #
#    Date: 4.4.21       #
#########################

from datetime import datetime
from os import mkdir


class Room:
    def __init__(self, id):
        """
        The builder Method of the Room Class.
        The Method is also opening a new Logs File for the room.
        :param id: int | The room number.
        """
        self.users = []
        self.id = id

        # Creates the Logs directory
        try:
            mkdir("Logs")
        except:
            pass

        with open(f"Logs\Channel Number {self.id} Logs.txt", "w") as f:
            f.write(f"<---------- Channel Number {self.id} Logs ---------->\n\n")

    def get_users(self):
        """
        Get Method that returning the users list.
        """
        return self.users

    def write_to_logs(self, data):
        """
        The function is working on writing the data to the room logs file.
        :param data: str | The data to write.
        """
        time_now = str(datetime.now())
        time_now = time_now[:time_now.index(".")]
        try:
            with open(f"Logs\\Channel Number {self.id} Logs.txt", "a", encoding="utf-8") as f:
                f.write(time_now + " | " + data + "\n\n")
        except Exception as e:
            print(e)
            print("An error occurred with writing the logs.\nPlease check if the Logs directory exists.")

    def add_user(self, user):
        """
        The Method is adding a new user to the Room users list.
        :param user: User Object of the new user.
        """
        self.users.append(user)
        self.write_to_logs(f">>> Client Connected. {user} <<<")

    def remove_user(self, user, room_number):
        """
        The Method is removing the user from the Room users list
        and setting a New Room for the user.
        :param user: User object to remove.
        :param NewRoom: Int number that present the room id.
        """
        if user in self.users:
            self.users.remove(user)
            user.set_room(room_number)
            self.write_to_logs(f">>> Client has been disconnected. {user} <<<")

    def get_room_number(self):
        return self.id
