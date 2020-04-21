#Import books.csv into Database

from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
import csv


db = SQLAlchemy()

# db.execute("CREATE TABLE books_1 (isbn INTEGER NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER NOT NULL)")
# db.commit()

class Books(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key = True)
    isbn = db.Column(db.String, nullable= False)
    author = db.Column(db.String, nullable = False)
    year = db.Column(db.String, nullable = False)

    count = 1

    def __init__(self, isbn, author, title, year):
        self.id = Books.count
        Books.count += 1

        self.bewertung = []

        self.isbn = isbn
        self.author = author
        self.title = title
        self.year = year

    def getinfo(self):
        print(f"Book {self.id}:\n{self.isbn}\n{self.author}\n{self.title}\n{self.year}")
        print("Reviews:")
        for eintrag in self.bewertung:
            print(f"{eintrag.bewertung}")
        print()

    def addReview(self, rev):
        self.bewertung.append(rev)
        Bewertung.book_id = self.id


class Bewertung(db.Model):
    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key=True)
    bewertung = db.Column(db.String, nullable = True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable = False)

    def __init__(self, bewertung):
        self.bewertung = bewertung
