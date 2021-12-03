import discord, time

TOKEN_file = open(".TOKEN", "r", encoding="utf-8")
TOKEN = TOKEN_file.read()
TOKEN_file.close()
client = discord.Client()

@client.event
async def on_ready():
	print("Logged in.")


member_connected_time = {}
@client.event
async def on_voice_state_update(member, before, after):
	if(before.channel == None):
		member_connected_time[member] = time.time()
		print(f"{member}さんが接続しました")
	else:
		time_now = time.time()
		connected_time = time_now - member_connected_time[member]
		print(f"{member}さんが切断しました ({connected_time}秒)")

client.run(TOKEN)