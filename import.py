#import Books into DATABASE

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv

engine = create_engine("postgres://iixnwpftseyics:5978adaa36ca766250b0280efe58fbd6f0e349467967e40e460b760b6cf382e5@ec2-54-247-103-43.eu-west-1.compute.amazonaws.com:5432/dc055c7ca8pmka")
db = scoped_session(sessionmaker(bind = engine))

# CREATE TABLE books (
#     id SERIAL PRIMARY KEY,
#     isbn VARCHAR NOT NULL,
#     title VARCHAR NOT NULL,
#     author VARCHAR NOT NULL,
#     year INTEGER NOT NULL
# );


def main():
    f = open("books.csv", "r")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
            {"isbn": isbn, "title": title, "author":author, "year":year})
    db.commit()

if __name__ == "__main__":
    main()
