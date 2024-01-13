import discord
import pandas as pd
import subprocess
import json
from asgiref.sync import async_to_sync
import asyncio

TOKEN = ""

client = discord.Client()


# requires `snscrap` library
COMMAND = r"snscrape --jsonl " \
          f"""--max-results num_results twitter-hashtag keyword"""


async def scrap_hashtag(hashtag, num_results):
    command = COMMAND.replace("keyword", hashtag).replace("num_results", str(num_results))
    cmd = subprocess.run(command, capture_output=True, shell=True, encoding="utf8")
    tweets = [json.loads(jline) for jline in cmd.stdout.splitlines()][:]

    loc, content, date, likes, replies, quotes, outlinks, convid, rt, url = [], [], [], [], [], [], [], [], [], []
    name, username = [], []
    print(cmd.stderr)

    for i, r in enumerate(tweets):
        try:
            content.append(r['renderedContent'])
            date.append(r['date'][:-6].replace('T', ' '))
            likes.append(r['likeCount'])
            replies.append(r['replyCount'])
            quotes.append(r['quoteCount'])
            rt.append(r['retweetCount'])
            url.append(r['url'])
            loc.append(r['user']['location'])
            name.append(r['user']['displayname'])
            username.append(r['user']['username'])
        except:
            print(i)

    df = pd.DataFrame(
        {
            'Name': name, 'UserName': username,
            'Content': content, 'Location': loc,
            'Likes': likes, 'Date': date, 'ReplyCount': replies,
            'QuoteCount': quotes, 'retweetCount': rt, 'Link': url
        }
    )
    df.to_excel(f'{hashtag}.xlsx', index=False)
    return str(df.shape)


@client.event
async def on_ready():
    print(f"WE have logged in as {client.user}")


@client.event
async def on_message(msg):
    username = str(msg.author).split("#")[0]
    user_msg = str(msg.content)
    channel = str(msg.channel.name)
    print(f"{username}: {user_msg} ({channel})")

    if msg.author == client.user:
        return

    if user_msg.find("!hashtag") != -1:
        hashtag = user_msg.split(" ")[1]
        num_results = int(user_msg.split(" ")[-1])
        await msg.channel.send(f"Scraping the tweets with the #{hashtag}")  # file=discord.File('test.py'))

        df_shape = await scrap_hashtag(hashtag, num_results)
        # await asyncio.sleep(10)
        await msg.channel.send(df_shape)
        await msg.channel.send(file=discord.File(f'{hashtag}.xlsx'))


client.run(TOKEN)
