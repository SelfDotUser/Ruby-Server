import ast
import json
import pytz
import datetime
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

toFile: str = os.getenv("NAME_OF_CSV")
toAuth: str = os.getenv("NAME_OF_AUTH")


class TimeManager:
    """
    The TimeManager class keeps track of time. This uses Pacific Standard Time.
    """
    def __init__(self):
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        self.pst: datetime.datetime = utc_now.astimezone(pytz.timezone('US/Pacific'))

    def get_date(self) -> str:
        """
        :return: The date in the PST timezone. "January 1, 2000" format.
        """
        current_day: str = self.pst.strftime("%B %d, %Y")

        return current_day

    def get_time(self) -> str:
        """
        :return: The time in the PST timezone. "01:00 AM" format.
        """
        current_time: str = self.pst.strftime('%I:%M %p')

        return current_time

    def current_month(self) -> str:
        """
        :return: The current month in "xxxx-xx" format.
        """
        month = self.pst.month if self.pst.month >= 10 else f"0{self.pst.month}"
        return f"{self.pst.year}-{month}"

    @staticmethod
    def get_days_in_month(year: int, month: int) -> int:
        """
        :return: The number of days there are in the specified month in the specified year.
        """
        return calendar.monthrange(year, month)[1]


class AWSManager:
    """
    The AWSManager gets/updates files from Amazon Web Services.
    """
    def __init__(self):
        self.s3 = boto3.resource(
            service_name='s3',
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )

        self.bucket_name: str = os.getenv("BUCKET_NAME")

    def update_file(self, file: str, data) -> None:
        """
        Gets content from a file, deletes the original, and uploads the updated version.

        :param file: Name of file
        :param data: Dictionary or string of the data
        """
        assert type(data) in (str, dict), "data must be either str or dict."

        bytes_data: bytes = self.s3.Bucket(self.bucket_name).Object(file).get()['Body'].read()

        if type(data) is dict:
            dictionary: dict = ConvertManager().bytes_to_dictionary(bytes_data)

            dictionary.update(data)

            self.s3.Bucket(self.bucket_name).Object(file).delete()
            data_for_aws: bytes = ConvertManager().to_bytes(dictionary)

            self.s3.Bucket(self.bucket_name).put_object(Key=file, Body=data_for_aws)

        elif type(data) is str:
            self.s3.Bucket(self.bucket_name).Object(file).delete()
            data_for_aws: bytes = ConvertManager().to_bytes(data)

            self.s3.Bucket(self.bucket_name).put_object(Key=file, Body=data_for_aws)

    def get_file(self, file: str) -> bytes:
        """
        :param file: Name of file

        :return: The data in bytes
        """
        bytes_data: bytes = self.s3.Bucket(self.bucket_name).Object(file).get()['Body'].read()

        return bytes_data


