# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import api

app = dash.Dash()

app.layout = html.Div([
    html.H1(
        children='Nutriset - Funding Progress Monitoring',
        style={'textAlign': 'center'}
    ),
    html.Div([
        dcc.Slider(
            id="year_slider",
            min=2015,
            max=2018,
            marks={i: i for i in [2015, 2016, 2017, 2018]},
            step=1,
            value=2018
        )],
        style={'margin': '25px'}),
    html.Div([
        dcc.Dropdown(id='plan_dropdown',
                     multi=True,
                     placeholder="Select a plan",
                     value="",
                     options=[])],
        style={'margin': '25px'}),

    html.Div([

        html.H3("Funding progress in the Food Security Cluster")
    ], className='Title'),
    dcc.Graph(id='funding-chart')

])


@app.callback(
    dash.dependencies.Output('plan_dropdown', 'options'),
    [dash.dependencies.Input('year_slider', 'value')])
def update_plan_dropdown(selected_year):
    plans = api.get_plan_list(selected_year)
    return [
        {'label': plan['name'], 'value': str(plan['id']) + '-' + plan['name']} for plan in plans
    ]


@app.callback(
    dash.dependencies.Output('funding-chart', 'figure'),
    [dash.dependencies.Input('plan_dropdown', 'value')])
def update_plan_funding_chart(selected_plans):
    if len(selected_plans) < 1:
        plans = api.get_plan_list(2018)
        selected_plans = [str(plan['id']) + '-' + plan['name'] for plan in plans]
        data = api.get_plan_funding(selected_plans)
    else:
        data = api.get_plan_funding(selected_plans)

    trace1 = go.Bar(
        y=data['total_funded'],
        x=data['plans'],
        marker=dict(
            color='#034f84',
        ),
        opacity=1,
        name='Total Funded'
    )

    trace2 = go.Bar(
        y=data['required'],
        x=data['plans'],
        text=data['percentages'],
        textposition='auto',
        marker=dict(
            color='#92a8d1',
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


if __name__ == '__main__':
    app.run_server(debug=True)
