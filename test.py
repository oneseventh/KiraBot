from ast import JoinedStr
from asyncore import read
from pydoc import cli
from pyreadline import Readline
from discord.ext import commands
import discord
import re
import asyncio
import os.path
import datetime
import time

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='?', intents=intents) 

channel_id = 0 # 채널 id

@client.event
async def on_ready():
    print("활성화")
    print(f"봇 이름 : {format(client.user.name)}")

@client.command()
async def set_welcome(ctx, channel: discord.TextChannel):
    await ctx.send(f"{channel.name} 채널에 환영인사를 남깁니다.")

@client.command()
async def set_role(ctx, role: discord.Role):
    await ctx.send(f"{role.name} 역할을 부여합니다.")
    await ctx.author.add_roles(role)

@client.command()
async def log_channel(ctx, channel: discord.TextChannel):
    await ctx.send(f"{channel.name} 채널에 로그를 저장합니다.")
    path = "C:\\Users\\Administrator\\Desktop\\discord_bot\\ScinceBot\\setting.txt"
    global channel_id
    if os.path.isfile(path):
        with open(path) as r:
            r.seek(0)
            lines = r.readlines()
            for line in lines:
                if channel.id == int(line):
                    channel_id = int(line)
    else:
        f = open(path, 'w')
        f.write(f"{channel.id}\n")
        channel_id = channel.id
        f.close()
    await ctx.send(channel_id)

@client.event
async def on_raw_message_delete(payload):
    if payload.cached_message.author.bot:
        return
    now = time.localtime()
    channel = client.get_channel(channel_id)
    embed=discord.Embed(title="님의 메세지를 삭제하였습니다", description=f"메세지가 삭제된 채널 <#{payload.cached_message.channel.id}>", color=0xf264e6)
    embed.set_author(name=payload.cached_message.author, icon_url=payload.cached_message.author.display_avatar)
    embed.add_field(name="삭제된 메세지 내용", value=payload.cached_message.content, inline=False)
    embed.add_field(name="삭제된 시간", value="``%04d-%02d-%02d %02d:%02d:%02d``" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), inline=False)
    embed.add_field(name="IDs", value=f"```diff\n+ {payload.cached_message.id} (message) \n+ {int(payload.guild_id)} (server) \n+ {int(channel_id)} (channel) ```", inline=False)
    embed.set_footer(text="만든 사람: 동건#3038")
    await channel.send(embed=embed)
    


client.run('MTAxMjMwODY0MTA2OTY4Mjc1OA.GBpEsf.cYITj1CIBdzLKykKoCC9noCRDbtPJz4uitRLcc')