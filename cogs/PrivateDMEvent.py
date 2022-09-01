"""
    #제작: @17th
    #최종 수정일: 2022년 08월 28일

"""

import random
import time

from nextcord.ext import commands


class PrivateDMEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    hello_msg = ["안녕", "ㅎㅇ", "하이"]
    goodnight_msg = ["잘자"]
    follow_me_msg = ["따라해", "따라해봐", "해봐"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            if not message.author.bot:
                hour = time.localtime().tm_hour
                if message.content.startswith(tuple(self.hello_msg)):
                    await message.add_reaction("👋")
                    await message.channel.send("안녕!")
                elif message.content.startswith(tuple(self.goodnight_msg)):
                    if 6 <= hour < 7:
                        await message.add_reaction("😊")
                        await message.channel.send(f'{message.author.mention}은 잘 잤어?')
                    elif 7 <= hour < 21:
                        await message.add_reaction("☀")
                        await message.channel.send(f'지금은 낮이잖아! 일 해야지!')
                    elif 21 <= hour < 23:
                        await message.add_reaction("😴")
                        await message.channel.send(f'고마워! {message.author.mention}도 잘 자!')
                    else:
                        await message.add_reaction("💤")
                        await message.channel.send('뭐해! 얼른 자!')
                elif message.content.startswith(tuple(self.follow_me_msg)):
                    await message.channel.send(message.content[str(message.content).index(" "):])
                else:
                    if random.randrange(1, 11) == 5:
                        await message.channel.send("{0}..?".format(message.content))


def setup(bot):
    bot.add_cog(PrivateDMEvent(bot))
