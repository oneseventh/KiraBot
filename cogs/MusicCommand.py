"""
    #제작: @17th
    #최종 수정일: 2022년 09월 04일

    코드 참고: https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d
    thanks for @vbe0201!
"""

import asyncio
import functools
import itertools
import math
from datetime import datetime

import nextcord.ui
import yt_dlp
from async_timeout import timeout
from gtts import gTTS
from nextcord import Interaction, FFmpegPCMAudio
from nextcord.ext import commands

import main
from utils import kira_language, alert


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(nextcord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, interaction: nextcord.Interaction, source: nextcord.FFmpegPCMAudio, *, data: dict,
                 volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = interaction.user
        self.channel = interaction.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')
        self.request_time = datetime.now().strftime("%H:%M:%S")

    def __str__(self):
        return '{0.title}'.format(self)

    @classmethod
    async def create_source(cls, interaction: nextcord.Interaction, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:  # True
            process_info = data
        else:  # False
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(interaction, nextcord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append(kira_language.get_text("music-duration-days").format(days))
        if hours > 0:
            duration.append(kira_language.get_text("music-duration-hours").format(hours))
        if minutes > 0:
            duration.append(kira_language.get_text("music-duration-minutes").format(minutes))
        if seconds > 0:
            duration.append(kira_language.get_text("music-duration-seconds").format(seconds))

        return ' '.join(duration)


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (nextcord.Embed(title=self.source.uploader, url=self.source.uploader_url,
                                description='**[{0}]({1})**'.format(cut_text(self.source.title, 24), self.source.url),
                                color=0xffffff)
                 .set_author(name=kira_language.get_text("music-embed-title-playing"))
                 .add_field(name=kira_language.get_text("music-embed-field-description"), value='```{0}```'
                            .format(cut_text(self.source.description, 100)),
                            inline=False)
                 .add_field(name=kira_language.get_text("music-embed-field-duration"),
                            value='``{0}``'.format(self.source.duration))
                 .add_field(name=kira_language.get_text("music-embed-field-view"),
                            value='``{0}``'.format(self.source.views))
                 .add_field(name=kira_language.get_text("music-embed-field-like"),
                            value='``{0}``'.format(self.source.likes))
                 .add_field(name=kira_language.get_text("music-embed-field-date"),
                            value='``{0}``'.format(self.source.upload_date))
                 .add_field(name=kira_language.get_text("music-embed-field-time"),
                            value='``{0}``'.format(self.source.request_time))
                 .add_field(name=kira_language.get_text("music-embed-field-requester"), value=self.requester.mention)

                 # .add_field(name='``채널``', value=ㅇ)
                 .set_image(url=self.source.thumbnail))

        return embed

    def current_song(self):
        return [self.source.title, self.source.duration, self.source.uploader,
                self.source.uploader_url, self.source.thumbnail, self.source.url, self.source.requester]


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __sizeof__(self):
        return len(self._queue)

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    # def shuffle(self):
    #     random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, interaction: nextcord.Interaction):
        self.bot = bot
        self._interaction = interaction

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                # 노래가 끝난 후, 다음 노래가 예약 될때 까지 3분 동안 기다립니다.
                # 만약, 3분이 지나도 새로운 노래가 예약되지 않는다면 성능을 위해 연결을 끊습니다.
                try:
                    async with timeout(180):  # 3분, 1초 = 1
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(embed=self.current.create_embed())

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


def cut_text(text: str, index: int):
    """
    텍스트를 입력한 값에 따라 잘라 줍니다.
    텍스트의 길이가 입력한 값에 미달한 경우 그대로 return 하며,
    텍스트의 길이가 입력한 값보다 길때는 텍스트를 자른 뒤 ... 을 붙여서 return 합니다.
        Args:
            text (str): 자를 텍스트
            index (int): 자를 길이
        Returns:
            result (str): 자른 텍스트
    """
    if len(text) > 180:
        return text[:index] + '...'
    else:
        return text


def speak(text, filename):
    tts = gTTS(text=text, lang='ko')
    filename = filename
    tts.save(filename)


class MusicCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    guild_id = main.GUILD_ID
    process_tts = False

    def get_voice_state(self, interaction: nextcord.Interaction):
        state = self.voice_states.get(interaction.guild.id)
        if not state:
            state = VoiceState(self.bot, interaction)
            self.voice_states[interaction.guild.id] = state

        return state

    @nextcord.slash_command(name="따라해봐", description="보이스 채널에 접속해서 말을 따라합니다.", guild_ids=guild_id)
    async def _tts_voice(self, interaction: nextcord.Interaction, text: str):
        if self.process_tts:
            return await alert.error(interaction, kira_language.get_text("music-error-alerady-use-tts"))

        if self.get_voice_state(interaction).voice is None:
            if not interaction.user.voice:
                return await alert.error(interaction, kira_language.get_text("music-alert-join-error"))
            self.process_tts = True
            await alert.info(interaction, "``{0}``을(를) 따라 읽어 볼게!".format(text))
            destination = interaction.user.voice.channel
            self.get_voice_state(interaction).voice = await destination.connect()
            file_name = "./temp/{0}{1}.mp3".format(str(interaction.user.id), str(datetime.now().strftime("%H%M%S")))
            speak("{0}".format(text), file_name)
            source = FFmpegPCMAudio(file_name)
            self.get_voice_state(interaction).voice.play(source)
            while True:
                await asyncio.sleep(1)
                if not self.process_tts:
                    break
                if self.get_voice_state(interaction).voice.is_playing():
                    await asyncio.sleep(3)
                    continue
                else:
                    await self.get_voice_state(interaction).stop()
                    self.process_tts = False
                    break
        else:
            await alert.error(interaction, kira_language.get_text("music-error-alerady-music-use"))

    @nextcord.slash_command(name="노래", description="서브 명령어", guild_ids=guild_id)
    async def command_song(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("서브 명령어를 입력해주세요.", ephemeral=True)

    @command_song.subcommand(name='입장', description="✨ 노래를 들려주기 위해서 보이스 채널에 입장해요! - 개발 {0}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME")))
    async def _join(self, interaction: nextcord.Interaction):
        """유저가 있는 보이스 채널에 입장 합니다. 또한, 데이터 충돌 방지를 위해 대기열을 초기화 합니다."""
        if not self.process_tts:
            try:
                del self.voice_states[interaction.guild.id]
            except KeyError:
                print("없음")
            if not interaction.user.voice:
                return await alert.error(interaction, kira_language.get_text("music-alert-join-error"))
            destination = interaction.user.voice.channel
            if self.get_voice_state(interaction).voice:
                await self.get_voice_state(interaction).voice.move_to(destination)
                return await alert.success(interaction, kira_language.get_text("music-alert-join").format(destination.id))

            self.get_voice_state(interaction).voice = await destination.connect()
            return await alert.success(interaction, kira_language.get_text("music-alert-join").format(destination.id))

        return await alert.error(interaction, kira_language.get_text("music-alert-tts-error"))

    @command_song.subcommand(name='나가기', description="✨ 접속 한 보이스 채널에서 퇴장해요. - 개발 {0}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME")))
    async def _leave(self, interaction: Interaction):
        """대기열을 정리한 후 보이스 채널에서 퇴장합니다."""
        if self.get_voice_state(interaction).voice is None:
            return await alert.error(interaction, kira_language.get_text("music-alert-leave-error"))

        await alert.success(interaction, kira_language.get_text("music-alert-leave"))
        await self.get_voice_state(interaction).stop()
        if self.process_tts:
            self.process_tts = False
        del self.voice_states[interaction.guild.id]

    @command_song.subcommand(name='정보', description="✨ 재생 중인 노래의 정보를 표시해요. - 개발 {0}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME")))
    async def _now(self, interaction: Interaction):
        """재생중인 노래를 표시합니다."""
        try:
            await interaction.response.send_message(embed=self.get_voice_state(interaction).current.create_embed())
        except AttributeError:
            await alert.info(interaction, kira_language.get_text("music-alert-now-error"))

    @command_song.subcommand(name='정지', description="✨ 재생 중인 노래를 멈춰요. "
                                                      "[곧 지원이 종료되는 명령어예요.] - 개발 {0}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME")))
    async def _pause(self, interaction: Interaction):
        """재생중인 노래를 멈춥니다."""

        if self.get_voice_state(interaction).voice.is_playing():
            self.get_voice_state(interaction).voice.pause()
            return await alert.success(interaction, kira_language.get_text("music-alert-pause"))
        return await alert.success(interaction, kira_language.get_text("music-alert-already-pause"))

    @command_song.subcommand(name='재생', description="✨ 멈춘 노래를 재시작해요. "
                                                       "[곧 지원이 종료되는 명령어예요.] - 개발 {0}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME")))
    async def _resume(self, interaction: Interaction):
        """멈춰 있는 노래를 재생합니다."""

        if self.get_voice_state(interaction).voice.is_paused():
            self.get_voice_state(interaction).voice.resume()
            return await alert.success(interaction, kira_language.get_text("music-alert-resume"))
        return await alert.success(interaction, kira_language.get_text("music-alert-already-resume"))

    @command_song.subcommand(name='넘기기', description="✨ 재생중인 노래를 넘겨요. - 개발 {0}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME")))
    async def _skip(self, interaction: Interaction):
        if not self.get_voice_state(interaction).is_playing:
            return await alert.error(interaction, kira_language.get_text("music-alert-skip-error"))
        self.get_voice_state(interaction).skip()
        await alert.success(interaction, kira_language.get_text("music-alert-skip"))

    @command_song.subcommand(name='대기열', description="✨ 노래 대기열 정보를 표시해요. - 개발 {0}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME")))
    async def _queue(self, interaction: Interaction, *,
                     page: int = nextcord.SlashOption(name='페이지',
                                                      description='✨ 페이지 번호를 입력해 줘! '
                                                                  'TIP. 1 페이지에는 10개의 노래가 표시돼!',
                                                      required=True)):
        """
            길드의 음악 재생 목록을 표시 합니다.
            1 페이지당 10개의 항목을 볼 수 있으며, 이는 조정할 수 있습니다.
            :param page: 표시할 페이지 번호
        """
        if page is None:
            page = 1
        if len(self.get_voice_state(interaction).songs) == 0:
            return await alert.info(interaction, kira_language.get_text("music-alert-queue-empty"))

        items_per_page = 10  # 1 페이지당 보이는 항목 개수
        pages = math.ceil(len(self.get_voice_state(interaction).songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(self.get_voice_state(interaction).songs[start:end], start=start):
            queue += '`#{0}` [{1}]({2}) - **{3}**\n' \
                .format(i + 1, cut_text(song.source.title, 24), song.source.url,
                        self.get_voice_state(interaction).current.current_song()[6])
        queue += '\n' + kira_language.get_text("music-queue-embed-field-pages").format(page, pages)

        embed = nextcord.Embed(
            title=kira_language.get_text("music-queue-embed-field-now-playing"),
            description="[**{0}**]({1}) - **{2}**".format(cut_text(self.get_voice_state(interaction)
                                                                   .current.current_song()[0], 24),
                                                          self.get_voice_state(interaction).current.current_song()[5],
                                                          self.get_voice_state(interaction).current.current_song()[6]),

            color=0xffffff)
        embed.set_author(name=kira_language.get_text("music-queue-embed-title-playlist"))
        embed.set_thumbnail(url=self.get_voice_state(interaction).current.current_song()[4])
        embed.add_field(name=kira_language.get_text("music-queue-embed-field-wait-counts")
                        .format(len(self.get_voice_state(interaction).songs)), value=queue)
        embed.set_footer(
            text=f"Developed by {kira_language.get_text('PART1_DEVELOPER_NAME')}",
            icon_url=f"{kira_language.get_text('PART1_DEVELOPER_PROFILE_URL')}")
        await interaction.response.send_message(embed=embed)

    @command_song.subcommand(name='제거', description="✨ 대기열에서 노래를 제거해요. - 개발 {0}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME")))
    async def _remove(self, interaction: Interaction,
                      index: str = nextcord.SlashOption(name='대기열',
                                                        description='✨ 노래가 위치 해있는 대기 번호를 입력 해 줘!',
                                                        required=True)):
        """ index에 대응 하는 노래를 대기열에서 제거 합니다. """

        if len(self.get_voice_state(interaction).songs) == 0:
            return await alert.error(interaction, kira_language.get_text("music-alert-queue-empty"))
        else:
            await alert.success(interaction, kira_language.get_text("music-alert-removed-song")
                                .format(index, self.get_voice_state(interaction).songs[index - 1].source.title))
            self.get_voice_state(interaction).songs.remove(index - 1)

    @command_song.subcommand(name='예약', description="✨ 원하는 노래를 들려 드려요! - 개발 {0}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME")))
    async def _play(self, interaction: Interaction,
                    search: str = nextcord.SlashOption(name='검색',
                                                       description='✨ 듣고 싶은 노래 제목이나 유튜브 URL을 적어 줘!',
                                                       required=True)):
        if not self.process_tts:
            if interaction.user.voice is None:
                return alert.error(interaction, kira_language.get_text("music-alert-join-error"))
            if self.get_voice_state(interaction).voice is None:
                destination = interaction.user.voice.channel
                self.get_voice_state(interaction).voice = await destination.connect()
            try:
                await interaction.response.defer()
                source = await YTDLSource.create_source(interaction, search, loop=self.bot.loop)
                song = Song(source)
                embed = nextcord.Embed(title=kira_language.get_text("embed-title-success"),
                                       description=kira_language.get_text("music-alert-enqueued-success")
                                       .format(source, len(self.get_voice_state(interaction).songs) + 1),
                                       color=nextcord.Color.green())
                embed.set_footer(
                    text=f"Developed by {kira_language.get_text('PART1_DEVELOPER_NAME')}",
                    icon_url=f"{kira_language.get_text('PART1_DEVELOPER_PROFILE_URL')}")
                embed.timestamp = datetime.now()
                await interaction.followup.send(embed=embed, ephemeral=True)
                await self.get_voice_state(interaction).songs.put(song)
            except YTDLError as e:
                return await alert.error(interaction, '재생할 수 없음: {}'.format(str(e)))
        else:
            return await alert.error(interaction, kira_language.get_text("music-alert-tts-error"))


def setup(bot):
    bot.add_cog(MusicCommand(bot))
