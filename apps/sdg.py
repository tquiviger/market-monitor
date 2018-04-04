# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import randomcolor
from dash.dependencies import Input, Output

from app import app
from conf import nutriset_config
from utils import csv_reader

rand_color = randomcolor.RandomColor()

sdg_indicators_df = csv_reader.get_sdg_indicators()

countries_df = sdg_indicators_df[['location_name']].drop_duplicates().sort_values(['location_name'])
years_df = sdg_indicators_df[['year_id']].drop_duplicates().sort_values(['year_id'])

layout = html.Div([
    html.Div([
        dcc.Dropdown(id='country-dropdown',
                     multi=False,
                     placeholder='Choose a country',
                     value='Afghanistan',
                     options=[{'label': country['location_name'], 'value': country['location_name']} for index, country
                              in
                              countries_df.iterrows()])], style={'margin': '15px'}),
    html.Div([
        dcc.Graph(id='sdg-chart')
    ], className='twelve columns')

])


def get_color(indicator):
    if 'asting' in indicator:
        return nutriset_config.WASTING_COLOR
    elif 'tunting' in indicator:
        return nutriset_config.STUNTING_COLOR
    elif 'verweight' in indicator:
        return nutriset_config.OVERWEIGHT_COLOR


def get_trace(df, indicator, dot=False):
    graphline = {}
    opacity = 1
    if dot:
        graphline = dict(
            shape='linear',
            dash='longdash'
        )
        opacity = 0.25
    return go.Scatter(
        x=df[df['indicator_short'] == indicator]['year_id'],
        y=df[df['indicator_short'] == indicator]['unscaled_value'],
        line=graphline,
        marker=dict(
            color=get_color(indicator),
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        name=indicator,
        opacity=opacity
    )


@app.callback(Output('sdg-chart', 'figure'),
              [Input('country-dropdown', 'value')])
def generate_country_dashboard(country):
    sdg_indicators = sdg_indicators_df[sdg_indicators_df['location_name'] == country]

    sdg_indicators = sdg_indicators[sdg_indicators['ihme_indicator_description'].str.contains('Indicator 2')]
    sdg_indicators['color'] = sdg_indicators.apply(get_color, axis=1)
    sdg_indicators_under_2016 = sdg_indicators[sdg_indicators['year_id'] <= 2016]
    sdg_indicators_over_2016 = sdg_indicators[sdg_indicators['year_id'] >= 2016]

    traces1 = [get_trace(sdg_indicators_under_2016, row['indicator_short'])
               for index, row in
               sdg_indicators[['indicator_short']].drop_duplicates().iterrows()]
    traces2 = [get_trace(sdg_indicators_over_2016, row['indicator_short'], dot=True)
               for index, row in
               sdg_indicators[['indicator_short']].drop_duplicates().iterrows()]

    print(traces2)
    return {
        'data': traces1 + traces2,
        'layout': go.Layout(showlegend=True,

                            )

    }

    # trace2 = go.Area(
    #     r=[57.49999999999999, 50.0, 45.0, 35.0, 20.0, 22.5, 37.5, 55.00000000000001],
    #     t=['North', 'N-E', 'East', 'S-E', 'South', 'S-W', 'West', 'N-W'],
    #     name='8-11 m/s',
    #     marker=dict(
    #         color='rgb(158,154,200)'
    #     )
    # )
    # trace3 = go.Area(
    #     r=[40.0, 30.0, 30.0, 35.0, 7.5, 7.5, 32.5, 40.0],
    #     t=['North', 'N-E', 'East', 'S-E', 'South', 'S-W', 'West', 'N-W'],
    #     name='5-8 m/s',
    #     marker=dict(
    #         color='rgb(203,201,226)'
    #     )
    # )
    # trace4 = go.Area(
    #     r=[20.0, 7.5, 15.0, 22.5, 2.5, 2.5, 12.5, 22.5],
    #     t=['North', 'N-E', 'East', 'S-E', 'South', 'S-W', 'West', 'N-W'],
    #     name='< 5 m/s',
    #     marker=dict(
    #         color='rgb(242,240,247)'
    #     )
    # )
    # data = [trace1, trace2, trace3, trace4]
    # layout = go.Layout(
    #     title='Wind Speed Distribution in Laurel, NE',
    #     font=dict(
    #         size=16
    #     ),
    #     legend=dict(
    #         font=dict(
    #             size=16
    #         )
    #     ),
    #     radialaxis=dict(
    #         ticksuffix='%'
    #     ),
    #     orientation=270
    # )
    # fig = go.Figure(data=data, layout=layout)
