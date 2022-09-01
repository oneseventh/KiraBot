"""
    #제작: @congachu  #수정: @17th
    #최종 수정일: 2022년 09월 01일
"""

import nextcord
import requests
from bs4 import BeautifulSoup
from nextcord import Interaction
from nextcord.ext import commands

import main
from utils import kira_language


class LeagueCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    guild_id = main.GUILD_ID

    @nextcord.slash_command(name="대회", description="contestkorea.com에서 대회 목록을 불러옵니다. - 개발 {0}, {1}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME"),
                                    kira_language.get_text("PART3_DEVELOPER_NAME")), guild_ids=[guild_id])
    async def _league(self, interaction: Interaction,
                      arg: str = nextcord.SlashOption(name="종류", choices={"인기": "인기", "추천": "추천",
                                                                          "최신": "최신", "전체": "전체"},
                                                      description="뭐라써야하지", required=True)):
        await interaction.response.defer()
        url = "https://www.contestkorea.com/?int_gbn=1"
        result = requests.get(url)
        if result.status_code == 200:
            soup = BeautifulSoup(result.content, "html.parser")
            # soup에서 <div class="list_style_1">인 태그 안에서 <span class="title"> 전부 가져오기
            hot_ct_li = soup.find("div", {"class": "list_style_1"}).find_all("span", {"class": "title"})
            # soup에서 <div class="clfx list_type_6">인 태그 안에서 <span class="title"> 전부 가져오기
            good_ct_li = soup.find("ul", {"class": "clfx list_type_6"}).find_all("span", {"class": "title"})
            # soup에서 <div class="list_type_2">인 태그 안에서 <span class="txt"> 전부 가져오기
            new_ct_li = soup.find("div", {"class": "list_style_2"}).find_all("span", {"class": "txt"})
            if arg == "인기":
                embed = nextcord.Embed(title="콘테스트 코리아 대회",
                                       description="출처: https://www.contestkorea.com/?int_gbn=1", color=0xdc143c)
                embed.add_field(name="주목 할 만한 대회",
                                value=f"1. {hot_ct_li[0].text}\n2. {hot_ct_li[1].text}\n3. {hot_ct_li[2].text}\n4. "
                                      f"{hot_ct_li[3].text}\n5. {hot_ct_li[4].text}",
                                inline=False)
                return await interaction.followup.send(embed=embed)
            elif arg == "추천":
                embed = nextcord.Embed(title="콘테스트 코리아 대회",
                                       description="출처: https://www.contestkorea.com/?int_gbn=1", color=0x66cc00)
                embed.add_field(name="추천 하고 싶은 대회",
                                value=f"1. {good_ct_li[0].text}\n2. {good_ct_li[1].text}\n3. {good_ct_li[2].text}\n4. "
                                      f"{good_ct_li[3].text}\n5. {good_ct_li[4].text}",
                                inline=False)
                return await interaction.followup.send(embed=embed)
            elif arg == "최신":
                embed = nextcord.Embed(title="콘테스트 코리아 대회",
                                       description="출처: https://www.contestkorea.com/?int_gbn=1", color=0x0000ff)
                embed.add_field(name="최신 대회",
                                value=f"1. {new_ct_li[0].text}\n2. {new_ct_li[1].text}\n3. {new_ct_li[2].text}\n4. "
                                      f"{new_ct_li[3].text}\n5. {new_ct_li[4].text}",
                                inline=False)
                return await interaction.followup.send(embed=embed)
            elif arg == "전체":
                embed = nextcord.Embed(title="콘테스트 코리아 대회",
                                       description="출처: https://www.contestkorea.com/?int_gbn=1", color=0x800080)
                embed.add_field(name="주목 할 만한 대회",
                                value=f"1. {hot_ct_li[0].text}\n2. {hot_ct_li[1].text}\n3. {hot_ct_li[2].text}\n4. "
                                      f"{hot_ct_li[3].text}\n5. {hot_ct_li[4].text}",
                                inline=False)
                embed.add_field(name="추천 하고 싶은 대회",
                                value=f"1. {good_ct_li[0].text}\n2. {good_ct_li[1].text}\n3. {good_ct_li[2].text}\n4. "
                                      f"{good_ct_li[3].text}\n5. {good_ct_li[4].text}",
                                inline=False)
                embed.add_field(name="최신 대회",
                                value=f"1. {new_ct_li[0].text}\n2. {new_ct_li[1].text}\n3. {new_ct_li[2].text}\n4. "
                                      f"{new_ct_li[3].text}\n5. {new_ct_li[4].text}",
                                inline=False)
                return await interaction.followup.send(embed=embed)

        return await interaction.followup.send("데이터를 가져오는데 실패했습니다.")


def setup(bot):
    bot.add_cog(LeagueCommand(bot))
