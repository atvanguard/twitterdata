import requests
from constants import BASE64_TOKEN

ACCESS_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAKmqyQAAAAAA606jjrzVFdGd%2Fm1U4yLrL4PVkcM%3DBJwqaDqrOAD5xpHz5jHRLa5yYYl7V4JfGCvGtiJmJ726k3HoGu'

class TwitterApiClient(object):
    def __init__(self):
        pass

    def retrieve_twitter_access_token(self):
        return ACCESS_TOKEN # If the ACCESS_TOKEN has expired comment this line
        url = 'https://api.twitter.com/oauth2/token'
        payload = {'grant_type': 'client_credentials'}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Authorization': 'Basic ' + BASE64_TOKEN
        }
        r = requests.post(url, params=payload, headers=headers)
        if r.status_code != 200:
            print r.text
            return None
        return r.json()['access_token']

    def retrieve_user_tweets_rpc(self, user, count=400, max_id=None):
        """RPC to twitter API to retrieve user tweets

        param user: User for which tweets are to be retrieved
        param max_id: Min id till which the tweets have been processed
        The tweets from the API call will have an id <= max_id
        """
        access_token = self.retrieve_twitter_access_token()
        url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
        headers = {'Authorization': 'Bearer ' + access_token}
        params = {
            'count': count,
            'screen_name': user,
            'trim_user': 1,
            'exclude_replies': 'true'
        }
        if max_id is not None:
            params['max_id'] = max_id

        r = requests.get(url, params=params, headers=headers)
        if r.status_code != 200 or 'errors' in r.json():
            print r.text # debugging
            return None
        # print json.dumps(r.json(), indent=4, separators=(',', ': '))
        return r.json() # dict

if __name__ == '__main__':
    print TwitterApiClient().retrieve_twitter_access_token()
    print TwitterApiClient().retrieve_user_tweets_rpc('Pink', 5)