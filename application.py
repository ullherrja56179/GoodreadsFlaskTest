import os
from flask import Flask, render_template, request, session
from flask_sessions import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

notess = []

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine("postgresql:///mydb")
db  = scoped_session(sessionmaker(bind=engine))

#starting Page where you can choose to login or register
@app.route("/")
def index():
    return render_template("index.html", message="WELCOME")

#if you choose Register you end up here with a form where you can fill in username and password
@app.route("/register", methods=["POST"])
def register():
    return render_template("register.html")

@app.route("/register_suc", methods=["POST"])
def success():
    username = request.form.get("username")
    password = request.form.get("password")

    if(db.execute("SELECT * FROM users WHERE (username=:username)", {"username":username}).rowcount == 0):
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                {"username": username, "password":password})
        db.commit()
    else:
        return render_template("index.html", message = "Username already exists")

    return render_template("success.html", message = "SUCCESS, You are now able to log in with your provided Data")

#if you choose Login you end up here
@app.route("/login", methods=["POST"])
def login():
    return render_template("login.html")

@app.route("/login_suc",methods=["POST"])
def login_success():
    username = request.form.get("username")
    password = request.form.get("password")

    if (db.execute("SELECT * FROM users WHERE (username=:username) AND (password=:password)", {"username":username, "password":password}).rowcount == 0):
        return render_template("register.html", message="User doesn't seem to exist!")
    else:
        return render_template("notes.html", user=username)


@app.route("/notes", methods=["POST"])
def notes():

    if session.get("id") is None:
        session["id"] = []

    if request.method == "POST":
        note = request.form.get("note")
        session["id"].append(note)

    return render_template("notes.html", notes=session["id"])
