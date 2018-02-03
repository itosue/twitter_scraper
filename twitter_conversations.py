import argparse
import re
import sqlite3
import sys

import tweepy
import yaml
from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener


class QueueListener(StreamListener):
    def __init__(self, args):
        super().__init__()
        if args.config:
            f = open(args.config, 'rt')
        else:
            f = open('config.yml', 'rt')
        cfg = yaml.load(f)['twitter']
        self.auth = OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
        self.auth.set_access_token(cfg['access_token'],
                                   cfg['access_token_secret'])
        self.api = tweepy.API(self.auth)
        self.db = args.db

    @staticmethod
    def is_ja_tweet(status):
        return status.user.lang == 'ja'

    @staticmethod
    def has_in_reply_to(status):
        return isinstance(status.in_reply_to_status_id, int)

    def on_status(self, status):
        if self.is_ja_tweet(status) and self.has_in_reply_to(status):

            statues = self.api.statuses_lookup([status.in_reply_to_status_id])
            if len(statues) == 0:
                return
            prev = statues[0]
            if prev.user.id == status.user.id:
                return

            if self.has_in_reply_to(prev):
                statues = self.api.statuses_lookup([prev.in_reply_to_status_id])
                if len(statues) == 0:
                    return
                prev_prev = statues[0]
                if prev_prev.user.id != status.user.id:
                    return
                print("========================================================"
                      "\n{}\n{}\n{}".format(self.sanitize_text(status.text),
                                            self.sanitize_text(prev.text),
                                            self.sanitize_text(
                                                prev_prev.text)))
                self.insert_conversation(status, prev, prev_prev)

    def insert_conversation(self, status1, status2, status3):
        for status in [status1, status2, status3]:
            self.insert_status(status)

        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        print("{} {} {}".format(status1.id, status2.id, status3.id))
        try:
            c.execute(
                "insert into conversation (sid1, sid2, sid3) values (?, ?, ?)",
                [
                    status1.id,
                    status2.id,
                    status3.id
                ])
        except sqlite3.IntegrityError as e:
            print(e)
        finally:
            conn.commit()
            conn.close()

    @staticmethod
    def sanitize_text(text):
        return re.sub("\s+", ' ', text).strip()

    def insert_status(self, status):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        text = self.sanitize_text(status.text)
        try:
            c.execute(
                "insert into status "
                "(id, text, in_reply_to_status_id, user_id, "
                "created_at, is_quote_status) "
                "values (?, ?, ?, ?, ?, ?)",
                [
                    status.id,
                    text,
                    status.in_reply_to_status_id,
                    status.user.id,
                    status.created_at.timestamp(),
                    status.is_quote_status
                ])
        except sqlite3.IntegrityError as e:
            # There can be same status already
            print(e)
        finally:
            conn.commit()
            conn.close()

    def on_error(self, status):
        print('ON ERROR:', status)

    def on_limit(self, track):
        print('ON LIMIT:', track)


def main():
    # parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=False,
                        help='config file path')
    parser.add_argument('--db', type=str, required=True,
                        help='path to sqlite3 db')
    args = parser.parse_args()

    listener = QueueListener(args)
    stream = Stream(listener.auth, listener)
    print("Listening...\n")
    stream.sample()


if __name__ == '__main__':
    sys.exit(main())
