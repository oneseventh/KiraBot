"""
    #제작: @17th
    #최종 수정일: 2022년 09월 01일
"""

from datetime import datetime

import nextcord
from nextcord.ext import commands

import main
from utils import guild_manager


class ReadyMessageEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            main.GUILD_ID.append(guild.id)
        for value in guild_manager.get_all_log_channel():
            guild_manager.set_log_channel(value[:value.index(":")], value[value.index(":")+1:], True)
        await self.bot.change_presence(activity=nextcord.Game(name="✨ 이쁘게 반짝반짝"))
        print('Bot Ready!')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild:
            if not message.author.bot:
                print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{message.guild.name} #{message.channel.name}]'
                      f' {message.author}: {message.content}')


def setup(bot):
    bot.add_cog(ReadyMessageEvent(bot))
