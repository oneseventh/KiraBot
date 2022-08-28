from ast import Continue, JoinedStr
from asyncore import read
from pydoc import cli
from tabnanny import check
from turtle import color
from unicodedata import category
from pyreadline import Readline
from discord.ext import commands
import discord
import re
import asyncio
import os.path
import datetime
import time
from datetime import timedelta

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='?', intents=intents) 

channel_id = 0 # 채널 id

@client.event
async def on_ready():
    print("활성화")
    print(f"봇 이름 : {format(client.user.name)}")
'''
@client.command()
async def set_welcome(ctx, channel: discord.TextChannel):
    await ctx.send(f"{channel.name} 채널에 환영인사를 남깁니다.")
'''

#역할을 부여하는 명령어
@client.command()
async def set_role(ctx, role: discord.Role):
    await ctx.send(f"{role.name} 역할을 부여합니다.")
    await ctx.author.add_roles(role)
#로그 저장할 채널을 설정하는 명령어
@client.command()
async def log_channel(ctx, channel: discord.TextChannel):
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
    if channel_id != 0:
        channel = client.get_channel(channel_id)
        embed=discord.Embed(title=f"{channel.name} 채널에 로그를 저장합니다.", description=f"한번 선택한 채널은 바꿀 수 없습니다\n(변경기능 개발중!)", color=0x5947FF)
        embed.add_field(name="ID", value=f"```diff\n+ {channel_id}```", inline=False)
        embed.set_footer(text=f"Request by {ctx.author} ・ Developed by 동건#3038", icon_url=ctx.author.display_avatar)
        await channel.send(embed=embed)

#로그 저장한 후 채널 ID가 잘 저장 되었는지 확인하는 명령어
@client.command()
async def selected_channel(ctx):
    await ctx.send(channel_id)
    await ctx.send(type(channel_id))
#메세지가 삭제되었을 때 로그를 저장하는 이벤트
@client.event
async def on_raw_message_delete(payload):
    if payload.cached_message.author.bot:
        return
    now = time.localtime()
    channel = client.get_channel(channel_id)
    embed=discord.Embed(title="님의 메세지를 삭제하였습니다", description=f"메세지가 삭제된 채널 <#{payload.cached_message.channel.id}>", color=0x5947FF)
    embed.set_author(name=payload.cached_message.author, icon_url=payload.cached_message.author.display_avatar)
    embed.add_field(name="삭제된 메세지 내용", value=payload.cached_message.content, inline=False)
    embed.add_field(name="삭제된 시간", value="``%04d-%02d-%02d %02d:%02d:%02d``" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), inline=False)
    embed.add_field(name="IDs", value=f"```diff\n+ {payload.cached_message.id} (message) \n+ {int(payload.guild_id)} (guild) \n+ {int(channel_id)} (channel) ```", inline=False)
    embed.set_footer(text="Developed by 동건#3038")
    await channel.send(embed=embed)
#메세지가 수정되었을 때 로그를 저장하는 이벤트
@client.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    now = time.localtime()
    channel = client.get_channel(channel_id)
    embed=discord.Embed(title="님의 메세지를 수정하였습니다", description=f"메세지가 수정된 채널 <#{before.channel.id}>", color=0xE189FC)
    embed.set_author(name=before.author, icon_url=before.author.display_avatar)
    embed.add_field(name="수정전 메세지 내용", value=before.content, inline=True)
    embed.add_field(name="수정후 메세지 내용", value=after.content, inline=True)
    embed.add_field(name="수정된 시간", value="``%04d-%02d-%02d %02d:%02d:%02d``" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), inline=False)
    embed.add_field(name="IDs", value=f"```diff\n+ {before.id} (message) \n+ {int(before.guild.id)} (guild) \n+ {int(channel_id)} (channel) ```", inline=False)
    embed.set_footer(text="Developed by 동건#3038")
    await channel.send(embed=embed)
#역할이 추가되었을 때 로그를 저장하는 이벤트
@client.event
async def on_guild_role_create(role):
    channel = client.get_channel(channel_id)
    embed=discord.Embed(title=f"<{role.name}> 역할이 생성되었습니다", color=0x00FF22)
    embed.add_field(name="IDs", value=f"```diff\n+ {role.id} (role) \n+ {int(role.guild.id)} (guild)```", inline=False)
    embed.set_footer(text="Developed by 동건#3038")
    await channel.send(embed=embed)
#역할이 삭제되었을 때 로그가 저장되는 이벤트
@client.event
async def on_guild_role_delete(role):
    channel = client.get_channel(channel_id)
    embed=discord.Embed(title=f"<{role.name}> 역할이 삭제되었습니다", color=0xFF0000)
    embed.add_field(name="IDs", value=f"```diff\n+ {role.id} (role) \n+ {int(role.guild.id)} (guild)```", inline=False)
    embed.set_footer(text="Developed by 동건#3038")
    await channel.send(embed=embed)
