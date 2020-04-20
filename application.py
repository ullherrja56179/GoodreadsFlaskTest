import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

# res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "KEY", "isbns": "9781632168146"})
# print(res.json())
# where key is: vkWoJEKsUDSL5TiKqfIQ
# isbns is user input for which isbn he wants review/rating

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(("postgresql:///mydb"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html", message="Welcome to my Review Page!")


@app.route("/register", methods=["POST", "GET"])
def register():
    if session.get("loggedin") is True:
        username = session.get("user")
        return render_template("error.html", message= f"Already Logged In {username}")
    else:
        return render_template("register.html")

@app.route("/register_suc", methods=["POST"])
def reg_success():

    username = request.form.get("username")
    password = request.form.get("password")

    if (db.execute("SELECT * FROM users WHERE (username=:username)", {"username":username}).rowcount == 0):
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username":username, "password":password})
        db.commit()
        return render_template("success.html", message = "You are now Registered!")
    else:
        return render_template("register.html", message = "User already Exsits, please choose another username")

@app.route("/login", methods=["POST", "GET"])
def login():
    if session.get("loggedin") is True:
        username = session.get("user")
        return render_template("error.html", message= f"You are already Logged In {username}")
    else:
        return render_template("login.html", message="please Login")

@app.route("/login_suc", methods=["POST"])
def log_success():
    if(session.get("loggedin") is True):
        username = session.get("user")
        return render_template("error.html", message= f"You are already Logged in {username}")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

        if (db.execute("SELECT * FROM users WHERE (username=:username) AND (password=:password)", {"username":username, "password":password}).rowcount == 0):
            return render_template("register.html", message="User doesn't seem to exist! Please Register")
        else:
            session["user"] = username
            session["loggedin"] = True
            return render_template("success.html", message = f"You are logged in now as {username}")

@app.route("/logout", methods=["POST"])
def logout():
    session["loggedin"] = False
    return render_template("index.html", message="You are now logged out!")
