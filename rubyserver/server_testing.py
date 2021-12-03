"""
Welcome to the server_testing.py module.

In the Testing class, we will be experimenting the features in the Ruby server. Take a look at the docstrings to see
what each is supposed to do.
"""
import requests

# TODO: Create the new user stuff.


class Testing:
    def __init__(self):
        self.root = "https://ruby-weight-management.herokuapp.com"

    def test1(self, user_id="759499444533067836"):
        """
        Purpose: To successfully get the weight from a user.

        Expected result: Printing the weight data to the terminal.
        """
        testing_route = f"/weight-{user_id}/"

        response = requests.get(f"{self.root}{testing_route}")

        print("PURPOSE: To successfully get the weight from a user.\n")
        print(f"Weight data for user_id of {user_id}.")
        print(f"Testing route: {self.root}{testing_route}\n")

        print(f"Data:\n{response.text}")

    def test2(self):
        """
        Purpose: To successfully update the weight for a user.

        Expected result: Getting a successful status code and printing the weight data for the user.
        """
        testing_route = "/update-weight/"
        testing_data = {
            "user_id": "759499444533067836",
            "weight": "190"
        }

        response = requests.post(f"{self.root}{testing_route}", json=testing_data)

        print("PURPOSE: To successfully update the weight for a user.\n")
        print(f"Weight data for user_id of 759499444533067836.")
        print(f"Testing route: {self.root}{testing_route}\n")
        print(f"Testing data: {testing_data}")

        print(f"Status: {response.json()['status']}")
        print(f"Data:\n{response.text}")

    def test3(self):
        """
        Purpose: To get an error due to the lack of "user_id".

        Expected result: An error on the terminal.
        """
        testing_route = "/update-weight/"
        testing_data = {
            "weight": "190"
        }

        response = requests.post(f"{self.root}{testing_route}", json=testing_data)

        print("PURPOSE: To get an error due to the lack of 'user_id'.\n")
        print(f"No user_id provided.")
        print(f"Testing route: {self.root}{testing_route}\n")
        print(f"Testing data: {testing_data}")

        print(f"{response.json()['status']}")
        print(f"Data:\n{response.text}")

    def test4(self):
        """
        Purpose: To get an error due to the lack of "weight".

        Expected result: An error on the terminal.
        """
        testing_route = "/update-weight/"
        testing_data = {
            "user_id": "759499444533067836",
        }

        response = requests.post(f"{self.root}{testing_route}", json=testing_data)

        print("PURPOSE: To get an error due to the lack of 'weight'.\n")
        print(f"Weight data for user_id of 759499444533067836.")
        print(f"Testing route: {self.root}{testing_route}\n")
        print(f"Testing data: {testing_data}")

        print(f"{response.json()['status']}")

    def test5(self):
        """
        Purpose: To get an error due to an extra key.

        Expected result: An error on the terminal.
        """
        testing_route = "/update-weight/"
        testing_data = {
            "user_id": "759499444533067836",
            "weight": "190",
            "extra key uwu": "sodngljn"
        }

        response = requests.post(f"{self.root}{testing_route}", json=testing_data)

        print("PURPOSE: To get an error due to an extra key.\n")
        print(f"Weight data for user_id of 759499444533067836.")
        print(f"Testing route: {self.root}{testing_route}\n")
        print(f"Testing data: {testing_data}")

        print(f"{response.json()['status']}")
        print(f"Data:\n{response.text}")

    def test6(self):
        """
        Purpose: To get an error because a user does not exist.

        Expected result: Printing the error data to the terminal.
        """
        testing_route = "/weight-dumpywumpy/"

        response = requests.get(f"{self.root}{testing_route}")

        print("PURPOSE: To get an error because a user does not exist.\n")

        print(f"Weight data for user_id of 759499444533067836.")
        print(f"Testing route: {self.root}{testing_route}\n")

        print(f"Data:\n{response.text}")

    def test7(self):
        """
        Purpose: To successfully create a new user.

        Expected result: A new user to be created. Soon after, test1 with the new ID will run.
        """
        testing_route = "/new-user/"
        testing_data = {"user_id": "34098523890"}

        response = requests.post(f"{self.root}{testing_route}", json=testing_data)

        print("PURPOSE: To successfully create a new user.\n")

        print(f"Data:\n{response.text}")
        print("-" * 20)
        Testing().test1(user_id="34098523890")

"""
print("-" * 20)
Testing().test1()
print("-" * 20)
Testing().test2()
print("-" * 20)
Testing().test3()
print("-" * 20)
Testing().test4()
print("-" * 20)
Testing().test5()
print("-" * 20)
Testing().test6()
print("-" * 20)
Testing().test7()
"""