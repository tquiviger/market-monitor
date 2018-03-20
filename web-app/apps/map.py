# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd

from app import app

WORKING_FOLDER = '/Users/thomas/work/nutriset/'
df = pd.read_csv(WORKING_FOLDER + 'jme_results.csv', sep=',')

for col in df.columns:
    df[col] = df[col].astype(str)

layout = html.Div(children=[
    html.Div([
        dcc.Dropdown(id='map-dropdown',
                     multi=False,
                     value='stunting',
                     options=[
                         {'label': 'Stunting', 'value': 'stunting'},
                         {'label': 'Wasting', 'value': 'wasting'},
                         {'label': 'Severe Wasting', 'value': 'severe_wasting'},
                         {'label': 'Overweight', 'value': 'overweight'},
                         {'label': 'Underweight', 'value': 'underweight'}
                     ])
    ], style={'margin': '15'}),

    html.Div([dcc.Graph(id='map-graph')])]
    , className="container")


@app.callback(
    Output('map-graph', 'figure'),
    [Input('map-dropdown', 'value')])
def update_map_chart(value):
    filtered_df = df[df[value].astype(float) > 0]
    data = [dict(
        zmin=0,
        type='choropleth',
        colorscale=[[0.0, '#FEF5E7'], [0.20, '#F9E79F'], [0.40, '#F5B041'], [0.60, '#DC7633'], [0.80, '#BA4A00'],
                    [1, '#CB4335']],
        autocolorscale=False,
        locations=filtered_df['iso_code'],
        z=filtered_df[value].astype(float),
        text=filtered_df['country_name'],
        marker=dict(
            line=dict(
                color='rgb(180,180,180)',
                width=0.5
            )),
        colorbar=dict(
            title="Prevalence (%)")
    )]

    return {
        'data': data,

        "layout": {
            'height': '600',
            'width': '900',
            "geo": {
                "projection": {
                    "type": "Mercator"
                },
                "showcoastlines": False,
                "showframe": False
            }
        }

    }
