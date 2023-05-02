from config import DC_TOKEN, DC_GUILD
from routes import Coordinates, Route

import discord
from discord import app_commands

import re


class BotClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    # By specifically naming the guild, the commands are updated faster on the server.
    async def setup_hook(self):
        self.tree.copy_global_to(guild=DC_GUILD)
        await self.tree.sync(guild=DC_GUILD)


intents = discord.Intents.default()
client = BotClient(intents=intents)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.tree.command(description='Get a nice greeting from the bot')
async def hello(interaction: discord.Integration):
    await interaction.response.send_message(content=f'Hey {interaction.user.mention}! Nice to see you.', ephemeral=True)


@client.tree.command(description='Choose addresses for the start and end')
async def start_and_end(interaction: discord.Integration, start_addr: str, end_addr: str):
    start_coords = routes.conv_addr_to_coords(start_addr)
    end_coords = routes.conv_addr_to_coords(end_addr)

    view = discord.ui.View()
    
    class AddressSelect(discord.ui.Select):
        def __init__(self, position: str) -> None:
            super().__init__(
                placeholder = f'Choose from one of your possible {position} addresses',
                min_values = 1,
                max_values = 1,
            )

    ui_start = AddressSelect('start')
    ui_end = AddressSelect('end')

    def check_type_address(ui):
        if re.search('.*end address.*', ui.placeholder):
            return 'end address'
        else:
            return 'start address'
    
    def fill_selectmenu(point_coords, ui, view):
        for coordinates in point_coords:
            option = discord.SelectOption(
                label = coordinates.label,
                description = f'Latitude: {coordinates.latitude}, Longtitude: {coordinates.longtitude}'
            )
            ui.append_option(option)
        view.add_item(ui)
        async def address_callback(interaction):
            await interaction.response.send_message(content=f'Chosen {check_type_address(ui)}: {ui.values[0]}\n{ui.options[0].description}', ephemeral=True)
        
        ui.callback=address_callback
    
    fill_selectmenu(start_coords, ui_start, view)
    fill_selectmenu(end_coords, ui_end, view)

    await interaction.response.send_message(content='Choose your preferred addresses', view=view)


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

    route = Route(
        coordinates_list=[Coordinates(latitude1, longitude1), Coordinates(latitude2, longitude2)]
    )

    discord_html_file = discord.File(route.get_html_map(), filename='map.html')
    discord_png_file = discord.File(route.get_png_map(), filename='map.png')

    await interaction.edit_original_response(
        content=f'Here is the route from {latitude1}, {longitude1} to {latitude2}, {longitude2}. Open the HTML file in your browser to see the route.',
        attachments=[discord_png_file, discord_html_file]
    )


client.run(DC_TOKEN)