class DataManager:
    """
    The DataManager keeps track of data within the SupportProtocol.
    """
    @staticmethod
    def create_frame() -> None:
        """
        This is for developmental purposes only. Creates a brand new set for testing.
        """
        assert not isPublic, '"isPublic" is set to True. This is a development function.'

        def create_new_data():
            return [random.randint(180, 200) for _ in range(0, 5)]

        frame = pd.DataFrame({
            "Date": ["2021-11-29", "2021-11-30", "2021-12-01", "2021-12-05", "2021-11-10"],
            "Matt": create_new_data(),
            "Carlos": create_new_data(),
            "Ruby": create_new_data()
        })

        frame.to_csv(toFile, index=False)

    @staticmethod
    def return_dataframe() -> pd.DataFrame:
        """
        Converts a .csv from AWS and makes it into a DataFrame object.

        :return: DataFrame object of the AWS user weight data
        """
        if isPublic:
            data_string: str = ConvertManager.bytes_to_string(AWSManager().get_file(toFile))
            f = io.StringIO(data_string)
            frame = pd.read_csv(f, index_col='Date')
            f.close()
        else:
            frame = pd.read_csv(toFile, index_col='Date')

        return frame

    @staticmethod
    def record_weight(data: bytes, passcode: str) -> bytes:
        """
        Records the weight of the individual.

        :param data: JSON data given from the outside world
        :param passcode: User passcode for authentication

        :return: Server response in bytes
        """
        data = ConvertManager.bytes_to_dictionary(data)
        data_to_return: dict[str, str] = {}
        successful = True

        # Checking if the data from the server is as specified in the documentation.
        # "user_id" and "weight" are the only and required things that should be in the data.
        if "user_id" not in data:
            data_to_return["message"] = "ERROR: 'user_id' must be included."
            successful = False
        elif "weight" not in data:
            data_to_return["message"] = "ERROR: 'weight' must be included."
            successful = False

        for key in data:
            if key not in ("user_id", "weight"):
                data_to_return["message"] = f"ERROR: '{key}' is unrecognized. Please remove it."
                successful = False

        user_id = data["user_id"]

        if not AuthManager.auth(user_id, passcode):
            data_to_return = {"message": f"ERROR: Wrong passcode."}
            successful = False

        user_exists = DataManager.user_check(user_id)

        if not user_exists:
            data_to_return = {"message": f"ERROR: User '{user_id}' is not in the database."}
            successful = False

        if not successful:
            return ConvertManager.to_bytes(data_to_return)

        weight = float(data["weight"])

        time = TimeManager().pst

        user_id: str = user_id if type(user_id) is str else str(user_id)
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
            AWSManager().update_file(os.getenv("NAME_OF_CSV"), dataframe.to_csv(index=True, index_label="Date"))

        data_to_return: bytes = DataManager.get_user_weight(user_id, "-", passcode)

        return data_to_return

    @staticmethod
    def get_user_weight(user_id: str, month_req: str, passcode: str) -> bytes:
        """
        Returns the user weight according to the month specified.

        :param user_id: The user id
        :param month_req: The month the program is requesting. "-" for this month, "xxxx-xx" format for any other.
        :param passcode: The user passcode
        :return: Server response in bytes
        """
        assert type(user_id) is str, 'For performance, please set "user_id" to a string.'

        if not AuthManager.auth(user_id, passcode):
            data = {"message": "ERROR: Wrong passcode."}

            return ConvertManager.to_bytes(data)

        user_exists = DataManager.user_check(user_id)

        if not user_exists:
            data = {"message": f"ERROR: User '{user_id}' is not in the database."}

            return ConvertManager.to_bytes(data)

        frame = DataManager.return_dataframe()
        dates = frame.index.values
        data = {"weight": {}, "message": "SUCCESS"}

        if month_req == "-":
            month = TimeManager().current_month()
        else:
            month_data = month_req.split("-")
            if len(month_data) > 0 and len(month_data[0]) == 4 and len(month_data[1]) == 2:
                month = month_req[:8]
            else:
                return ConvertManager.to_bytes({
                    "message": "ERROR: Requested month is in wrong format. Must be in format xxxx-xx (YEAR-MONTH)."
                })

        for index, value in enumerate(frame.loc[:, user_id]):
            if month in dates[index]:
                data["weight"][dates[index]] = value

        return ConvertManager.to_bytes(data)

    @staticmethod
    def user_check(user_id: str) -> bool:
        """
        Checks if a user exists.

        :param user_id: The user id
        :return: Boolean
        """
        assert type(user_id) is str, '"user_id" must be a string.'

        frame = DataManager.return_dataframe()

        return True if user_id in frame.columns.values else False

    @staticmethod
    def new_user(data: bytes) -> bytes:
        """
        Creates a new user.

        :param data: JSON data from the outside world
        :return: Server response in bytes
        """
        dictionary = ConvertManager.bytes_to_dictionary(data)
        data_to_return = {}
        successful = True

        if "user_id" not in dictionary:
            data_to_return["message"] = "ERROR: 'user_id' must be included."
            successful = False
        elif "passcode" not in dictionary:
            data_to_return['message'] = "ERROR: 'passcode' must be included."
            successful = False

        for key in dictionary:
            if key not in ("user_id", "passcode"):
                data_to_return["message"] = f"ERROR: '{key}' is unrecognized. Please remove it."
                successful = False

        if not successful:
            return ConvertManager.to_bytes(data_to_return)

        user_id = dictionary["user_id"]

        if not DataManager.user_check(user_id):
            frame = DataManager.return_dataframe()

            length = len(frame.index.values)
            frame[user_id] = [0.0 for _ in range(0, length)]

            if not isPublic:
                frame.to_csv(toFile, index=True, index_label="Date")

                f = open(toAuth)
                content = f.read()
                f.close()

                auth: dict = json.loads(content)

                auth[user_id] = dictionary['passcode']

                f = open(toAuth, "w")
                f.write(json.dumps(auth))
                f.close()
            else:
                AWSManager().update_file(toFile, frame.to_csv(index=True, index_label="Date"))

                auth: dict = ConvertManager.bytes_to_dictionary(AWSManager().get_file(toAuth))

                auth[user_id] = dictionary['passcode']

                AWSManager().update_file(toAuth, auth)

            returning_data = {"message": "SUCCESS"}

            return ConvertManager.to_bytes(returning_data)
        else:
            returning_data = {"message": f"ERROR: User '{user_id}' already exists."}
            return ConvertManager.to_bytes(returning_data)


class ConvertManager:
    """
    The ConvertManager helps convert things to bytes and vise versa.
    """
    @staticmethod
    def bytes_to_string(data_to_convert: bytes) -> str:
        """
        Converts bytes to strings.

        :param data_to_convert: Data in bytes
        :return: Data as a string
        """
        return data_to_convert.decode('utf-8')

    @staticmethod
    def bytes_to_dictionary(data_to_convert: bytes) -> dict:
        """
        Converts bytes to a dictionary.

        :param data_to_convert: Data in bytes
        :return: Data as a dictionary
        """
        return ast.literal_eval(data_to_convert.decode('utf-8'))

    @staticmethod
    def to_bytes(data_to_convert) -> bytes:
        """
        Converts either string or dictionary to bytes.

        :param data_to_convert: Data in str/dict format
        :return: Data in bytes
        """
        assert type(data_to_convert) in (dict, str), "data must be either dict or str."

        if type(data_to_convert) == dict:
            return json.dumps(data_to_convert, indent=2).encode('utf-8')
        elif type(data_to_convert) == str:
            return data_to_convert.encode('utf-8')


class AuthManager:
    """
    AuthManager manages authentication.
    """
    @staticmethod
    def auth(username: str, passcode: str) -> bool:
        """
        Returns whether or not the username/passcode combination is valid.

        :param username: username
        :param passcode: passcode
        :return: boolean
        """
        if isPublic:
            auth_d: dict = ConvertManager.bytes_to_dictionary(AWSManager().get_file(toAuth))
        else:
            auth_d: dict = json.loads(open(toAuth).read())

        return True if auth_d[username] == passcode else False
