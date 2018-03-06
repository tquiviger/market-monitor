# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import api

app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(
        children='Nutriset - Market Monitor',
        style={'textAlign': 'center'}
    ),
    dcc.Dropdown(id='year_dropdown',
                 multi=False,
                 value=[2018],
                 options=[{'label': i, 'value': i} for i in [2015, 2016, 2017, 2018]]),

    dcc.Dropdown(id='plan_dropdown',
                 multi=True,
                 value="",
                 options=[]),

    html.Div([
        html.Div([
            html.H3("Funding progress in the Food Security Cluster")
        ], className='Title'),
        dcc.Graph(id='funding-chart'),
    ], className='five columns wind-polar')

])


@app.callback(
    dash.dependencies.Output('plan_dropdown', 'options'),
    [dash.dependencies.Input('year_dropdown', 'value')])
def update_plan_dropdown(selected_year):
    plans = api.get_plan_list(selected_year)
    return [
        {'label': plan['name'], 'value': str(plan['id']) + '-' + plan['name']} for plan in plans
    ]


@app.callback(
    dash.dependencies.Output('funding-chart', 'figure'),
    [dash.dependencies.Input('plan_dropdown', 'value')])
def update_plan_funding_chart(selected_plans):
    if selected_plans == '':
        data = []
    else:
        data = api.get_plan_funding(selected_plans)

    layout = go.Layout(
        barmode='group'
    )

    return {
        'data': data,
        'layout': dcc.Graph(
            id='funding-chart',
            figure={
                'data': data,
                'layout': layout
            }
        )}


if __name__ == '__main__':
    app.run_server(debug=True)
