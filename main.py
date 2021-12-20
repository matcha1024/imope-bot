import discord_bot, tweet, streaming
from multiprocessing import Process
import time


if __name__ == '__main__':
        p = Process(target = streaming.main)
        p.start()
        discord_bot.main()
