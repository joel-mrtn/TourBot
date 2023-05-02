from config import ORS_KEY
from typing import List

import io
import openrouteservice
import folium


class Coordinates:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude


class Route:
    def __init__(self, coordinates_list: List[Coordinates]):
        self.ors_client = openrouteservice.Client(key=ORS_KEY)
        self.coordinates_list = coordinates_list

        self.route = self.ors_client.directions(
            coordinates=[(coords.longitude, coords.latitude) for coords in self.coordinates_list],
            profile='cycling-regular',
            format='geojson'
        )

    def get_html_map(self):
        map = folium.Map(zoom_start=13, zoom_control=True)
        route_layer = folium.GeoJson(self.route, name='route')
        route_layer.add_to(map)
        map.fit_bounds(route_layer.get_bounds())

        start_icon = folium.Icon(color='green', icon='glyphicon-home')
        end_icon = folium.Icon(color='red', icon='glyphicon-flag')

        folium.Marker([self.coordinates_list[0].latitude, self.coordinates_list[0].longitude], popup='Start', icon=start_icon).add_to(map)
        folium.Marker([self.coordinates_list[-1].latitude, self.coordinates_list[-1].longitude], popup='End', icon=end_icon).add_to(map)

        html_map = map.get_root().render()
        return io.BytesIO(html_map.encode())

    def get_png_map(self):
        map = folium.Map(zoom_start=13, zoom_control=False)
        route_layer = folium.GeoJson(self.route, name='route')
        route_layer.add_to(map)
        map.fit_bounds(route_layer.get_bounds())

        start_icon = folium.Icon(color='green', icon='glyphicon-home')
        end_icon = folium.Icon(color='red', icon='glyphicon-flag')

        folium.Marker([self.coordinates_list[0].latitude, self.coordinates_list[0].longitude], popup='Start', icon=start_icon).add_to(map)
        folium.Marker([self.coordinates_list[-1].latitude, self.coordinates_list[-1].longitude], popup='End', icon=end_icon).add_to(map)

        img_data = map._to_png(1)
        return io.BytesIO(img_data)


class Address:
    def __init__(self, id, label, latitude, longtitude):
        self.id = id
        self.label = label
        self.latitude = latitude
        self.longtitude = longtitude


def conv_addr_to_coords(address: str):
    client = openrouteservice.Client(key=config.ORS_KEY)
    json_data = client.pelias_search(text=address)
    
    addresses = []
    
    for feature in json_data['features']:
        address = Address(
            id = feature['properties']['id'],
            label = feature['properties']['label'],
            latitude = feature['geometry']['coordinates'][1],
            longtitude = feature['geometry']['coordinates'][0]
        )
        addresses.append(address)
    
    return addresses