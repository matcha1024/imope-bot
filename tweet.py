from twython import Twython, TwythonError
from auth import twythonInfo
def doTweet(text):
    twitter = twythonInfo()
    twitter.update_status(status=text)