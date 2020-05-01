# Initial imports
import os
import re
import dash
import folium
import overpy
import random
import base64
import geocoder
import numpy as np
import pandas as pd
import openrouteservice

import dash_core_components as dcc
import dash_html_components as html
from openrouteservice import client
from dash.dependencies import Input, Output, State
from shapely.geometry import Polygon, Point, mapping, MultiPolygon

import dash_bootstrap_components as dbc
import pathlib
# Dash app properties
# To display the wheel next to the cursor while loading
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'https://codepen.io/chriddyp/pen/brPBPO.css',
                        dbc.themes.SKETCHY]
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}],
    external_stylesheets=external_stylesheets
)

APP_PATH = "C:\\Users\\daphn\\Documents\\EUvsVirus"

server = app.server

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
# Process
# Initial display: world map + input boxes
# Implement: user selection on the world map (if add_start is none then select point is start else if add_start is not none then select point is add_end)
# Compute route on inputs
# Update display

# My input
class my_input():
    def __init__(self):
        self.map_background = "stamenwatercolor"

    def initial_map(self):
        initial_map = folium.Map(tiles=self.map_background,
                                 location=([0, 0]),
                                 zoom_start=1)
        initial_map.add_child(folium.LatLngPopup())
        return initial_map._repr_html_()

def add_score(dang_list, results):
    nodes = [node for node in results.nodes]

    for node in nodes:
        try:
            if 'amenity' in node.tags:
                #I create a new key in the tags dictionary, called dangerscore, whose value correspond to the score in the
                #csv file for the type of amenity or shop the node is.
                node.tags['dangerscore'] = dang_list.loc[dang_list['tags'] == node.tags['amenity']]['dangerscore'].item()
            else:
                node.tags['dangerscore'] = dang_list.loc[dang_list['tags'] == node.tags['shop']]['dangerscore'].item()
        except:
            node.tags['dangerscore'] = 0

    return nodes



# App
app.layout = html.Div(
    id="root",
    children=[
        dbc.Row(
            dbc.Col(
                html.Div(id="header", children=
                [html.H1(children="AdventuRoad",
                         style={'textAlign': 'left', 'color': "#F4C065",
                                'font-size': '60px', 'margin':'10px'}),
                html.P(id="description", children= """
                An application to compute the safest walking way to take 
                in the city during the corona virus crisis while having fun.""",
                    style={'textAlign': 'left', 'color': "white",
                           'font-size': '24px', 'margin':'10px'}),
                html.Br()
                 ],
                     ), width={"size": 12}),
            className="h-25", form=True, justify="start"
        ),

        dbc.Row(
            [
                dbc.Col(html.Div(id="left-column", children=
                [
                    html.Div(id="input-start",children=
                    [
                        html.Br(),
                        html.P(id="input-start-text",children="Type your start address",
                               style={'color': "white", 'font-size': '18px',
                                      'margin':'10px'}),
                        dcc.Input(id="add_start", type="text",placeholder=""),
                    ], style={'margin-bottom': '10px', 'textAlign':'center',
                             'width': '220px', 'margin':'auto'}
                             ),
                    html.Div(id="input-end",children=
                    [
                        html.Br(),
                        html.P(id="input-end-text",children="Type your arrival address",
                               style={'color': "white", 'font-size': '18px',
                                      'margin-left': '30px'}),
                        dcc.Input(id="add_end", type="text",placeholder=""),
                        html.Br()
                    ], style={'margin-bottom': '10px', 'textAlign':'center',
                             'width': '220px', 'margin':'auto'}
                             ),

                    html.Div(id="input-level",children=
                    [
                        html.Br(),
                        html.P(id="level-text",children="What level of safety?",
                               style={'color': "white", 'font-size': '18px',
                                      'margin-left': '30px'}),
                        dcc.Dropdown(id="fearlevel", options=
                        [
                            {'label': '1 - Avoids high risk areas', 'value': 3},
                            {'label': '2 - Avoids high  and medium risk areas', 'value': 2},
                            {'label': '3 - Avoids all public places', 'value': 1},
                            {'label': '-SHOW- No restrictions', 'value': 4}
                        ], value=3
                                     ),
                        html.Br(),
                    ], style={'margin-left': '30px', 'textAlign':'center',
                              'width': '220px', 'margin':'auto'}
                             ),
                    html.Div(id="input-button", children=
                    [
                        html.Br(),
                        html.Button('Submit', id='button', style={"background-color": "white"}),
                        html.Br(),
                    ], style={'margin-bottom': '10px', 'textAlign':'center',
                             'width': '220px', 'margin':'auto'}
                             )
                    ]), width={"size": 3, "order": 1, "offset": 0.7}), # end of left-column

                dbc.Col(html.Div(
                     id="display_map",
                     children=[
                         html.Br(),
                         html.P(id="map-title", children="Directions",
                                style={'textAlign': 'center', 'color': "white",
                                       'font-size': '18px'}),
                         html.Iframe(id='map',
                                     srcDoc=my_input().initial_map(),
                                     style={'border': 'none', 'width': '100%', 'height': 500}),
                         html.Br(),
                         html.P(id="map-greetings", children=" Have a safe trip :)",
                                style={'textAlign': 'center', 'color': "#F4C065",
                                       'font-size': '18px'}),
                     ]
                 ), width={"size": 7, "order": 'last', "offset": 1},
                ) # end right column
             ], className="h-75", form=True, justify="start"),
        dbc.Row(
            [
            dbc.Col(
                html.Div(id="more-information", children=
                [html.P(id="thanks", children="Thank you for using our app and special thanks to Open Street Map and related projects.",
                        style={'textAlign': 'left', 'color': "white",
                               'font-size': '18px', 'margin-left': '30px'}),],),
            width={"order": 1, "offset": 0}),
            dbc.Col(
                html.A("Link to the Devpost", href="https://devpost.com/software/eurocovidfighters-u19r03",
                       style={'color': "white",'font-size': '18px'}),
                width={"order": 2, "offset": 1}
            ),
            dbc.Col(
                    html.A("Link to the GitHub", href="https://github.com/TutuFruit/hackathon_exchange",
                           style={'color': "white", 'font-size': '18px'}),
                    width={"order": 3, "offset": 1}
                ),

            # dbc.Col(
            #     html.Img(src='data:image/png;base64,{}'.format(encoded_image))
            # )
            ],
        ),
    ], style={"background-color": "#081746",
              'fontColor': 'white'}) # ECB blue? '#13226F'


