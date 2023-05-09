from routes import Address, Route
from typing import List

import discord


class AddressSelect(discord.ui.Select):
    def __init__(self, position_text: str, address_list: List[Address]):
        super().__init__(
            placeholder=f"Choose from one of your possible {position_text} addresses",
            min_values=1,
            max_values=1,
        )
        self.address_list = address_list

        for address in self.address_list:
            self.append_option(discord.SelectOption(
                label=address.label,
                description=f"Latitude: {address.coordinates.latitude}, Longitude: {address.coordinates.longitude}",
            ))

    async def callback(self, interaction: discord.Interaction):
        address = next(
            address for address in self.address_list if address.label == self.values[0]
        )

        self.selected_value = address

        await interaction.response.send_message(
                content=f"Chosen {address.label}",
                ephemeral=True,
        )


class AddressSelectButton(discord.ui.Button):
    def __init__(self, *, custom_id: str, label: str, start_select: AddressSelect, end_select: AddressSelect):
        super().__init__(custom_id=custom_id, label=label)
        self.start_select = start_select
        self.end_select = end_select

    async def callback(self, interaction: discord.Interaction):
        start_address = self.start_select.selected_value
        end_address = self.end_select.selected_value

        await test_map(
            interaction=interaction,
            start_address=start_address,
            end_address=end_address
        )


class AddressSelectView(discord.ui.View):
    def __init__(self, start_select: AddressSelect, end_select: AddressSelect, button: discord.ui.Button):
        super().__init__(timeout=900)
        self.add_item(start_select)
        self.add_item(end_select)
        self.add_item(button)


class RouteButtonsView(discord.ui.View):
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


async def test_map(interaction: discord.Interaction, start_address: Address, end_address: Address):    
    # The map generation could take more than 3 secconds (which invalidates the discord token for this interaction)
    # A first response is sent to prevent this
    await interaction.response.send_message("Please wait... Generating the map.")

    route = Route(
        route_points=[start_address.coordinates, end_address.coordinates]
    )

    discord_html_file = discord.File(route.get_html_map(), filename='map.html')
    discord_png_file = discord.File(route.get_png_map(), filename='map.png')

    await interaction.edit_original_response(
        content=f'Here is the route from {start_address.label} to {end_address.label}. Open the HTML file in your browser to see the route.',
        attachments=[discord_png_file, discord_html_file]
    )
