import discord, time, json, datetime, random, asyncio
from discord.ext import commands ,tasks
import nest_asyncio
nest_asyncio.apply()

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
client = commands.Bot(command_prefix='--')

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

def notice_point(point,member,type):
	embed = discord.Embed(
		title = f"ポイント獲得:{type}",
		description = f"{member}さんが{point}ポイント獲得しました。"
	)
	return embed

notice_channel = 917398065957195796
member_connected_time = {}

@client.event
async def on_ready():
    print("Logged in.")

@client.event
async def on_voice_state_update(member, before, after):
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
            await client.get_channel(notice_channel).send(embed = notice_point(logbo,member.name,"ログボ"))

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
        if 	0 <= connected_time:
            await client.get_channel(notice_channel).send(embed = notice_point(int(connected_time / 60),member.name,"通話"))



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
        out += f"{ctx.author.nick}さん: {json[user_id]['point']}\n"

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

def main():
	TOKEN_file = open(".TOKEN", "r", encoding="utf-8")
	TOKEN = TOKEN_file.read()
	TOKEN_file.close()

	client.run(TOKEN)

main()