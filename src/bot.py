import config
import routes

import discord
from discord import app_commands
from PIL import Image


class BotClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    # By specifically naming the guild, the commands are updated faster on the server.
    async def setup_hook(self):
        self.tree.copy_global_to(guild=config.DC_GUILD)
        await self.tree.sync(guild=config.DC_GUILD)


intents = discord.Intents.default()
client = BotClient(intents=intents)


# Console log at start
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.tree.command(description='Get a nice greeting from the bot')
async def hello(interaction: discord.Integration):
    await interaction.response.send_message(content=f'Hey {interaction.user.mention}! Nice to see you.', ephemeral=True)


@client.tree.command(description='Generate a HTML file with a route which you can open in your browser')
@app_commands.describe(
    latitude1='The latitude of the first coordinate',
    longitude1='The longitude of the first coordinate',
    latitude2='The latitude of the seccond coordinate',
    longitude2='The longitude of the seccond coordinate',
)
async def map(interaction: discord.Integration, latitude1: float, longitude1: float, latitude2: float, longitude2: float):
    if latitude1 < -90 or latitude1 > 90 or latitude2 < -90 or latitude2 > 90:
        await interaction.response.send_message("Invalid latitude value. Latitude must be between -90 and 90 degrees.", ephemeral=True)
        return

    if longitude1 < -180 or longitude1 > 180 or longitude2 < -180 or longitude2 > 180:
        await interaction.response.send_message("Invalid longitude value. Longitude must be between -180 and 180 degrees.", ephemeral=True)
        return

    map_html_file = routes.get_html_map(latitude1, longitude1, latitude2, longitude2)
    discord_file = discord.File(map_html_file, filename='map.html')

    await interaction.response.send_message(content=f'Here is the route from {latitude1}, {longitude1} to {latitude2}, {longitude2}. Open this HTML file in your browser to see the route.', file=discord_file)

client.run(config.DC_TOKEN)
