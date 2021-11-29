import pytz
from datetime import datetime
import calendar


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
