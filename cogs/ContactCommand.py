"""
    #제작: @17th
    #최종 수정일: 2022년 09월 04일
"""

import nextcord
from nextcord import SlashOption, Interaction, File
from nextcord.ext import commands
from nextcord.ui import TextInput, Modal

from utils import alert


class ContactCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class WriteContact(Modal):
        def __init__(self, bot):
            self.bot = bot
            super().__init__(
                "개발자에게 문의 하기"
            )

            self.contact_name = TextInput(label="문의 내용", placeholder="빠른 처리를 위해 문의 내용을 \"자세하게\" 입력해 줘!\n"
                                                                     "- 노래가 안 돼요. (X)\n"
                                                                     "- /play 노래가 재생되지 않아요. 에러 메시지는.. (O)",
                                          max_length=4000, style=nextcord.TextInputStyle.paragraph, required=True)
            self.add_item(self.contact_name)
            self.image = TextInput(label="이미지 | TIP. 반드시 https://로 시작 해야 해!",
                                   placeholder="이미지가 있다면 이미지 링크를 입력해 줘!", min_length=10,
                                   required=False)
            self.add_item(self.image)

        async def callback(self, interaction: Interaction):
            if len(self.image.value) > 9:
                if not self.image.value.startswith("https://"):
                    return await alert.error(interaction, "이미지 링크는 반드시 https://로 시작 해야 해!")
            developer = await self.bot.fetch_user(574411212599590940)
            if interaction.guild is not None:
                embed = nextcord.Embed(title="문의가 들어 왔어!", description="``{0}`` 길드의 ``{1}``가 문의를 접수 했어!"
                                       .format(interaction.guild.name, interaction.user), color=0xffffff)
            else:
                embed = nextcord.Embed(title="문의가 들어 왔어!", description="``{0}``가 문의를 접수 했어!"
                                       .format(interaction.user), color=0xffffff)

            embed.set_image(url=self.image.value)
            embed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar)
            embed.add_field(name="문의 내용", value="```{0}```".format(self.contact_name.value), inline=False)
            await developer.send(embed=embed)
            await interaction.response.send_message("제출되었습니다.")

    @nextcord.slash_command(name="contact", description="개발자에게 문의 하기")
    async def _contact(self, interaction: Interaction):
        await interaction.response.send_modal(self.WriteContact(self.bot))


def setup(bot):
    bot.add_cog(ContactCommand(bot))
