import os

from nextcord.ext import commands
from utils import parse_authkey

import nextcord

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

GUILD_ID = 959030740643893309
channel_id = 0
language = 'ko'

bot = commands.Bot(command_prefix='!', intents=intents)

for file in os.listdir('cogs'):
    if file.endswith('.py'):
        bot.load_extension("cogs." + file[:-3])


def reset():
    for cog_file in os.listdir('cogs'):
        if cog_file.endswith('.py'):
            bot.unload_extension("cogs." + cog_file[:-3])
            bot.load_extension("cogs." + cog_file[:-3])


bot.run(token=parse_authkey.get_auth_key('discord-token'))