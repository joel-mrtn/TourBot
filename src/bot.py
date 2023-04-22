import os

import discord
from dotenv import load_dotenv

# get token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    # ignore self messages
    if message.author == client.user:
        return
    
    if message.content == 'foo':
        await message.channel.send('bar')

client.run(TOKEN)