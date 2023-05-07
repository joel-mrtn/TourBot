from config import DC_TOKEN, DC_GUILD
from typing import List
from routes import Address, Coordinates, Route
from discord import app_commands

import discord
import re


selected_start_addr:str
selected_start_desc:str
selected_end_addr:str
selected_end_desc:str


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
async def gen_map(interaction: discord.Integration, start_addr: str, end_addr: str):
    start_coords = Address.conv_addr_to_coords(start_addr)
    end_coords = Address.conv_addr_to_coords(end_addr)

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

    def check_type_address(ui: AddressSelect):
        if re.search('.*end address.*', ui.placeholder):
            return 'end address'
        else:
            return 'start address'
    
    def fill_selectmenu(address_list: List[Address], ui: AddressSelect, view: discord.ui.View):
        for address_obj in address_list:
            option = discord.SelectOption(
                label = address_obj.label,
                description = f'Latitude: {address_obj.coordinates.latitude}, Longitude: {address_obj.coordinates.longitude}'
            )
            ui.append_option(option)
        view.add_item(ui)
        async def address_callback(interaction):
            global selected_end_addr, selected_end_desc, selected_start_addr, selected_start_desc
            await interaction.response.send_message(content=f'Chosen {check_type_address(ui)}: {ui.values[0]}\n{ui.options[0].description}', ephemeral=True)
            if check_type_address(ui) == 'end address':
                selected_end_addr = ui.values[0]
                selected_end_desc = ui.options[0].description
            else:
                selected_start_addr = ui.values[0]
                selected_start_desc = ui.options[0].description
                    
        ui.callback=address_callback

    fill_selectmenu(start_coords, ui_start, view)
    fill_selectmenu(end_coords, ui_end, view)

    def create_gen_button(view: discord.ui.View):
        button = discord.ui.Button(
            custom_id = "gen_map",
            label = "Generate map",
        )

        async def gen_map_callback(interaction):
            await test_map(interaction)

        button.callback = gen_map_callback

        view.add_item(button)
    
    create_gen_button(view)

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


async def test_map(interaction: discord.Integration):    
    # The map generation could take more than 3 secconds (which invalidates the discord token for this interaction)
    # A first response is sent to prevent this
    await interaction.response.send_message("Please wait... Generating the map.")

    start_coords = Coordinates(float(re.findall("Latitude: ([\d.]+)", selected_start_desc)[0]), float(re.findall("Longitude: ([\d.]+)", selected_start_desc)[0]))
    end_coords = Coordinates(float(re.findall("Latitude: ([\d.]+)", selected_end_desc)[0]), float(re.findall("Longitude: ([\d.]+)", selected_end_desc)[0]))

    route = Route(
        coordinates_list=[start_coords, end_coords]
    )

    discord_html_file = discord.File(route.get_html_map(), filename='map.html')
    discord_png_file = discord.File(route.get_png_map(), filename='map.png')

    await interaction.edit_original_response(
        content=f'Here is the route from {selected_start_addr} to {selected_end_addr}. Open the HTML file in your browser to see the route.',
        attachments=[discord_png_file, discord_html_file]
    )


client.run(DC_TOKEN)
