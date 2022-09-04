"""
    #제작: @17th
    #최종 수정일: 2022년 09월 04일
"""

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

    @nextcord.slash_command(name="메모", description="✨ 새로운 메모를 쓰거나 쓴 메모를 확인 할 수 있어요. - 개발 {0}"
                            .format(kira_language.get_text("PART1_DEVELOPER_NAME")), guild_ids=guild_id)
    async def _memo(self, interaction: Interaction):
        pass

    @_memo.subcommand(name="읽기", description="✨ 쓴 메모를 읽어요.")
    async def read(self, interaction: Interaction):
        await interaction.response.send_message(f"{kira_language.get_text('memo-list-info-text')}",
                                                view=MemoListView(interaction.user.id), ephemeral=True)

    @_memo.subcommand(name="쓰기", description="✨ 메모를 쓸 수 있어요.")
    async def _write(self, interaction: Interaction):
        if await get_memo_count(interaction.user.id) >= 10:
            return await alert.error(interaction, kira_language.get_text('memo-error-created-max'))
        return await interaction.response.send_modal(WriteMemo())


class MemoList(nextcord.ui.Select):
    def __init__(self, user_id: int):
        memo_list = []
        if get_memo_count(user_id) == 0:
            memo_list.append(nextcord.SelectOption(label="메모가 없어요!",
                                                   description="/메모 쓰기로 메모를 써보세요!", value="X"))

        for memo in get_memo_list(user_id):
            if len(memo[1]) > 30:
                memo_list.append(
                    nextcord.SelectOption(label=memo[0], value=memo[0], description=memo[1][:30] + "..."))
                continue
            memo_list.append(nextcord.SelectOption(label=memo[0], value=memo[0], description=memo[1]))
        super().__init__(placeholder="✨ 읽을 메모를 선택해 줘!", min_values=1, max_values=1, options=memo_list)

    async def callback(self, interaction: Interaction):
        if self.values[0] != "X":
            await get_memo(interaction, self.values[0])


class MemoListView(nextcord.ui.View):
    def __init__(self, user_id: int):
        super().__init__()
        self.add_item(MemoList(user_id))


class MemoButton(nextcord.ui.View):
    def __init__(self, interaction: nextcord.Interaction, memo_name: str):
        super().__init__()
        self.interaction = interaction
        self.memo_name = memo_name

    @nextcord.ui.button(label=kira_language.get_text("memo-button-text-download"),
                        style=nextcord.ButtonStyle.gray, emoji="💾")
    async def download(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await download_memo(interaction, interaction.user.id, self.memo_name)

    @nextcord.ui.button(label=kira_language.get_text("memo-button-text-remove"),
                        style=nextcord.ButtonStyle.red, emoji="🔥")
    async def remove(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await remove_memo(interaction, interaction.user.id, self.memo_name)


def get_memo_count(user_id: int):
    conn = sqlite3.connect('././memo.db', isolation_level=None)
    c = conn.cursor()
    c.execute("SELECT COUNT(memo_name) FROM memo WHERE user_id = {0}".format(user_id))
    result = c.fetchone()
    c.close()
    conn.close()
    return int(result[0])


async def get_memo(interaction: Interaction, memo_name: str):
    user_id = interaction.user.id
    if check_memo_exist(user_id, memo_name):
        conn = sqlite3.connect('././memo.db', isolation_level=None)
        c = conn.cursor()
        c.execute("SELECT * FROM memo WHERE user_id = ? AND memo_name = ?",
                  (user_id, memo_name))
        result = c.fetchone()

        embed = nextcord.Embed(title=kira_language.get_text("memo-embed-description"),
                               color=0xffffff)
        embed.set_author(name=kira_language.get_text("memo-embed-title"))
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
        await interaction.response.send_message(embed=embed, view=MemoButton(interaction, result[3]),
                                                ephemeral=True)


def get_memo_list(user_id: int):
    """
    작성한 메모의 목록을 가져옵니다..
    :param user_id: 유저의 디스코드 ID
    :return: List를 반환합니다. [(메모 이름, 메모 내용)]
    """
    with sqlite3.connect('././memo.db', isolation_level=None) as conn:
        c = conn.cursor()
        c.execute(f"SELECT memo_name, content FROM memo WHERE user_id = {user_id}")
        result = c.fetchall()
        c.close()
    return result


def check_memo_exist(user_id: int, memo_name: str):
    conn = sqlite3.connect('././memo.db', isolation_level=None)
    c = conn.cursor()
    c.execute("SELECT * FROM memo WHERE user_id = ? AND memo_name = ?", (user_id, memo_name))
    if c.fetchone() is None:
        return False
    return True


async def download_memo(interaction: Interaction, user_id: int, memo_name: str):
    file_path = f"././temp/{memo_name}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"메모 이름: {memo_name}\n")
        conn = sqlite3.connect('././memo.db', isolation_level=None)
        c = conn.cursor()
        c.execute("SELECT * FROM memo WHERE user_id = ? AND memo_name = ?", (user_id, memo_name))
        result = c.fetchone()
        c.close()
        f.write(f"내용:\n{result[4]}")
    await interaction.user.send(f"``{memo_name}-{user_id}.txt`` "
                                f"{kira_language.get_text('memo-private-dm-message')}",
                                files=[nextcord.File(file_path)])
    await alert.success(interaction, kira_language.get_text('memo-download-success'))


async def remove_memo(interaction: Interaction, user_id: int, memo_name: str):
    conn = sqlite3.connect('././memo.db', isolation_level=None)
    c = conn.cursor()
    c.execute("DELETE FROM memo WHERE user_id = ? AND memo_name = ?", (user_id, memo_name))
    conn.commit()
    c.close()
    conn.close()
    await alert.success(interaction, kira_language.get_text('memo-remove-success'))


class WriteMemo(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            kira_language.get_text("memo-write-modal-title")
        )

        self.memo_name = ui.TextInput(label="메모 이름을 적어줘!", placeholder="ex. 내일 모하지?",
                                      max_length=10, style=nextcord.TextInputStyle.short, required=True)
        self.add_item(self.memo_name)
        self.memo_content = ui.TextInput(label="메모할 내용을 적어줘!",
                                         max_length=2000, style=nextcord.TextInputStyle.paragraph, required=True)
        self.add_item(self.memo_content)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        if check_memo_exist(interaction.user.id, self.memo_name.value):
            await alert.error(interaction, kira_language.get_text("memo-error-name-already-exist"))
            return
        else:
            memo_content = self.memo_content.value
            conn = sqlite3.connect('././memo.db', isolation_level=None)
            c = conn.cursor()
            c.execute("INSERT INTO memo (user_id, memo_name, content) VALUES (?, ?, ?)",
                      (interaction.user.id, self.memo_name.value, memo_content.replace("'", "'")))
            conn.commit()
            conn.close()
            await alert.success(interaction,
                                f"``{self.memo_name.value}`` {kira_language.get_text('memo-success-write')}\n"
                                f"**{kira_language.get_text('memo-embed-field-memo-content')}**"
                                f"```{self.memo_content.value}```")
            return


def setup(bot):
    bot.add_cog(MemoCommand(bot))
