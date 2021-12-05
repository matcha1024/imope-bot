from twython import Twython, TwythonError
from auth import getTweetInfo
twitter = getTweetInfo()
def doTweet(text,imagePath = ''):
    if imagePath == '':
        twitter.update_status(status=text)
    else:
        image = open(imagePath,'rb')
        responseimg = twitter.upload_media(media=image)
        twitter.update_status(status=text,media_ids=[responseimg['media_id']])

def doReply(text,id,imagePath = ''):
    if imagePath == '':
        twitter.update_status(status=text, in_reply_to_status_id=id, auto_populate_reply_metadata=True)
    else:
        image = open(imagePath,'rb')
        responseimg = twitter.upload_media(media=image)
        twitter.update_status(status=text,in_reply_to_status_id=id,media_ids=[responseimg['media_id']])
