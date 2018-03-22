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

def get_sankey_data():
    data = api.get_wfp_funding()
    funding_total = data['total_funded']
    i = 1
    sources = []
    targets = []
    values = []
    colors = ["black"]
    labels = ['WFP']
    link_labels = []
    for funding_source in sorted(data['funding_source'], key=lambda x: x['totalFunding'], reverse=True)[:20]:
        sources.append(i)
        targets.append(0)
        values.append(funding_source['totalFunding'])
        labels.append(funding_source['name'])
        link_labels.append('{:02.2f}%'.format(funding_source['totalFunding'] / funding_total * 100))
        colors.append(rand_color.generate(hue='orange')[0])
        i = i + 1
    for funding_dest in sorted(data['funding_destination'], key=lambda x: x['totalFunding'], reverse=True)[:20]:
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

    return trace1

layout = html.Div([
    html.Div([
        html.Div([
            dcc.Graph(
                id='funding-chart-wfp-sankey',
                figure={
                    'data': [get_sankey_data()],
                    'layout': go.Layout(
                        width=1118,
                        height=772,
                        title='Funding source and destination (10 largest)'
                    )

                })

        ], className='eight columns')
    ], className='row')
])



