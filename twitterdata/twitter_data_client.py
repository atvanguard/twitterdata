import json

from database.database_client import DatabaseClient
from .twitter_api_client import TwitterApiClient

class TwitterData(object):
    """Class to perform application operations
    for both core and management API
    """
    def __init__(self, app=None):
        self.db = DatabaseClient(app)
        self.twitter_api_client = TwitterApiClient()

    @staticmethod
    def __lies_in_timerange(timestamp, start, end):
        if timestamp >= start and timestamp <=end:
            return True
        return False

    @staticmethod
    def __increment_value(response, key, value):
        if key in response.keys():
            response[key] += value
        else:
            response[key] = value

    @staticmethod
    def __calculate_approachability(num, den):
        if num == 0:
            return 0
        else:
            return float(num/den)

    @staticmethod
    def __approachability_cmp(a, b):
        if a[1] > b[1]:
            return -1
        elif a[1] == b[1]:
            return 0
        return 1

    @staticmethod
    def __default_response():
        return {'message': 'User not tracked'}

    # Core API methods
    # (a)
    def search_tweets(self, query, handle=None):
        """Search all Tweets.
        If handle is provided, search only among the user tweets
        """
        tweets = []
        result = {}
        if handle is not None:
            # Search tweets only for the user
            user = self.db.read_user(handle)
            if user is None:
                return self.__default_response()
            tweets = user.tweets
        else:
            tweets = self.db.get_all_tweets()

        # Process tweets to find a match with the pattern
        for tweet in tweets:
            data = eval(tweet.tweet_data)
            if query in data['text']:
                # if query is present in tweet text then
                # add tweet corresponding to user in the response
                if tweet.author in result.keys():
                    result[tweet.author].append(data['text'])
                else:
                    result[tweet.author] = [data['text']]
        return result

    # (b)
    def mentions_by_user(self, handle):
        """Evalute the tracked users having been mentioned
        by the user (denoted by param handle)
        """
        user = self.db.read_user(handle)
        if user is None:
            return self.__default_response()

        mentions = set()
        # Process tweets to aggregate mentions
        for tweet in user.tweets:
            data = eval(tweet.tweet_data)
            # set union
            mentions |= set(data['mentions'])
        return {handle: list(mentions)}

    # (c)
    def tweet_count(self, start, end):
        """Count tweets for all tracked users
        in the given time range
        """
        tweets = self.db.get_all_tweets()
        result = {}
        for tweet in tweets:
            data = eval(tweet.tweet_data)
            if self.__lies_in_timerange(data['created_at'], start, end):
                self.__increment_value(result, key=tweet.author, value=1)
        return result

    # (d)
    def retweets_leaderboard(self, start, end):
        """Generate retweet leaderboard
        for retweets in the given time range
        """
        tweets = self.db.get_all_tweets()
        leaderboard = {}
        for tweet in tweets:
            data = eval(tweet.tweet_data)
            if self.__lies_in_timerange(data['created_at'], start, end):
                self.__increment_value(leaderboard, key=tweet.author, value=data['retweets'])
        return leaderboard

    # (e)
    def approachable_users(self, count=5):
        """Evalalute approachability of the users"""
        users = self.db.get_all_users()
        users_set = set(users)
        result = []

        print len(users)
        for user in users:
            print user.handle
            tweets_with_unverified_user_mention = 0
            total_tweets_with_mention = 0
            for tweet in user.tweets:
                data = eval(tweet.tweet_data)
                if len(data['mentions']) > 0:
                    # Atleast one mention
                    total_tweets_with_mention += 1
                    if len(set(data['mentions']) - users_set) > 0:
                        tweets_with_unverified_user_mention += 1

            result.append((user.handle,
                self.__calculate_approachability(tweets_with_unverified_user_mention, total_tweets_with_mention)))

        result.sort(self.__approachability_cmp)
        # Return count number of results
        if len(result) <= count:
            return result
        return result[0:count]

    #Management API methods
    # (a)
    def track_new_user(self, handle):
        user = self.db.read_user(handle)
        if user is not None:
            return 'User already tracked'

        max_id = None
        while True:
            # Twitter API call
            tweets = self.twitter_api_client.retrieve_user_tweets_rpc(
                user=handle,
                max_id=max_id)
            if tweets is None:
                # User doesn't exist in twitter
                return 'User not found'
            if len(tweets) == 0:
                break
            max_id = self.db.process_tweet_and_save_to_db(handle, tweets)
            if max_id is None:
                # Stop retrieving tweets
                break
            else:
                max_id -= 1

        return handle + ' processed'

    # (b)
    def get_tracked_users(self):
        users = self.db.get_all_users()
        return map(lambda x: x.handle, users)
