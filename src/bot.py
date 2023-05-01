import config
import routes

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


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.tree.command(description='Get a nice greeting from the bot')
async def hello(interaction: discord.Integration):
    await interaction.response.send_message(content=f'Hey {interaction.user.mention}! Nice to see you.', ephemeral=True)


@client.tree.command(description='Get the coordinates of an address')
async def addr_to_coords(interaction: discord.Integration, address: str):
    coords = routes.conv_addr_to_coords(address)

    view = discord.ui.View()
    ui = discord.ui.Select(
        placeholder = 'Choose from one of your possible addresses',
        min_values = 1,
        max_values = 1,
    )

    for coordinates in coords:
                option = discord.SelectOption(
                    label = coordinates.label,
                    description = f'Latitude: {coordinates.longtitude}, Longtitude: {coordinates.longtitude}'
                )
                ui.append_option(option)

    view.add_item(ui)
    await interaction.response.send_message(content='Choose an address',view=view)

    # Reaction for a chosen address
    async def address_callback(interaction):
        await interaction.response.edit_message(content=f'Chosen address: {ui.values[0]}')

    ui.callback = address_callback


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
    
    # The map generation could take more than 3 secconds (which invalidates the discord token for this interaction)
    # A first response is sent to prevent this
    await interaction.response.send_message("Please wait... Generating the map.")

    map_html_file = routes.get_html_map(latitude1, longitude1, latitude2, longitude2)
    map_png_file = routes.get_png_map_preview(latitude1, longitude1, latitude2, longitude2)

    discord_html_file = discord.File(map_html_file, filename='map.html')
    discord_png_file = discord.File(map_png_file, filename='map.png')

    await interaction.edit_original_response(content=f'Here is the route from {latitude1}, {longitude1} to {latitude2}, {longitude2}. Open the HTML file in your browser to see the route.', attachments=[discord_png_file, discord_html_file])


client.run(config.DC_TOKEN)
