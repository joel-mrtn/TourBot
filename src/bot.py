import os

import discord
from discord import app_commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


class BotClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)


intents = discord.Intents.default()
intents.message_content = True

client = BotClient(intents=intents)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.tree.command(name='hello')
async def hello(interaction: discord.Integration):
    await interaction.response.send_message(f'Hey {interaction.user.mention}! Nice to see you.')


client.run(TOKEN)
