import schedule, time, json, datetime
import discord

client = discord.Client()
notice_channel = 917413934162649088

point_list = []
is_done = False
def total():
	global point_list, is_done
	json_file = open("./userinfo.json")
	json_value = json.load(json_file)
	json_file.close()

	point_list = []
	for v in json_value:
		point_list.append( [json_value[v]["point"], v] )
		json_value[v]["point"] = 0

	json_write = open("./userinfo.json", "w")
	json.dump(json_value, json_write)
	json_write.close()

	point_list.sort(reverse=True)
	is_done = True


schedule.every(5).seconds.do(total)

@client.event
async def on_ready():
	global point_list, is_done
	while True:
		schedule.run_pending()

		if(is_done):
			date_now = datetime.datetime.now()
			date_2w_ago = date_now - datetime.timedelta(weeks = 2)
			description = f"期間: {date_2w_ago} ~ {date_now} \n"

			rank = 1
			description += "ポイントがリセットされました。 \n"
			for v in point_list:
				member = await client.guilds[0].fetch_member(int(v[1]))
				name = member.display_name
				description += f"{rank}位: {name} さん ({v[0]}ポイント) \n"
				rank += 1
			
			embed = discord.Embed(
				title = "ポイント集計",
				description = description
			)

			await client.get_channel(notice_channel).send(embed = embed)

		is_done = False
		time.sleep(2)

TOKEN_file = open(".TOKEN", "r", encoding="utf-8")
TOKEN = TOKEN_file.read()
TOKEN_file.close()

client.run(TOKEN)