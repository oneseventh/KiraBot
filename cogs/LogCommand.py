"""
    #제작: @donggeon  #수정: @17th
    #최종 수정일: 2022년 09월 01일
"""

import os.path
from nextcord.ext import commands
import nextcord
import main
from utils import guild_manager

channel_id = main.channel_id


class LogCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    guild_id = main.GUILD_ID

    @nextcord.slash_command(name="set_textchannel", description="텍스트 채널선택을 통해 로그를 저장합니다!", guild_ids=[guild_id])
    async def log_channel(self, interaction: nextcord.Interaction,
                          channel: nextcord.TextChannel = nextcord.SlashOption(name="텍스트채널",
                                                                               description="로그를 저장할 채널을 선택해주세요!",
                                                                               required=True)):
        path = "./setting.txt"
        global channel_id
        if os.path.isfile(path):
            with open(path) as r:
                r.seek(0)
                lines = r.readlines()
                for line in lines:
                    if channel.id == int(line):
                        guild_manager.set_log_channel(int(line))
        else:
            f = open(path, 'w')
            f.write(f"{channel.id}\n")
            guild_manager.set_log_channel(channel.id)
            f.close()
        if guild_manager.get_current_log_channel_id() != 0:
            embed = nextcord.Embed(title=f"{channel.name} 채널에 로그를 저장합니다.",
                                   description=f"한번 선택한 채널은 바꿀 수 없습니다\n(변경기능 개발중!)", color=0x5947FF)
            embed.add_field(name="Selected channel ID", value=f"```diff\n+ {guild_manager.get_current_log_channel_id()}```", inline=False)
            embed.set_footer(text=f"Request by {interaction.user} ・ Developed by 동건#3038",
                             icon_url=interaction.user.display_avatar)
            await interaction.response.send_message(embed=embed)
        else:
            guild_manager.set_log_channel(channel.id)
            await interaction.response.send_message("error")


def setup(bot):
    bot.add_cog(LogCommands(bot))