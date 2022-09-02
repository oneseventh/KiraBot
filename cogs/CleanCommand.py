"""
    #제작: @congachu  #수정: @17th
    #최종 수정일: 2022년 09월 01일
"""

import nextcord
from nextcord import Interaction
from nextcord.ext import commands

import main
from utils import alert, kira_language


class CleanCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    guild_id = main.GUILD_ID

    # 청소 기능
    @nextcord.slash_command(name="청소", description="메시지를 청소합니다. - 개발 {0}, {1}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME"),
                                    kira_language.get_text("PART3_DEVELOPER_NAME")), guild_ids=guild_id)
    async def _clean(self, interaction: Interaction,
                     amount: int = nextcord.SlashOption(name="개수",
                                                        description="삭제할 메시지의 개수를 입력해주세요.",
                                                        required=True,
                                                        max_value=99)):
        if interaction.user.guild_permissions.manage_roles:
            await interaction.channel.purge(limit=int(amount) + 1)
            return await alert.success(interaction, kira_language.get_text("clean-alert-success").format(amount))
        await alert.no_permission(interaction)


def setup(bot):
    bot.add_cog(CleanCommand(bot))
