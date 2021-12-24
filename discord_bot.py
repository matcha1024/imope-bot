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
voice_channel_index = {888778279560028230:0, 729707646508335108:1, 813619755905712168:2, 813619833031491585:3}

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

notice_channel = 921758153341812736
logs_channel = 923552788041060402
member_connected_time = {}
voice_enable_time = {}
duel_flg = False
duel_pre = False
duel_id = []
duel_res = dict()
def user_voice_state_check(member,before,after):
        time_now = time.time()
        for role in member.roles:
                if role.id == 923923777375592468:
                        print("免除")
                        return
        id = str(member.id)
        if not before.self_mute and after.self_mute:
                if not member_connected_time[id] == 0:
                        voice_enable_time[id] += time_now - member_connected_time[id]
        elif before.self_mute and not after.self_mute:
                member_connected_time[id] = time_now

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
                voice_enable_time[str(member.id)] = 0
                member_connected_time[str(member.id)] = 0
                is_mute = "ミュート" if after.self_mute else ""
                await client.get_channel(logs_channel).send(f"{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')} {member.display_name}がボイチャ接続 {is_mute}")
        elif before.channel and after.channel:
                if before.self_mute and not after.self_mute:
                        await client.get_channel(logs_channel).send(f"{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')} {member.display_name}がミュート解除")
                elif not before.self_mute and after.self_mute:
                        await client.get_channel(logs_channel).send(f"{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')} {member.display_name}がミュート設定")
        else:
                voice_channel_member[voice_channel_index[before.channel.id]].remove(member.id)
                if after.channel:
                        voice_channel_member[voice_channel_index[after.channel.id]].append(member.id)
                if not after.channel:
                        is_mute = "ミュート" if after.self_mute else ""
                        await client.get_channel(logs_channel).send(f"{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')} {member.display_name}がボイチャ切断 {is_mute}") 
        allsum = sum(len(v) for v in voice_channel_member)

        if 0 < allsum and not voice_member_tweet.is_running():
                print("起動")
                voice_member_tweet.start()
        elif 0 == allsum and voice_member_tweet.is_running():
                print("停止")
                voice_member_tweet.cancel()

        member_id = str(member.id)
        json = load_json()
        user_voice_state_check(member,before,after)
        if(after.channel):
                if(not before.channel and not after.self_mute):
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
                if not after.self_mute:
                        voice_enable_time[member_id] += time_now - member_connected_time[member_id]
                connected_time = voice_enable_time[member_id]

                try:
                        json[member_id]["point"] += int(connected_time / 60)
                except:
                        json[member_id]["point"] = int(connected_time / 60)
                write_json(json)

                print(f"{member_id}さんが切断しました ({connected_time}秒)")
                if      60 <= connected_time:
                        await client.get_channel(notice_channel).send(embed = notice_point(int(connected_time / 60),member.name,"通話", datetime.datetime.now()))

        ranking = get_ranking()
        medals = ["🥇", "🥈", "🥉"]
        for v in ranking:
                member = await client.guilds[0].fetch_member(int(v[1]))
                nick = demoji.replace(string=member.display_name, repl="")
                if medals:
                        nick = medals[0] + nick
                        medals = medals[1:]
                try:
                        await member.edit(nick=nick)
                except:
                        print("Administrator")




@client.command()
async def man(ctx):
    embed = discord.Embed(title = "マニュアル", description = "いもぺ部BOT使用法")
    f = open("help.txt", "r", encoding = "UTF-8")
    lines = f.readlines()
    lineIndex = 0
    title = ""
    description = ""
    while(lineIndex < len(lines)):
        line = lines[lineIndex].strip()
        if(line.startswith("# ")):
            title = line[2:].strip()
        else:
            description += f"{line.strip()}\n"

        if(lineIndex+1 < len(lines) and (lines[lineIndex+1].startswith("# ")) or lineIndex+1 == len(lines)):
            embed.add_field(name=title, value=f"{description}\n", inline=False)
            description = ""
        lineIndex += 1
    await ctx.send(embed=embed)

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

