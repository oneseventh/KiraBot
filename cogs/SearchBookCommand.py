import math
import traceback
from datetime import datetime

import nextcord
import requests
from nextcord.ext import commands

import main
from utils import alert, kira_language, parse_authkey


class SearchBookCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    guild_id = main.GUILD_ID

    @nextcord.slash_command(name="search", description="✨ 책 이름을 알려주면 책을 검색해 줄게!", guild_ids=[guild_id])
    async def search_book(self, interaction: nextcord.Interaction,
                          bookname: str = nextcord.SlashOption(name="책_이름", description="✨ 책 이름을 입력해 줘!", min_length=3),
                          page: int = nextcord.SlashOption(name="페이지", description="✨ 검색할 페이지를 알려 줘! (선택)",
                                                           min_value=1, max_value=1000, required=False)):
        if page is None:  # 만약 페이지가 지정 되어 있지 않다면,
            page = 1  # 페이지를 1로 설정

        if page <= 0:  # 만약 페이지가 0이거나 0보다 작다면,
            await interaction.response.send_message(kira_language.get_text("search-book-value-error-1"))  # 문구 출력
            return

        url = f"https://dapi.kakao.com/v3/search/book?sort=latest&page={math.ceil(page / 10)}&query={bookname}"

        header = {'Authorization': f'KakaoAK {parse_authkey.get_auth_key("kakao-api-key")}'}  # header에 카카오 API키를 입력
        result = requests.get(url, headers=header)  # 요청을 보낸 후
        data = result.json()  # data 변수에 json 결과 값을 저장함.

        if page <= 10:
            content = page - 1
        else:
            content = page - (10 * (math.ceil(page / 10))) - 1
        try:
            if data['meta']['total_count'] != 0:
                if data['meta']['pageable_count'] >= 1000:
                    embed = nextcord.Embed(
                        title=f":book: '{bookname}' {kira_language.get_text('search-book-search-result')} **({page}/{data['meta']['pageable_count']})**",
                        description=f"``{kira_language.get_text('search-book-embed-field-overflowed')}``\n"
                                    f"**{data['documents'][content]['title']}**", color=nextcord.Color.green())
                else:
                    embed = nextcord.Embed(
                        title=f":book: '{bookname}' {kira_language.get_text('search-book-search-result')} **({page}/{data['meta']['pageable_count']})**",
                        description=f"**{data['documents'][content]['title']}**", color=nextcord.Color.green())
                embed.set_thumbnail(url=f"{data['documents'][content]['thumbnail']}")
                embed.add_field(name=kira_language.get_text("search-book-embed-field-author"),
                                value=f"``{data['documents'][content]['authors'][0]}``", inline=True)
                embed.add_field(name=kira_language.get_text("search-book-embed-field-publisher"),
                                value=f"``{data['documents'][content]['publisher']}``", inline=True)
                embed.add_field(name=kira_language.get_text("search-book-embed-field-price"),
                                value=f"``{data['documents'][content]['sale_price']}원 (KAKAO)``",
                                inline=True)
                embed.add_field(name=kira_language.get_text("search-book-embed-field-published-date"),
                                value=f"``{(data['documents'][content]['datetime'])[:data['documents'][content]['datetime'].index('T')]}``",
                                inline=True)
                embed.add_field(name=kira_language.get_text("search-book-embed-field-isbn"),
                                value=f"``{(data['documents'][content]['isbn'])}``",
                                inline=True)
                embed.add_field(name=kira_language.get_text("search-book-embed-field-status"),
                                value=f"``{(data['documents'][content]['status'])}``", inline=True)
                embed.add_field(name=kira_language.get_text("search-book-embed-field-book-details"),
                                value=f"```{cut_text(data['documents'][content]['contents'], 150)}```",
                                inline=False)
                embed.set_footer(
                    text=f"Request by {interaction.user} ・ Developed by {kira_language.get_text('PART1_DEVELOPER_NAME')}",
                    icon_url=f"{interaction.user.display_avatar}")
                embed.timestamp = datetime.now()
                await interaction.response.send_message(embed=embed)
            else:
                embed = nextcord.Embed(
                    title=f":book: '{bookname}' {kira_language.get_text('search-book-search-no-result-1')}",
                    description=f"{kira_language.get_text('search-book-search-no-result-2')} ``{bookname}``",
                    color=nextcord.Color.red())
                embed.set_footer(
                    text=f"Request by {interaction.user} ・ Developed by {kira_language.get_text('PART1_DEVELOPER_NAME')}",
                    icon_url=f"{interaction.user.display_avatar}")
                embed.timestamp = datetime.now()
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            await alert.critical_error(interaction, e.__class__.__name__, str(e), str(traceback.format_exc()))


def cut_text(text: str, index: int):
    if len(text) >= index:
        return text[:index] + "..."
    else:
        return text


def setup(bot):
    bot.add_cog(SearchBookCommand(bot))
