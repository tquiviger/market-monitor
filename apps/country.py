# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import plotly.graph_objs as go
import api
import json
import randomcolor
import os
from nutriset_coefs import *

from app import app

WORKING_FOLDER = os.environ.get('WORKING_FOLDER', '/Users/thomas/work/nutriset/')

rand_color = randomcolor.RandomColor()

detailed_country_data = pd.read_csv(WORKING_FOLDER + 'jme_detailed_results.csv', sep=',',
                                    dtype={'severe_wasting': float, 'wasting': float,
                                           'stunting_children': int, 'severe_wasting_children': int,
                                           'moderate_wasting_children': int,
                                           'overweight': float, 'stunting': float, 'underweight': float,
                                           'under5': int})

simple_country_data = pd.read_csv(WORKING_FOLDER + 'jme_results.csv', sep=',',
                                  dtype={'severe_wasting': float, 'wasting': float,
                                         'stunting_children': int, 'severe_wasting_children': int,
                                         'moderate_wasting_children': int,
                                         'overweight': float, 'stunting': float, 'underweight': float,
                                         'under5': int})

countries = simple_country_data[['iso_code', 'country_name']].drop_duplicates()

layout = html.Div([
    html.Div([dcc.Dropdown(id='country-dropdown',
                           multi=False,
                           placeholder='Choose a country',
                           value='AFG',
                           options=[{'label': country['country_name'], 'value': country['iso_code']} for index, country
                                    in
                                    countries.iterrows()])], style={'margin': '15'}),
    html.Div(id='intermediate-funding-buffer', style={'display': 'none'}),
    html.Div([
        html.Div(id='country-details', className='four columns'),
        html.Div([dcc.Graph(id='country-chart')], className='eight columns')
    ], className='row'),

    html.Div([
        html.Div(id='country-funding', className='four columns')
    ], className='row'),

    html.Div([
        html.Div([dcc.Graph(id='funding-chart-sankey')], className='eight columns')
    ], className='row'),
    html.Div([
        html.Div([dcc.Graph(id='funding-chart-progress')], className='twelve columns')
    ], className='row')
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
                     html.Th('Wasting (Prevalence)'),
                     html.Td(df['wasting'])
                 ]),
                 html.Tr([
                     html.Th('Wasting (Children)'),
                     html.Td(df['wasting_children'])
                 ]),
                 html.Tr([
                     html.Th('Severe Wasting (Prevalence)'),
                     html.Td(df['severe_wasting'])
                 ], style={'color': SEVERE_WASTING_COLOR}),
                 html.Tr([
                     html.Th('Severe Wasting (Children)'),
                     html.Td(df['severe_wasting_children'])
                 ], style={'color': SEVERE_WASTING_COLOR}),
                 html.Tr([
                     html.Th('Moderate Wasting (Prevalence)'),
                     html.Td(df['moderate_wasting'])
                 ], style={'color': MODERATE_WASTING_COLOR}),
                 html.Tr([
                     html.Th('Moderate Wasting (Children)'),
                     html.Td(df['moderate_wasting_children'])
                 ], style={'color': MODERATE_WASTING_COLOR}),
                 html.Tr([
                     html.Th('Stunting (Prevalence)'),
                     html.Td(df['stunting'])
                 ], style={'color': STUNTING_COLOR}),
                 html.Tr([
                     html.Th('Stunting (Children)'),
                     html.Td(df['stunting_children'])
                 ], style={'color': STUNTING_COLOR}),
                 html.Tr([
                     html.Th('Overweight (Prevalence)'),
                     html.Td(df['overweight'])
                 ], style={'color': OVERWEIGHT_COLOR}),
                 html.Tr([
                     html.Th('Underweight (Prevalence)'),
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

         ], style={'font-size': 'small'})


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

    trace0 = go.Scatter(
        y=df[df['wasting'] > 0]['wasting'],  # negative values mean data not found
        x=df['year'],
        marker=dict(
            color='#000',
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        name='Wasting'
    )

    trace1 = go.Scatter(
        y=df[df['stunting'] > 0]['stunting'],  # negative values mean data not found
        x=df[df['stunting'] > 0]['year'],
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
        y=df[df['moderate_wasting'] > 0]['moderate_wasting'],  # negative values mean data not found
        x=df[df['moderate_wasting'] > 0]['year'],
        marker=dict(
            color=MODERATE_WASTING_COLOR,
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        name='Moderate Wasting'
    )

    trace3 = go.Scatter(
        y=df[df['severe_wasting'] > 0]['severe_wasting'],  # negative values mean data not found
        x=df[df['severe_wasting'] > 0]['year'],
        marker=dict(
            color=SEVERE_WASTING_COLOR,
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        name='Severe Wasting'
    )

    return {
        'data': [trace0, trace3, trace2, trace1],
        'layout': go.Layout(
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
        html.H6('Funding details for 2018'),
        html.P('Total funded : {0}$'.format(format(data['total_funded'], ',')))
    ])


@app.callback(
    Output('funding-chart-sankey', 'figure'),
    [Input('intermediate-funding-buffer', 'children')])
def update_funding_chart_sankey(funding_data):
    data = json.loads(funding_data)
    funding_total = data['total_funded']
    i = 1
    sources = []
    targets = []
    values = []
    colors = ["black"]
    labels = ['Funding']
    link_labels = []
    for funding_source in sorted(data['funding_source'], key=lambda x: x['totalFunding'], reverse=True)[:10]:
        sources.append(i)
        targets.append(0)
        values.append(funding_source['totalFunding'])
        labels.append(funding_source['name'])
        link_labels.append('{:02.2f}%'.format(funding_source['totalFunding'] / funding_total * 100))
        colors.append(rand_color.generate(hue='orange')[0])
        i = i + 1
    for funding_dest in sorted(data['funding_destination'], key=lambda x: x['totalFunding'], reverse=True)[:10]:
        sources.append(0)
        targets.append(i)
        values.append(funding_dest['totalFunding'])
        labels.append(funding_dest['name'])
        link_labels.append('{:02.2f}%'.format(funding_dest['totalFunding'] / funding_total * 100))
        colors.append(rand_color.generate(hue='blue')[0])
        i = i + 1
    trace1 = go.Sankey(
        type='sankey',
        node=dict(
            pad=15,
            thickness=20,
            line=dict(
                color="black",
                width=0.5
            ),
            label=labels,
            color=colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            label=link_labels
        ),
        name='Stunting'
    )

    return {
        'data': [trace1],
        'layout': go.Layout(
            width=1118,
            height=772,
            title='Funding source and destination (10 largest)'
        )

    }


@app.callback(
    Output('funding-chart-progress', 'figure'),
    [Input('intermediate-funding-buffer', 'children')])
def update_funding_chart_progress(funding_data):
    funding_data = json.loads(funding_data)
    data = api.get_country_funding(funding_data['country'], 2018)

    trace1 = go.Bar(
        y=data['total_funded'],
        x=data['plans'],
        text=data['percentages'],
        textposition='auto',
        marker=dict(
            color='rgb(49,130,189)',
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        opacity=1,
        name='Total Funded'
    )

    trace2 = go.Bar(
        y=data['required'],
        x=data['plans'],
        marker=dict(
            color='#92a8d1',
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        opacity=0.25,
        name='Total Required'
    )

    return {
        'data': [trace1, trace2],
        'layout': go.Layout(
            barmode='overlay',
            title='Funding progress for 2018 plans'
        )

    }
