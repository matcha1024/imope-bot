import discord

async def point(message, name, points):
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

async def points(message, points):
	out = ""
	for v in points:
		out += f"{v}さん: {points[v]}\n"

	embed = discord.Embed(
		title = "ポイント一覧表",
		description = out
	)

	await message.channel.send(embed = embed)

async def help(message):
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
			print(description)
			embed.add_field(name=title, value=f"{description}\n", inline=False)
			description = ""
		lineIndex += 1
			
	await message.channel.send(embed = embed)
