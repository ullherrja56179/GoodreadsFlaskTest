from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
import json
from jsonpath_rw import parse

engine = create_engine("postgresql:///mydb")
db = scoped_session(sessionmaker(bind = engine))

def main():
    username = input("Bitte username: ")
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
    user = db.execute("SELECT * FROM users WHERE (username=:username)",{"username":username}).fetchone()
    getid = user.values()
    id = getid[0]
    print(id)

    review = db.execute("SELECT * FROM review").fetchall()
    for eintrag in review:
        print(eintrag)

    username = input("Username: ")
    password = input("password: ")
    users = db.execute("SELECT * FROM users WHERE (username=:username) AND (password=:password)",{"username":username, "password":password}).fetchone()
    print(users.id, users.username)

    id = 9
    review = db.execute("SELECT * FROM review JOIN users ON users.id=review.user_id WHERE book_id='9'").fetchall()
    print(review)
    for eintrag in review:
        print(eintrag.username, eintrag.rev)

    # import requests
    # isbns = db.execute("SELECT isbn FROM books_1").fetchmany(5)
    # print(isbns)
    # isbns.pop(0)
    # for isbn in isbns:
    #     isbn_get = isbn[0]
    #     print(isbn_get)
    #     res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":"vkWoJEKsUDSL5TiKqfIQ", "isbns":isbn_get})
    #     blubb = res.json()
    #     result = blubb['books']
    #     json = result[0]
    #     print(json)
    #     print(json['isbn'], json['ratings_count'])

#SELECT * FROM books_1 JOIN review ON review.book_id = books_1.id;

if __name__ == "__main__":
    main()
