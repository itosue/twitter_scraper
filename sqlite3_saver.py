import sqlite3
import os
from datetime import datetime

DB_NAME = os.getenv("HOME") + "/Google Drive/all_tweets.db"


def tweet_datetime_to_unixtime(tweet_datetime):
    d = datetime.strptime(tweet_datetime, '%a %b %d %H:%M:%S %z %Y')
    return d.timestamp()

def insert_user(user):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("insert into user(id, name, screen_name, description) values (?, ?, ?, ?)",
                  [
                      user['id'],
                      user['name'],
                      user['screen_name'],
                      user['description']
                  ])
    except sqlite3.IntegrityError as e:
        # There can be same user already
        print(e)
    finally:
        conn.commit()
        conn.close()

def insert_tweet(tweet):
    # "retweet of reply tweet" is useless for our use case.
    if 'retweeted_status' in tweet:
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("insert into status (id, text, in_reply_to_status_id, user_id, created_at, is_quote_status) values (?, ?, ?, ?, ?, ?)",
                  [
                      tweet['id'],
                      tweet['text'],
                      tweet['in_reply_to_status_id'],
                      tweet['user']['id'],
                      tweet_datetime_to_unixtime(tweet['created_at']),
                      tweet['is_quote_status']
                  ])
        # todo save retweeted_status recursively, but this already might be there
        # todo save user, but it might be already there.
    except sqlite3.IntegrityError as e:
        # There can be same status already
        print(e)
    finally:
        conn.commit()
        conn.close()
        insert_user(tweet['user'])
