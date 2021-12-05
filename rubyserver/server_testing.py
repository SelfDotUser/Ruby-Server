"""
Welcome to the server_testing.py module.

In the Testing class, we will be experimenting the features in the Ruby server. Take a look at the docstrings to see
what each is supposed to do.
"""
import requests
from requests.auth import HTTPBasicAuth


class Testing:
    def __init__(self):
        self.root = "http://127.0.0.1:5000"

    def test1(self):
        full = f"{self.root}/api/weight/759499444533067836/-/"

        response = requests.get(full, auth=HTTPBasicAuth('some_username', 'some_password'))
        print(response.text)


Testing().test1()
