from routes import Address, Route
from typing import List
from math import floor

import discord
import ui

class RouteInteraction:
    start_address_input: str
    end_address_input: str
    stops_address_input: List[str]

    start_address: Address
    end_address: Address
    stops_address: List[Address]

    cycling_profile: str

    def __init__(self):
        self.stops_address_input = []
        self.stops_address = []

# ------------------------------------------------------------------------------------------------

async def ready(interaction: discord.Interaction):
    obj = RouteInteraction()

    await interaction.response.send_message(
        content=f'Hey {interaction.user.mention}! Welcome to the TourBot route generation. This tool will help you to create the route of your choice based on your prefered stops. Press the button below when you feel ready and enjoy!',
        view=ui.TextButtonView(ui.NextFunctionButton(
            custom_id='ready',
            label='I\'m ready!',
            next_function=first_address_input,
            interaction_obj=obj
        ))
    )

async def first_address_input(interaction: discord.Interaction, obj: RouteInteraction):
    await interaction.response.send_message(
        content=f'Very good! First of all, enter the start and end address of your route.',
        view=ui.TextButtonView(ui.NextFunctionButton(
            custom_id='start_first_input',
            label='Start input',
            next_function=first_address,
            interaction_obj=obj
        ))
    )

async def first_address(interaction: discord.Interaction, obj: RouteInteraction):
    modal = ui.FirstAddressInputModal(
        custom_id='first_modal',
        next_function=select_first_addresses,
        interaction_obj=obj
    )

    await interaction.response.send_modal(modal)

async def select_first_addresses(interaction: discord.Interaction, obj: RouteInteraction):
    await interaction.response.send_message(
        content="Please wait..."
    )

    start_address_list = Address.get_addres_list_from_str(obj.start_address_input)
    end_address_list = Address.get_addres_list_from_str(obj.end_address_input)

    start_address_select = ui.AddressSelect(position_text='start', address_list=start_address_list)
    end_address_select = ui.AddressSelect(position_text='end', address_list=end_address_list)

    button = ui.FirstAddressSelectButton(
        custom_id='first_addresses_submit',
        label='Submit',
        start_select=start_address_select,
        end_select=end_address_select,
        next_function=stops_question,
        interaction_obj=obj
    )

    await interaction.edit_original_response(
        content="Select the right address.",
        view=ui.FirstAddressSelectView(
            start_address_select,
            end_address_select,
            button
        )
    )

async def stops_question(interaction: discord.Interaction, obj: RouteInteraction):
    await interaction.response.send_message(
        content=f'Understood! Do you want to add some stops in between your start and end address?',
        view=ui.TextButtonViews(
            button1=ui.NextFunctionButton(
                custom_id='stops_yes',
                label='Yes',
                next_function=stops_address,
                interaction_obj=obj
            ),
            button2=ui.NextFunctionButton(
                custom_id='stops_no',
                label='No',
                next_function=select_profile,
                interaction_obj=obj
            )
        )
    )

async def stops_address_input(interaction: discord.Interaction, obj: RouteInteraction):
    await interaction.response.send_message(
        content=f'Alright! You can enter up to 3 stops.',
        view=ui.TextButtonView(ui.NextFunctionButton(
            custom_id='start_stops_input',
            label='Start input',
            next_function=first_address,
            interaction_obj=obj
        ))
    )

async def stops_address(interaction: discord.Interaction, obj: RouteInteraction):
    modal = ui.StopAddressInputModal(
        custom_id='stops_modal',
        next_function=select_stops_addresses,
        interaction_obj=obj
    )

    await interaction.response.send_modal(modal)

async def select_stops_addresses(interaction: discord.Interaction, obj: RouteInteraction):
    await interaction.response.send_message(content="Please wait...")

    stop_address_selects: List[ui.AddressSelect] = []
    stop_number = 0

    for stop_address_input in obj.stops_address_input:
        stop_number += 1

        stop_address_list = Address.get_addres_list_from_str(stop_address_input)
        stop_address_selects.append(ui.AddressSelect(position_text=f'stop{stop_number}', address_list=stop_address_list))

    button = ui.StopAddressSelectButton(
        custom_id='first_addresses_submit',
        label='Submit',
        stop_selects=stop_address_selects,
        next_function=select_profile,
        interaction_obj=obj
    )

    await interaction.edit_original_response(
        content="Select the right address.",
        view=ui.StopAddressSelectView
            (
                stop_selects=stop_address_selects,
                button=button
            )
    )

