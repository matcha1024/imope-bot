import discord, time, json

TOKEN_file = open(".TOKEN", "r", encoding="utf-8")
TOKEN = TOKEN_file.read()
TOKEN_file.close()
client = discord.Client()

points_file = open("./points.json")
points = json.load(points_file)
points_file.close()

@client.event
async def on_ready():
	print("Logged in.")

member_connected_time = {}
@client.event
async def on_voice_state_update(member, before, after):
	member = member.name
	if(before.channel == None):
		member_connected_time[member] = time.time()
		print(f"{member}さんが接続しました")
	else:
		time_now = time.time()
		connected_time = time_now - member_connected_time[member]

		try:
			points[member] += int(connected_time)
		except:
			points[member] = int(connected_time)
		points_write = open("./points.json", "w")
		json.dump(points, points_write)
		points_write.close()

		print(f"{member}さんが切断しました ({connected_time}秒)")

client.run(TOKEN)