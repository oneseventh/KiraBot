import os

from nextcord.ext import commands
from utils import parse_authkey

import nextcord

intents = nextcord.Intents.default()
intents.message_content = True

GUILD_ID = 1011601743399890975
bot = commands.Bot(command_prefix='!', intents=intents)

for file in os.listdir('cogs'):
    if file.endswith('.py'):
        bot.load_extension("cogs." + file[:-3])

bot.run(token=parse_authkey.get_auth_key('discord-token'))
