import discord

def point(message, name, points):
	embed = discord.Embed()
	try:
		embed = discord.Embed(
			title = f"{name}さんの現在のポイント",
			description = f"{points[message.author.name]}"
		)
	except:
		embed = discord.Embed(
			title = f"Error.",
			description = f"{name}さんはポイントを持っていません。"
		)
	return embed


def points(points):
	out = ""
	for v in points:
		out += f"{v}さん: {points[v]}\n"

	embed = discord.Embed(
		title = "ポイント一覧表",
		description = out
	)

	return embed

def help():
	embed = discord.Embed(title="マニュアル",description="簡易的な使用方法です\n コマンドは[]で囲んであります")
	f = open('help.txt','r',encoding='UTF-8')
	lines = f.readlines()
	lineIndex = 0
	title=''
	description=''
	while(lineIndex < len(lines)):
		line = lines[lineIndex].strip()
		if(line.startswith('# ')):
			title = line[2:].strip()
		else:
			description += f"{line.strip()}\n"

		if(lineIndex+1 < len(lines) and (lines[lineIndex + 1].startswith('# ')) or lineIndex+1 == len(lines)):
			embed.add_field(name=title, value=f"{description}\n", inline=False)
			description = ""
		lineIndex += 1
			
	return embed
