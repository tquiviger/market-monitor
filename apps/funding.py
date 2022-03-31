# -*- coding: utf-8 -*-
from dash import dcc
from dash import html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from api import fts_api
from app import app

layout = html.Div([

    html.Div([html.H3('Funding progress for emergency plans (Nutrition Cluster)')
              ], className='twelve columns'),
    html.Div([
        dcc.Dropdown(id='plan_dropdown',
                     multi=True,
                     placeholder="Select a plan",
                     value="",
                     options=[]
                     )
    ], className='six columns offset-by-three'),

    html.Div([
        dcc.Slider(
            id="year_slider",
            min=2018,
            max=2022,
            marks={i: i for i in [2018, 2019, 2020, 2021, 2022]},
            step=1,
            value=2022,
            included=False
        )
    ], className='six columns offset-by-three'),

    html.Div([
        dcc.Graph(id='funding-chart')
    ], className='row twelve columns', style={"margin": "25px"})

])


@app.callback(
    Output('plan_dropdown', 'options'),
    [Input('year_slider', 'value')])
def update_plan_dropdown(selected_year):
    plans = fts_api.get_plan_list(selected_year)
    return [
        {'label': plan['planVersion']['name'], 'value': str(plan['id']) + '-' + plan['planVersion']['name']} for plan in
        plans
    ]


@app.callback(
    Output('funding-chart', 'figure'),
    [Input('plan_dropdown', 'value')])
def update_plan_funding_chart(selected_plans):
    if len(selected_plans) < 1:
        plans = fts_api.get_plan_list(2021)
        selected_plans = [str(plan['id']) + '-' + plan['planVersion']['name'] for plan in plans]
        data = fts_api.get_plan_funding(selected_plans)
    else:
        data = fts_api.get_plan_funding(selected_plans)

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
            barmode='overlay'
        )

    }
