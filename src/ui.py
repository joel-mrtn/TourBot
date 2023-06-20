from routes import Address, Route
from typing import List

import discord


# Text Buttons -----------------------------------------------------------------------------------

class TextButtonView(discord.ui.View):
    def __init__(self, ready_button: discord.ui.Button):
        super().__init__(timeout=900)
        self.add_item(ready_button)


class TextButtonViews(discord.ui.View):
    def __init__(self, button1: discord.ui.Button, button2: discord.ui.Button):
        super().__init__(timeout=900)
        self.add_item(button1)
        self.add_item(button2)


class NextFunctionButton(discord.ui.Button):
    def __init__(self, *, custom_id: str, label: str, next_function: callable, interaction_obj):
        super().__init__(custom_id=custom_id, label=label)
        self.next_function = next_function
        self.interaction_obj = interaction_obj

    async def callback(self, interaction: discord.Interaction):
        await self.next_function(interaction, self.interaction_obj)

# First Address Input ----------------------------------------------------------------------------

class FirstAddressInputModal(discord.ui.Modal, title="Enter the start and end address"):
    start_address = discord.ui.TextInput(label='Start address', required=True)
    end_address = discord.ui.TextInput(label='End address', required=True)

    def __init__(self, custom_id: str, next_function: callable, interaction_obj):
        super().__init__(custom_id=custom_id)
        self.next_function = next_function
        self.interaction_obj = interaction_obj
    
    async def on_submit(self, interaction: discord.Interaction):
        self.interaction_obj.start_address_input = self.start_address.value
        self.interaction_obj.end_address_input = self.end_address.value

        await self.next_function(interaction, self.interaction_obj)

class StopAddressInputModal(discord.ui.Modal, title="Enter up to 3 stops"):
    stop1_address = discord.ui.TextInput(label='Stop 1', required=True)
    stop2_address = discord.ui.TextInput(label='Stop 2', required=False)
    stop3_address = discord.ui.TextInput(label='Stop 3', required=False)

    def __init__(self, custom_id: str, next_function: callable, interaction_obj):
        super().__init__(custom_id=custom_id)
        self.next_function = next_function
        self.interaction_obj = interaction_obj
    
    async def on_submit(self, interaction: discord.Interaction):
        self.interaction_obj.stops_address_input.append(self.stop1_address)

        if len(self.stop2_address.value) > 1:
            self.interaction_obj.stops_address_input.append(self.stop2_address)
        if len(self.stop3_address.value) > 1:
            self.interaction_obj.stops_address_input.append(self.stop3_address)

        await self.next_function(interaction, self.interaction_obj)

# General Address Select -------------------------------------------------------------------------

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
                delete_after=5
        )

# First Address Select ---------------------------------------------------------------------------

class FirstAddressSelectButton(discord.ui.Button):
    def __init__(self, *, custom_id: str, label: str, start_select: AddressSelect, end_select: AddressSelect, next_function: callable, interaction_obj):
        super().__init__(custom_id=custom_id, label=label)
        self.start_select = start_select
        self.end_select = end_select
        self.next_function = next_function
        self.interaction_obj = interaction_obj

    async def callback(self, interaction: discord.Interaction):
        self.interaction_obj.start_address = self.start_select.selected_value
        self.interaction_obj.end_address = self.end_select.selected_value

        await self.next_function(interaction, self.interaction_obj)


class FirstAddressSelectView(discord.ui.View):
    def __init__(self, start_select: AddressSelect, end_select: AddressSelect, button: discord.ui.Button):
        super().__init__(timeout=900)
        self.add_item(start_select)
        self.add_item(end_select)
        self.add_item(button)

# Stop Address Select ----------------------------------------------------------------------------

class StopAddressSelectButton(discord.ui.Button):
    def __init__(self, *, custom_id: str, label: str, stop_selects: List[AddressSelect], next_function: callable, interaction_obj):
        super().__init__(custom_id=custom_id, label=label)
        self.stop_selects = stop_selects
        self.next_function = next_function
        self.interaction_obj = interaction_obj

    async def callback(self, interaction: discord.Interaction):
        for stop_select in self.stop_selects:
            self.interaction_obj.stops_address.append(stop_select.selected_value)

        await self.next_function(interaction, self.interaction_obj)

class StopAddressSelectView(discord.ui.View):
    def __init__(self, stop_selects: List[AddressSelect], button: discord.ui.Button):
        super().__init__(timeout=900)
        
        for stop_select in stop_selects:
            self.add_item(stop_select)

        self.add_item(button)

# HTML Route View --------------------------------------------------------------------------------

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
