"""
Welcome to the server_testing.py module.

In the Testing class, we will be experimenting the features in the Ruby server. Take a look at the docstrings to see
what each is supposed to do.
"""
import requests
from requests.auth import HTTPBasicAuth
import random


class Testing:
    def __init__(self):
        self.root = "http://127.0.0.1:5000"

    def test1(self):
        full = f"{self.root}/api/weight/759499444533067836/2021-11/"

        response = requests.get(full, auth=HTTPBasicAuth('759499444533067836', '441022'))
        print(response.text)

    def test2(self):
        full = f"{self.root}/api/new-user/"

        response = requests.post(full, json={"user_id": str(random.randint(1000000000, 9999999999)), "passcode": str(random.randint(100000, 999999))})
        print(response.text)


Testing().test2()
