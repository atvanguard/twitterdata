import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from database import model
from database.model import db, User, Tweet
DB_FILE = 'sqlite://'

class DBModelTestCase(unittest.TestCase):
    '''Tests for model.py'''

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = DB_FILE
        self.app.config['TESTING'] = True
        db.init_app(self.app)
        db.session.expire_on_commit = False
        # self.app.app_context().push()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def commitToDb(self, objs):
        for item in objs:
            db.session.add(item)
        db.session.commit()
        db.session.remove()

        # To prevent DetachedInstanceError
        # Investigate further
        l = []
        for item in objs:
            l.append(db.session.merge(item))
        return l

    def testUser(self):
        with self.app.app_context():
            user1 = User(handle='arpit')
            l = self.commitToDb([user1])

            result = User.query.all()
            self.assertEqual(1, len(result))

    def testUserTweet1ToMany(self):
        with self.app.app_context():
            self.commitToDb([
                User(handle='arpit',
                    tweets=[
                        Tweet(tweet_data='Tweet1'),
                        Tweet(tweet_data='Tweet2'),
                        Tweet(tweet_data='Tweet3')])])

            # Test 1-artist-to-many-tracks
            user_query = User.query.all()
            self.assertEqual(1, len(user_query))
            self.assertEqual(User(handle='arpit'), user_query[0])

            def assert_tweet_present_in_user_object(tweet_data, tweet_id):
                positives = filter(lambda x: x.tweet_data == tweet_data, user_query[0].tweets)
                self.assertEqual(1, len(positives))
                self.assertEqual(tweet_id, positives[0].id)
            assert_tweet_present_in_user_object('Tweet1', 1)
            assert_tweet_present_in_user_object('Tweet2', 2)
            assert_tweet_present_in_user_object('Tweet3', 3)

            tweet_query = Tweet.query.all()
            self.assertEqual(3, len(tweet_query))
            # Test many-tracks-to-1-artist
            for tweet in ['Tweet2', 'Tweet3', 'Tweet1']:
                positives = filter(lambda x: x.tweet_data == tweet, tweet_query)
                self.assertEqual(1, len(positives))
                self.assertEqual(User(handle='arpit'), positives[0].user)