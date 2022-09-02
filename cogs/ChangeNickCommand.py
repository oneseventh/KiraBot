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
from utils import alert


class ChangeNickCommand(commands.Cog):
    def __init(self, bot):
        self.bot = bot

    guild_id = main.GUILD_ID

    @nextcord.slash_command(name="닉변", description="닉네임을 변경합니다. - 개발 {0}, {1}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME"),
                                    kira_language.get_text("PART3_DEVELOPER_NAME")), guild_ids=guild_id)
    async def _change_nick(self, interaction: Interaction,
                           target: nextcord.Member = nextcord.SlashOption(
                               name="대상",
                               description="대상을 선택해주세요.",
                               required=True),
                           nick: str = nextcord.SlashOption(
                               name="닉네임",
                               description="변경할 닉네임을 입력해주세요.",
                               required=True,
                               max_length=32)):

        if not interaction.user.guild_permissions.manage_nicknames:
            if target is not interaction.user:
                return await alert.no_permission(interaction)
        try:
            await target.edit(nick=nick)
            await alert.success(interaction,
                                kira_language.get_text("change-nick-embed-success").format(target.mention, nick))
        except nextcord.errors.Forbidden:
            await alert.no_permission(interaction)


def setup(bot):
    bot.add_cog(ChangeNickCommand(bot))
