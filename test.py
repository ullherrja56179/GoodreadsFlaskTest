from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
import json
from jsonpath_rw import parse
from werkzeug.security import check_password_hash, generate_password_hash

engine = create_engine("postgres://iixnwpftseyics:5978adaa36ca766250b0280efe58fbd6f0e349467967e40e460b760b6cf382e5@ec2-54-247-103-43.eu-west-1.compute.amazonaws.com:5432/dc055c7ca8pmka")
db = scoped_session(sessionmaker(bind = engine))

class User():

    def __init__(self, username, passwordhashed):
        self.username = username
        self.passwordhashed = passwordhashed

def main():
    # username = input("Bitte username: ")
    # isbn = input("Bitte Geben Sie eine ISBN ein: ")
    #
    # if (db.execute("SELECT * FROM books_1 WHERE isbn = :isbn", {"isbn":isbn}).rowcount == 0):
    #     print("ISBN nicht gefunden")
    # else:
    #     book = ((db.execute("SELECT * FROM books_1 WHERE isbn = :isbn", {"isbn":isbn})).fetchone())
    #     values = book.values() #values sind isbn, title, author, year
    #     id = values[0]
    #     print(id)
    #
    #     bewerte = []
    #
    #     eingabe = input("Bewertung bitte: ")
    #     bewerte.append(eingabe)
    #
    #     for eintrag in bewerte:
    #         db.execute("INSERT INTO bewertungen (rev, book_id) VALUES (:rev, :book_id)",{"rev": eintrag, "book_id": id})
    #
    #     db.commit()
    # user = db.execute("SELECT * FROM users WHERE (username=:username)",{"username":username}).fetchone()
    # getid = user.values()
    # id = getid[0]
    # print(id)
    #
    # review = db.execute("SELECT * FROM review").fetchall()
    # for eintrag in review:
    #     print(eintrag)
    #


    # username = input("Username: ")
    # passw = input("password: ")
    # password = generate_password_hash(passw)
    #
    # if(db.execute("SELECT * FROM users WHERE (username=:username)",{"username":username}).rowcount is 0):
    #     print("gibt es schon")
    # else:
    #     db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username":username, "password":password})
    #     db.commit()
    #
    # user = User(username, password)
    #
    # print()
    # username = input("username: ")
    # password = input("Password: ")
    # hashed = db.execute("SELECT password FROM users WHERE username:=username", {"username":username}).fetchone()
    # print(hashed)
    # check = check_password_hash(hashed, password)
    #
    # if check is True:
    #     users = db.execute("SELECT * FROM users WHERE (username=:username)",{"username":username}).fetchone()
    #     print(users.id, users.username)
    # else:
    #     print("Da ist etwas schief gelaufen")
    #


    # id = 9
    # review = db.execute("SELECT * FROM review JOIN users ON users.id=review.user_id WHERE book_id='9'").fetchall()
    # print(review)
    # for eintrag in review:
    #     print(eintrag.username, eintrag.rev)

    isbn = input("ISBN: ")
    isbn = f"%{isbn}%"
    book = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn",{"isbn":isbn}).fetchone()
    print(book)

    id = book.id
    count = db.execute("SELECT count(id) FROM review WHERE book_id=:id", {"id":id}).fetchone()
    avg_rating = db.execute("SELECT avg(rating) FROM review WHERE book_id=:id", {"id":id}).fetchone()
    print(count[0], round(avg_rating[0],2))

if __name__ == "__main__":
    main()
