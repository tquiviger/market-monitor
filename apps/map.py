# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from utils import csv_reader

simple_jme = csv_reader.get_simple_jme()

for col in simple_jme.columns:
    simple_jme[col] = simple_jme[col].astype(str)

layout = html.Div(children=[
    html.Div([
        dcc.Dropdown(id='map-dropdown',
                     multi=False,
                     value='stunting',
                     options=[
                         {'label': 'Stunting', 'value': 'stunting'},
                         {'label': 'Wasting', 'value': 'wasting'},
                         {'label': 'Severe Wasting', 'value': 'severe_wasting'},
                         {'label': 'Moderate Wasting', 'value': 'moderate_wasting'},
                         {'label': 'Overweight', 'value': 'overweight'},
                         {'label': 'Underweight', 'value': 'underweight'}
                     ])
    ], style={'margin': '15'}),

    html.Div([dcc.Graph(id='map-chart')])]
    , className="container")


@app.callback(
    Output('map-chart', 'figure'),
    [Input('map-dropdown', 'value')])
def update_map_chart(value):
    filtered_df = simple_jme[simple_jme[value].astype(float) > 0]
    data = [dict(
        zmin=0,
        type='choropleth',
        colorscale=[[0.0, '#3288bd'], [0.20, '#99d594'], [0.40, '#e6f598'], [0.60, '#fee08b'], [0.80, '#fc8d59'],
                    [1, '#d53e4f']],
        autocolorscale=False,
        locations=filtered_df['iso_code'],
        z=filtered_df[value].astype(float),
        text=filtered_df['country_name'] + ' - Data from : ' + filtered_df['year'],
        colorbar=dict(
            title="Prevalence (%)")
    )]

    return {
        'data': data,

        "layout": {
            'height': '600',
            'width': '900',
            "geo": {
                "showcoastlines": True,
                "showframe": False
            }
        }

    }
