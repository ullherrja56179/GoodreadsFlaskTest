import os

from flask import Flask, session, render_template, request, jsonify, abort
from flask_session import Session
from flask import redirect, url_for, flash
from sqlalchemy import create_engine
# from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
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
        infostring = ("->" + str(self.id) + "\n" + "Autor: " + self.author +
            "\n" + "Title: " + self.title + "ISBN: " + self.isbn + "\n" + "YEAR: " + str(self.year))
        return infostring

    def getCounts(self):
        counts = ("Avg. Rating: " + str(self.avg_rating) + "Rating-Count: "
            + str(self.rat_count) + "Review-Count: " + str(self.rev_count))
        return counts


class User():

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def getGoodReads(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
        params={"key":"vkWoJEKsUDSL5TiKqfIQ", "isbns":isbn})
    helper = res.json()
    result = helper['books']
    json = result[0]
    return json

def getReview(mybook):
    return(db.execute("SELECT * FROM review JOIN users ON users.id=review.user_id WHERE book_id=:id",
        {"id":mybook.id}).fetchall())

def getUser(username, password):
    return(db.execute("SELECT * FROM users WHERE (username=:username) AND (password=:password)",
        {"username":username, "password":password}).fetchone())


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


books_list = []

@app.route("/")
def index():
    if session.get("loggedin") is None:
        session["loggedin"] = False
        session["user"] = None
        session["user_id"] = None
    return render_template("index.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if session.get("loggedin"):
        user = session.get("user")
        #flash(f"You are Logged In as {user}")
        return redirect(url_for("log_success"))
    else:
        return render_template("register.html")

@app.route("/register_good", methods=["POST"])
def reg_success():
    username = request.form.get("username")
    password = request.form.get("password")

    if (db.execute("SELECT * FROM users WHERE (username=:username)", {"username":username}).rowcount == 0):
        if username is "" or password is "":
            flash("Must Provide Username AND Password")
            return redirect(url_for('register'))
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
            {"username":username, "password":password})
        db.commit()
        user = getUser(username, password)
        session["user_id"] = user.id
        session["user"] = username
        session["loggedin"] = True
        return render_template("search_books.html", info="You are now Registered")
    else:
        flash("User already Exsits, please choose another username")
        return redirect(url_for("register"))

@app.route("/search", methods=["POST", "GET"])
def log_success():
    if request.method == "GET":
        if session.get("loggedin") is True:
            user = session.get("user")
            return render_template("search_books.html", info=f"You are Logged In as {user}")
        else:
            flash("You need to Log In first")
            return redirect(url_for("index"))

    if request.method == "POST":
        if(session.get("loggedin") is True):
            user = session.get("user")
            return render_template("search_books.html", info=f"You are already Logged In as {user}")
        else:
            username = request.form.get("username")
            password = request.form.get("password")

            if (db.execute("SELECT * FROM users WHERE (username=:username)", {"username":username}).rowcount == 0):
                return render_template("register.html", alert="User doesn't seem to exist! Please Register")
            else:
                if(password is ""):
                    flash("You need do provide a password!")
                    return redirect(url_for("index")) #here
                user = getUser(username, password)
                session["user_id"] = user.id
                session["user"] = username
                session["loggedin"] = True
                return render_template("search_books.html", info=f"You are now Logged In as {username}")

@app.route("/books", methods=["POST"])
def search():
        isbn = request.form.get("isbn")
        isbn = f"%{isbn}%"
        author = request.form.get("author")
        author = f"%{author}%"
        title = request.form.get("title")
        title = f"%{title}%"
        books = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn AND author LIKE :author AND title LIKE :title LIMIT 20",
                    {"isbn":isbn, "author":author, "title":title}).fetchall()
        if books:
            return render_template("result.html", books = books)
        else:
            return render_template("search_books.html", alert = "No Books found")

@app.route("/book_infos", methods=["POST", "GET"])
def info():
    if request.method == "GET":
        if(session.get("loggedin") is True):
            flash("You need to Choose a Book first!")
            return redirect(url_for("search"))
        else:
            flash("You are not Logged In, Please do that first")
            return redirect(url_for("index"))

    if request.method == "POST":
        id = request.form.get("id")
        book = db.execute("SELECT * FROM books WHERE id=:id", {"id":id}).fetchone()
        json_string = getGoodReads(book.isbn)
        rev_count = json_string['work_text_reviews_count']
        avg_rating = json_string['average_rating']
        ratings_count = json_string['work_ratings_count']
        mybook = Book(book.id, book.isbn, book.author, book.title, book.year, rev_count, avg_rating, ratings_count)
        books_list.append(mybook)
        review = getReview(mybook)
        return render_template("success.html", book = mybook, review = review)

@app.route("/book_reviews",  methods=["POST"])
def add_review():
    mybook = books_list[-1]
    new_review = request.form.get("review")
    rating = request.form.get("rating")
    user_id = session.get("user_id")
    review = getReview(mybook)
    if(db.execute("SELECT * FROM review WHERE user_id=:user_id AND book_id=:book_id",
            {"user_id":user_id, "book_id":mybook.id}).rowcount is not 0):
        return render_template("error.html", alert = "You Already submitted a Review!")
    else:
        db.execute("INSERT INTO review (rev, book_id, user_id, rating) VALUES (:bewertung, :book_id, :user_id, :rating)",
            {"bewertung":new_review, "book_id":mybook.id, "user_id":user_id, "rating":rating})
        db.commit()
        review = getReview(mybook)
        return render_template("success.html", book = mybook, review = review, id=mybook.id, infos=mybook.getCounts())

@app.route("/logout", methods=["POST", "GET"])
def logout():
    session["loggedin"] = False
    session["user"] = None
    session["user_id"] = None
    flash("You are now logged out!")
    return redirect(url_for("index"))

@app.route("/api/isbn/<string:isbn>", methods=["GET"])
def isbn(isbn):
    isbn = f"%{isbn}%"
    book = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn",{"isbn":isbn}).fetchone()
    if book is None:
        abort(404)
    else:
        id = book.id
        count_arr = db.execute("SELECT count(id) FROM review WHERE book_id=:id", {"id":id}).fetchone()
        avg_rating = db.execute("SELECT avg(rating) FROM review WHERE book_id=:id", {"id":id}).fetchone()
        count = count_arr[0]
        if(count is 0):
            # count="No Reviews yet"
            # avg_rating="No ratings yet"
            avg_rating = 0
        else:
            avg_rating = str(round(avg_rating[0], 2))
        response = {
        "title": book.title,
        "isbn": book.isbn,
        "author": book.author,
        "review": {
            "count": count,
            "avg_rating": avg_rating
        }
        }
        return(jsonify(response))
