# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import plotly.graph_objs as go
import api
import json

from app import app

STUNTING_COLOR = '#82E0AA'
WASTING_COLOR = '#F4D03F'
OVERWEIGHT_COLOR = '#884EA0'
UNDERWEIGHT_COLOR = '#5DADE2'
SEVERE_WASTING_COLOR = '#D35400'

WORKING_FOLDER = '/Users/thomas/work/nutriset/'
detailed_country_data = pd.read_csv(WORKING_FOLDER + 'jme_detailed_results.csv',
                                    sep=',',
                                    dtype={
                                        'severe_wasting': float,
                                        'wasting': float,
                                        'overweight': float,
                                        'stunting': float,
                                        'underweight': float,
                                        'under5': float}
                                    )

simple_country_data = pd.read_csv(WORKING_FOLDER + 'jme_results.csv',
                                  sep=',',
                                  dtype={
                                      'severe_wasting': float,
                                      'wasting': float,
                                      'overweight': float,
                                      'stunting': float,
                                      'underweight': float,
                                      'under5': float}
                                  )

countries = simple_country_data[['iso_code', 'country_name']].drop_duplicates()

layout = html.Div([
    dcc.Dropdown(id='country-dropdown',
                 multi=False,
                 placeholder='Choose a country',
                 value='AFG',
                 options=[{'label': country['country_name'], 'value': country['iso_code']} for index, country in
                          countries.iterrows()]),
    html.Div(id='intermediate-funding-buffer', style={'display': 'none'}),
    html.Div([
        html.Div(id='country-details', className='four columns'),
        html.Div([dcc.Graph(id='country-chart')], className='eight columns')
    ], className='row'),

    html.Div([
        html.Div(id='country-funding', className='four columns')
    ], className='row'),
    #
    # html.Div([
    #     # html.Div([dcc.Graph(id='funding-chart-donors')], className='six columns'),
    #     # html.Div([dcc.Graph(id='funding-chart-recipients')], className='six columns')
    # ], className='row')
]
    , className="ten columns offset-by-one")


def get_country_table(df, year):
    return html.Div(
        [html.H6('Latest Data ({0})'.format(year)),
         html.Table(
             [
                 html.Tr([
                     html.Th('UN sub-region'),
                     html.Td(df['UN_subregion'])
                 ]),
                 html.Tr([
                     html.Th('UN region'),
                     html.Td(df['UN_region'])
                 ]),
                 html.Tr([
                     html.Th('Severe Wasting Prevalence'),
                     html.Td(df['severe_wasting'])
                 ], style={'color': SEVERE_WASTING_COLOR}),
                 html.Tr([
                     html.Th('Wasting Prevalence'),
                     html.Td(df['wasting'])
                 ], style={'color': WASTING_COLOR}),
                 html.Tr([
                     html.Th('Stunting Prevalence'),
                     html.Td(df['stunting'])
                 ], style={'color': STUNTING_COLOR}),
                 html.Tr([
                     html.Th('Overweight Prevalence'),
                     html.Td(df['overweight'])
                 ], style={'color': OVERWEIGHT_COLOR}),
                 html.Tr([
                     html.Th('Underweight Prevalence'),
                     html.Td(df['underweight'])
                 ], style={'color': UNDERWEIGHT_COLOR}),
                 html.Tr([
                     html.Th('Under 5 population'),
                     html.Td(df['under5'])
                 ])

             ]),
         html.Div(children=[html.P('Source : ' + df['source'].astype(str)),
                            html.P('By : ' + df['report_author'].astype(str))],
                  style={'font-size': 'x-small'}
                  )

         ], style={'font-size': 'x-small'})


@app.callback(
    Output('country-details', 'children'),
    [Input('country-dropdown', 'value')])
def generate_country_dashboard(selected_iso_code):
    simple_data = simple_country_data[simple_country_data['iso_code'] == selected_iso_code]
    data_year = simple_data['year'].unique()[0]

    return html.Div([
        get_country_table(simple_data, str(data_year.astype(int)))

    ])


@app.callback(
    Output('country-chart', 'figure'),
    [Input('country-dropdown', 'value')])
