"""
    #제작: @donggeon  #수정: @17th
    #최종 수정일: 2022년 09월 04일
"""

import os.path
from nextcord.ext import commands
import nextcord
import main
from utils import guild_manager

channel_id = main.LOG_CHANNEL_ID


class LogCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    guild_id = main.GUILD_ID
    log_channel_id = main.LOG_CHANNEL_ID

    @nextcord.slash_command(name="로그", description="로그 채널을 설정 합니다.", guild_ids=guild_id)
    async def logging_channel(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel =
                              nextcord.SlashOption(name="채널", description="로깅할 채널", required=True)):
        guild_manager.set_log_channel(interaction.guild.id, channel.id)
        embed = nextcord.Embed(title=f"이 채널에 로그를 저장합니다.", description="설정된 채널 <#{0}>"
                               .format(channel.id), color=0x5947FF)
        embed.add_field(name="Selected channel ID",
                        value=f"```diff\n+ {channel.id}```",
                        inline=False)
        embed.set_footer(text=f"Request by {interaction.user} ・ Developed by 동건#3038",
                         icon_url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(LogCommands(bot))