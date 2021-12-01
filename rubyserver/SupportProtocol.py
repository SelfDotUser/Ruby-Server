import ast
import json
import pytz
from datetime import datetime
import calendar
import pandas as pd
import random


# Keeping this here so that the proper keys are set without struggle.
isPublic = False
toFile = "data.csv"

# TODO: Add a "user check" function that checks whether a user exists w/ a boolean whether or not to create one.
# TODO: Add AWSManager class.


class TimeManager:
    def __init__(self):
        utc_now = pytz.utc.localize(datetime.utcnow())
        self.pst = utc_now.astimezone(pytz.timezone('US/Pacific'))

    def get_date(self):
        """
        Returns the date in the PST timezone. "January 1, 2000" format.
        """
        current_day = self.pst.strftime("%B %d, %Y")

        return current_day

    def get_time(self):
        """
        Returns the current time in the PST timezone. "01:00 AM" format.
        """
        current_time = self.pst.strftime('%I:%M %p')

        return current_time

    @staticmethod
    def get_days_in_month(year: int, month: int):
        """
        Returns the number of days there are in the specified month in the specified year.

        :return: Integer
        """
        return calendar.monthrange(year, month)[1]


class DataManager:
    @staticmethod
    def create_frame():
        """
        This is for developmental purposes only.
        Creates a brand new set for testing.
        """

        def create_new_data():
            return [random.randint(195, 200) for i in range(0, 5)]

        data = pd.DataFrame({
            "Date": ["2021-11-29", "2021-11-30", "2021-12-01", "2021-12-05", "2021-11-10"],
            "Matt": create_new_data(),
            "Carlos": create_new_data(),
            "Ruby": create_new_data()
        })

        data.to_csv(toFile, index=False)

    @staticmethod
    def return_dataframe():
        frame = pd.read_csv(toFile, index_col='Date')

        return frame

    @staticmethod
    def record_weight(data: bytes):
        """
        Records the weight of the individual.
        """
        data = ConvertManager.bytes_to_dictionary(data)
        data_to_return = {}
        successful = True

        # Checking if the data from the server is as specified in the documentation.
        # "user_id" and "weight" are the only and required things that should be in the data.
        if "user_id" not in data:
            data_to_return["status"] = "ERROR: 'user_id' must be included."
            successful = False
        elif "weight" not in data:
            data_to_return["status"] = "ERROR: 'weight' must be included."
            successful = False

        for key in data:
            if key not in ("user_id", "weight"):
                data_to_return["status"] = f"ERROR: '{key}' is unrecognized. Please remove it."
                successful = False

        if not successful:
            return ConvertManager.dictionary_to_bytes(data_to_return)

        user_id = data["user_id"]
        weight = float(data["weight"])

        assert type(weight) is int or type(weight) is float, '"weight" parameter must be either an integer or a float.'

        time = TimeManager().pst

        user_id = user_id if type(user_id) is str else str(user_id)
        day = time.day if time.pst.day >= 10 else f"0{time.pst.day}"
        month = time.pst.month if time.pst.month >= 10 else f"0{time.pst.month}"
        date = f"{time.pst.year}-{month}-{day}"

        dataframe = DataManager.return_dataframe()

        exists = True if date in dataframe.index.values else False

        if not exists:
            for user in dataframe.columns.values:
                dataframe.loc[date, user] = 0.0 if user != user_id else weight
        else:
            dataframe.loc[date, user_id] = weight

        dataframe.to_csv(toFile, index=True, index_label="Date")

        data_to_return["weight"] = DataManager.get_user_weight(user_id, False)
        data_to_return["status"] = "200"

        return ConvertManager.dictionary_to_bytes(data_to_return)

    @staticmethod
    def get_user_weight(user_id: str, convert: bool):
        """
        Returns the weight for the specified user.
        :param user_id: String
        :param convert: Boolean, specify if you want it converted or not.
        :return: Dictionary of the data for the specified user.
        """
        assert type(user_id) is str, 'For performance, please set "user_id" to a string.'

        frame = DataManager.return_dataframe()
        dates = frame.index.values
        data = {}

        for index, value in enumerate(frame.loc[:, user_id]):
            data[dates[index]] = value

        if convert:
            return ConvertManager.dictionary_to_bytes(data)
        else:
            return data


class ConvertManager:
    """
    Converts from bytes to dictionary and vice versa.
    """

    @staticmethod
    def bytes_to_dictionary(data_to_convert: bytes):
        """
        Converts bytes into a dictionary.
        :param data_to_convert: Bytes
        :return: Dictionary
        """

        return ast.literal_eval(data_to_convert.decode('utf-8'))

    @staticmethod
    def dictionary_to_bytes(data_to_convert: dict):
        """
        Converts dictionary into bytes.
        :param data_to_convert: Dictionary
        :return: Bytes
        """

        return json.dumps(data_to_convert, indent=2).encode('utf-8')


print(DataManager.get_user_weight("Carlos"))
