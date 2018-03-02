# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import api

app = dash.Dash()


def generate_plans_dropdown():
    plans = api.get_plan_list()

    return html.Div([
        html.Div([
            html.Div(style={'margin-left': '10px'}),
            dcc.Dropdown(id='plan_dropdown',
                         multi=True,
                         value=[""],
                         options=[
                             {'label': plan['name'], 'value': str(plan['id']) + '-' + plan['name']} for plan in plans
                         ])
        ], className='')

    ], className='row')


app.layout = html.Div(children=[
    html.H1(
        children='Nutriset - Market Monitor',
        style={'textAlign': 'center'}
    ),

    generate_plans_dropdown(),
    dcc.Graph(id='funding-chart')
])


@app.callback(
    dash.dependencies.Output('funding-chart', 'figure'),
    [dash.dependencies.Input('plan_dropdown', 'value')])
def update_plan_funding_chart(selected_plans):
    if selected_plans[0] == '':
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
