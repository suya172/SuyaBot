from datetime import datetime, timedelta
import pytz
import cohere
from Config import DISCORD_TOKEN, COHERE_TOKEN, DEBUG_CHANNEL_ID
import pickle
import discord
from discord import app_commands
from discord.app_commands import describe
from discord.ext import tasks
from typing import List, Union
import random

# Cohereに関する変数
co = cohere.Client(api_key=COHERE_TOKEN, client_name="SuyaBot")

# Discordに関する変数
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

history = []
channels: List[int] = []
# preamble: str = open('preamble.txt', 'r', encoding='utf-8').read()
preamble: str = open('preamble2.txt', 'r', encoding='utf-8').read()

# テキスト文字列をchunk_sizeで指定した大きさに分割し、リストに格納する https://note.com/el_el_san/n/n845c0efdfc4a
def split_text(text, chunk_size=1500):
  return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# メッセージに時刻を付け加えて出力 (デバッグ用)
def debug(message: str):
    content: str = datetime.now(pytz.timezone("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S") + ' ' + message
    print(content)
    
    

# 特定の、もしくは全てのチャンネルにメッセージを送信
async def send_message(message: str, channel: Union[int,None] = None):
    if channel is None:
        _c = 'all channels'
        for channel in channels:
            await client.get_channel(channel).send(message)
    else:
        _c = f'{channel}({client.get_channel(channel).name})'
        await client.get_channel(channel).send(message)
    debug(f"Sent message to {_c}: {message}")
    await client.get_channel(DEBUG_CHANNEL_ID).send(f"Sent message to {_c}: {message}")

# チャンネルの登録・解除
@tree.command(name='register', description='すやぼっとが返信するチャンネルを登録します。既に登録されている場合は解除します。')
async def register(ctx: discord.Interaction):
    res:str = ''
    if ctx.channel.id in channels:
        channels.remove(ctx.channel.id)
        res = f'{ctx.channel.id}({ctx.channel.name}) を解除しました。'
    else:
        channels.append(ctx.channel.id)
        res = f'{ctx.channel.id}({ctx.channel.name}) を登録しました。'
    await ctx.response.send_message(res)
    with open('channels.pkl', 'wb') as f:
        pickle.dump(channels, f)

@tasks.loop(seconds=59)
async def check_time():
    now = datetime.now(pytz.timezone("Asia/Tokyo"))
    if now.minute == 0 and now.hour == 0:
        with open('emoticon.txt', 'r', encoding='utf-8') as f:
            emoticons = f.readlines()
        emoticon = random.choice(emoticons).strip()
        await send_message('今日も一日お疲れ様！' + emoticon)
    # 60分の1の確率で独り言
    if random.randint(1,60) == 1:
        content = f'現在時刻は{now.hour}:{now.minute}です。あなたはなんとなく独り言を呟きたくなりました。あなたらしい独り言を呟いてください。独り言なので、意味のない鳴き声でも構いません。「すや」が言いそうな、自然な独り言を呟いてください。'
        content = preamble + '\n' + content
        res = co.chat(
            message=content,
            model="command-a-03-2025",
        )
        splitted_text = split_text(res.text,chunk_size=50)
        for chunk in splitted_text:
            await send_message(chunk, message.channel.id)


@client.event
async def on_message(message: discord.Message):
    global history, channels

    if message.author == client.user:
        return
    if message.channel.id not in channels:
        return
    content :str = ''
    if message.content.startswith('すや、'):
        content = message.content[3:]
    elif message.content.startswith(f'<@!{client.user.id}>'):
        content = message.content[len(client.user.id)+1:]
    else:
        return
    debug(f"Got message : {content}")
    content = f'あなたに話しかけた人の名前は「{message.author.name}」です。[]内のメッセージに対し、あなたらしい適切な返答をしてください。[{content}]'
    content = preamble + '\n' + content
    if len(history) > 0:
        res = co.chat(
            message=content,
            model="command-a-03-2025",
            chat_history=history
        )
    else:
        res = co.chat(
            message=content,
            model="command-a-03-2025",
        )
    splitted_text = split_text(res.text)
    for chunk in splitted_text:
        await send_message(chunk, message.channel.id)
    history = res.chat_history
    print(history[len(history)-1])
    with open('history.pkl', 'wb') as f:
        pickle.dump(history, f)

@client.event
async def on_ready():
    debug(f'We have logged in as {client.user}')
    if len(channels) == 0:
        debug('No channels registered.')
    else:
        debug(f'{len(channels)} channels registered.')
    await client.change_presence(activity=discord.Game("かつてあった青春"))
    await tree.sync()
    debug('Command tree synced.')
    check_time.start()
    await send_message("すやぼっとが来たよ！")

if __name__ == "__main__":
    try:
        with open('history.pkl', 'rb') as f:
            history = pickle.load(f)
            print('history loaded')
    except Exception:
        history = []
        print('failed to load history')

    try:
        with open('channels.pkl', 'rb') as f:
            channels = pickle.load(f)
            print('channels loaded')
    except Exception:
        channels = []

    client.run(DISCORD_TOKEN)
