from config import ORS_KEY
from typing import List

import io
import openrouteservice
import folium


class Coordinates:
    def __init__(self, latitude: float, longitude: float, elevation: float = None):
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation


class RouteStep:
    def __init__(self, distance: float, duration: float, instruction: str, way_points: List[Coordinates]):
        self.distance = distance
        self.duration = duration
        self.instruction = instruction
        self.way_points = way_points


class RouteSegment:
    def __init__(self, distance: float, duration: float, ascent: float, descent: float, route_steps: List[RouteStep]):
        self.distance = distance
        self.duration = duration
        self.ascent = ascent
        self.descent = descent
        self.route_steps = route_steps


class Route:
    def __init__(self, route_points: List[Coordinates]):
        self.ors_client = openrouteservice.Client(key=ORS_KEY)
        self.route_points = route_points

        # API call
        self.geojson = self.ors_client.directions(
            coordinates=[(coords.longitude, coords.latitude) for coords in self.route_points],
            elevation=True,
            profile='cycling-regular',
            format='geojson'
        )

        geojson_properties = self.geojson['features'][0]['properties']
        geojson_coordinates = self.geojson['features'][0]['geometry']['coordinates']

        self.distance: float = geojson_properties['summary']['distance']
        self.duration: float = geojson_properties['summary']['duration']
        self.ascent: float = geojson_properties['ascent']
        self.descent: float = geojson_properties['descent']

        self.segments = [
            RouteSegment(**{
                'distance': segment['distance'],
                'duration': segment['duration'],
                'ascent': segment['ascent'],
                'descent': segment['descent'],
                'route_steps': [
                    RouteStep(**{
                        'distance': step['distance'],
                        'duration': step['duration'],
                        'instruction': step['instruction'],
                        'way_points': [
                            Coordinates(**{
                                'latitude': geojson_coordinates[i][1],
                                'longitude': geojson_coordinates[i][0],
                                'elevation': geojson_coordinates[i][2],
                            }) for i in range(step['way_points'][0], step['way_points'][1])
                        ]
                    }) for step in segment['steps']
                ]
            }) for segment in geojson_properties['segments']
        ]

    def get_html_map(self):
        map = folium.Map(zoom_start=13, zoom_control=True)
        route_layer = folium.GeoJson(self.geojson, name='route')
        route_layer.add_to(map)
        map.fit_bounds(route_layer.get_bounds())

        start_icon = folium.Icon(color='green', icon='glyphicon-home')
        waypoint_icon = folium.Icon(color='blue', icon='star')
        end_icon = folium.Icon(color='red', icon='glyphicon-flag')

        folium.Marker([self.route_points[0].latitude, self.route_points[0].longitude], popup='Start', icon=start_icon).add_to(map)
        folium.Marker([self.route_points[1].latitude, self.route_points[1].longitude], popup='point', icon=waypoint_icon).add_to(map)
        folium.Marker([self.route_points[-1].latitude, self.route_points[-1].longitude], popup='End', icon=end_icon).add_to(map)

        html_map = map.get_root().render()
        return io.BytesIO(html_map.encode())

    def get_png_map(self):
        map = folium.Map(zoom_start=13, zoom_control=False)
        route_layer = folium.GeoJson(self.geojson, name='route')
        route_layer.add_to(map)
        map.fit_bounds(route_layer.get_bounds())

        start_icon = folium.Icon(color='green', icon='glyphicon-home')
        waypoint_icon = folium.Icon(color='blue', icon='star')
        end_icon = folium.Icon(color='red', icon='glyphicon-flag')

        folium.Marker([self.route_points[0].latitude, self.route_points[0].longitude], popup='Start', icon=start_icon).add_to(map)
        folium.Marker([self.route_points[1].latitude, self.route_points[1].longitude], popup='point', icon=waypoint_icon).add_to(map)
        folium.Marker([self.route_points[-1].latitude, self.route_points[-1].longitude], popup='End', icon=end_icon).add_to(map)

        img_data = map._to_png(1)
        return io.BytesIO(img_data)


class Address:
    def __init__(self, id: str, label: str, coordinates: Coordinates):
        self.id = id
        self.label = label
        self.coordinates = coordinates


    def conv_addr_to_coords(address: str):
        client = openrouteservice.Client(key=ORS_KEY)
        json_data = client.pelias_search(text=address)
    
        addresses = []
    
        for feature in json_data['features']:
            address = Address(
                id = feature['properties']['id'],
                label = feature['properties']['label'],
                coordinates = Coordinates(feature['geometry']['coordinates'][1], feature['geometry']['coordinates'][0])
            )
            addresses.append(address)
    
        return addresses
