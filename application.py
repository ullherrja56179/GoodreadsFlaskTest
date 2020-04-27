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

    def __init__(self, id, isbn, author, title, year, rev_count, avg_rating, rat_count):
        self.id = id
        self.isbn = isbn
        self.author = author
        self.title = title
        self.year = year
        self.rev_count = rev_count
        self.avg_rating = avg_rating
        self.rat_count = rat_count

        self.reviews = []

    def getInfo(self):
        infostring = ("->" + str(self.id) + "\n" + "Autor: " + self.author + "\n" + "Title: " + self.title + "ISBN: " + self.isbn + "\n" + "YEAR: " + self.year)
        return infostring

    def getCounts(self):
        counts = ("Avg. Rating: " + str(self.avg_rating) + "Rating-Count: " + str(self.rat_count) + "Review-Count: " + str(self.rev_count))
        return counts


class User():

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

def getGoodReads(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":"vkWoJEKsUDSL5TiKqfIQ", "isbns":isbn})
    helper = res.json()
    result = helper['books']
    json = result[0]
    return json


books_list = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if session.get("loggedin"):
        return render_template("search_books.html", info = "You are logged in, seach a book!")
    else:
        return render_template("register.html")

@app.route("/register_good", methods=["POST"])
def reg_success():

    username = request.form.get("username")
    password = request.form.get("password")

    if (db.execute("SELECT * FROM users WHERE (username=:username)", {"username":username}).rowcount == 0):
        if username is "" or password is "":
            return render_template("register.html", alert = "Must Provide Username and Password")
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username":username, "password":password})
        db.commit()
        user = db.execute("SELECT * FROM users WHERE (username=:username) AND (password=:password)",
            {"username":username, "password":password}).fetchone()
        session["user_id"] = user.id
        session["user"] = username
        session["loggedin"] = True
        return render_template("search_books.html", info="You are now Registered")
    else:
        return render_template("register.html", alert = "User already Exsits, please choose another username")

@app.route("/login", methods=["POST", "GET"])
def login():
    if session.get("loggedin") is False:
        return render_template("index.html", alert="please Login")
    else:
        return render_template("search_books.html", info="You are already Logged In")

@app.route("/login_good", methods=["POST", "GET"])
def log_success():
    if request.method == "GET":
        if session.get("loggedin") is not False:
            return render_template("search_books.html")
        else:
            return render_template("index.html", alert = "You need to Log In first")

    if request.method == "POST":
        if(session.get("loggedin") is not False):
            return render_template("search_books.html", info="You are already Logged In")
        else:
            username = request.form.get("username")
            password = request.form.get("password")

            if (db.execute("SELECT * FROM users WHERE (username=:username)", {"username":username}).rowcount == 0):
                return render_template("register.html", alert="User doesn't seem to exist! Please Register")
            else:
                if(password is ""):
                    return render_template("index.html", alert="Must Provide Username and Password")
                user = db.execute("SELECT * FROM users WHERE (username=:username) AND (password=:password)",
                    {"username":username, "password":password}).fetchone()
                session["user_id"] = user.id
                session["user"] = username
                session["loggedin"] = True
                return render_template("search_books.html", info="You are now Logged In")

@app.route("/logout", methods=["POST", "GET"])
def logout():
    session["loggedin"] = False
    session["username"] = None
    session["user_id"] = None
    books_list = []
    return render_template("index.html", info="You are now logged out!")

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
    books = db.execute("SELECT * FROM books_1 WHERE isbn LIKE :isbn AND author LIKE :author AND title LIKE :title AND year LIKE :year LIMIT 20",
                {"isbn":isbn, "author":author, "title":title, "year":year}).fetchall()
    if books:
        return render_template("result.html", books = books)
    else:
        return render_template("search_books.html", alert = "No Books found")

@app.route("/book_infos", methods=["POST", "GET"])
def info():
    id = request.form.get("id")
    book = db.execute("SELECT * FROM books_1 WHERE id=:id", {"id":id}).fetchone()
    json_string = getGoodReads(book.isbn)
    rev_count = json_string['work_text_reviews_count']
    avg_rating = json_string['average_rating']
    ratings_count = json_string['work_ratings_count']
    mybook = Book(book.id, book.isbn, book.author, book.title, book.year, rev_count, avg_rating, ratings_count)
    books_list.append(mybook)
    review = db.execute("SELECT * FROM review JOIN users ON users.id=review.user_id WHERE book_id=:id", {"id":mybook.id}).fetchall()
    message = mybook.getInfo()
    return render_template("success.html", book = mybook, review = review)

@app.route("/book_reviews",  methods=["POST"])
def add_review():
    mybook = books_list[-1]
    new_review = request.form.get("review")
    user_id = session.get("user_id")
    review = db.execute("SELECT * FROM review JOIN users ON users.id=review.user_id WHERE book_id=:id", {"id":mybook.id}).fetchall()
    if(db.execute("SELECT * FROM review WHERE user_id=:user_id AND book_id=:book_id", {"user_id":user_id, "book_id":mybook.id}).rowcount is not 0):
        return render_template("error.html", alert = "You Already submitted a Review!")
    else:
        db.execute("INSERT INTO review (rev, book_id, user_id) VALUES (:bewertung, :book_id, :user_id)",
            {"bewertung":new_review, "book_id":mybook.id, "user_id":user_id})
        db.commit()
        review = db.execute("SELECT * FROM review JOIN users ON users.id=review.user_id WHERE book_id=:id", {"id":mybook.id}).fetchall()
        return render_template("success.html", book = mybook, review = review, id=mybook.id, infos=mybook.getCounts())
