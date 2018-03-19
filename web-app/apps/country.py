# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import plotly.graph_objs as go

from app import app

WORKING_FOLDER = '/Users/thomas/work/nutriset/'
detailed_country_data = pd.read_csv(WORKING_FOLDER + 'jme_detailed_results.csv',
                                    sep=',',
                                    dtype={
                                        'severe_wasting': float,
                                        'wasting': float,
                                        'overweight': float,
                                        'stunting': float,
                                        'underweight': float,
                                        'under5': float}
                                    )

simple_country_data = pd.read_csv(WORKING_FOLDER + 'jme_results.csv',
                                  sep=',',
                                  dtype={
                                      'severe_wasting': float,
                                      'wasting': float,
                                      'overweight': float,
                                      'stunting': float,
                                      'underweight': float,
                                      'under5': float}
                                  )

countries = simple_country_data[['iso_code', 'country_name']].drop_duplicates()

layout = html.Div([
    html.Div([
        dcc.Dropdown(id='country_dropdown',
                     multi=False,
                     placeholder='Choose a country',
                     value='',
                     options=[{'label': country['country_name'], 'value': country['iso_code']} for index, country in
                              countries.iterrows()])
    ]),

    html.Div(id='country_details'),
    dcc.Graph(id='country-chart')]
    , className="container")


def get_country_table(df):
    df = df[
        ["iso_code", "country_name", "UN_subregion", "UN_region",
         "severe_wasting", "wasting", "overweight", "stunting", "underweight", "under5"]]
    return html.Table(
        [html.Tr([html.Th(col) for col in
                  ['ISO Code', 'Country Name', 'UN sub-region', 'UN Region', 'Severe Wasting Prevalence',
                   'Wasting Prevalence', 'Overweight Prevalence',
                   'Stunting Prevalence', 'Underweight Prevalence',
                   'Under 5 Population'
                   ]])] +
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in df.columns
        ]) for i in range(min(len(df), 10))]
    )


@app.callback(
    Output('country_details', 'children'),
    [Input('country_dropdown', 'value')])
def generate_country_dashboard(selected_iso_code):
    simple_data = simple_country_data[simple_country_data['iso_code'] == selected_iso_code]
    country_name = simple_data['country_name'].unique()

    return html.Div([
        html.H1('Country : ' + country_name),

        get_country_table(simple_data)

    ])


@app.callback(
    Output('country-chart', 'figure'),
    [Input('country_dropdown', 'value')])
def update_plan_funding_chart(selected_iso_code):
    df = detailed_country_data[detailed_country_data['iso_code'] == selected_iso_code]
    trace1 = go.Scatter(
        y=df['stunting'],
        x=df['year'],
        textposition='auto',
        marker=dict(
            color='#F9E79F',
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        name='Stunting'
    )

    trace2 = go.Scatter(
        y=df['wasting'],
        x=df['year'],
        marker=dict(
            color='#73C6B6',
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        name='Wasting'
    )

    return {
        'data': [trace1, trace2],
        'layout': go.Layout(
            barmode='overlay'
        )

    }