async def select_profile(interaction: discord.Interaction, obj: RouteInteraction):
    select = ui.ProfileSelect()

    button = ui.ProfileSelectButton(
        custom_id='profile_select',
        label='Submit',
        select=select,
        next_function=route_output,
        interaction_obj=obj
    )

    await interaction.response.send_message(
        content='Awesome! Lastly choose the option that describes your bycicle best.',
        view=ui.ProfileSelectView(
            select=select,
            button=button
        )
    )

async def route_output(interaction: discord.Interaction, obj: RouteInteraction):
    # The map generation could take more than 3 secconds (which invalidates the discord token for this interaction)
    # A first response is sent to prevent this
    await interaction.response.send_message("Please wait... Generating the map.")

    # Collect route points
    route_points = [obj.start_address]
    if obj.stops_address != None:
        for stop_address in obj.stops_address:
            route_points.append(stop_address)
    route_points.append(obj.end_address)

    # Create route
    route = Route(route_points=route_points, profile=obj.cycling_profile)

    # Prepare output
    overview_embed = discord.Embed(
        title='Your route',
        description=f'Here is the route. Open the HTML file in your browser to see the route.',
        color=discord.Color.green()
    )
    overview_embed.insert_field_at(
        index=0,
        name='Start address',
        value=f'{route.route_points[0].label}\n({route.route_points[0].coordinates.latitude}, {route.route_points[0].coordinates.longitude})',
        inline=False
    )
    overview_embed.insert_field_at(
        index=1,
        name='End address',
        value=f'{route.route_points[-1].label}\n({route.route_points[-1].coordinates.latitude}, {route.route_points[-1].coordinates.longitude})',
        inline=False
    )
    overview_embed.set_image(url='attachment://map.png')
    overview_embed.set_footer(text=f'The interactive map generation will only be available the first 15 minutes and 15 minutes after the first generation.')

    details_embed = discord.Embed(
        title='Detailed info',
        description='This is an overview of the route information.',
        color=discord.Color.blue()
    )
    details_embed.insert_field_at(
        index=0,
        name='Segments',
        value=f'{len(route.segments)}',
        inline=True
    )
    details_embed.insert_field_at(
        index=1,
        name='Total distance',
        value=f'{round(route.distance)} m',
        inline=True
    )
    details_embed.insert_field_at(
        index=2,
        name='Total duration',
        value=f'{floor(route.duration/60/60)}:{floor(route.duration/60%60)} h',
        inline=True
    )
    details_embed.insert_field_at(
        index=3,
        name='Total ascent',
        value=f'{round(route.ascent)} m',
        inline=True
    )
    details_embed.insert_field_at(
        index=4,
        name='Total descent',
        value=f'{round(route.descent)} m',
        inline=True
    )

    all_embeds = [overview_embed, details_embed]

    if len(route.segments) > 1:
        segment_embeds = []
        segment_counter = 0

        for segment in route.segments:
            segment_counter += 1

            segment_embed = discord.Embed(
                title=f'Segment {segment_counter}',
                color=discord.Color.gold()
            )

            segment_embed.insert_field_at(
                index=0,
                name='Total distance',
                value=f'{round(segment.distance)} m',
                inline=True
            )

            segment_embed.insert_field_at(
                index=1,
                name='Total duration',
                value=f'{floor(segment.duration/60/60)}:{floor(segment.duration/60%60)} h',
                inline=True
            )
            segment_embed.insert_field_at(
                index=2,
                name='Total ascent',
                value=f'{round(segment.ascent)} m',
                inline=True
            )
            segment_embed.insert_field_at(
                index=3,
                name='Total descent',
                value=f'{round(segment.descent)} m',
                inline=True
            )

            segment_embeds.append(segment_embed)
            
        all_embeds += segment_embeds

    await interaction.edit_original_response(
        content=None,
        embeds=all_embeds,
        attachments=[discord.File(route.get_png_map(), filename='map.png')],
        view=ui.RouteButtonsView(route)
    )
