"""
    #제작: @congachu  #수정: @17th
    #최종 수정일: 2022년 09월 01일
"""

import random

import nextcord
from nextcord import Interaction
from nextcord.ext import commands

import main
from utils import kira_language


class FollowMeCommand(commands.Cog):
    def __init(self, bot):
        self.bot = bot

    guild_id = main.GUILD_ID

    @nextcord.slash_command(name="따라해", description="말을 따라합니다. - 개발 {0}, {1}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME"),
                                    kira_language.get_text("PART3_DEVELOPER_NAME")), guild_ids=[guild_id])
    async def _game_odd(self, interaction: Interaction,
                        text: str = nextcord.SlashOption(name="말",
                                                        description="따라할 말을 적어주세요!", required=True)):
        await interaction.response.send_message(text)


def setup(bot):
    bot.add_cog(FollowMeCommand(bot))
