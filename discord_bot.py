import discord, time, json, datetime, random, asyncio,demoji
from discord.ext import commands ,tasks
import nest_asyncio
from tweet import doTweet
nest_asyncio.apply()

intents = discord.Intents.default()
intents.members = True

# client = discord.Client(intents=intents)
client = commands.Bot(command_prefix='--', intents=intents)
voice_channel_member = [[],[],[],[]]
before_tweet_date = datetime.datetime(2018,1,1)
voice_channel_index = {917348889714130958:0,921585246087036978:1,921585330476417055:2,921585395710451782:3}

def load_json():
	file = open('./userinfo.json')
	file_value = json.load(file)
	file.close()
	return file_value

def write_json(write):
	file_write = open('./userinfo.json', "w")
	json.dump(write, file_write)
	file_write.close()
	return

def notice_point(point,member,type, t):
	embed = discord.Embed(
		title = f"ポイント獲得:{type}",
		description = f"{member}さんが{point}ポイント獲得しました。 ({t.year}/{t.month}/{t.day}/{t.hour}:{t.minute}:{t.second})"
	)
	return embed

def get_ranking():
	json = load_json()
	ranking = []

	for v in json:
		ranking.append([json[v]["point"], v])
	ranking.sort()
	ranking.reverse()
	return ranking

notice_channel = 917413934162649088
member_connected_time = {}

@client.event
async def on_ready():
	print("Logged in.")

@tasks.loop(minutes=30)
async def voice_member_tweet():
	global before_tweet_date
	tweet_time = datetime.datetime.now() - before_tweet_date
	if tweet_time.seconds < 60*5:
		return
	before_tweet_date = datetime.datetime.now()

	voice_name = ["おえかきボイチャ:","ボイスチャンネル1:","ボイスチャンネル2:","ボイスチャンネル3:"]
	message = "ボイスチャンネル接続状況\n\n"
	for i in range(4):
		message += voice_name[i]
		if len(voice_channel_member[i]) == 0:
			message += "なし\n"
		else:
			message += "\n"
			for id in voice_channel_member[i]:
				name = await client.guilds[0].fetch_member(int(id))
				message += f"{' '*6}・{name.display_name}\n"
	message += f"\n{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')} 現在"
	doTweet(message)

@client.event
async def on_voice_state_update(member, before, after):
	if not before.channel:
		voice_channel_member[voice_channel_index[after.channel.id]].append(member.id)
	else:
		voice_channel_member[voice_channel_index[before.channel.id]].remove(member.id)
		if after.channel:
			voice_channel_member[voice_channel_index[after.channel.id]].append(member.id)
	allsum = sum(len(v) for v in voice_channel_member)

	if 0 < allsum and not voice_member_tweet.is_running():
		print("起動")
		voice_member_tweet.start()
	elif 0 == allsum and voice_member_tweet.is_running():
		print("停止")
		voice_member_tweet.cancel()

	member_id = str(member.id)
	json = load_json()
	if(before.channel == None):
		member_connected_time[member_id] = time.time()

		today = datetime.datetime.now().day
		if not member_id in json:
			json[member_id] = {}
			json[member_id]["nick"] = member.nick
		try:
			last = json[member_id]["login"]["last"]
		except:
			last = -1
		if(not last == today):
			try:
				json[member_id]["login"]["logbo"] += 1
			except:
				json[member_id]["login"] = {}
				json[member_id]["login"]["logbo"] = 1
			json[member_id]["login"]["last"] = today

			lowest = json[member_id]["login"]["logbo"]
			logbo = random.choice(range(lowest, lowest + 10))

			write_json(json)

			try:
				json[member_id]["point"] += logbo
			except:
				json[member_id]["point"] = logbo
			write_json(json)
			await client.get_channel(notice_channel).send(embed = notice_point(logbo,member.name,"ログボ", datetime.datetime.now()))

		print(f"{member.name}さんが接続しました")
	else:
		time_now = time.time()
		connected_time = time_now - member_connected_time[member_id]

		try:
			json[member_id]["point"] += int(connected_time / 60)
		except:
			json[member_id]["point"] = int(connected_time / 60)
		write_json(json)

		print(f"{member_id}さんが切断しました ({connected_time}秒)")
		if 	60 <= connected_time:
			await client.get_channel(notice_channel).send(embed = notice_point(int(connected_time / 60),member.name,"通話", datetime.datetime.now()))

	# ranking = get_ranking()
	# medals = ["🥇", "🥈", "🥉"]
	# i = 0
	# for v in ranking:
	# 	member = await client.guilds[0].fetch_member(int(v[1]))
	# 	nick = member.display_name
	# 	if(nick[0] == medals[0] or nick[0] == medals[1] or nick[0] == medals[2]):
	# 		nick = nick[1:]
	# 	if(i < 3):
	# 		nick = medals[i] + nick
	# 	try:
	# 		await member.edit(nick=nick)
	# 	except:
	# 		print("Administrator.")

	# 	i += 1



@client.command()
async def point(ctx):
	name = ctx.author.nick if ctx.author.nick else ctx.author.name
	points = load_json()
	point = points[str(ctx.author.id)]["point"]
	try:
		embed = discord.Embed(
			title = f"{name}さんの現在のポイント",
			description = f"{point}"
		)

		await ctx.send(embed = embed)
	except:
		embed = discord.Embed(
			title = f"Error.",
			description = f"{name}さんはポイントを持っていません。"
		)

		await ctx.send(embed = embed)

@client.command()
async def points(ctx):
	out = ""
	json = load_json()
	for user_id in json:
		member = await client.guilds[0].fetch_member(int(user_id))
		out += f"{member.display_name}さん: {json[user_id]['point']}\n"

	embed = discord.Embed(
		title = "ポイント一覧表",
		description = out
	)
	await ctx.send(embed = embed)

@client.event
async def on_message(message):
	if(message.author.bot):
		return
	await client.process_commands(message)

@client.event
async def on_member_update(before, after):
	if(not before.nick == after.nick):
		ranking = 0
		top3 = get_ranking()[:3]
		for v in top3:
			if(int(v[1]) == after.id):
				break
			ranking += 1

		medals = ["🥇", "🥈", "🥉"]
		nick = after.display_name

		nick = demoji.replace(string=nick, repl="")
		if(ranking < 3):
			nick = medals[ranking] + nick

		member = await client.guilds[0].fetch_member(int(after.id))
		try:
			await member.edit(nick=nick)
		except:
			print("Administrator")


def main():
	TOKEN_file = open(".TOKEN", "r", encoding="utf-8")
	TOKEN = TOKEN_file.read()
	TOKEN_file.close()

	client.run(TOKEN)

main()