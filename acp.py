import os
from functools import reduce
from hashlib import md5
from Crypto.Util import number

"""
'A Practical and Flexible Key Management Mechanism
For Trusted Collaborative Computing'
X. Zou, et. al.
https://ieeexplore.ieee.org/document/4509697
"""


class User:
    def __init__(self, username, password):
        self.username = username
        self.__password = password

    def get_SID(self):
        return md5(self.__password.encode("utf-8")).hexdigest()


class ACP:
    def __init__(self, role, users):
        self.role = role
        self.users = users
        self.z = hex(number.getRandomInteger(128))
        self.q = hex(number.getPrime(128))
        self.__A_x = self.__get_A_x()
        self.__K = hex(number.getRandomInteger(128))

    def __get_A_x(self):
        A_x = []
        for user in self.users:
            message = user.get_SID() + self.z
            A_x.append(md5(message.encode("utf-8")).hexdigest())
        return A_x

    def get_P_x(self, SID):
        message = SID + self.z
        x = md5(message.encode("utf-8")).hexdigest()

        P_x = reduce(lambda x, y: x * y,
                     [int(x, 16) - int(val, 16) for val in self.__A_x])
        P_x = (P_x + int(self.__K, 16)) % int(self.q, 16)
        return hex(P_x)

    def __update_secret(self):
        self.__K = hex(number.getRandomInteger(128))

    def remove_user(self, username):
        idx = -1
        for i, user in enumerate(self.users):
            if user.username == username:
                idx = i
        if idx > -1:
            self.users = self.users.pop(idx)
        self.__get_A_x()
        self.__update_secret()
