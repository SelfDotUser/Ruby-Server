from pandas.io.formats.format import Datetime64Formatter
import pytz
from datetime import datetime
import calendar
import pandas as pd
import random


# Keeping this here so that the proper keys are set without struggle.
isPublic = False


class Now():
    def __init__(self):
        utc_now = pytz.utc.localize(datetime.utcnow())
        self.pst = utc_now.astimezone(pytz.timezone('US/Pacific'))


    def getDate(self):
        """
        Returns the date in the PST timezone. "January 1, 2000" format.
        """
        currentDay = self.pst.strftime("%B %d, %Y")

        return currentDay


    def getTime(self):
        """
        Returns the current time in the PST timezone. "01:00 AM" format.
        """
        currentTime = self.pst.strftime('%I:%M %p')

        return currentTime


    def getDaysInMonth(year:int, month:int):
        """
        Returns the number of days there are in the specified month in the specified year.

        :return: Integer
        """
        return calendar.monthrange(year, month)[1]


class DataManager():
    @staticmethod
    def create_frame():
        """
        This is for developmental purposes only.
        Creates a brand new set for testing.
        """

        def create_new_data():
            return [random.randint(195, 200) for number in range(0, 5)]

        data = pd.DataFrame({
            "Date": ["2021-11-29", "2021-11-30", "2021-12-01", "2021-12-05", "2021-11-10"],
            "Matt": create_new_data(),
            "Carlos": create_new_data(),
            "Ruby": create_new_data()
        })

        data.to_csv("rubyserver/data.csv", index=False)


    @staticmethod
    def returnDataFrame():
        frame = pd.read_csv("rubyserver/data.csv", index_col='Date')

        return frame


    @staticmethod
    def recordWeight(id: str, weight):
        """
        Records the weight of the individual.
        """
        assert type(weight) is int or type(weight) is float, '"weight" parameter must be either an integer or a float.'

        id = id if type(id) is str else str(id)
        day = Now().pst.day if Now().pst.day >= 10 else f"0{Now().pst.day}"
        month = Now().pst.month if Now().pst.month >= 10 else f"0{Now().pst.month}"
        date = f"{Now().pst.year}-{month}-{day}"

        dataframe = DataManager.returnDataFrame()

        exists = True if date in dataframe.index.values else False

        if not exists:
            for user in dataframe.columns.values:
                dataframe.loc[date, user] = 0.0 if user != id else weight
        else:
            dataframe.loc[date, id] = weight

        dataframe.to_csv(f"rubyserver/data.csv", index=True, index_label="Date")

DataManager.recordWeight("Ruby", 300)