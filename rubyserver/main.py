from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)


@app.route("/weight-for-<user_id>/", methods=["GET"])
def get_weight():
    """
    Using the UserID provided in the link, this would return a JSON file with the user data and the weight during the
    month.

    :return: Bytes JSON data
    """
    pass


@app.route("/send-weight-for-<user_id>/", methods=["POST"])
def post_weight():
    """
    Using the UserID provided in the link and a bytes dictionary with the UserID, weight, and current date/time, this
    would update the user's weight.

    :return: A success/error message.
    """
    pass
