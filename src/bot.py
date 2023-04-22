import os

import discord
from discord import app_commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MY_GUILD = discord.Object(id=os.getenv('MY_GUILD'))


class BotClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    # By specifically naming the guild, the commands are updated faster on the server.
    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = BotClient(intents=intents)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.tree.command(description='Get a nice greeting from the bot.')
async def hello(interaction: discord.Integration):
    await interaction.response.send_message(f'Hey {interaction.user.mention}! Nice to see you.')


client.run(TOKEN)
