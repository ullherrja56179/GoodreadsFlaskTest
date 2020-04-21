from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgresql:///mydb")
db = scoped_session(sessionmaker(bind = engine))

def main():
    isbn = input("Bitte Geben Sie eine ISBN ein: ")

    if (db.execute("SELECT * FROM books_1 WHERE isbn = :isbn", {"isbn":isbn}).rowcount == 0):
        print("ISBN nicht gefunden")
    else:
        book = ((db.execute("SELECT * FROM books_1 WHERE isbn = :isbn", {"isbn":isbn})).fetchone())
        values = book.values() #values sind isbn, title, author, year
        id = values[0]
        print(id)

        bewerte = []

        eingabe = input("Bewertung bitte: ")
        bewerte.append(eingabe)

        for eintrag in bewerte:
            db.execute("INSERT INTO bewertungen (rev, book_id) VALUES (:rev, :book_id)",{"rev": eintrag, "book_id": id})

        db.commit()


if __name__ == "__main__":
    main()
