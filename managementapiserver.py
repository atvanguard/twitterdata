from flask import Flask, request, jsonify, url_for, render_template, Response
from twitterdata.twitter_api_client import TwitterApiClient
from twitterdata.twitter_data_client import TwitterData
from twitterdata.constants import DB_FILE

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_FILE
twitter_data = TwitterData(app)

@app.route('/track')
def track_new_user():
    user = request.args.get('user')
    new_user = twitter_data.track_new_user(user)
    return jsonify({'newly_tracked_user': new_user})

@app.route('/tracked')
def tracked_users():
    tracked_users = twitter_data.get_tracked_users()
    return jsonify({'tracked_users': tracked_users})

if __name__ == "__main__":
    app.run(debug=True, port=8800)