import os

from flask import Flask, session, render_template, request, jsonify
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
# if not os.getenv("DATABASE_URL"):
#     raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(("postgresql:///mydb"))
db = scoped_session(sessionmaker(bind=engine))

class Book():

    def __init__(self, id, isbn, author, title, year):
        self.id = id
        self.isbn = isbn
        self.author = author
        self.title = title
        self.year = year

        self.reviews = []

    def getInfo(self):
        infostring = ("->" + str(self.id) + "\n" + "Autor: " + self.author + "\n" + "Title: " + self.title + "ISBN: " + self.isbn + "\n" + "YEAR: " + self.year)
        # for eintrag in self.reviews:
        #     infostring = infostring + "\n" + eintrag
        return infostring

    def addReview(self, rev):
        self.reviews.append(rev)
        Review.book_id = self.id


class Review():
    def __init__(self, review):
        self.review = review


@app.route("/")
def index():
    return render_template("index.html", message="Welcome to my Review Page!")

@app.route("/register", methods=["POST", "GET"])
def register():
    if session.get("loggedin"):
        return render_template("search_books.html", message = "You are logged in, seach a book!")
    else:
        return render_template("register.html")

@app.route("/register_good", methods=["POST"])
def reg_success():

    username = request.form.get("username")
    password = request.form.get("password")

    if (db.execute("SELECT * FROM users WHERE (username=:username)", {"username":username}).rowcount == 0):
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username":username, "password":password})
        db.commit()
        return render_template("search_books.html")
    else:
        return render_template("register.html", message = "User already Exsits, please choose another username")

@app.route("/login", methods=["POST", "GET"])
def login():
    if session.get("loggedin") is False:
        return render_template("login.html", message="please Login")
    else:
        return render_template("search_books.html")

@app.route("/login_good", methods=["POST"])
def log_success():
    if(session.get("loggedin") is not False):
        return render_template("search_books.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

        if (db.execute("SELECT * FROM users WHERE (username=:username)", {"username":username}).rowcount == 0):
            return render_template("register.html", message="User doesn't seem to exist! Please Register")
        else:
            users = db.execute("SELECT * FROM users WHERE (username=:username) AND (password=:password)", {"username":username, "password":password}).fetchone()
            vals = users.values()
            id = vals[0]
            session["user_id"] = id
            session["user"] = username
            session["loggedin"] = True
            username = session.get("user")
            id = session.get("user_id")
            message = (f"Hello {username} with id {id}")
            return render_template("search_books.html", message = message)

@app.route("/logout", methods=["POST"])
def logout():
    session["loggedin"] = False
    session["username"] = None
    session["user_id"] = None
    return render_template("index.html", message="You are now logged out!")

@app.route("/books", methods=["POST"])
def search():
    isbn = request.form.get("isbn")
    isbn = f"%{isbn}%"
    author = request.form.get("author")
    author = f"%{author}%"
    title = request.form.get("title")
    title = f"%{title}%"
    year = request.form.get("year")
    year = f"%{year}%"
    books = db.execute("SELECT * FROM books_1 WHERE isbn LIKE :isbn AND author LIKE :author AND title LIKE :title AND year LIKE :year LIMIT 20", {"isbn":isbn, "author":author, "title":title, "year":year}).fetchall()
    if books:
        return render_template("result.html", books = books)
    else:
        return render_template("error.html", message = "No Books found")

@app.route("/book_infos", methods=["POST", "GET"])
def info():
    id = request.form.get("id")
    book = db.execute("SELECT * FROM books_1 WHERE id=:id", {"id":id}).fetchone()
    mybook = Book(book.id, book.isbn, book.author, book.title, book.year)
    review = db.execute("SELECT * FROM review WHERE book_id=:id", {"id":mybook.id}).fetchall()
    message = mybook.getInfo()
    return render_template("success.html", message = message, review = review, id=mybook.id)

@app.route("/book_reviews",  methods=["POST"])
def add_review():
    id = request.form.get("id")
    new_review = request.form.get("review")
    book = db.execute("SELECT * FROM books_1 WHERE id=:id", {"id":id}).fetchone()
    mybook = Book(book.id, book.isbn, book.author, book.title, book.year)
    user_id = session.get("user_id")
    review = db.execute("SELECT * FROM review WHERE book_id=:id", {"id":mybook.id}).fetchall()
    if(db.execute("SELECT * FROM review WHERE user_id=:user_id", {"user_id":user_id}).rowcount is not 0):
        return render_template("error.html", message = "DID ONE ALREADY")
    else:
        db.execute("INSERT INTO review (rev, book_id, user_id) VALUES (:bewertung, :book_id, :user_id)", {"bewertung":new_review, "book_id":mybook.id, "user_id":user_id})
        db.commit()
        message = mybook.getInfo()
        review = db.execute("SELECT * FROM review").fetchall()
        return render_template("success.html", message = message, review = review, id=mybook.id)
