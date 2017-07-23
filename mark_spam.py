import sqlite3
import argparse
import sys


def select_likely_spam(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("select text, count(*) from status where is_spam = 0 group by text order by count(*) desc limit 50")
    rows =  cursor.fetchall()
    conn.close()
    return rows


def mark_as_spam(db, rows):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    for row in rows:
        cursor.execute("update status set is_spam = 1 where text = ? and is_spam = 0", [row[0]])
    conn.commit()
    conn.close()
    return rows


def mark_spam():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, required=True, help='path to sqlite3 db')
    args = parser.parse_args()
    db = args.db
    likely_spams = select_likely_spam(db)
    for spam in likely_spams:
        print(spam[1], spam[0].replace('\n', ''))
    shall = input("%s (y/N) " % "Do you want to mark them as spam").lower() == 'y'
    if shall:
        mark_as_spam(db, likely_spams)
        print("done")
    else:
        print("canceled")


if __name__ == '__main__':
    mark_spam()
