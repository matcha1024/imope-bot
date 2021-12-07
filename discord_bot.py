import discord, time, json, datetime, random, asyncio
import discord_commands
from discord.ext import commands

points_path = "./date/points.json"
login_path = "./date/login.json"
intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
client = commands.Bot(command_prefix='--')

def load_json(path):
	file = open(path)
	file_value = json.load(file)
	file.close()
	return file_value

def write_json(write, path):
	file_write = open(path, "w")
	json.dump(write, file_write)
	file_write.close()
	return

def notice_point(point,member,type):
	embed = discord.Embed(
		title = f"ポイント獲得:{type}",
		description = f"{member}さんが{point}ポイント獲得しました。"
	)
	return embed

loop = asyncio.get_event_loop()
notice_channel = 917413934162649088

def main():
	TOKEN_file = open(".TOKEN", "r", encoding="utf-8")
	TOKEN = TOKEN_file.read()
	TOKEN_file.close()

	points = load_json(points_path)

	@client.event
	async def on_ready():
		print("Logged in.")

	member_connected_time = {}
	@client.event
	async def on_voice_state_update(member, before, after):
		member = member.name
		if(before.channel == None):
			member_connected_time[member] = time.time()

			login = load_json(login_path)

			today = datetime.datetime.now().day
			try:
				last = login[member]["last"]
			except:
				last = -1
			if(not last == today):
				try:
					login[member]["logbo"] += 1
				except:
					login[member] = {}
					login[member]["logbo"] = 1
				login[member]["last"] = today

				lowest = login[member]["logbo"]
				logbo = random.choice(range(lowest, lowest + 10))

				write_json(login, login_path)

				try:
					points[member] += logbo
				except:
					points[member] = logbo
				write_json(points, points_path)
				loop.run_until_complete(notice_point(logbo,member,"ログボ",client.get_channel(notice_channel)))
				await client.get_channel(notice_channel).send(embed = notice_point(logbo,member,"ログボ"))

			print(f"{member}さんが接続しました")
		else:
			time_now = time.time()
			connected_time = time_now - member_connected_time[member]

			try:
				points[member] += int(connected_time / 60)
			except:
				points[member] = int(connected_time / 60)
			write_json(points, points_path)

			print(f"{member}さんが切断しました ({connected_time}秒)")
			if 	60 <= connected_time:
				await client.get_channel(notice_channel).send(embed = notice_point(int(connected_time / 60),member,"通話"))

	@client.event
	async def on_message(message):
		points = load_json(points_path)

		name = message.author.name
		if(message.author.nick):
			name = message.author.nick
		if(message.author.bot):
			return

		if(message.content == '--point'):
			await message.channel.send(embed = discord_commands.point(message, name, points))
		elif(message.content == '--points'):
			await message.channel.send(embed = discord_commands.points(points))
		elif(message.content == '--help'):
			await message.channel.send(embed = discord_commands.help())

	client.run(TOKEN)
