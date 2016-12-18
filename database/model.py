from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

from twitterdata.constants import DB_FILE

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    handle = db.Column(db.String(50), primary_key=True)

    # Establish a one-to-many relationship with Tweets
    # backref establishes a bidirectional relationship in one-to-many,
    # where the "reverse" side is a many to one
    tweets = db.relationship('Tweet', backref='user')

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.handle == other.handle)

class Tweet(db.Model):
    __tablename__ = 'tweet'
    id = db.Column(db.Integer, primary_key=True)
    tweet_data = db.Column(db.String(1000))
    author = db.Column(db.String(50), db.ForeignKey('user.handle'))

def create_app():
    app = Flask(__name__)
    print os.getcwd()
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_FILE
    init_db(app)
    return app

def init_db(app=None):
    if app is not None:
        db.init_app(app)
        dbfname = app.config['SQLALCHEMY_DATABASE_URI'].split('///')[1]
        print dbfname
        if not os.path.isfile(dbfname):
            with app.app_context():
                db.create_all()

if __name__ == '__main__':
    create_app()