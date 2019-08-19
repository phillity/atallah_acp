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
    def __init__(self, role, users):
        self.role = role
        self.users = users
        self.z = hex(number.getRandomInteger(128))
        self.q = hex(number.getPrime(128))
        self.__K = hex(number.getRandomInteger(128))
        self.coefficients = self.__get_coefficients()

        # Make sure key value is smaller than prime used for modulo
        while int(self.__K, 16) < int(self.q, 16):
            self.__K = hex(number.getRandomInteger(128))

    def __get_coefficients(self):
        SIDs = []
        for user in self.users:
            message = user.get_SID() + self.z
            SIDs.append(-int(md5(message.encode("utf-8")).hexdigest(), 16))

        coefficients = []
        for i in range(0, len(SIDs) + 1):
            SID_comb = combinations(SIDs, i)
            poly_term = 0
            for comb in SID_comb:
                product = 1
                for term in comb:
                    product = (product * term) % int(self.q, 16)
                poly_term = (poly_term + product) % int(self.q, 16)
            coefficients.append(poly_term)

        coefficients[-1] = (coefficients[-1] +
                            int(self.__K, 16)) % int(self.q, 16)

        return coefficients

    def evaluate_polynomial(self, SID):
        message = SID + self.z
        x = int(md5(message.encode("utf-8")).hexdigest(), 16)
        return hex(np.poly1d(self.coefficients)(x) % int(self.q, 16))

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