def update_plan_funding_chart(selected_iso_code):
    df = detailed_country_data[detailed_country_data['iso_code'] == selected_iso_code]

    trace1 = go.Scatter(
        y=df[df['stunting'] > 0]['stunting'],  # negative values mean data not found
        x=df['year'],
        textposition='auto',
        marker=dict(
            color=STUNTING_COLOR,
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        name='Stunting'
    )

    trace2 = go.Scatter(
        y=df[df['wasting'] > 0]['wasting'],  # negative values mean data not found
        x=df['year'],
        marker=dict(
            color=WASTING_COLOR,
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        name='Wasting'
    )

    trace3 = go.Scatter(
        y=df[df['severe_wasting'] > 0]['severe_wasting'],  # negative values mean data not found
        x=df['year'],
        marker=dict(
            color=SEVERE_WASTING_COLOR,
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        name='Severe Wasting'
    )

    trace4 = go.Scatter(
        y=df[df['underweight'] > 0]['underweight'],  # negative values mean data not found
        x=df['year'],
        marker=dict(
            color=UNDERWEIGHT_COLOR,
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        name='Underweight'
    )

    trace5 = go.Scatter(
        y=df[df['overweight'] > 0]['overweight'],  # negative values mean data not found
        x=df['year'],
        marker=dict(
            color=OVERWEIGHT_COLOR,
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        name='Overweight'
    )

    return {
        'data': [trace3, trace2, trace1, trace5, trace4],
        'layout': go.Layout(
            barmode='overlay',
            title='Malnutrition metrics evolution',
        )

    }


@app.callback(
    Output('intermediate-funding-buffer', 'children'),
    [Input('country-dropdown', 'value')])
def generate_funding_info(selected_iso_code):
    return json.dumps(api.get_country_funding_by_orga(selected_iso_code))

@app.callback(
    Output('country-funding', 'children'),
    [Input('intermediate-funding-buffer', 'children')])
def generate_funding_info(funding_data):
    data = json.loads(funding_data)
    return html.Div([
        html.H6('Funding details'),
        html.P('Total funded for 2018 : {0}$'.format(format(data['total_funded'], ',')))

    ])

# @app.callback(
#     Output('funding-chart-donor', 'figure'),
#     [Input('country-dropdown', 'value')])
# def update_plan_funding_chart(selected_iso_code):
#     df = detailed_country_data[detailed_country_data['iso_code'] == selected_iso_code]
#
#     trace1 = go.Scatter(
#         y=df[df['stunting'] > 0]['stunting'],  # negative values mean data not found
#         x=df['year'],
#         textposition='auto',
#         marker=dict(
#             color=STUNTING_COLOR,
#             line=dict(
#                 color='rgb(8,48,107)',
#                 width=1.5)
#         ),
#         name='Stunting'
#     )
#
#     trace2 = go.Scatter(
#         y=df[df['wasting'] > 0]['wasting'],  # negative values mean data not found
#         x=df['year'],
#         marker=dict(
#             color=WASTING_COLOR,
#             line=dict(
#                 color='rgb(8,48,107)',
#                 width=1.5)
#         ),
#         name='Wasting'
#     )
#
#     trace3 = go.Scatter(
#         y=df[df['severe_wasting'] > 0]['severe_wasting'],  # negative values mean data not found
#         x=df['year'],
#         marker=dict(
#             color=SEVERE_WASTING_COLOR,
#             line=dict(
#                 color='rgb(8,48,107)',
#                 width=1.5)
#         ),
#         name='Severe Wasting'
#     )
#
#     trace4 = go.Scatter(
#         y=df[df['underweight'] > 0]['underweight'],  # negative values mean data not found
#         x=df['year'],
#         marker=dict(
#             color=UNDERWEIGHT_COLOR,
#             line=dict(
#                 color='rgb(8,48,107)',
#                 width=1.5)
#         ),
#         name='Underweight'
#     )
#
#     trace5 = go.Scatter(
#         y=df[df['overweight'] > 0]['overweight'],  # negative values mean data not found
#         x=df['year'],
#         marker=dict(
#             color=OVERWEIGHT_COLOR,
#             line=dict(
#                 color='rgb(8,48,107)',
#                 width=1.5)
#         ),
#         name='Overweight'
#     )
#
#     return {
#         'data': [trace3, trace2, trace1, trace5, trace4],
#         'layout': go.Layout(
#             barmode='overlay',
#             title='Malnutrition metrics evolution',
#         )
#
#     }
