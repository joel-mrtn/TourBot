import config

import io
from PIL import Image
import openrouteservice
import folium

lon1 = 8.673921
lat1 = 50.110121

lon2 = 8.650596
lat2 = 49.878321

# Set up the OpenRouteService client and request a route between two coordinates
client = openrouteservice.Client(key=config.ORS_KEY)
coords = ((lon1, lat1), (lon2, lat2))
routes = client.directions(coordinates=coords, profile='cycling-regular', format='geojson')

# Create a map centered on the starting point and add the generated route
map = folium.Map(location=[lat1, lon1], zoom_start=13, zoom_control=False)
route_layer = folium.GeoJson(routes, name='route')
route_layer.add_to(map)

# Add markers for the start and end points
folium.Marker([lat1, lon1], popup='Start').add_to(map)
folium.Marker([lat2, lon2], popup='End').add_to(map)

# Generate an image
img_data = map._to_png(1)
img = Image.open(io.BytesIO(img_data))
img.save('image.png')

# Generate a map
map.save('route_map.html')
