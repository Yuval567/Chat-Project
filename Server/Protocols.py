#########################
#     Chat Project      #
#      Protocols.py     #
#    By: Yuval Cohen    #
#    Date: 4.4.21       #
#########################

from cryptography.fernet import Fernet


def Send_Message(message, soc, key):
    """
    The function is encrypting message and send it to his destination.
    :param message: string | The message.
    :param soc: Socket object | The socket destination.
    """
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    len_message = str(len(encrypted_message)).zfill(3)
    soc.send((len_message.encode() + encrypted_message))


def Receive_Message(soc, key):
    """
    The function is reeving message and decrypting it.
    :param soc: Socket object | the socket
    :return: The message.
    """
    f = Fernet(key)
    len_message = int(soc.recv(3))
    encrypted_message = soc.recv(len_message)
    return f.decrypt(encrypted_message).decode()
