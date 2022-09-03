import os
import sys

from nextcord.ext import commands
from nextcord.gateway import DiscordWebSocket

from utils import parse_authkey

import nextcord

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

GUILD_ID = []
LOG_CHANNEL_ID = []
language = 'ko'

bot = commands.Bot(command_prefix='!', intents=intents)

for file in os.listdir('cogs'):
    if file.endswith('.py'):
        bot.load_extension("cogs." + file[:-3])

bot.run(token=parse_authkey.get_auth_key('discord-token'))
