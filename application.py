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
    return render_template("index.html")

#if you choose Register you end up here with a form where you can fill in username and password
@app.route("/register", methods=["POST"])
def register():
    return render_template("register.html")

#if you choose Login you end up here
@app.route("/login", methods=["POST"])
def login():
    return render_template("login.html")

@app.route("/success",methods=["POST"])
def login_success():
    username = request.form.get("username")
    password = request.form.get("password")

    if (db.execute("SELECT * FROM users WHERE (username=:username) AND (password=:password)", {"username":username, "password":password}).rowcount == 0):
        return render_template("error.html", message="User not found")
    else:
        return render_template("notes.html")


@app.route("/success", methods=["POST"])
def success():
    username = request.form.get("username")
    password = request.form.get("password")

    db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
            {"username": username, "password":password})
    db.commit()

    return render_template("success.html", message = "SUCCESS, You are registered")

@app.route("/notes", methods=["POST"])
def notes():

    if session.get("id") is None:
        session["id"] = []

    if request.method == "POST":
        note = request.form.get("note")
        session["id"].append(note)

    return render_template("notes.html", notes=session["id"])
