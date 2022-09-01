"""
    #제작: @17th
    #최종 수정일: 2022년 09월 01일
"""

from datetime import datetime

import nextcord

from utils import kira_language


async def critical_error(interaction: nextcord.Interaction, errorname: str, errorcause: str, traceback: str):
    error_time = datetime.now().strftime('%Y%m%d%H%M%S')  # �쒓컙�� 20220828200000 �앹쑝濡� 臾몄옄濡� ����
    embed = nextcord.Embed(title=kira_language.get_text("error-embed-title"),
                           description=f"{kira_language.get_text('error-embed-description-part-1')}"
                                       f"{error_time}{kira_language.get_text('error-embed-description-part-2')}",
                           color=nextcord.Color.red())  # �ㅻ쪟 硫붿떆吏� 留뚮뱾湲�
    embed.add_field(name="**Error**", value=f"``{errorname}``", inline=True)
    embed.add_field(name="**Reason**", value=f"``{errorcause}``", inline=True)
    embed.set_thumbnail(url=f"https://i.gifer.com/origin/78/787899e9d4e4491f797aba5c61294dfc_w200.gif")
    embed.set_footer(
        text=f"Developed by {kira_language.get_text('PART1_DEVELOPER_NAME')}",
        icon_url=f"{kira_language.get_text('PART1_DEVELOPER_PROFILE_URL')}")
    embed.timestamp = datetime.now()
    with open(f"././logs/error_{error_time}.log", "w") as f:  # �ㅻ쪟 濡쒓렇 湲곕줉�� �꾪븳 �뚯씪 �닿린
        f.write(traceback)  # �뚯씪�� �ㅻ쪟 異쒕젰�섍린
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)  # �꾩뿉�� 留뚮뱺 �ㅻ쪟 硫붿떆吏� 蹂대궡湲�


async def success(interaction: nextcord.Interaction, embed_desc: str,
                  view: nextcord.ui.View = None, image_url: str = None):
    embed = nextcord.Embed(title=kira_language.get_text("embed-title-success"), description=embed_desc,
                           color=nextcord.Color.green())
    if image_url is not None:
        embed.set_thumbnail(url=image_url)
    embed.set_footer(
        text=f"Developed by {kira_language.get_text('PART1_DEVELOPER_NAME')}",
        icon_url=f"{kira_language.get_text('PART1_DEVELOPER_PROFILE_URL')}")
    embed.timestamp = datetime.now()
    if view is not None:
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True, delete_after=10)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)


async def error(interaction: nextcord.Interaction, embed_desc: str, image_url: str = None):
    embed = nextcord.Embed(title=kira_language.get_text("embed-title-error"), description=embed_desc,
                           color=nextcord.Color.red())
    if image_url is not None:
        embed.set_thumbnail(url=image_url)
    embed.set_footer(
        text=f"Developed by {kira_language.get_text('PART1_DEVELOPER_NAME')}",
        icon_url=f"{kira_language.get_text('PART1_DEVELOPER_PROFILE_URL')}")
    embed.timestamp = datetime.now()
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)


async def info(interaction: nextcord.Interaction, info_content: str, image_url: str = None):
    embed = nextcord.Embed(title=kira_language.get_text("embed-title-info"),
                           description=info_content,
                           color=nextcord.Color.purple())
    embed.set_footer(
        text=f"Developed by {kira_language.get_text('PART1_DEVELOPER_NAME')}",
        icon_url=f"{kira_language.get_text('PART1_DEVELOPER_PROFILE_URL')}")
    embed.timestamp = datetime.now()
    if image_url is not None:
        embed.set_thumbnail(url=image_url)
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)


async def developing(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title=kira_language.get_text("embed-title-developing"),
                           description=kira_language.get_text("embed-title-developing-info"),
                           color=nextcord.Color.dark_gray())
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/1011601900312997968/1013778867779014656/211FC54D586EFEC031.gif")
    embed.set_footer(
        text=f"Developed by {kira_language.get_text('PART1_DEVELOPER_NAME')}",
        icon_url=f"{kira_language.get_text('PART1_DEVELOPER_PROFILE_URL')}")
    embed.timestamp = datetime.now()
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)


async def no_permission(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title=kira_language.get_text("embed-title-no-permission"),
                           description=kira_language.get_text("no-permission"),
                           color=0xffffff)
    embed.set_footer(
        text=f"Developed by {kira_language.get_text('PART1_DEVELOPER_NAME')}",
        icon_url=f"{kira_language.get_text('PART1_DEVELOPER_PROFILE_URL')}")
    embed.timestamp = datetime.now()
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
