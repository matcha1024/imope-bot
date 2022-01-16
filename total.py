import datetime,calendar
import discord,json
from tweet import doTweet

client = discord.Client()
notice_channel = 921758153341812736
role_id = [922115979788574851,922116968767696926,922117055753375765]

def get_end_month(dt):
    return calendar.monthrange(dt.year,dt.month)

def get_aggregation_period(dt):
    if dt.day == 1:
        last_date = (dt.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
        end_month = get_end_month(last_date)[1]
        date_first = last_date.replace(day=int(end_month/2)+1)
        date_end = last_date.replace(day=end_month)
    else:
        date_first = dt.replace(day=1)
        date_end = dt.replace(day=int(get_end_month(dt)[1]/2))
    return date_first.strftime('%Y/%m/%d'),date_end.strftime('%Y/%m/%d')

def get_next_aggregation_period(dt):
	text = "次回の集計期間\n"
	if dt.day == 1:
		date_end = dt.replace(day=int(get_end_month(dt)[1]/2))
		text += f"{dt.strftime('%Y/%m/%d')} ~ {date_end.strftime('%Y/%m/%d')}"
	else:
		date_first = dt.replace(day=int(get_end_month(dt)[1]/2)+1)
		date_end = dt.replace(day=int(get_end_month(dt)[1]))
		text += f"{date_first.strftime('%Y/%m/%d')} ~ {date_end.strftime('%Y/%m/%d')}"
	print(text)
	print(type(text))
	return text

def total():
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
    return point_list

@client.event
async def on_ready():
	date_now = datetime.datetime.now()
	date_first,date_end = get_aggregation_period(date_now)
	description = f"期間: {date_first} ~ {date_end} \n"
	twitter_message = description

	rank = 1
	description += "ポイントがリセットされました。 \n"
	for v in total():
		member = await client.guilds[0].fetch_member(int(v[1]))
		member_roles = [user_role.id for user_role in member.roles]
		name = member.display_name
		description += f"{rank}位: {name} さん ({v[0]}ポイント) \n"
		if len(description) <= 130:
			twitter_message = description
		for role in role_id:
			if role in member_roles:
				await member.remove_roles(member.guild.get_role(role))
		if rank <= 3:
			print(role_id[rank-1])
			await member.add_roles(member.guild.get_role(role_id[rank-1]))
		rank += 1
	embed = discord.Embed(
		title = "ポイント集計",
		description = description
	)
# 同じ内容のツイートをすると怒られてしまうので、テストの際などは下の2行をコメントアウトして行うこと
	doTweet(twitter_message + "#いもぺ順位")
	doTweet(get_next_aggregation_period(dt))
	await client.get_channel(notice_channel).send(embed = embed)
	await client.close()

dt = datetime.datetime.now()
cronlog = open("/home/ubuntu/imope-bot/logs/total.py", "a")
if not int(dt.day) in [1,int(get_end_month(dt)[1]/2)+1]:
	cronlog.write(str(dt) + ": Not the aggregation date\n")
	exit()
cronlog.write(str(dt) + ": Today is the aggregation day\n")
cronlog.close()
date_first,date_end = get_aggregation_period(dt)
print(date_first,date_end)
TOKEN_file = open(".TOKEN", "r", encoding="utf-8")
TOKEN = TOKEN_file.read()
TOKEN_file.close()

client.run(TOKEN)
