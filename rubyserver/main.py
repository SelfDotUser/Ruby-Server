from flask import Flask, request
from markupsafe import escape
from rubyserver.SupportProtocol import DataManager

app = Flask(__name__)


@app.route("/weight-<user_id>/", methods=["GET"])
def get_weight(user_id):
    """
    Using the UserID provided in the link, this would return a JSON file with the user data and the weight during the
    month.

    :return: Bytes JSON data
    """
    return DataManager.get_user_weight(escape(user_id).striptags(), True)


@app.route("/update-weight/", methods=["POST"])
def post_weight():
    """
    Using the UserID provided in the link and a bytes dictionary with the UserID, weight, and current date/time, this
    would update the user's weight.

    :return: A success/error message.
    """
    return DataManager.record_weight(request.data)


@app.route("/new-user/", methods=["POST"])
def new_user():
    return DataManager.new_user(request.data)
