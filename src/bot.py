from config import DC_TOKEN, DC_GUILD
from routes import Coordinates, Route
from discord import app_commands

import routes
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


class route_buttons_view(discord.ui.View):
    def __init__(self, route: Route):
        super().__init__(timeout=900)
        self.route = route

    @discord.ui.button(custom_id='route_html', emoji='\U0001F5FA', label='Interactive map')
    async def route_html(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            content="Please wait... Generating the map.",
            ephemeral=True
        )

        await interaction.edit_original_response(
            content=f'Download the HTML file below and open it in your web browser to see the map.',
            attachments=[discord.File(self.route.get_html_map(), filename='map.html')]
        )


intents = discord.Intents.default()
client = BotClient(intents=intents)


@client.tree.command(description='Get a nice greeting from the bot')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(content=f'Hey {interaction.user.mention}! Nice to see you.', ephemeral=True)


@client.tree.command(description='Choose addresses for the start and end')
async def start_and_end(interaction: discord.Interaction, start_addr: str, end_addr: str):
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
async def map(interaction: discord.Interaction, latitude1: float, longitude1: float, latitude2: float, longitude2: float):
    if latitude1 < -90 or latitude1 > 90 or latitude2 < -90 or latitude2 > 90:
        await interaction.response.send_message("Invalid latitude value. Latitude must be between -90 and 90 degrees.", ephemeral=True)
        return

    if longitude1 < -180 or longitude1 > 180 or longitude2 < -180 or longitude2 > 180:
        await interaction.response.send_message("Invalid longitude value. Longitude must be between -180 and 180 degrees.", ephemeral=True)
        return
    
    # The map generation could take more than 3 secconds (which invalidates the discord token for this interaction)
    # A first response is sent to prevent this
    await interaction.response.send_message("Please wait... Generating the route.")

    route = Route(
        route_points=[Coordinates(latitude1, longitude1), Coordinates(latitude2, longitude2)]
    )

    overview_embed = discord.Embed(
        title='Your route',
        description=f'Here is the route from {latitude1}, {longitude1} to {latitude2}, {longitude2}. Open the HTML file in your browser to see the route.'
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
        view=route_buttons_view(route)
    )


client.run(DC_TOKEN)
