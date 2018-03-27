# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import plotly
from dash.dependencies import Input, Output, State

from app import app
from conf.nutriset_coefs import *
from utils import csv_reader

df = csv_reader.get_simple_jme()

layout = html.Div(children=[
    html.H4(children='Malnutrition Data'),

    html.Div([
        html.Div([dt.DataTable(
            rows=df.to_dict('records'),
            columns=['iso_code', 'country_name', 'UN_subregion', 'UN_region',
                     'severe_wasting', 'moderate_wasting', 'wasting', 'stunting', 'overweight', 'underweight',
                     'under5'],
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id='raw-datatable'
        )], className='twelve columns')
    ], className='row'),

    html.Div([
        html.Div(id='selected-indexes', className='twelve columns')
    ], className='row'),

    html.Div([
        html.Div([dcc.Graph(
            id='graph-gapminder'
        )], className='twelve columns')
    ], className='row'),

])


@app.callback(
    Output('raw-datatable', 'selected_row_indices'),
    [Input('graph-gapminder', 'clickData')],
    [State('raw-datatable', 'selected_row_indices')])
def update_selected_row_indices(click_data, selected_row_indices):
    if click_data:
        for point in click_data['points']:
            if point['pointNumber'] in selected_row_indices:
                selected_row_indices.remove(point['pointNumber'])
            else:
                selected_row_indices.append(point['pointNumber'])
    return selected_row_indices


@app.callback(
    Output('graph-gapminder', 'figure'),
    [Input('raw-datatable', 'rows'),
     Input('raw-datatable', 'selected_row_indices')])
def update_figure(rows, selected_row_indices):
    dff = pd.DataFrame(rows)
    fig = plotly.tools.make_subplots(
        rows=4, cols=1,
        subplot_titles=(
            'Stunting Prevalance', 'Severe Wasting Prevalence', 'Moderate Wasting Prevalence', 'Population Under 5',),
        shared_xaxes=True)
    marker = {'color': [STUNTING_COLOR] * len(dff)}
    for i in (selected_row_indices or []):
        marker['color'][i] = '#000'
    fig.append_trace({
        'x': dff['iso_code'],
        'y': dff['stunting'],
        'type': 'bar',
        'marker': marker
    }, 1, 1)
    marker = {'color': [SEVERE_WASTING_COLOR] * len(dff)}
    for i in (selected_row_indices or []):
        marker['color'][i] = '#000'
    fig.append_trace({
        'x': dff['iso_code'],
        'y': dff['severe_wasting'],
        'type': 'bar',
        'marker': marker
    }, 2, 1)
    marker = {'color': [MODERATE_WASTING_COLOR] * len(dff)}
    for i in (selected_row_indices or []):
        marker['color'][i] = '#000'
    fig.append_trace({
        'x': dff['iso_code'],
        'y': dff['moderate_wasting'],
        'type': 'bar',
        'marker': marker
    }, 3, 1)
    marker = {'color': ['0074D9'] * len(dff)}
    for i in (selected_row_indices or []):
        marker['color'][i] = '#000'
    fig.append_trace({
        'x': dff['iso_code'],
        'y': dff['under5'],
        'type': 'bar',
        'marker': marker
    }, 4, 1)
    fig['layout']['showlegend'] = False
    fig['layout']['height'] = 800
    fig['layout']['margin'] = {
        'l': 40,
        'r': 10,
        't': 60,
        'b': 200
    }
    return fig
