# -*- coding: utf-8 -*-
import dash_html_components as html
import dash_core_components as dcc

layout = html.Div([
    html.H1(
        children='Nutriset - Country',
        style={'textAlign': 'center'}
    ),
    dcc.Link('Go to funding', href='/funding')

])

