from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
import sys


class ChatMember:
    def __init__(self, name, sender_info):
        self.name = name
        self.sender_info = sender_info
        self.messages = []

    def add_message(self, message):
        self.messages.append(message)

    def delete_messages(self):
        self.messages = []

    def send_messages(self, s):
        temp = "\n".join(self.messages)
        s.sendto(temp.encode(), self.sender_info)
        self.delete_messages()

    def change_name(self, new_name):
        self.name = new_name

    def get_name(self):
        return self.name

    def get_sender_info(self):
        return self.sender_info


class Server:
    def __init__(self, source_ip, source_port):
        self._source_ip = source_ip
        self._source_port = source_port
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind((self._source_ip, self._source_port))
        self.messages = []
        # holds sender_info: chat_member
        self.user_dict = {}

    def run(self):
        while True:
            data, sender_info = self.socket.recvfrom(2048)
            self.handle_message(data.decode(), sender_info)

    def check_if_valid(self, command, message, sender_info):
        error = ""
        if sender_info not in self.user_dict.keys() and command is not "1":
            error = "user doesn't exists. Please sign up first"
        elif sender_info not in self.user_dict.keys() and command is "1":
            if len(message) is 0:
                error = "error, sign in command is \"1 [Name]\""
            else:
                return True
        else:
            if command is "1":
                error = "You are already signed in as: " + self.user_dict.get(sender_info).get_name()
            elif command is "2" and len(" ".join(message).strip(" ")) is 0:
                    error = "error, can't send empty messages"
            elif command is "3" and len(message) is 0:
                    error = "error, can't change name to empty string"
            else:
                return True
        self.socket.sendto(error.encode(), sender_info)
        return False


    def handle_message(self, data, sender_info):
        raw_data = data.split(" ")
        command = raw_data.pop(0)
        if not self.check_if_valid(command,raw_data,sender_info):
            return
        # insert new user to DB
        if command is "1":
            names = []
            user_name = " ".join(raw_data)
            for member in self.user_dict.values():
                member.add_message(user_name + " has joined")
                names.append(member.get_name())
            self.user_dict[sender_info] = ChatMember(user_name, sender_info)
            self.socket.sendto(", ".join(names).encode(), sender_info)

        # insert messege from certain user to other user's message queue
        elif command is "2":
            user = self.user_dict.get(sender_info)
            for member in self.user_dict.values():
                if member.get_sender_info() is not user.get_sender_info():
                    member.add_message(user.get_name() + ": " + " ".join(raw_data))
                else:
                    user.send_messages(self.socket)
        # change my name
        elif command is "3":
            new_name = " ".join(raw_data)
            user = self.user_dict.get(sender_info)
            for member in self.user_dict.values():
                if member.get_sender_info() is not user.get_sender_info():
                    member.add_message(user.get_name() + " has changed his name to " + new_name)
            user.change_name(new_name)
            user.send_messages(self.socket)

        # delete user from DB
        elif command is "4":
            user = self.user_dict.get(sender_info)
            for member in self.user_dict.values():
                if member.get_sender_info() is not user.get_sender_info():
                    member.add_message(user.get_name() + " has left the group")
            user.delete_messages()
            user.send_messages(self.socket)
            del self.user_dict[sender_info]


        # get info from server
        elif command is "5":
            user = self.user_dict.get(sender_info)
            user.send_messages(self.socket)

        # illegal request
        else:
            self.socket.sendto("Illegal request".encode(), sender_info)


server = Server('127.0.0.1', 1234)
server.run()
