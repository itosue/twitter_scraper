import argparse
import sqlite3


def normalize_line(text):
    return text.replace('\n', ' ')


def dump(db, include_user):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(
        "select b.text, a.text, b.in_reply_to_status_id, b.user_id from status a, status b where a.is_spam = 0 and b.is_spam = 0 and a.in_reply_to_status_id = b.id")
    for row in cursor:
        tweet = row[0]
        reply = row[1]
        in_reply_to_status_id = row[2]
        user_id = row[3]
        if in_reply_to_status_id != 0:
            parent_cursor = conn.cursor()
            parent_cursor.execute("select text from status where id = ? limit 1", [in_reply_to_status_id])
            parent_tweet = parent_cursor.fetchone()
            if parent_tweet is not None:
                tweet = parent_tweet[0] + ' ' + tweet
        if include_user:
            user_cursor = conn.cursor()
            user_cursor.execute("select name, description from user where id = ? limit 1", [user_id])
            user = user_cursor.fetchone()
            if user is not None:
                # Assuming username is more important
                user_text = (user[1] or '') + (user[0] or '')
                tweet = user_text + tweet
        print(normalize_line(tweet))
        print(normalize_line(reply))
    conn.close()


def dump_main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, required=True, help='path to sqlite3 db')
    parser.add_argument('--include_user', type=str, required=True, help='if include_user_bio in tweet yes/no')
    args = parser.parse_args()
    db = args.db
    include_user = args.include_user == 'yes'
    dump(db, include_user)


if __name__ == '__main__':
    dump_main()