@app.callback(
    dash.dependencies.Output("map", "srcDoc"),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State("add_start", "value"),
     dash.dependencies.State("add_end", "value"),
     dash.dependencies.State("fearlevel", "value")],
)


def update_map(n_clicks, add_start, add_end, fearlevel):
    if any([add_end is None, add_start is None]):
        return my_input().initial_map()
    else:
        # 1. Reverse-geocoding (i.e finding geo coordinates from addresses)
        # Also handles lat/long
        if re.match(r"(\d{1,2}\.\d{1,12})", add_start) is None:
            geocod_start = geocoder.osm(add_start)
            start_lat = geocod_start.lat
            start_lng = geocod_start.lng
        else:
            start_lat = float(add_start.split(" ")[0])
            start_lng = float(add_start.split(" ")[1])

        if re.match(r"(\d{1,2}\.\d{1,12})", add_end) is None:
            geocod_end = geocoder.osm(add_end)
            end_lat = geocod_end.lat
            end_lng = geocod_end.lng

        else:
            end_lat = float(add_end.split(" ")[0])
            end_lng = float(add_end.split(" ")[1])

        # 2. Compute the box to look for POI around
        box = [
            (start_lat, end_lng),
            (end_lat, end_lng),
            (end_lat, start_lng),
            (start_lat, start_lng)
        ]

        poly_box = Polygon(box)
        poly_box = poly_box.buffer(0.005).simplify(0.05)

        # 3. Retrieve the POI in the area
        try:
            api = overpy.Overpass()
            result_nodes = api.query("(node['shop']{0};node['amenity']{0};);out;".format(str(poly_box.exterior.bounds)))
            result_areas = api.query("(area['shop']{0};area['amenity']{0};);out;".format(str(poly_box.exterior.bounds)))
        except overpy.exception.OverpassGatewayTimeout:
            return """<h1 style="color:white;">TOO MANY ELEMENTS ON THE WAY!</h1>"""


        # 4. Filter the POI in the box to keep only the points to be avoid
        # Loading the csv for the danger levels
        dang_list = pd.read_csv(os.path.join(APP_PATH, os.path.join("assets", "DangerScoreList.csv")),
                                delimiter=',')
        # Score the POI in the area
        nodes_score = add_score(dang_list, result_nodes)  # nodes_score is a list of overpy objects, with lat and lon info,

        dangers_poly = []  # sites_poly
        # I define dangerous a POI with score greater than 1
        for node in nodes_score:
            try:
                if node.tags['dangerscore'] >= fearlevel:
                    lat = node.lat
                    lon = node.lon

                    dangers_poly_coords = Point(lon, lat).buffer(0.0005).simplify(0.05)
                    dangers_poly.append(dangers_poly_coords)
            except:
                pass

        danger_buffer_poly = []  # site_buffer_poly, which is the input for the avoid polygon option
        for danger_poly in dangers_poly:
            poly = Polygon(danger_poly)
            danger_buffer_poly.append(poly)

        # 5.Request the route
        route_request = {'coordinates': [[start_lng, start_lat], [end_lng, end_lat]],
                         # Careful long then lat and not lat then long
                         'format_out': 'geojson',
                         'profile': 'foot-walking',
                         'preference': 'shortest',
                         'instructions': False,
                         'options': {'avoid_polygons': mapping(MultiPolygon(danger_buffer_poly))}}

        api_key = '5b3ce3597851110001cf6248d14c60f017174b11b170ff63fdbf48b3'
        clnt = client.Client(key=api_key)

        try:
            route_directions = clnt.directions(**route_request)

        except openrouteservice.exceptions.ApiError:
            return """<h1 style="color:white;">MISSION TOO DANGEROUS!</h1>"""



        # 6.Display the route and the dangerous points
        # Create the base map
        map = folium.Map(tiles=my_input().map_background, location=([start_lat, start_lng]), zoom_start=14)  # Create map

        # Beginning and end markers
        folium.Marker([start_lat, start_lng], popup='<i>Start:</i> <b>{}</b>'.format(add_start),
                      icon=folium.Icon(color="green", icon="street-view", prefix="fa")).add_to(map)

        folium.Marker([end_lat, end_lng], popup='<i>End:</i> <b>{}</b>'.format(add_end),
                      icon=folium.Icon(icon="fa-check-square", prefix="fa")).add_to(map)

        # Plotting the route
        style_route = {'fillColor': 'green', 'color': 'green', "weight": 5}
        folium.features.GeoJson(data=route_directions,
                                name='Route',
                                style_function=lambda x: style_route,
                                overlay=True).add_to(map)

        # Plotting the dangerous areas
        # style_danger = {'fillColor': '#f88494', 'color': '#ff334f'}
        # folium.features.GeoJson(data=mapping(MultiPolygon(danger_buffer_poly)),
        #                         style_function=lambda x: style_danger,
        #                         overlay=True).add_to(map)

        # Adding icons (I haven't found dragons actually available :( )
        for node in nodes_score:
            if node.tags['dangerscore'] >= fearlevel:
                # Retrieve the type of place
                if "amenity" in node.tags:
                    type_place = node.tags["amenity"]
                else:
                    type_place = node.tags["shop"]

                # Create the markers
                if node.tags['dangerscore'] == 3:
                    folium.Marker([node.lat, node.lon], popup='<b>{}</b>'.format(type_place),
                                  icon=folium.features.CustomIcon(
                                      os.path.join(APP_PATH, os.path.join("assets", "skull.png")),
                                      icon_size=(30, 30)
                                  )).add_to(map)

                elif node.tags['dangerscore'] == 2:
                    folium.Marker([node.lat, node.lon], popup='<b>{}</b>'.format(type_place),
                                  icon=folium.features.CustomIcon(
                                      random.choice(
                                          [os.path.join(APP_PATH, os.path.join("assets", "dragon1_purple.png")),
                                           os.path.join(APP_PATH, os.path.join("assets", "spat.png")),
                                           os.path.join(APP_PATH, os.path.join("assets", "dragon2.png"))]),
                                      icon_size=(30, 30)
                                  )).add_to(map)

                else:
                    folium.Marker([node.lat, node.lon], popup='<b>{}</b>'.format(type_place),
                                  icon= folium.features.CustomIcon(
                                      os.path.join(APP_PATH, os.path.join("assets", "ghost.png")),
                                      icon_size=(30, 30)
                                  )).add_to(map)

        # Create legend
        # legend_html = """
        # <div style ="position: fixed; bottom: 50px; left: 50px; width: 200px;
        # height: 150px;z-index: 9999; font-size: 12px;"> <h5 style="font-family:verdana;">Legend</h5>
        # <div class="figure"> <img src="{0}"; width="25"; height="25"">&nbsp;High risk</div><br>
        # <div class="figure"> <img src="{1}"; width="25"; height="25">&nbsp;Medium risk</div><br>
        # <div class="figure"> <img src="{2}"; width="25"; height="25">&nbsp;Low</div><br>
        # </div>
        # """.format(os.path.join(APP_PATH, os.path.join("assets", "skull.png")),
        #            os.path.join(APP_PATH, os.path.join("assets", "dragon1_purple.png")),
        #            os.path.join(APP_PATH, os.path.join("assets", "ghost.png")))
        #
        # map.get_root().html.add_child(folium.Element(legend_html))

        # Add the lat long pop-up on click
        map.add_child(folium.LatLngPopup())

        return map._repr_html_()



if __name__ == "__main__":
    app.run_server(debug=True)

