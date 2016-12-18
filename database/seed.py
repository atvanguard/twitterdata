from twitterdata.twitter_data_client import TwitterData
import sys

def main():
    """Seed the database with users mentioned in verified.txt"""
    count = None
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
        print 'Seeding database with %s users' % sys.argv[1]
    with open('database/verified.txt') as f:
        users = f.readlines()[0].split(', ')
        if count is not None:
            users = users[0:count]

    twitter_data = TwitterData()
    for user in users:
        print twitter_data.track_new_user(user)

if __name__ == '__main__':
    main()