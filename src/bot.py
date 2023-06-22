from config import DC_TOKEN, DC_GUILD
from discord import app_commands

import discord
import commands.interactions as interactions


class BotClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        await self.wait_until_ready()

        print(f'{client.user} has connected to Discord!')

    # By specifically naming the guild, the commands are updated faster on the server.
    async def setup_hook(self):
        self.tree.copy_global_to(guild=DC_GUILD)
        await self.tree.sync(guild=DC_GUILD)


intents = discord.Intents.default()
client = BotClient(intents=intents)


@client.tree.command(description='Get a nice greeting from the bot.')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(content=f'Hey {interaction.user.mention}! Nice to see you.', ephemeral=True)


@client.tree.command(description='Create a route based on multiple stops.')
async def route(interaction: discord.Interaction):
    await interactions.ready(interaction)


client.run(DC_TOKEN)
