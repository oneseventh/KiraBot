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


class GameCommand(commands.Cog):
    def __init(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="홀짝", description="홀짝을 맞춰보세요! - 개발 {0}, {1}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME"),
                                    kira_language.get_text("PART3_DEVELOPER_NAME")))
    async def _game_odd(self, interaction: Interaction,
                        odd: int = nextcord.SlashOption(name="값", choices={"홀": 1, "짝": 2},
                                                        description="홀이나 짝을 골라주세요!", required=True)):
        random_odd = random.randint(1, 2)
        if odd == random_odd:
            await interaction.response.send_message(embed=nextcord.Embed(
                title=kira_language.get_text("game-odd-embed-title"),
                description=kira_language.get_text("game-odd-embed-win").format("홀" if random_odd == 1 else "짝",
                                                                                "홀" if odd == 1 else "짝")))
        else:
            await interaction.response.send_message(embed=nextcord.Embed(
                title=kira_language.get_text("game-odd-embed-title"),
                description=kira_language.get_text("game-odd-embed-defeat").format("홀" if random_odd == 1 else "짝",
                                                                                   "홀" if odd == 1 else "짝")))


def setup(bot):
    bot.add_cog(GameCommand(bot))
