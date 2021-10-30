#########################
#     Chat Project      #
#       User.py         #
#    By: Yuval Cohen    #
#    Date: 4.4.21       #
#########################

class User:
    def __init__(self, soc, address, nickname, room, key):
        """
        The builder Method of the User Class.
        :param soc: The Socket object of the user.
        :param address: The Address of the user.
        :param nickname: The nickname of the user.
        :param room: The room number of the user.
        """
        self.soc = soc
        self.address = address
        self.nickname = nickname
        self.room = room
        self.key = key

    def get_name(self):
        """
        The Method returns the nickname of the user.
        """
        return self.nickname

    def get_soc(self):
        """
        The Method returns the Socket Object of the user.
        """
        return self.soc

    def get_address(self):
        """
        The Method returns the address of the user.
        :return:
        """
        return self.address

    def get_room(self):
        """
        The Method returns the room number of the user.
        """
        return self.room

    def get_key(self):
        """
        This Method return the user's key.
        """
        return self.key

    def set_room(self, room):
        """
        The Method Setting a new room number for the user.
        :param room: int | The new room number.
        """
        self.room = room

    def __str__(self):
        return f"Nickname: {self.nickname} | Address: {self.address}"
