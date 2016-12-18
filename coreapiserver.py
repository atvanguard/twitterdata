from flask import Flask, request, jsonify
from twitterdata.twitter_data_client import TwitterData
from twitterdata.constants import DB_FILE
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_FILE
twitter_data = TwitterData(app)

# part (a)
@app.route('/search')
def get_search_tweets():
    user = request.args.get('user')
    query = request.args.get('query')
    if query is None:
        return 'No query provided'
    matching_tweets = twitter_data.search_tweets(query, user)
    return jsonify(matching_tweets)

# part (b)
@app.route('/mentionsby')
def get_mentions_by_user():
    user = request.args.get('user')
    print user
    mentions = twitter_data.mentions_by_user(user) #set
    return jsonify(mentions)

# part (c)
@app.route('/tweetcount')
def get_tweet_count():
    start = request.args.get('start')
    end = request.args.get('end')
    tweet_count = twitter_data.tweet_count(int(start), int(end)) #set
    return jsonify(tweet_count)

# part (d)
@app.route('/retweets')
def get_retweet_leaderboard():
    start = request.args.get('start')
    end = request.args.get('end')
    leaderboard = twitter_data.retweets_leaderboard(int(start), int(end)) #set
    return jsonify(leaderboard)

# part (e)
@app.route('/approach')
def get_approachability():
    t = twitter_data.approachable_users()
    return jsonify(t)

if __name__ == "__main__":
    app.run(debug=True)