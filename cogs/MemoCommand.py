import sqlite3
from datetime import datetime

import nextcord
from nextcord import Interaction, ui
from nextcord.ext import commands

import main
from utils import alert, kira_language


class MemoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('././memo.db', isolation_level=None)
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS memo \
                             (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                       "timestamp DATETIME DEFAULT (DATETIME('now', 'localtime')), "
                       "user_id INTEGER, memo_name TEXT, content TEXT)")

    guild_id = main.GUILD_ID

    @nextcord.slash_command(name="memo", description="✨ 나에게 알려줄 메모를 쓰거나 쓴 메모를 확인 할 수 있어!", guild_ids=[guild_id])
    async def memo(self, interaction: Interaction,
                   action: int = nextcord.SlashOption(name="행동", choices={"읽기": 1, "쓰기": 2, "삭제": 3},
                                                      description="✨ 메모를 읽을 지, 메모를 새로 쓸지, 메모를 지울 지 알려줘!",
                                                      required=True)):
        if action == 1:
            conn = sqlite3.connect('././memo.db', isolation_level=None)
            c = self.conn.cursor()
            c.execute("SELECT COUNT(memo_name) FROM memo WHERE user_id = ? AND memo_name = ?", (interaction.user.id, '히히'))
            result = c.fetchone()
            if result[0] == 0:
                await alert.error(interaction, f"``name`` {kira_language.get_text('memo-error-not-found')}")
                return
            self.c.execute("SELECT * FROM memo WHERE user_id = ? AND memo_name = ?", (interaction.user.id, '히히'))
            result = self.c.fetchone()
            c.close()

            embed = nextcord.Embed(title=kira_language.get_text("memo-embed-title"),
                                   description=kira_language.get_text("memo-embed-description"),
                                   color=nextcord.Color.random())
            embed.set_author(name=f"Request by {interaction.user}", icon_url=interaction.user.avatar)
            embed.add_field(name=kira_language.get_text("memo-embed-field-memo-num"),
                            value=f"``#{result[0]}``", inline=True)
            embed.add_field(name=kira_language.get_text("memo-embed-field-memo-name"),
                            value=f"``{result[3]}``", inline=True)
            embed.add_field(name=kira_language.get_text("memo-embed-field-memo-time"),
                            value=f"``{result[1]}``", inline=True)
            embed.add_field(name=kira_language.get_text("memo-embed-field-memo-content"),
                            value=f"```{result[4]}```", inline=False)
            embed.set_footer(
                text=f"Developed by {kira_language.get_text('PART1_DEVELOPER_NAME')}",
                icon_url=f"{kira_language.get_text('PART1_DEVELOPER_PROFILE_URL')}")
            embed.timestamp = datetime.now()
            await interaction.response.send_message(embed=embed, view=MemoButton(interaction, result[3]), ephemeral=True)
        elif action == 2:
            await interaction.response.send_modal(WriteMemo())
        elif action == 3:
            await alert.developing(interaction)


class MemoButton(nextcord.ui.View):
    def __init__(self, interaction: nextcord.Interaction, memo_name: str):
        super().__init__()
        self.interaction = interaction
        self.memo_name = memo_name

    @nextcord.ui.button(label=kira_language.get_text('memo-button-text-download'),
                        style=nextcord.ButtonStyle.gray, emoji="💾")
    async def download(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await download_memo(interaction, interaction.user.id, self.memo_name)

    @nextcord.ui.button(label=kira_language.get_text('memo-button-text-remove'),
                        style=nextcord.ButtonStyle.red, emoji="🔥")
    async def remove(self, button: nextcord.Button, interaction: nextcord.Interaction):
        pass


def check_memo(user_id: int, memo_name: str):
    conn = sqlite3.connect('././memo.db', isolation_level=None)
    c = conn.cursor()
    c.execute("SELECT * FROM memo WHERE user_id = ? AND memo_name = ?", (user_id, memo_name))
    if c.fetchone() is None:
        return False
    return True


async def download_memo(interaction: Interaction, user_id: int, memo_name: str):
    file_path = f"././temp/{memo_name}-{user_id}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"user-id: {str(user_id)}\n")
        f.write(f"memo-name: {memo_name}\n")
        conn = sqlite3.connect('././memo.db', isolation_level=None)
        c = conn.cursor()
        c.execute("SELECT * FROM memo WHERE user_id = ? AND memo_name = ?", (user_id, memo_name))
        result = c.fetchone()
        c.close()
        f.write(f"memo:\n{result[4]}")
    await interaction.user.send(f"``{memo_name}-{user_id}.txt`` "
                                f"{kira_language.get_text('memo-private-dm-message')}",
                                files=[nextcord.File(file_path)])
    await alert.success(interaction, kira_language.get_text('memo-download-success'))


async def remove_memo(interaction: Interaction, user_id: int, memo_name: str):
    conn = sqlite3.connect('././memo.db', isolation_level=None)
    c = conn.cursor()
    c.execute("DELETE FROM memo WHERE user_id = ? AND memo_name = ?", (user_id, memo_name))
    c.close()


class WriteMemo(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            kira_language.get_text("memo-write-modal-title")
        )

        self.memo_name = ui.TextInput(label="메모 이름을 적어줘!", placeholder="ex. 내일 모하지?",
                                 max_length=10, style=nextcord.TextInputStyle.short, required=True)
        self.add_item(self.memo_name)
        self.memo_content = ui.TextInput(label="메모할 내용을 적어줘!",
                                    max_length=500, style=nextcord.TextInputStyle.paragraph, required=True)
        self.add_item(self.memo_content)
        self.lang = kira_language.get_current_lang()

    async def callback(self, interaction: nextcord.Interaction) -> None:
        if check_memo(interaction.user.id, self.memo_name.value):
            await alert.error(interaction, kira_language.get_text(self.lang, "memo-error-name-already-exist"))
            return
        else:
            memo_content = self.memo_content.value
            conn = sqlite3.connect('././memo.db', isolation_level=None)
            c = conn.cursor()
            c.execute("INSERT INTO memo (user_id, memo_name, content) VALUES (?, ?, ?)",
                      (interaction.user.id, self.memo_name.value, memo_content.replace("'", "'")))
            conn.commit()
            conn.close()
            await alert.success(interaction, f"``{self.memo_name.value}``"
                                             f" {kira_language.get_text(self.lang, 'memo-success-write')}\n"
                                             f"**{kira_language.get_text(self.lang, 'memo-embed-field-memo-content')}**"
                                             f"```{self.memo_content.value}```")
            return


def setup(bot):
    bot.add_cog(MemoCommand(bot))
