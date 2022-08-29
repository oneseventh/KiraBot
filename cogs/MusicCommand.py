import nextcord.ui
from nextcord import Interaction
from nextcord.ext import commands

import main
from utils import kira_language, alert


class MusicCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    guild_id = main.GUILD_ID

    @nextcord.slash_command(name="join", description="✨ 노래를 재생하기 위해서 접속중인 음성 채널에 들어갈거야!", guild_ids=[guild_id])
    async def test(self, interaction: Interaction, vc: nextcord.VoiceChannel =
    nextcord.SlashOption(name="음성_채널", description="✨ 들어갈 음성 채널을 멘션해 줘!", required=False)):
        voice_channel = nextcord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        if voice_channel is not None:
            await interaction.guild.voice_client.disconnect(force=True)
            if vc is None:
                if interaction.user.voice is None:
                    await alert.error(interaction,
                                      kira_language.get_text('ko', "bot-request-enter-voice-"
                                                                   "channel-if-user-not-joined-voice-channel"))
                    return
                else:
                    await interaction.user.voice.channel.connect()
                    # await interaction.response.send_message(embed=no_queue(), view=QueueButton(interaction))
                    await interaction.response.send_message("ㅇ")
                    return
            else:
                await vc.connect()
                # await interaction.response.send_message(embed=no_queue(), view=QueueButton(interaction))
                await interaction.response.send_message("ㅇ")
                return

        else:
            if interaction.user.voice is None:
                await alert.error(interaction,
                                  kira_language.get_text('ko', "bot-request-enter-voice-"
                                                               "channel-if-user-not-joined-voice-channel"))
                return
            else:
                await interaction.user.voice.channel.connect()
                # await interaction.response.send_message(embed=no_queue(), view=QueueButton(interaction))
                await interaction.response.send_message("ㅇ")
                return


class EnterButton(nextcord.ui.View):
    def __init__(self, interaction: nextcord.Interaction):
        super().__init__()
        self.interaction = interaction

    @nextcord.ui.button(label=kira_language.get_text('ko', 'music-bot-button-text-reenter'),
                        style=nextcord.ButtonStyle.green, emoji="✨")
    async def reenter(self, button: nextcord.Button, inter: nextcord.Interaction):
        if inter.user.voice is None:
            await inter.response.send_message(kira_language.get_text
                                              ('ko', "bot-request-enter-voice-channel-if-user-not-joined"
                                                     "-voice-channel"))
            return
        else:
            await inter.user.voice.channel.connect()
            return


def setup(bot):
    bot.add_cog(MusicCommand(bot))
