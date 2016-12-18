from model import db, User, Tweet, create_app, init_db
import time
import calendar

class DatabaseClient(object):
    def __init__(self, app=None):
        if app is None:
            self.app = create_app()
        else:
            self.app = app
            init_db(self.app)
        self.app.app_context().push()

    @staticmethod
    def __commit_to_db(entity):
        db.session.add(entity)
        db.session.commit()

    @staticmethod
    def __parse_timestamp(timestamp):
        parsed_time = time.strptime(timestamp, "%a %b %d %H:%M:%S +0000 %Y")
        # Convert to epoch
        return calendar.timegm(parsed_time)

    @staticmethod
    def __greater_than_jan(epoch_time):
        # 1451606400 = Jan 01 00:00:00 2016
        if epoch_time >= 1451606400:
            return True
        return False

    @staticmethod
    def __lesser_than_jul(epoch_time):
        # 1467331200 = Jul 01 00:00:00 2016
        if epoch_time < 1467331200:
            return True
        return False

    @staticmethod
    def __process_tweet(tweet_data):
        tweet = {
            'text': tweet_data['text'],
            'retweets': tweet_data['retweet_count'],
            'mentions': map(lambda x: x['screen_name'], tweet_data['entities']['user_mentions']),
            'created_at': DatabaseClient.__parse_timestamp(tweet_data['created_at'])
        }
        tweet_id = tweet_data['id']
        return Tweet(id=tweet_id, tweet_data=str(tweet))

    def get_all_tweets(self):
        return Tweet.query.all()

    def get_all_users(self):
        return User.query.all()

    def read_user(self, handle):
        '''Reads user from DB, returns None if not found'''
        user_query = User.query.filter_by(handle=handle)
        if user_query.count():
            return user_query.first()
        return None

    def process_tweet_and_save_to_db(self, handle, tweets):
        # Check if user is already in the db
        user = self.read_user(handle)
        if user is None:
            # If not, create a new object
            user = User(handle=handle)
        user_tweets = map(lambda x: x.id, user.tweets)

        # Denotes the min id among all the processed tweets.
        # This works like a pagination token in the next call to twitter API
        min_id = float("inf")

        for tweet in tweets:
            min_id = min(min_id, tweet['id'])
            if tweet['id'] in user_tweets:
                # Ignore, if tweet is already present in the db
                continue
            timestamp = self.__parse_timestamp(tweet['created_at'])
            if not self.__greater_than_jan(timestamp):
                # Return None if we should stop retrieving tweets
                min_id = None
                break
            if self.__lesser_than_jul(timestamp):
                # The tweet lies in our desired range
                processed_tweet = self.__process_tweet(tweet)
                user.tweets.append(processed_tweet)


        print str(len(user.tweets)) + ' tweets for the user added to db'
        self.__commit_to_db(user)
        return min_id