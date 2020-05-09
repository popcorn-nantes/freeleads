from twython import TwythonStreamer
from pymongo import MongoClient
import os
import slack
from vocabulary import BANS, TECHS, RH


# client = MongoClient()
# db = client.freeleads
# tweets = db.tweet
# leads = db.lead


SLACK_API_TOKEN = os.environ.get('SLACK_API_TOKEN')
TWITTER_APP_KEY = os.environ.get('TWITTER_APP_KEY')
TWITTER_APP_SECRET = os.environ.get('TWITTER_APP_SECRET')
TWITTER_OAUTH_TOKEN = os.environ.get('TWITTER_OAUTH_TOKEN')
TWITTER_OAUTH_TOKEN_SECRET = os.environ.get('TWITTER_OAUTH_TOKEN_SECRET')


class LeadStreamer(TwythonStreamer):

    def on_success(self, data):
        if data.get("retweeted_status"):  # filter retweets
            print("RETWEET")
            return
        self.detect_lead(data)

    def on_error(self, status_code, data):
        print(status_code)
        print(data)
        self.disconnect()

    def detect_lead(self, data):        
        text, hashtags = self.get_text(data)
        url = self.get_url(data)
        text_lowered = text.lower()   

        for ban in BANS:
            if ban in text_lowered or ban in hashtags:
                return

        for tech in TECHS:
            if tech in text_lowered or tech in hashtags:
                #tweet_id = tweets.insert_one(data).inserted_id
                print("TECH")
                for rhword in RH:
                    if rhword in text_lowered or rhword in hashtags:
                        #lead_id = leads.insert_one(data).inserted_id
                        print("LEAD")
                        self.post(url)
                        break
                break

    def post(self, url):
        slackclient.chat_postMessage(
            as_user=False,
            username="Twitter bot",
            channel='#tuyaux-boulot-twitter-bot',
            text=url
        )

    def get_text(self, data):
        text = data.get("extended_tweet", {}).get("full_text") or data.get("text")
        print(text)

        hashtags = data.get("entities", {}).get("hashtags", [])
        hashtags = [h["text"].lower() for h in hashtags]
        print(hashtags)

        return text, hashtags

    def get_url(self, data):
        tweet_id = data.get("id")
        user = data.get("user")
        user_name = user and user.get("screen_name")

        if user_name and tweet_id:
            url = f"https://twitter.com/{user_name}/status/{tweet_id}"
        elif data.get("entities", {}).get("urls"):
            url = data.get("entities", {})["urls"][0].get("url")
        else:
            url = ''
        return url


slackclient = slack.WebClient(token=SLACK_API_TOKEN, ssl=False)
stream = LeadStreamer(TWITTER_APP_KEY, TWITTER_APP_SECRET, TWITTER_OAUTH_TOKEN, TWITTER_OAUTH_TOKEN_SECRET)
stream.statuses.filter(track=TECHS, language="fr")
