# -*- coding: utf-8 -*-
import json

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import randomcolor
from dash.dependencies import Input, Output

import api
from app import app
from conf.nutriset_coefs import *
from utils import csv_reader

rand_color = randomcolor.RandomColor()

detailed_country_data = csv_reader.get_detailed_jme()

simple_country_data = csv_reader.get_simple_jme()

countries = simple_country_data[['iso_code', 'country_name']].drop_duplicates()

layout = html.Div([
    html.Div([dcc.Dropdown(id='country-dropdown',
                           multi=False,
                           placeholder='Choose a country',
                           value='AFG',
                           options=[{'label': country['country_name'], 'value': country['iso_code']} for index, country
                                    in
                                    countries.iterrows()])], style={'margin': '15px'}),
    html.Div(id='intermediate-funding-buffer', style={'display': 'none'}, className='row'),

    html.Div([
        html.Div(id='country-details', className='four columns'),
        html.Div([dcc.Graph(id='country-chart')], className='eight columns')
    ], className='row'),

    html.Div([
        html.Div(id='country-funding', className='four columns')
    ], className='row'),

    html.Div([
        html.Div([dcc.Graph(id='funding-chart-sankey')], className='twelve columns')
    ], className='row'),
    html.Div([
        html.Div([dcc.Graph(id='funding-chart-progress')], className='twelve columns')
    ], className='row'),
    html.Div([
        html.Div([dcc.Graph(id='wfp-funding-chart')], className='twelve columns')
    ], className='row'),
    html.Div([
        html.Div([dcc.Graph(id='unicef-funding-chart')], className='twelve columns')
    ], className='row')
])


def get_country_table(df, year):
    return html.Div(
        [
            html.H6('Latest Data update : {0}'.format(year)),
            html.Table(

                [
                    html.Tr([html.Th([col], style={'text-align': 'center'}) for col in
                             ['', html.I(className="fas fa-percent fa-lg"), html.I(className="fas fa-child fa-lg")]]
                            )] +
                [html.Tr([
                    html.Th(col['title']),
                    html.Td(df[col['type']]),
                    html.Td(df[col['type'] + '_children'])
                ], style={'color': col['color']}) for col in [
                    {'title': 'Wasting', 'type': 'wasting', 'color': 'black'},
                    {'title': 'Severe Wasting', 'type': 'severe_wasting', 'color': SEVERE_WASTING_COLOR},
                    {'title': 'Moderate Wasting', 'type': 'moderate_wasting', 'color': MODERATE_WASTING_COLOR},
                    {'title': 'Stunting', 'type': 'stunting', 'color': STUNTING_COLOR},
                    {'title': 'Overweight', 'type': 'overweight', 'color': OVERWEIGHT_COLOR},
                    {'title': 'Underweight', 'type': 'underweight', 'color': UNDERWEIGHT_COLOR},
                ]]),
            html.Div(children=[
                html.P('Source : ' + df['source'].astype(str)),
                html.P('By : ' + df['report_author'].astype(str))],
                style={'font-size': 'x-small'})
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
        x=df[df['wasting'] > 0]['year'],
        fill='tozeroy',
        marker=dict(
            color='#ffcc66',
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
            barmode='overlay',
            title='Malnutrition evolution',
        )

    }


@app.callback(
    Output('intermediate-funding-buffer', 'children'),
    [Input('country-dropdown', 'value')])
def fill_intermediate_buffer(selected_iso_code):
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
            # width=1118,
            # height=772,
            title='Funding source and destination (10 largest)'
        )

    }


@app.callback(
    Output('funding-chart-progress', 'figure'),
    [Input('intermediate-funding-buffer', 'children')])
def update_funding_chart_progress(funding_data):
    funding_data = json.loads(funding_data)
    data = api.get_country_funding_for_year(funding_data['country'], 2018)

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


@app.callback(
    Output('wfp-funding-chart', 'figure'),
    [Input('country-dropdown', 'value')])
def update_funding_chart_wfp(iso_code):
    return get_funding_chart_by_orga(iso_code, 'wfp')


@app.callback(
    Output('unicef-funding-chart', 'figure'),
    [Input('country-dropdown', 'value')])
def update_funding_chart_unicef(iso_code):
    return get_funding_chart_by_orga(iso_code, 'unicef')


def get_funding_chart_by_orga(iso_code, organization):
    data = api.get_country_funding_for_organization(iso_code, organization)
    labels = []
    values = []
    for orga in data['funding_source']:
        labels.append(orga['name'])
        values.append(orga['totalFunding'])

    trace = go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        hoverinfo='label+value',
        showlegend=False,
        textinfo='percent',
        marker=dict(
            line=dict(color='#000000',
                      width=2)))
    return {
        'data': [trace],
        'layout': go.Layout(
            width=1100,
            title=organization + ' funding origin for the country, for 2017/2018, for FS and N clusters'
        )

    }
