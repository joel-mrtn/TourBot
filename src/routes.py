import config

import io
import openrouteservice
import folium


def create_map(lat1: float, lon1: float, lat2: float, lon2: float):
    client = openrouteservice.Client(key=config.ORS_KEY)
    coords = ((lon1, lat1), (lon2, lat2))
    routes = client.directions(coordinates=coords, profile='cycling-regular', format='geojson')

    map = folium.Map(location=[lat1, lon1], zoom_start=13, zoom_control=True)
    route_layer = folium.GeoJson(routes, name='route')
    route_layer.add_to(map)
    map.fit_bounds(route_layer.get_bounds())

    start_icon = folium.Icon(color='green', icon='glyphicon-home')
    end_icon = folium.Icon(color='red', icon='glyphicon-flag')

    folium.Marker([lat1, lon1], popup='Start', icon=start_icon).add_to(map)
    folium.Marker([lat2, lon2], popup='End', icon=end_icon).add_to(map)

    return map


def get_html_map(map: folium.Map):
    html_map = map.get_root().render()
    map_html_file = io.BytesIO(html_map.encode())

    return map_html_file

def get_png_map_preview(map: folium.Map):
    img_data = map._to_png(1)
    img = io.BytesIO(img_data)

    return img

def get_html_map_old(lat1: float, lon1: float, lat2: float, lon2: float):
    client = openrouteservice.Client(key=config.ORS_KEY)
    coords = ((lon1, lat1), (lon2, lat2))
    routes = client.directions(coordinates=coords, profile='cycling-regular', format='geojson')

    map = folium.Map(location=[lat1, lon1], zoom_start=13, zoom_control=True)
    route_layer = folium.GeoJson(routes, name='route')
    route_layer.add_to(map)
    map.fit_bounds(route_layer.get_bounds())

    start_icon = folium.Icon(color='green', icon='glyphicon-home')
    end_icon = folium.Icon(color='red', icon='glyphicon-flag')

    folium.Marker([lat1, lon1], popup='Start', icon=start_icon).add_to(map)
    folium.Marker([lat2, lon2], popup='End', icon=end_icon).add_to(map)

    html_map = map.get_root().render()
    map_html_file = io.BytesIO(html_map.encode())
    
    return map_html_file


def get_png_map_preview_old(lat1: float, lon1: float, lat2: float, lon2: float):
    client = openrouteservice.Client(key=config.ORS_KEY)
    coords = ((lon1, lat1), (lon2, lat2))
    routes = client.directions(coordinates=coords, profile='cycling-regular', format='geojson')

    map = folium.Map(location=[lat1, lon1], zoom_start=13, zoom_control=False)
    route_layer = folium.GeoJson(routes, name='route')
    route_layer.add_to(map)
    map.fit_bounds(route_layer.get_bounds())

    start_icon = folium.Icon(color='green', icon='glyphicon-home')
    end_icon = folium.Icon(color='red', icon='glyphicon-flag')

    folium.Marker([lat1, lon1], popup='Start', icon=start_icon).add_to(map)
    folium.Marker([lat2, lon2], popup='End', icon=end_icon).add_to(map)

    img_data = map._to_png(1)
    img = io.BytesIO(img_data)

    return img
