import ast
import json
import pytz
from datetime import datetime
import calendar
import pandas as pd
import random
from dotenv import load_dotenv
import os
import boto3
import io


isPublic = True

if not isPublic:
    load_dotenv()

# TODO: Remove this after finished beta testing.
load_dotenv()

toFile = os.getenv("NAME_OF_CSV")


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


class AWSManager:
    def __init__(self):
        """
        Initiate AWS S3 credentials.
        """
        self.s3 = boto3.resource(
            service_name='s3',
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )

        self.bucket_name = os.getenv("BUCKET_NAME")

    def update_file(self, file: str, data, type_of: str):
        """
        Gets content from a file, deletes the original, and uploads the updated version.
        :param file: Name of file.
        :param data: Dictionary of updated data.
        :param type_of: Type of file. Can either be "str" or "dict".
        """
        types = ("str", "dict")

        assert type(type_of) is str, '"type_of" must be a string.'
        assert type_of in types, '"type_of" must either be "str" or "dict".'

        bytes_data = self.s3.Bucket(self.bucket_name).Object(file).get()['Body'].read()

        if type_of == "dict":
            dictionary = ConvertManager().bytes_to_dictionary(bytes_data)

            dictionary.update(data)

            self.s3.Bucket(self.bucket_name).Object(file).delete()
            data_for_aws = ConvertManager().dictionary_to_bytes(dictionary)

            self.s3.Bucket(self.bucket_name).put_object(Key=file, Body=data_for_aws)

        elif type_of == "str":
            self.s3.Bucket(self.bucket_name).Object(file).delete()
            data_for_aws = ConvertManager().string_to_bytes(data)

            self.s3.Bucket(self.bucket_name).put_object(Key=file, Body=data_for_aws)

    def get_file(self, file: str, type_of: str):
        """
        Returns the content of a file.
        :param file: Name of file.
        :param type_of: The type of file we need. Can be "dict" or "str".
        :return: Dictionary
        """
        types = ("str", "dict")

        assert type(type_of) is str, '"type_of" must be a string.'
        assert type_of in types, '"type_of" must either be "str" or "dict".'

        bytes_data = self.s3.Bucket(self.bucket_name).Object(file).get()['Body'].read()

        if type_of == "dict":
            return ConvertManager().bytes_to_dictionary(bytes_data)
        elif type_of == "str":
            return ConvertManager().bytes_to_string(bytes_data)


class DataManager:
    @staticmethod
    def create_frame():
        """
        This is for developmental purposes only.
        Creates a brand new set for testing.
        """
        assert not isPublic, '"isPublic" is set to True. This is a development function.'

        def create_new_data():
            return [random.randint(180, 200) for i in range(0, 5)]

        frame = pd.DataFrame({
            "Date": ["2021-11-29", "2021-11-30", "2021-12-01", "2021-12-05", "2021-11-10"],
            "Matt": create_new_data(),
            "Carlos": create_new_data(),
            "Ruby": create_new_data()
        })

        frame.to_csv(toFile, index=False)

    @staticmethod
    def return_dataframe():
        if isPublic:
            data_string = AWSManager().get_file(toFile, "str")
            f = io.StringIO(data_string)
            frame = pd.read_csv(f, index_col='Date')
            f.close()
        else:
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
        day = time.day if time.day >= 10 else f"0{time.day}"
        month = time.month if time.month >= 10 else f"0{time.month}"
        date = f"{time.year}-{month}-{day}"

        dataframe = DataManager.return_dataframe()

        exists = True if date in dataframe.index.values else False

        if not exists:
            for user in dataframe.columns.values:
                dataframe.loc[date, user] = 0.0 if user != user_id else weight
        else:
            dataframe.loc[date, user_id] = weight

        if not isPublic:
            dataframe.to_csv(toFile, index=True, index_label="Date")
        else:
            AWSManager().update_file(os.getenv("NAME_OF_CSV"), dataframe.to_csv(index=True, index_label="Date"), "str")

        data_to_return = DataManager.get_user_weight(user_id, False)

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

        user_exists = DataManager.user_check(user_id, False)

        if not user_exists:
            data = {"status": f"ERROR: User '{user_id}' is not in the database."}

            if convert:
                return ConvertManager.dictionary_to_bytes(data)
            else:
                return data

        frame = DataManager.return_dataframe()
        dates = frame.index.values
        data = {"weight": {}, "status": 200}

        for index, value in enumerate(frame.loc[:, user_id]):
            data["weight"][dates[index]] = value

        if convert:
            return ConvertManager.dictionary_to_bytes(data)
        else:
            return data

    @staticmethod
    def user_check(user_id: str, create: bool):
        assert type(user_id) is str, '"user_id" must be a string.'
        assert type(create) is bool, '"create" must be a boolean.'

        frame = DataManager.return_dataframe()

        if user_id in frame.columns.values:
            return True
        elif user_id not in frame.columns.values and create:
            length = len(frame.index.values)
            frame[user_id] = [0.0 for i in range(0, length)]

            frame.to_csv(toFile, index=True, index_label="Date")

            return True
        else:
            return False

    @staticmethod
    def new_user(data: bytes):
        dictionary = ConvertManager.bytes_to_dictionary(data)
        user_id = dictionary["user_id"]

        if not DataManager.user_check(user_id, False):
            frame = DataManager.return_dataframe()

            length = len(frame.index.values)
            frame[user_id] = [0.0 for i in range(0, length)]

            if not isPublic:
                frame.to_csv(toFile, index=True, index_label="Date")
            else:
                AWSManager().update_file(toFile, frame.to_csv(index=True, index_label="Date"), "str")

            returning_data = {"status": 200}

            return ConvertManager.dictionary_to_bytes(returning_data)
        else:
            returning_data = {"status": f"ERROR: User {user_id} already exists."}
            return ConvertManager.dictionary_to_bytes(returning_data)


class ConvertManager:
    """
    Converts from bytes to dictionary and vice versa.
    """
    @staticmethod
    def bytes_to_string(data_to_convert: bytes):
        return data_to_convert.decode('utf-8')

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

    @staticmethod
    def string_to_bytes(data_to_convert: str):
        return data_to_convert.encode('utf-8')
