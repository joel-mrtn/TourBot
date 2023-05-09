from config import DC_TOKEN, DC_GUILD
from routes import Address, Coordinates, Route
from discord import app_commands
from ui import AddressSelect, RouteButtonsView, AddressSelectView, AddressSelectButton

import discord


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


@client.tree.command(description='Choose addresses for the start and end')
async def gen_map(interaction: discord.Interaction, start_addr: str, end_addr: str):
    start_address_list = Address.get_addres_list_from_str(start_addr)
    end_address_list = Address.get_addres_list_from_str(end_addr)

    start_select = AddressSelect(position_text='start', address_list=start_address_list)
    end_select = AddressSelect(position_text='start', address_list=end_address_list)

    button = AddressSelectButton(
        custom_id='gen_map',
        label='Generate map',
        start_select=start_select,
        end_select=end_select
    )

    view = AddressSelectView(
        start_select=start_select,
        end_select=end_select,
        button=button
    )

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


client.run(DC_TOKEN)
