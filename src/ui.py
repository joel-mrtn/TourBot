from discord.emoji import Emoji
from discord.enums import ButtonStyle
from discord.interactions import Interaction
from discord.partial_emoji import PartialEmoji
from routes import Address, Route, Coordinates
from typing import Any, List, Optional, Union

import discord
import re


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
    def __init__(self, *, custom_id: str, label: str, start_select: AddressSelect):
        super().__init__(custom_id=custom_id, label=label)
        self.start_select = start_select

    async def callback(self, interaction: discord.Interaction):
        address = self.start_select.selected_value

        await interaction.response.send_message(content=f'{address.label}')


class AddressSelectView(discord.ui.View):
    def __init__(self, select_menu: AddressSelect, button: discord.ui.Button):
        super().__init__(timeout=900)
        self.add_item(select_menu)
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


class Elements:
    def __init__(self) -> None:
        self.selected_start_addr = ""
        self.selected_start_desc = ""
        self.selected_end_addr = ""
        self.selected_end_desc = ""
    
    def add_start(self, label: str, desc: str):
        self.selected_start_addr = label
        self.selected_start_desc = desc
    
    def add_end(self, label: str, desc: str):
        self.selected_end_addr = label
        self.selected_end_desc = desc

    def check_type_address(ui: AddressSelect):
        if re.search(".*end address.*", ui.placeholder):
            return "end address"
        else:
            return "start address"


    def fill_selectmenu(self, address_list: List[Address], ui: AddressSelect, view: discord.ui.View):
        for address_obj in address_list:
            option = discord.SelectOption(
                label=address_obj.label,
                description=f"Latitude: {address_obj.coordinates.latitude}, Longitude: {address_obj.coordinates.longitude}",
            )
            ui.append_option(option)
        view.add_item(ui)

        async def address_callback(interaction):
            #global selected_end_addr, selected_end_desc, selected_start_addr, selected_start_desc
            await interaction.response.send_message(
                content=f"Chosen {Elements.check_type_address(ui)}: {ui.values[0]}\n{ui.options[0].description}",
                ephemeral=True,
            )
            if Elements.check_type_address(ui) == "end address":
                self.add_end(ui.values[0], ui.options[0].description)
            else:
                self.add_start(ui.values[0], ui.options[0].description)

        ui.callback = address_callback

        return self