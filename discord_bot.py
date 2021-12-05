import discord, time, json, datetime, random

points_path = "./date/points.json"
login_path = "./date/login.json"

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

def main():
	TOKEN_file = open(".TOKEN", "r", encoding="utf-8")
	TOKEN = TOKEN_file.read()
	TOKEN_file.close()
	client = discord.Client()

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

				logbo = random.choice(range(lowest, lowest + 10))

				write_json(login, login_path)

				try:
					points[member] += logbo
				except:
					points[member] = logbo
				write_json(points, points_path)

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

	@client.event
	async def on_message(message):
		points = load_json(points_path)

		name = message.author.name
		if(message.author.nick):
			name = message.author.nick
		if(message.author.bot):
			return
		if(message.content == '!point'):
			try:
				embed = discord.Embed(
					title = f"{name}さんの現在のポイント",
					description = f"{points[message.author.name]}"
				)

				await message.channel.send(embed = embed)
			except:
				embed = discord.Embed(
					title = f"Error.",
					description = f"{name}さんはポイントを持っていません。"
				)

				await message.channel.send(embed = embed)


		elif(message.content == '!points'):
			out = ""
			for v in points:
				out += f"{v}さん: {points[v]}\n"

			embed = discord.Embed(
				title = "ポイント一覧表",
				description = out
			)

			await message.channel.send(embed = embed)

	client.run(TOKEN)