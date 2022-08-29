import nextcord
from nextcord.ext import commands


class ReadyEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=nextcord.Game(name="✨ 이쁘게 반짝반짝"))
        print('Bot Ready!')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == "�뚯뒪��":
            print("O")


def setup(bot):
    bot.add_cog(ReadyEvent(bot))