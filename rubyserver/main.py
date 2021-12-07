from flask import Flask, request, render_template
from markupsafe import escape
from rubyserver.SupportProtocol import DataManager

app = Flask(__name__)


@app.route("/api/weight/<month>/", methods=["GET"])
def get_weight(month) -> bytes:
    """
    Using the UserID provided in the link, this would return a JSON file with the user data and the weight during the
    month.

    :param month: The month requested. "-" for the current month, "xxxx-xx" format for any other.
    :return: Server response in bytes.
    """
    return DataManager.get_user_weight(request.authorization.username, escape(month).striptags(),
                                       request.authorization.password)


@app.route("/api/update-weight/", methods=["POST"])
def post_weight() -> bytes:
    """
    Using the UserID provided in the link and a bytes dictionary with the UserID, weight, and current date/time, this
    would update the user's weight.

    :return: Server response in bytes.
    """
    return DataManager.record_weight(request.data, request.authorization.password)


@app.route("/api/new-user/", methods=["POST"])
def new_user() -> bytes:
    """
    Creates a new user.

    :return: Server response in bytes.
    """
    return DataManager.new_user(request.data)


@app.route("/", methods=["GET"])
def index():
    """
    :return: Index page
    """
    return render_template('/index.html')


@app.route("/about.html", methods=["GET"])
def about():
    """
    :return: About page
    """
    return render_template('/about.html')

@app.route("/developers.html", methods=["GET"])
def developers():
    """
    :return: Developers page
    """
    return render_template("/developers.html")
