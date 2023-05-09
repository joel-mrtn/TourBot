from config import DC_TOKEN, DC_GUILD
from typing import List
from routes import Address, Coordinates, Route
from discord import app_commands
from ui import AddressSelect, Elements, RouteButtonsView, AddressSelectView, AddressSelectButton

import discord
import re


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


@client.tree.command(description='Get a nice greeting from the bot')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(content=f'Hey {interaction.user.mention}! Nice to see you.', ephemeral=True)


@client.tree.command(description="Select test command")
async def select_test(interaction: discord.Interaction):
    adress_list = Address.conv_addr_to_coords('Rheingaustraße 7')

    start_select = AddressSelect('start', adress_list)
    button = AddressSelectButton(
        custom_id='gen_map',
        label='Generate map',
        start_select=start_select
    )
    view = AddressSelectView(start_select, button=button)

    await interaction.response.send_message(view=view)


@client.tree.command(description='Choose addresses for the start and end')
async def gen_map(interaction: discord.Interaction, start_addr: str, end_addr: str):
    start_coords = Address.conv_addr_to_coords(start_addr)
    end_coords = Address.conv_addr_to_coords(end_addr)

    view = discord.ui.View()

    ui_start = AddressSelect('start')
    ui_end = AddressSelect('end')

    elements = Elements()

    elements.fill_selectmenu(start_coords, ui_start, view)
    elements.fill_selectmenu(end_coords, ui_end, view)

    def create_gen_button(view: discord.ui.View):
        button = discord.ui.Button(
            custom_id = "gen_map",
            label = "Generate map",
        )

        async def gen_map_callback(interaction):
            await test_map(interaction, elements)

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
    latitude3='The latitude of the waypoint coordinate',
    longitude3='The longitude of the waypoint coordinate'
)
async def map(interaction: discord.Interaction, latitude1: float, longitude1: float, latitude2: float, longitude2: float, latitude3: float, longitude3: float):
    if latitude1 < -90 or latitude1 > 90 or latitude2 < -90 or latitude2 > 90 or latitude3 < -90 or latitude3 > 90:
        await interaction.response.send_message("Invalid latitude value. Latitude must be between -90 and 90 degrees.", ephemeral=True)
        return

    if longitude1 < -180 or longitude1 > 180 or longitude2 < -180 or longitude2 > 180 or longitude3 < -180 or longitude3 > 180:
        await interaction.response.send_message("Invalid longitude value. Longitude must be between -180 and 180 degrees.", ephemeral=True)
        return
    
    # The map generation could take more than 3 secconds (which invalidates the discord token for this interaction)
    # A first response is sent to prevent this
    await interaction.response.send_message("Please wait... Generating the route.")

    route = Route(
        route_points=[Coordinates(latitude1, longitude1), Coordinates(latitude2, longitude2), Coordinates(latitude3, longitude3)]
    )

    overview_embed = discord.Embed(
        title='Your route',
        description=f'Here is the route from {latitude1}, {longitude1} to {latitude3}, {longitude3} via {latitude2}, {longitude3}. Open the HTML file in your browser to see the route.'
    )
    overview_embed.set_image(url='attachment://map.png')
    overview_embed.set_footer(text=f'The interactive map generation will only be available the first 15 minutes and 15 minutes after the first generation.')

    details_embed = discord.Embed(
        title='Detailed info',
        description='This is an overview of the route information (TBD).'
    )

    await interaction.edit_original_response(
        content=None,
        embeds=[overview_embed, details_embed],
        attachments=[discord.File(route.get_png_map(), filename='map.png')],
        view=RouteButtonsView(route)
    )


async def test_map(interaction: discord.Integration, elements: Elements):    
    # The map generation could take more than 3 secconds (which invalidates the discord token for this interaction)
    # A first response is sent to prevent this
    await interaction.response.send_message("Please wait... Generating the map.")

    start_coords = Coordinates(float(re.findall("Latitude: ([\d.]+)", elements.selected_start_desc)[0]), float(re.findall("Longitude: ([\d.]+)", elements.selected_start_desc)[0]))
    end_coords = Coordinates(float(re.findall("Latitude: ([\d.]+)", elements.selected_end_desc)[0]), float(re.findall("Longitude: ([\d.]+)", elements.selected_end_desc)[0]))

    route = Route(
        route_points=[start_coords, end_coords]
    )

    discord_html_file = discord.File(route.get_html_map(), filename='map.html')
    discord_png_file = discord.File(route.get_png_map(), filename='map.png')

    await interaction.edit_original_response(
        content=f'Here is the route from {elements.selected_start_addr} to {elements.selected_end_addr}. Open the HTML file in your browser to see the route.',
        attachments=[discord_png_file, discord_html_file]
    )


client.run(DC_TOKEN)
