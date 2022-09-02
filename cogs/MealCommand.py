"""
    #제작: @17th
    #최종 수정일: 2022년 08월 29일
"""

import traceback

import nextcord.ui
import requests as requests
from nextcord import Interaction
from nextcord.ext import commands
from datetime import datetime

import main
from utils import parse_authkey
from utils import kira_language
from utils import alert


class MealCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    guild_id = main.GUILD_ID
    neis_api_key = parse_authkey.get_auth_key('neis-api-key')

    @nextcord.slash_command(name="meal", description="✨ 학교의 급식을 확인할 수 있어! (기본값은 인천정보과학고등학교 입니다.) - 개발 {0}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME")), guild_ids=guild_id)
    async def check_meal(self, interaction: Interaction,
                         date: int = nextcord.SlashOption(name="날짜", description="✨ 날짜를 입력해 줘! (예. 20220828)",
                                                          min_value=19700101, max_value=20380119, required=False),
                         school: str = nextcord.SlashOption(name="학교",
                                                            description="✨ 학교 이름을 입력해 줘! (예. 인천정보과학고등학교)",
                                                            required=False)
                         ):
        school_name = ""
        if school is not None:
            school_array = self.get_school(school)
            if school_array is None:
                return await alert.error(interaction, kira_language.get_text("school-meal-error-school-not-found"))
            url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={self.neis_api_key}" \
                  f"&Type=json&plndex=1&pSize=30&ATPT_OFCDC_SC_CODE={school_array[0]}&SD_SCHUL_CODE={school_array[1]}&MLSV_YMD="
            school_name = school_array[2]
        elif school is None:
            url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={self.neis_api_key}" \
                  "&Type=json&plndex=1&pSize=30&ATPT_OFCDC_SC_CODE=E10&SD_SCHUL_CODE=7310564&MLSV_YMD="
            school_name = "인천정보과학고등학교"
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
            url = url + datetime.now().strftime("%Y%m%d")
        else:
            if int(str(date)[4:6]) > 12 or int(str(date)[4:6]) == 0 \
                    or int(str(date)[6:8]) > 31 or int(str(date)[6:8]) == 0:
                await alert.error(interaction, kira_language.get_text("school-meal-incorrect-date-type"))
                return
            url += url + str(date)
        response = requests.get(url)
        if response.status_code == 200:
            meal_data = response.json()
            try:
                data = meal_data['mealServiceDietInfo'][1]['row'][0]['DDISH_NM'].replace("<br/>", "\n")
                result_food = ""
                for line in data.splitlines():
                    result_food += "- " + line[:line.index("  ")] + "\n"
                embed = nextcord.Embed(title=kira_language.get_text("school-meal-embed-title").format(school_name),
                                       description=f"``{str(date)[:4]}년 {str(date)[4:6]}월 {str(date)[6:8]}일`` " +
                                                   kira_language.get_text("school-meal-embed-today"),
                                       color=nextcord.Color.green())
                embed.set_author(name=f"Request by {interaction.user}", icon_url=interaction.user.display_avatar)
                embed.add_field(name=kira_language.get_text("school-meal-embed-lunch"), value=f"```{result_food}```",
                                inline=False)
                embed.add_field(name=kira_language.get_text("school-meal-embed-kcal"),
                                value=f"``{meal_data['mealServiceDietInfo'][1]['row'][0]['CAL_INFO']}``", inline=True)
                embed.set_footer(
                    text=f"Developed by {kira_language.get_text('PART1_DEVELOPER_NAME')}",
                    icon_url=f"{kira_language.get_text('PART1_DEVELOPER_PROFILE_URL')}")
                await interaction.response.send_message(embed=embed)
                embed.timestamp = datetime.now()
            except KeyError:
                await alert.error(interaction, f"``{str(date)[:4]}년 {str(date)[4:6]}월 {str(date)[6:8]}일`` "
                                  + kira_language.get_text('school-meal-embed-no-data'))
            except Exception as e:
                await alert.critical_error(interaction, e.__class__.__name__, str(e), str(traceback.format_exc()))

    def get_school(self, scname: str):
        url = "https://open.neis.go.kr/hub/schoolInfo?KEY=" + self.neis_api_key + "&Type=json&pIndex=1&pSize=100&SCHUL_NM=" + scname
        response = requests.get(url)
        if response.status_code == 200:
            school_data = response.json()
            try:
                sc_code = str(school_data['schoolInfo'][1]['row'][0]['ATPT_OFCDC_SC_CODE'])
                sd_code = str(school_data['schoolInfo'][1]['row'][0]['SD_SCHUL_CODE'])
                school_name = str(school_data['schoolInfo'][1]['row'][0]['SCHUL_NM'])
                return [sc_code, sd_code, school_name]
            except KeyError:
                return None


def setup(bot):
    bot.add_cog(MealCommand(bot))
