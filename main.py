import datetime
import time
import traceback
from datetime import datetime

import discord
import requests
import youtube_dl
from discord import app_commands, ui

intents = discord.Intents.default()
intents.message_content = True

guild_id = 1011601743399890975  # 임시
neis_api_key = "8bdc6dd4fca4419aaf7601919e8c685c"
kakao_api_key = "f1a1c158837e9702168f03ecd6b463cd"

lang = "en"
fallback_lang = "ko"


# 언어 파일 불러오기
def get_text(path: str):
    with open(f"./lang/{lang}.lang", 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith(path):
                if line[line.index(":") + 2:].replace("<br>", "\n") == "" or None:
                    with open(f"./lang/{fallback_lang}.lang", 'r', encoding='utf-8') as fi:
                        for line2 in fi:
                            if line2.startswith(path):
                                return line2[line2.index(":") + 2:].replace("<br>", "\n")
                else:
                    return line[line.index(":") + 2:].replace("<br>", "\n")


class init_client(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.finished = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.finished:
            await sc.sync(guild=discord.Object(id=guild_id))
            self.finished = True
        print("Synced!")


bot = init_client()
sc = app_commands.CommandTree(bot)


class Enter_Button(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

    @discord.ui.button(label="돌아오기", style=discord.ButtonStyle.green, emoji="🚪")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.voice is None:
            await interaction.response.send_message(get_text("bot-request-enter-voice-channel-if-user-not-joined"
                                                             "-voice-channel"))
            return
        else:
            await interaction.user.voice.channel.connect()
            await interaction.response.send_message(embed=no_queue(), view=QueueButton(interaction))
            return


class Music_Button(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

    @discord.ui.button(label="이전", style=discord.ButtonStyle.primary, emoji="⏮")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title=get_text("embed-title-sorry"), description=get_text("still-developed"),
                              color=discord.Color.dark_gray()).set_thumbnail(
            url=f"{bot.user.avatar}")
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="멈춤", style=discord.ButtonStyle.gray, emoji="⏸")
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.interaction.guild.voice_client.is_playing():
            embed = discord.Embed(title=get_text("embed-title-success"), description=get_text("song-stopped"),
                                  color=discord.Color.green()).set_thumbnail(
                url=f"{bot.user.avatar}")
            await interaction.response.send_message(embed=embed)
            self.interaction.guild.voice_client.pause()
        else:
            embed = discord.Embed(title=get_text("embed-title-error"), description=get_text("song-already-stopped"),
                                  color=discord.Color.red()).set_thumbnail(
                url=f"{bot.user.avatar}")
            await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="재생", style=discord.ButtonStyle.gray, emoji="▶")
    async def play(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.interaction.guild.voice_client.is_playing():
            embed = discord.Embed(title=get_text("embed-title-error"), description=get_text("song-already-resumed"),
                                  color=discord.Color.red()).set_thumbnail(
                url=f"{bot.user.avatar}")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title=get_text("embed-title-success"), description=get_text("song-resumed"),
                                  color=discord.Color.green()).set_thumbnail(
                url=f"{bot.user.avatar}")
            await interaction.response.send_message(embed=embed)
            self.interaction.guild.voice_client.resume()

    @discord.ui.button(label="다음", style=discord.ButtonStyle.primary, emoji="⏭")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title=get_text("embed-title-success"), description=get_text("song-skipped"),
                              color=discord.Color.green()).set_thumbnail(
            url=f"{bot.user.avatar}")
        await interaction.response.send_message(embed=embed)
        self.interaction.guild.voice_client.stop()

    @discord.ui.button(label="나가기", style=discord.ButtonStyle.danger, emoji="🚪")
    async def exit(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title=get_text("embed-title-success"), description=get_text("leave-voice-room"),
                              color=discord.Color.green()).set_thumbnail(
            url=f"{bot.user.avatar}")
        await interaction.response.send_message(embed=embed, view=Enter_Button(interaction))
        await interaction.guild.voice_client.disconnect(force=True)


