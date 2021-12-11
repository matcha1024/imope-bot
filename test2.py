import discord
client = discord.Client()

@client.event
async def on_message(message):
	await message.channel.send("test")
	await message.channel.send("test2")

def main():
	TOKEN_file = open(".TOKEN", "r", encoding="utf-8")
	TOKEN = TOKEN_file.read()
	TOKEN_file.close()

	client.run(TOKEN)

main()