#역할이 수정되었을 때 로그가 저장되는 이벤트
@client.event
async def on_guild_role_update(before, after):
    channel = client.get_channel(channel_id)
    checking = False
    embed=discord.Embed(title=f"<{before.name}> 역할이 업데이트 되었습니다", color=after.colour)
    if(before.name != after.name):
        embed.add_field(name=f"{before.name} -> {after.name}", inline=False)
        checking = True
    if(before.colour != after.colour):
        embed.add_field(name="색상", value=f"{before.colour} -> {after.colour}(임베드색상)", inline=False)
        checking = True
    if(before.position != after.position):
        embed.add_field(name="순서", value=f"{before.position} -> {after.position} ```diff\n- 순서(position)는 역할 우선순위를 말합니다.(수가 높을수록 우선)```", inline=False)
        checking = True
    if(before.hoist != after.hoist):
        embed.add_field(name="역할 분리여부(Hoist)", value=f"{before.hoist} -> {after.hoist}", inline=False)
        checking = True
    if(before.mentionable != after.mentionable):
        embed.add_field(name="멘션", value=f"{before.mentionable} -> {after.mentionable}", inline=False)
        checking = True
    if(checking == True):
        embed.add_field(name="IDs", value=f"```diff\n+ {after.id} (role) \n+ {int(after.guild.id)} (guild)```", inline=False)
        embed.set_footer(text="Developed by 동건#3038")
        await channel.send(embed=embed)


#채널이 추가되었을 때 로그가 저장되는 이벤트
@client.event
async def on_guild_channel_create(channel):
    channel = client.get_channel(channel_id)
    embed=discord.Embed(title=f"<{channel.name}> 채널이 생성되었습니다", color=0x00FF22)
    embed.add_field(name="IDs", value=f"```diff\n+ {channel.id} (role) \n+ {int(channel.guild.id)} (guild)```", inline=False)
    embed.set_footer(text="Developed by 동건#3038")
    await channel.send(channel.abc.GuildChannel.CategoryChannel.name)
#채널이 삭제되었을 때 로그가 저장되는 이벤트
@client.event
async def on_guild_channel_delete(channel):
    channel = client.get_channel(channel_id)
    embed=discord.Embed(title=f"<{channel.name}> 채널이 삭제되었습니다", color=0xFF0000)
    embed.add_field(name="IDs", value=f"```diff\n+ {channel.id} (role) \n+ {int(channel.guild.id)} (guild)```", inline=False)
    embed.set_footer(text="Developed by 동건#3038")
    await channel.send(embed=embed)
#채널이 수정되었을 때 로그가 저장되는 이벤트
@client.event
async def on_guild_channel_update(before, after):
    channel = client.get_channel(channel_id)
    checking = False
    embed=discord.Embed(title=f"<{before.name}> 채널이 업데이트 되었습니다", color=0xFFF700)
    if(before.name != after.name):
        embed.add_field(name="이름",value=f"{before.name} -> {after.name}", inline=False)
        checking = True
    if(before.category != after.category):
        embed.add_field(name="카테고리",value=f"{before.category} -> {after.category}", inline=False)
        checking = True
    if(before.topic != after.topic):
        embed.add_field(name="변경전 채널주제",value=f"{before.topic}", inline=True)
        embed.add_field(name="변경후 채널주제",value=f"{after.topic}", inline=True)
        checking = True
    if (before.nsfw != after.nsfw):
        embed.add_field(name="NSFW",value=f"{before.nsfw} -> {after.nsfw}", inline=False)
        checking = True
    if(checking == True):
            embed.set_footer(text="Developed by 동건#3038")
            await channel.send(embed=embed)
    #채널의 특정 역할의 권한이 추가되거나 삭제되었을때 생성되는 로그 이벤트 기능
    '''
    if(before.changed_roles != after.changed_roles):
        if(before.changed_roles == None):
            embed.add_field(name="추가된 역할",value={before.changed_roles[1]}, inline=False)
        else:
            embed.add_field(name="삭제된 역할",value=f"{before.changed_roles[1]}", inline=False)
        checking = True
    '''
#invite 코드가 생성되었을때 로그를 저장하는 이벤트
@client.event
async def on_invite_create(invite):
    channel = client.get_channel(channel_id)
    embed=discord.Embed(title=f"<#{invite.channel.name}> 채널에서 초대코드가 생성되었습니다", color=0x86FFC3)
    embed.add_field(name="생성자",value=f"``{invite.inviter}``", inline=True)
    embed.add_field(name="초대코드",value=f"{invite.code}", inline=True)
    embed.add_field(name="초대코드 만료기간",value=f"``{invite.expires_at}``\n(UTC+00:00 기준)", inline=True)
    if invite.max_uses == 0:
        embed.add_field(name="초대인원 제한",value=f"``무제한``", inline=True)
    else:
        embed.add_field(name="초대인원 제한",value=f"``{invite.max_uses}명``", inline=True)
    embed.add_field(name="임시초대여부",value=f"{invite.temporary}", inline=True)
    embed.set_footer(text="Developed by 동건#3038")
    await channel.send(embed=embed)
#invite 코드가 삭제되었을때 로그를 저장하는 이벤트
@client.event
async def on_invite_delete(invite):
    channel = client.get_channel(channel_id)
    now = time.localtime()
    embed=discord.Embed(title=f"<#{invite.channel.name}> 채널에서 초대코드가 삭제되었습니다", color=0xFF0000)
    embed.add_field(name="초대코드",value=f"{invite.code}", inline=True)
    embed.add_field(name="초대코드가 삭제된 일시",value="``%04d-%02d-%02d %02d:%02d:%02d``" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), inline=True)
    embed.set_footer(text="Developed by 동건#3038")
    await channel.send(embed=embed)
    

client.run(token=open(".token", "r").readline())