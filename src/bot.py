import config

import discord
from discord import app_commands


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
    await interaction.response.send_message(f'Hey {interaction.user.mention}! Nice to see you.')


@client.tree.command(description='Displays the location of a point in a map')
@app_commands.describe(
    latitude='The latitude of the coordinate',
    longitude='The longitude of the coordinate',
)
async def map(interaction: discord.Integration, latitude: float, longitude: float):
    if latitude < -90 or latitude > 90:
        await interaction.response.send_message("Invalid latitude value. Latitude must be between -90 and 90 degrees.")
        return

    if longitude < -180 or longitude > 180:
        await interaction.response.send_message("Invalid longitude value. Longitude must be between -180 and 180 degrees.")
        return

    # Call function to get the map as an image
    # Display map image
    # Get a link to the coordinates on openstreetmap
    # Display link as a button
    await interaction.response.send_message(f'The coordinates are {latitude}, {longitude}')


client.run(config.DC_TOKEN)