class GetMusicURL(ui.Modal, title=get_text("modal-title-song-queue")):
    answer = ui.TextInput(label=get_text("modal-label-want-youtube-link"),
                          style=discord.TextStyle.short, placeholder="https://www.youtube.com/watch...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        YDL_OPTIONS = {'format': 'bestaudio'}
        vc = interaction.guild.voice_client
        try:
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(self.answer.value, download=False)
                url2 = info['formats'][0]['url']
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                title = info.get('title')
                if len(title) > 20:
                    title = title[:19] + "..."
                description = info.get('description')
                if len(description) > 80:
                    description = description[:80] + "..."
                await bot.change_presence(
                    activity=discord.Activity(type=discord.ActivityType.listening, name=f"{title}"))
                embed = discord.Embed(title=f"{title}", url=f"{self.answer.value}", description=f"{description}",
                                      color=discord.Color.dark_gold()) \
                    .set_thumbnail(
                    url=f"{bot.user.avatar}").add_field(
                    name=get_text("music-bot-embed-duration"),
                    value=f"``{str(datetime.timedelta(seconds=int(info.get('duration'))))}``").set_image(
                    url=f"{info.get('thumbnail')}").add_field(name=get_text("music-bot-embed-viewer"),
                                                              value=f"``{format(info.get('view_count'), ',')}``",
                                                              inline=True).add_field(
                    name=get_text("music-bot-embed-like"),
                    value=f"``{format(info.get('like_count'), ',')}``",
                    inline=True).set_author(
                    name=f"{info.get('uploader')}",
                    url=f"{info.get('uploader_url')}").set_footer(
                    text=f"Request by {interaction.user} ・ Developed by {get_text('PART1_DEVELOPER_NAME')}",
                    icon_url=f"{interaction.user.avatar}")
                await interaction.response.send_message(embed=embed, view=Music_Button(interaction))
                vc.play(source)
        except Exception as e:
            await print_error(interaction, e.__class__.__name__, str(e), str(traceback.format_exc()))


def utc_to_kst(origin_time):
    return (origin_time + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %T")


@sc.command(guild=discord.Object(id=guild_id), name='profile', description='대상의 프로필 정보를 확인 합니다.')
async def chk_profile(interaction: discord.Interaction, member: discord.Member = None):
    global display_name
    if member is None:
        user = interaction.user
        if interaction.user.display_name is not None:
            display_name = interaction.user.display_name
        else:
            if interaction.user.display_name == interaction.user.name:
                display_name = get_text("NONE")
        admin = interaction.user.guild_permissions.administrator
        avatar = interaction.user.avatar
        joined = interaction.user.joined_at
    else:
        user = member
        if member.display_name is not None:
            display_name = member.display_name
        else:
            if member.display_name == member.name:
                display_name = get_text("NONE")
        admin = member.guild_permissions.administrator
        avatar = member.avatar
        joined = member.joined_at

    profile_embed = discord.Embed(description=f'{get_text("profile-embed-display-name")} ``{display_name}``',
                                  color=0x00ff00) \
        .set_author(name=f"{user} {get_text('profile-embed-info')}", icon_url=avatar)
    profile_embed.add_field(name=get_text("profile-embed-joined-at"), value=f"``{utc_to_kst(joined)}``", inline=True)
    profile_embed.add_field(name=get_text("profile-embed-is-admin"), value=f"``{admin}``", inline=True)
    profile_embed.set_footer(text=f"Request by {interaction.user} ・ Developed by {get_text('PART1_DEVELOPER_NAME')}",
                             icon_url=f"{interaction.user.avatar}")
    profile_embed.set_image(url=f"{avatar}")
    await interaction.response.send_message(embed=profile_embed)


class QueueButton(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

    @discord.ui.button(label="예약", style=discord.ButtonStyle.primary, emoji="⏰")
    async def queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GetMusicURL())

    @discord.ui.button(label="나가기", style=discord.ButtonStyle.danger, emoji="🚪")
    async def exit(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title=get_text("embed-title-success"), description=get_text("leave-voice-room"),
                              color=discord.Color.green()).set_thumbnail(
            url=f"{bot.user.avatar}")
        await interaction.response.send_message(embed=embed)
        await interaction.guild.voice_client.disconnect(force=True)


def no_queue():
    embed = discord.Embed(title=get_text("song-no-playing"), description=get_text("song-want-to-listen"),
                          color=discord.Color.dark_gray())
    embed.set_thumbnail(
        url=f"{bot.user.avatar}")
    embed.set_footer(text=f"Request by {bot.user} ・ Developed by {get_text('PART1_DEVELOPER_NAME')}",
                     icon_url=f"{bot.user.avatar}")
    return embed


@sc.command(guild=discord.Object(id=guild_id), name='급식', description='인천정보과학고등학교의 급식을 받아옵니다!')
async def getFood(interaction: discord.Interaction, date: int = None):
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={neis_api_key}&Type=json&plndex=1&pSize=30" \
          f"&ATPT_OFCDC_SC_CODE=E10&SD_SCHUL_CODE=7310564&MLSV_YMD= "
    if date is None:
        date = datetime.datetime.now().strftime("%Y%m%d")
        url = url + datetime.datetime.now().strftime("%Y%m%d")
        print(url)
    else:
        fdate = str(date)
        if 7 <= len(fdate) >= 9:
            await interaction.response.send_message(get_text("school-meal-incorrect-date-type"))
            return
        url = url + fdate
    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()
        try:
            data = json_data['mealServiceDietInfo'][1]['row'][0]['DDISH_NM'].replace("<br/>", "\n")
            food = ""
            for line in data.splitlines():
                food += line[:line.index("  ")] + "\n"

            embed = discord.Embed(title=get_text("school-meal-embed-title"),
                                  description=f"``{date}{get_text('school-meal-embed-today')}``",
                                  color=discord.Color.green())
            embed.set_author(name="인천정보과학고등학교",
                             icon_url="https://file.namu.moe/file"
                                      "/e5ac92921b59842e2eb681127aea37551ee51c92d1c8a08ec73f22e7987753c6bc7b436ae5bb98352cceac39f59fd152587c63f5cd77431fcb634cd46de9814e")
            embed.add_field(name="중식", value=f"``{food.replace(' ', '')}``", inline=False).add_field(name="칼로리",
                                                                                                     value=f"``{json_data['mealServiceDietInfo'][1]['row'][0]['CAL_INFO']}``",
                                                                                                     inline=True).set_footer(
                text=f"Request by {interaction.user} ・ Developed by 서현",
                icon_url=f"{interaction.user.avatar}").set_thumbnail(
                url=f"{bot.user.avatar}")
            await interaction.response.send_message(embed=embed)
        except KeyError as e:
            embed = discord.Embed(title=get_text("schol-meal-embed-title"),
                                  description=f"{date}{get_text('school-meal-embed-today')}", color=discord.Color.red())
            embed.set_author(name="인천정보과학고등학교",
                             icon_url="https://file.namu.moe/file/e5ac92921b59842e2eb681127aea37551ee51c92d1c8a08ec73f22e7987753c6bc7b436ae5bb98352cceac39f59fd152587c63f5cd77431fcb634cd46de9814e")
            embed.add_field(name=get_text('school-meal-embed-lunch'), value=get_text("school-meal-embed-no"),
                            inline=False).set_thumbnail(
                url=f"{bot.user.avatar}")
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await print_error(interaction, e.__class__.__name__, str(e), str(traceback.format_exc()))
    else:
        await interaction.response.send_message("오류가 발생했습니다!")
        return


@sc.command(guild=discord.Object(id=guild_id), name='언어', description='언어를 설정합니다.')
async def change_lang(interaction: discord.Interaction):
    global lang
    global fallback_lang
    if lang == "ko":
        lang = "en"
        fallback_lang = "ko"
        await interaction.response.send_message("Changed to English")
    else:
        lang = "ko"
        fallback_lang = "en"
        await interaction.response.send_message("Changed Korean")


@sc.command(guild=discord.Object(id=guild_id), name='입장', description='반짝반짝 봇이 노래를 재생하기 위해 통화방에 입장합니다!')
async def join_channel(interaction: discord.Interaction, channel: discord.VoiceChannel = None):
    voice_channel = discord.utils.get(bot.voice_clients, guild=interaction.guild)

    if voice_channel is not None:
        await interaction.guild.voice_client.disconnect(force=True)
        if channel is None:
            if interaction.user.voice is None:
                await interaction.response.send_message(get_text("bot-request-enter-voice-channel-if-user-not-joined"
                                                                 "-voice-channel"))
                return
            else:
                vc = await interaction.user.voice.channel.connect()
                await interaction.response.send_message(embed=no_queue(), view=QueueButton(interaction))
                return
        else:
            vc = await channel.connect()
            await interaction.response.send_message(embed=no_queue(), view=QueueButton(interaction))
            return

    else:
        if interaction.user.voice is None:
            await interaction.response.send_message(get_text("bot-request-enter-voice-channel-if-user-not-joined"
                                                             "-voice-channel"))
            return
        else:
            print("bot is not connected any voice, parameter is null, user is already connected voice channel")
            vc = await interaction.user.voice.channel.connect()
            await interaction.response.send_message(embed=no_queue(), view=QueueButton(interaction))
            return


def cut_text(text: str, index: int):
    if len(text) >= index:
        return text[:index] + "..."
    else:
        return text


# 에러 처리 함수
async def print_error(interaction: discord.Interaction, errorname: str, errorcause: str, traceback: str):
    error_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # 시간을 20220828200000 식으로 문자로 저장
    embed = discord.Embed(title=get_text("error-embed-title"),
                          description=f"{get_text('error-embed-description-part-1')}{error_time}{get_text('error-embed-description-part-2')}",
                          color=discord.Color.red())  # 오류 메시지 만들기
    embed.add_field(name="**Error**", value=f"``{errorname}``", inline=True)
    embed.add_field(name="**Reason**", value=f"``{errorcause}``", inline=True)
    embed.set_thumbnail(url=f"https://i.gifer.com/origin/78/787899e9d4e4491f797aba5c61294dfc_w200.gif")
    embed.set_footer(text=f"Request by {interaction.user} ・ Developed by {get_text('PART1_DEVELOPER_NAME')}",
                     icon_url=f"{interaction.user.avatar}")
    with open(f"./logs/error_{error_time}.log", "w") as f:  # 오류 로그 기록을 위한 파일 열기
        f.write(traceback)  # 파일에 오류 출력하기
    await interaction.response.send_message(embed=embed)  # 위에서 만든 오류 메시지 보내기


# 책을 검색하는 명령어. {bookname}(필수)로 책 이름을 입력 받음. 선택에 따라 {page}도 입력 가능.
@sc.command(guild=discord.Object(id=guild_id), name='검색', description='책을 검색합니다')
async def search_book(interaction: discord.Interaction, bookname: str, page: int = None):
    if page is None:  # 만약 페이지가 지정 되어 있지 않다면,
        page = 1  # 페이지를 1로 설정

    if page <= 0:  # 만약 페이지가 0이거나 0보다 작다면,
        await interaction.response.send_message(get_text("search-book-value-error-1"))  # 문구 출력
        return

    url = f"https://dapi.kakao.com/v3/search/book?sort=latest&size={page}&query={bookname}"

    header = {'Authorization': f'KakaoAK {kakao_api_key}'}  # header에 카카오 API키를 입력
    result = requests.get(url, headers=header)  # 요청을 보낸 후
    data = result.json()  # data 변수에 json 결과 값을 저장함.

    content = page - 1
    try:
        if data['meta']['total_count'] != 0:
            embed = discord.Embed(
                title=f":book: '{bookname}' {get_text('search-book-search-result')} **({page}/{data['meta']['total_count']})**",
                description=f"**{data['documents'][content]['title']}**", color=discord.Color.green())
            embed.set_author(name="using Kakao API",
                             icon_url="https://t1.kakaocdn.net/kakaocorp/kakaocorp/admin/1b884871017800001.png")
            embed.set_thumbnail(url=f"{data['documents'][content]['thumbnail']}")
            embed.add_field(name=get_text("search-book-embed-publish-author"),
                            value=f"``{data['documents'][content]['authors'][0]}``", inline=True)
            embed.add_field(name=get_text("search-book-embed-publisher"),
                            value=f"``{data['documents'][content]['publisher']}``", inline=True)
            embed.add_field(name=get_text("search-book-embed-publish-price"),
                            value=f"``{data['documents'][content]['sale_price']}원 (KAKAO)``",
                            inline=True)
            embed.add_field(name=get_text("search-book-embed-publish-date"),
                            value=f"``{(data['documents'][content]['datetime'])[:data['documents'][content]['datetime'].index('T')]}``",
                            inline=True)
            embed.add_field(name=get_text("search-book-embed-isbn"),
                            value=f"``{(data['documents'][content]['isbn'])[(data['documents'][content]['isbn']).index(' ') + 1:]}``",
                            inline=True)
            embed.add_field(name=get_text("search-book-embed-status"),
                            value=f"``{(data['documents'][content]['status'])}``", inline=True)
            embed.add_field(name=get_text("search-book-embed-book-details"),
                            value=f"``{cut_text(data['documents'][content]['contents'], 150)}``",
                            inline=False)
            embed.set_footer(text=f"Request by {interaction.user} ・ Developed by {get_text('PART1_DEVELOPER_NAME')}",
                             icon_url=f"{interaction.user.avatar}")
            embed.timestamp = datetime.datetime.now()
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title=f":book: '{bookname}' {get_text('search-book-search-no-result-1')}",
                                  description=f"{get_text('search-book-search-no-result-2')} ``{bookname}``",
                                  color=discord.Color.red())
            embed.set_author(name="using Kakao API",
                             icon_url="https://t1.kakaocdn.net/kakaocorp/kakaocorp/admin/1b884871017800001.png")
            embed.set_footer(text=f"Request by {interaction.user} ・ Developed by {get_text('PART1_DEVELOPER_NAME')}",
                             icon_url=f"{interaction.user.avatar}")
            embed.timestamp = datetime.datetime.now()
            await interaction.response.send_message(embed=embed)
    except Exception as e:
        await print_error(interaction, e.__class__.__name__, str(e), str(traceback.format_exc()))


# 메시지를 받았을 때 이벤트
@bot.event
async def on_message(message):
    if not message.guild:  # 메시지를 받은 곳이 서버가 아니고
        hour = time.localtime().tm_hour
        if not message.author.bot:  # 보낸 사람이 봇이 아니라면
            if 6 <= hour < 11:  # 6시 이상이거나 11시 이하라면 {멘션} おはようございます。 전송
                await message.channel.send(f'{message.author.mention}, おはようございます。')
            elif 12 <= hour < 18:  # 12시 이상이거나 18시 이하라면 {멘션} こんにちは。 전송
                await message.channel.send(f'{message.author.mention}, こんにちは。')
            elif 19 <= hour < 23:  # 19시 이상이거나 23시 이하라면 {멘션} こんばんは。 전송
                await message.channel.send(f'{message.author.mention}{get_text("message-not-guild-19-23")}')
            else:  # 그 외라면 {멘션} お休みなさい。전송
                await message.channel.send(f'{message.author.mention}, お休みなさい。')


# 토큰 유출 방지를 위해서 토큰은 외부 파일에 저장 후 불러옴.
# 토큰 파일은 .gitignore로 무시함.
bot.run(token=open(".token", "r").readline())
