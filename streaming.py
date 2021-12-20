from twython import Twython, TwythonError, TwythonStreamer
from tweet import doReply
from auth import getTweetInfo,consumer_key,consumer_secret,access_token,access_token_secret
from command import doCommand
twitter = getTweetInfo()
class MyStreamer(TwythonStreamer):
    def followInfo(replayd_id):
        userInfo = twitter.lookup_friendships(user_id = replayd_id)
        print(userInfo[0]['connections'])
        if userInfo[0]['connections'][0] == 'none':
            return 0
        return len(userInfo[0]['connections'])

    def on_success(self, data):
        replied_user_id = data['user']['id']
        replied_id = data['id']
        message = ''
        print(twitter.lookup_friendships(screen_name = data['user']['screen_name']))
        followState = MyStreamer.followInfo(replied_user_id)
        print(followState)
        if followState == 0:
            message = 'フォローをしてくれた後にメンションをするとフォローバックします。'
        elif followState == 1:
            twitter.create_friendship(id = replied_user_id)
            message = 'フォローありがとう！\nフォローバックしたよ！もしされていなかったら管理者に連絡して下さい。'

        # FFの関係になければ処理終了
        if followState < 2:
            doReply(message,replied_id)
            return
        command = data['text'].replace('@imope_bot ','')
        print(command)
        doCommand(command,replied_id,data)
    def on_error(self, status_code, data):
        print(status_code)


# print("streaming test")
stream = MyStreamer(consumer_key,consumer_secret,access_token,access_token_secret)
stream.statuses.filter(track='@imope_bot')