@client.command()
async def duel(ctx):
        global duel_flg,duel_id
        print("test")
        if duel_flg:
                return
        duel_flg = True
        duel_id = []
        duel_id.append(ctx.author.id)
        await ctx.send(embed = discord.Embed(description = "決闘を始めます。\n対戦したい人は「参加」とメッセージを送ってください。\n他のメッセージの場合キャンセルされます。"))

@client.command()
async def rduel(ctx):
        global duel_flg,duel_id,duel_pre,duel_res
        if  not str(ctx.author.id) in ['833198910251728896','491265560135598081','704130953307750452']:
                return
        duel_flg = False
        duel_pre = False
        duel_id = []
        duel_res = dict()
        await ctx.send(embed = discord.Embed(description = "決闘がキャンセルされました。"))

# クソザコ実装ごめんという気持ちでいっぱい
# 時間あるときに直します。。。
@client.event
async def on_message(message):
        global duel_flg,duel_id,duel_pre,duel_res
        if(message.author.bot):
                return
        if duel_flg:
                if duel_pre:
                        if message.content == "サイコロ" and message.author.id in duel_id:
                                if  message.author.id not in duel_res:
                                        res = random.randint(1,6)
                                        duel_res[message.author.id] = res
                                        await message.channel.send(embed = discord.Embed(description = f"{message.author.display_name}は{res}を出しました。"))
                                        print(duel_res)
                                if len(duel_res) == 2:
                                        point = []
                                        if duel_res[duel_id[0]] == duel_res[duel_id[1]]:
                                                await message.channel.send(embed = discord.Embed(description = "引き分けのためやり直しです。"))
                                                duel_res = dict()
                                        elif duel_res[duel_id[0]] > duel_res[duel_id[1]]:
                                                await message.channel.send(embed = discord.Embed(description = f"{duel_id[2]}の勝利!"))
                                                point = [10,-10]
                                        else:
                                                await message.channel.send(embed = discord.Embed(description = f"{duel_id[3]}の勝利!"))
                                                point = [-10,10]
                                        await client.get_channel(notice_channel).send(embed = notice_point(point[0],duel_id[2],"決闘", datetime.datetime.now()))
                                        await client.get_channel(notice_channel).send(embed = notice_point(point[1],duel_id[3],"決闘", datetime.datetime.now()))
                                        json = load_json()
                                        json[str(duel_id[0])]["point"] += point[0]
                                        json[str(duel_id[1])]["point"] += point[1]
                                        write_json(json)
                                        duel_flg = False
                                        duel_pre = False
                                        duel_id = []
                                        duel_res = dict()
                                        ranking = get_ranking()
                                        medals = ["🥇", "🥈", "🥉"]
                                        for v in ranking:
                                                member = await client.guilds[0].fetch_member(int(v[1]))
                                                nick = demoji.replace(string=member.display_name, repl="")
                                                if medals:
                                                        nick = medals[0] + nick
                                                        medals = medals.pop(0)
                                                try:
                                                        await member.edit(nick=nick)
                                                except:
                                                        print("Administrator")

                                                
                elif message.content == '参加' and message.author.id != duel_id[0]:
                        duel_id.append(message.author.id)
                        member1 = await client.guilds[0].fetch_member(int(duel_id[0]))
                        member2 = await client.guilds[0].fetch_member(int(duel_id[1]))
                        duel_id.append(member1.display_name)
                        duel_id.append(member2.display_name)
                        await message.channel.send(embed = discord.Embed(description =f"{duel_id[2]} vs {duel_id[3]}\nサイコロ　とメッセージを送るとサイコロを振れます。振り直しはできません。"))
                        duel_pre = True
                else:
                        duel_flg = False
                        await message.channel.send(embed = discord.Embed(description = '決闘がキャンセルされました。'))
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
