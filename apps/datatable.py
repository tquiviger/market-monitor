# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_table_experiments as dt
import plotly
import pandas as pd

from app import app

WORKING_FOLDER = '/Users/thomas/work/nutriset/'
df = pd.read_csv(WORKING_FOLDER + 'jme_results.csv',
                 sep=',',
                 dtype={
                     'severe_wasting': float,
                     'wasting': float,
                     'overweight': float,
                     'stunting': float,
                     'underweight': float,
                     'under5': float})

layout = html.Div(children=[
    html.H4(children='Malnutrition Data'),
    dt.DataTable(
        rows=df.to_dict('records'),
        columns=['iso_code', 'country_name', 'UN_subregion', 'UN_region',
                 'severe_wasting', 'wasting', 'overweight', 'stunting', 'underweight', 'under5'],
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='raw-datatable'
    ),
    html.Div(id='selected-indexes'),
    dcc.Graph(
        id='graph-gapminder'
    )
], className="container")


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
        rows=3, cols=1,
        subplot_titles=('Stunting Prevalance', 'Wasting Prevalence', 'Population Under 5',),
        shared_xaxes=True)
    marker = {'color': ['#0074D9'] * len(dff)}
    for i in (selected_row_indices or []):
        marker['color'][i] = '#FF851B'
    fig.append_trace({
        'x': dff['iso_code'],
        'y': dff['stunting'],
        'type': 'bar',
        'marker': marker
    }, 1, 1)
    fig.append_trace({
        'x': dff['iso_code'],
        'y': dff['wasting'],
        'type': 'bar',
        'marker': marker
    }, 2, 1)
    fig.append_trace({
        'x': dff['iso_code'],
        'y': dff['under5'],
        'type': 'bar',
        'marker': marker
    }, 3, 1)
    fig['layout']['showlegend'] = False
    fig['layout']['height'] = 800
    fig['layout']['margin'] = {
        'l': 40,
        'r': 10,
        't': 60,
        'b': 200
    }
    return fig


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})
