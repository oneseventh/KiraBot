import asyncio
import traceback
from datetime import timedelta

import nextcord.ui
import youtube_dl
from nextcord import Interaction
from nextcord.ext import commands

import main
from utils import kira_language, alert


class MusicQueue:
    def __init__(self, max_size=50):
        self.queue_list = [None] * max_size
        self.capacity = max_size
        self.front = 0
        self.rear = -1
        self.count = 0

    def dequeue(self):
        if self.is_empty():
            print("Queue underflow")
        x = self.queue_list[self.front]
        del self.queue_list[self.front]
        self.front = (self.front + 1) % self.capacity
        self.count = self.count - 1
        return x

    def enqueue(self, value):
        if self.is_full():
            print("Queue overflow")
        self.rear = (self.rear + 1) % self.capacity
        self.queue_list[self.rear] = value
        self.count = self.count + 1

    def get(self, index):
        return self.queue_list[index]

    def get_all(self):
        return self.queue_list

    def get_front(self):
        if self.is_empty():
            print("Queue underflow")
        return self.queue_list[self.front]

    def size(self):
        return self.count

    def is_empty(self):
        return self.count == 0

    def is_full(self):
        return self.size() == self.capacity


class MusicCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    q = MusicQueue(50)
    guild_id = main.GUILD_ID

    @nextcord.slash_command(name="join",
                            description="✨ 노래를 재생하기 위해서 접속중인 음성 채널에 들어갈거야!", guild_ids=[guild_id])
    async def test(self, interaction: Interaction, vc: nextcord.VoiceChannel =
    nextcord.SlashOption(name="음성_채널", description="✨ 들어갈 음성 채널을 멘션해 줘!", required=False)):
        voice_channel = nextcord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        if voice_channel is not None:
            await interaction.guild.voice_client.disconnect(force=True)
            if vc is None:
                if interaction.user.voice is None:
                    await alert.error(interaction,
                                      kira_language.get_text("bot-request-enter-voice-"
                                                             "channel-if-user-not-joined-voice-channel"))
                    return
                else:
                    await interaction.user.voice.channel.connect()
                    # await interaction.response.send_message(embed=no_queue(), view=QueueButton(interaction))
                    await interaction.response.send_modal(MusicForm())
                    return
            else:
                await vc.connect()
                # await interaction.response.send_message(embed=no_queue(), view=QueueButton(interaction))
                await interaction.response.send_modal(MusicForm())
                return

        else:
            if interaction.user.voice is None:
                await alert.error(interaction,
                                  kira_language.get_text("bot-request-enter-voice-"
                                                         "channel-if-user-not-joined-voice-channel"))
                return
            else:
                await interaction.user.voice.channel.connect()
                # await interaction.response.send_message(embed=no_queue(), view=QueueButton(interaction))
                await interaction.response.send_modal(MusicForm())
                return

    @nextcord.slash_command(name="summon_button", description="✨ [TEST]", guild_ids=[guild_id])
    async def summon_button(self, interaction: Interaction):
        await interaction.response.send_message(view=MusicButton(interaction))

    @nextcord.slash_command(name="add_queue", description="✨ [TEST]", guild_ids=[guild_id])
    async def add_queue(self, interaction: nextcord.Interaction, url: str):
        self.q.enqueue(url)
        await alert.success(interaction, f"``{url}``이 재생목록 에 추가되었습니다.")

    @nextcord.slash_command(name="view_queue", description="✨ [TEST]", guild_ids=[guild_id])
    async def view_queue(self, interaction: nextcord.Interaction):
        if self.q.count == 0:
            await alert.info(interaction, f"재생 목록에 아무것도 없습니다.")
            return
        songs = ""
        count = 1
        for song in self.q.get_all():
            if song is None:
                continue
            songs += f"{count}. ``{song}``\n"
            count += 1
        songs += f"재생목록에 총 {self.q.count}개의 항목이 있습니다.\n"
        songs += f"{self.q.get_all()}"
        await alert.info(interaction, songs)

    @nextcord.slash_command(name="delete_queue", description="✨ [TEST]", guild_ids=[guild_id])
    async def delete_queue(self, interaction: nextcord.Interaction):
        self.q.dequeue()
        await alert.success(interaction, f"재생 목록에서 첫번째 음악이 삭제되었습니다.")


class EnterButton(nextcord.ui.View):
    def __init__(self, interaction: nextcord.Interaction):
        super().__init__()
        self.interaction = interaction

    @nextcord.ui.button(label=kira_language.get_text('music-bot-button-text-reenter'),
                        style=nextcord.ButtonStyle.green, emoji="✨")
    async def reenter(self, button: nextcord.Button, inter: nextcord.Interaction):
        if inter.user.voice is None:
            await inter.response.send_message(kira_language.get_text
                                              (kira_language.get_current_lang(),
                                               "bot-request-enter-voice-channel-if-user-not-joined"
                                               "-voice-channel"))
            return
        else:
            await inter.user.voice.channel.connect()
            return


