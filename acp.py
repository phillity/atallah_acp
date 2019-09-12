import os
import numpy as np
from itertools import combinations
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
    def _init_(self, secret):
        self.z = hex(number.getRandomInteger(128))
        self.q = hex(number.getPrime(128))
        self.__K = secret
        self.coefficients = []

        # Make sure key value is smaller than prime used for modulo
        while int(self.__K, 16) >= int(self.q, 16):
            self.q = hex(number.getRandomInteger(128))

    def get_coefficients(self, users):
        SIDs = []
        for user in users:
            message = user.get_SID() + self.z
            SIDs.append(-int(md5(message.encode("utf-8")).hexdigest(), 16))
        coefficients = []
        coefficients.append(1)
        iq = int(self.q, 16)
        for i in range(0, len(SIDs)):
            coefficients.append(0)
            for j in range(1, len(coefficients)):
                coefficients[len(coefficients) - j] = coefficients[len(coefficients) - j] + coefficients[len(coefficients) - j - 1] * SIDs[i] % iq

        coefficients[-1] = (coefficients[-1] +
                            int(self.__K, 16)) % iq
        self.coefficients = coefficients
        return coefficients

    def evaluate_polynomial(self, SID):
        message = SID + self.z
        x = int(md5(message.encode("utf-8")).hexdigest(), 16)
        cur = 1
        res = 0
        iq = int(self.q, 16)
        for i in range(0, len(self.coefficients)):
            res = (res + cur * self.coefficients[len(self.coefficients) - 1 - i] % iq) % iq
            cur = cur * x % iq
        return hex(res)[2:]

    """
    def __update_secret(self):
        self.__K = hex(number.getRandomInteger(128))

    def remove_user(self, username):
        idx = -1
        for i, user in enumerate(self.users):
            if user.username == username:
                idx = i
        if idx > -1:
            self.users = self.users.pop(idx)
        self.__update_secret()
        self.__get_coefficients()
    """
