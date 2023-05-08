from routes import Address
from typing import List

import discord

import re


class AddressSelect(discord.ui.Select):
    def __init__(self, position: str) -> None:
        super().__init__(
            placeholder=f"Choose from one of your possible {position} addresses",
            min_values=1,
            max_values=1,
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