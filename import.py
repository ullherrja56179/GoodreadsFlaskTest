#import Books into DATABASE

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv

engine = create_engine("postgresql:///mydb")
db = scoped_session(sessionmaker(bind = engine))

# CREATE TABLE books_1 {
#     id SERIAL PRIMARY KEY,
#     isbn INTEGER NOT NULL,
#     title VARCHAR NOT NULL,
#     author VARCHAR NOT NULL,
#     year INTEGER NOT NULL
# }


def main():
    f = open("books.csv", "r")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books_1 (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
            {"isbn": isbn, "title": title, "author":author, "year":year})
    db.commit()

if __name__ == "__main__":
    main()