class MusicButton(nextcord.ui.View):
    def __init__(self, interaction: nextcord.Interaction):
        super().__init__()
        self.interaction = interaction

    # @nextcord.ui.button(label="이전", style=nextcord.ButtonStyle.primary, emoji="⏮")
    # async def back(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
    #     await alert.developing(interaction)

    @nextcord.ui.button(label="재생", style=nextcord.ButtonStyle.green)
    async def play(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        try:
            if self.interaction.guild.voice_client.is_playing():
                await alert.error(interaction, kira_language.get_text("song-already-resumed"))
            else:
                self.interaction.guild.voice_client.resume()
                await alert.success(interaction, kira_language.get_text("song-resumed"))
        except AttributeError as e:
            await alert.critical_error(interaction, e.__class__.__name__, str(e), str(traceback.format_exc()))

    @nextcord.ui.button(label="멈춤", style=nextcord.ButtonStyle.gray)
    async def pause(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.interaction.guild.voice_client.is_playing():
            self.interaction.guild.voice_client.pause()
            await alert.success(interaction, kira_language.get_text("song-stopped"))
        else:
            await alert.error(interaction, kira_language.get_text("song-already-stopped"))

    @nextcord.ui.button(label="스킵", style=nextcord.ButtonStyle.danger)
    async def next(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.interaction.guild.voice_client.stop()
        await alert.success(interaction, kira_language.get_text("song-skipped"))

    @nextcord.ui.button(label="나가기", style=nextcord.ButtonStyle.danger)
    async def exit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.guild.voice_client.disconnect(force=True)
        await alert.success(interaction, kira_language.get_text("leave-voice-room"))


class MusicForm(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            kira_language.get_text("modal-title-song-queue")
        )
        self.answer = nextcord.ui.TextInput(label=kira_language.get_text("modal-label-want-youtube-link"),
                                            style=nextcord.TextInputStyle.short,
                                            placeholder="https://www.youtube.com/watch...",
                                            required=True)
        self.add_item(self.answer)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        YDL_OPTIONS = {'format': 'bestaudio'}
        vc = interaction.guild.voice_client
        try:
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(self.answer.value, download=False)
                url2 = info['formats'][0]['url']
                source = await nextcord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                title = info.get('title')
                if len(title) > 20:
                    title = title[:19] + "..."
                description = info.get('description')
                if len(description) > 80:
                    description = description[:80] + "..."
                # await bot.change_presence(
                #     activity=discord.Activity(type=discord.ActivityType.listening, name=f"{title}"))
                embed = nextcord.Embed(title=f"{title}", url=f"{self.answer.value}", description=f"{description}",
                                       color=nextcord.Color.dark_gold()) \
                    .add_field(
                    name=kira_language.get_text("music-bot-embed-duration"),
                    value=f"``{str(timedelta(seconds=int(info.get('duration'))))}``").set_image(
                    url=f"{info.get('thumbnail')}").add_field(name=kira_language.get_text("music-bot-embed-viewer"),
                                                              value=f"``{format(info.get('view_count'), ',')}``",
                                                              inline=True).add_field(
                    name=kira_language.get_text("music-bot-embed-like"),
                    value=f"``{format(info.get('like_count'), ',')}``",
                    inline=True).set_author(
                    name=f"{info.get('uploader')}",
                    url=f"{info.get('uploader_url')}").set_footer(
                    text=f"Request by {interaction.user} ・ Developed by {kira_language.get_text('PART1_DEVELOPER_NAME')}",
                    icon_url=f"{interaction.user.avatar}")
                await interaction.response.send_message(embed=embed, view=MusicButton(interaction))
                vc.play(source)
        except Exception as e:
            await alert.critical_error(interaction, e.__class__.__name__, str(e), str(traceback.format_exc()))


def no_queue():
    embed = nextcord.Embed(title=kira_language.get_text("song-no-playing"),
                           description=kira_language.get_text("song-want-to-listen"),
                           color=nextcord.Color.dark_gray())
    embed.set_footer(text=f"Developed by {kira_language.get_text('PART1_DEVELOPER_NAME')}",
                     icon_url=f"{kira_language.get_text('PART1_DEVELOPER_PROFILE_URL')}")
    return embed


def utc_to_kst(origin_time):
    return (origin_time + timedelta(hours=9)).strftime("%Y-%m-%d %T")


def setup(bot):
    bot.add_cog(MusicCommand(bot))
