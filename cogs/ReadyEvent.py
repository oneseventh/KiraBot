from datetime import datetime

import nextcord
from nextcord.ext import commands

import cogs.SearchBookCommand


class ReadyEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=nextcord.Game(name="✨ 이쁘게 반짝반짝"))
        print('Bot Ready!')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild:
            if not message.author.bot:
                print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{message.guild.name} #{message.channel.name}]'
                      f' {message.author}: {message.content}')


def setup(bot):
    bot.add_cog(ReadyEvent(bot))
