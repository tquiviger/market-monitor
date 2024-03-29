# -*- coding: utf-8 -*-
import json
import locale

import plotly.graph_objs as go
import randomcolor
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from api import fts_api, reliefweb_api
from app import app
from conf.nutriset_config import *
from utils import csv_reader, functions

locale.setlocale(locale.LC_ALL, '')

rand_color = randomcolor.RandomColor()

detailed_country_data = csv_reader.get_detailed_jme()
simple_country_data = csv_reader.get_simple_jme()
relief_web_data = csv_reader.get_relief_web()
who_stunting_data = csv_reader.get_who_stunting()
who_wasting_data = csv_reader.get_who_wasting()

countries = simple_country_data[['iso_code', 'country_name']].drop_duplicates()

layout = html.Div([
    html.Div([
        dcc.Dropdown(id='country-dropdown',
                     multi=False,
                     placeholder='Choose a country',
                     value='AFG',
                     options=[{'label': country['country_name'], 'value': country['iso_code']} for index, country
                              in
                              countries.iterrows()])], style={'margin': '15px'}),

    html.Div([
        html.Div(id='country-details', className='six columns'),
        html.Div(id='country-map', className='six columns'),
    ], className='twelve columns'),
    html.Div([
        html.Div(
            [dcc.Graph(id='country-chart')], className='twelve columns')
    ], className='twelve columns'),
    html.Div([
        html.Div(id='country-funding'),
        html.Div([
            dcc.Slider(
                id="year-slider",
                min=2018,
                max=2022,
                marks={i: i for i in [2018, 2019, 2020, 2021, 2022]},
                step=1,
                value=2022,
                included=False
            )
        ], className='six columns offset-by-three', style={"margin-bottom": "25px"}),
    ], className='twelve columns',
        style={'border-top-width': '1px', 'border-top-style': 'solid', 'border-top-color': 'lightgray'}),
    html.Div([
        html.Div(id='funding-chart-sankey', className='twelve columns'),
        html.Div(id='funding-chart-progress', className='twelve columns')
    ], className='twelve columns'),
    html.Div([
        html.Div(id='wfp-funding-chart', className='six columns'),
        html.Div(id='unicef-funding-chart', className='six columns'),
    ], className='twelve columns'),
    html.Div([
        html.Div(id='reports-list'),
    ], className='twelve columns',
        style={'margin-top': '15px', 'border-top-width': '1px', 'border-top-style': 'solid',
               'border-top-color': 'lightgray'}),
    html.Div(id='relief-web-data', className='twelve columns',
             style={'border-top-width': '1px', 'border-top-style': 'solid', 'border-top-color': 'lightgray'}),
    html.Div(id='intermediate-funding-buffer', style={'display': 'none'}, className='row')

])


def get_needs_kg(df, col_type):
    result = ""
    try:
        result = functions.format_number_col(df[col_type + '_needs_kg'] / 1000) + ' tons'
    except Exception:
        pass
    return result


def get_country_table(df, year):
    return html.Div(
        [
            html.H3('Needs -  Data from {0}'.format(year)),
            html.Table(

                [
                    html.Tr([html.Th([col], style={'text-align': 'center'}) for col in
                             [
                                 '',
                                 html.I(className="fas fa-percent fa-lg"),
                                 html.I(className="fas fa-child fa-lg"),
                                 html.I(className="fas fa-box fa-lg")
                             ]]
                            )] +
                [html.Tr([
                    html.Th(col['title']),
                    html.Td(df[col['type']]),
                    html.Td(functions.format_number_col(df[col['type'] + '_children'])),
                    html.Td(get_needs_kg(df, col['type']))
                ], style={'color': col['color']}) for col in [
                    {'title': 'Severe Wasting', 'type': 'severe_wasting', 'color': SEVERE_WASTING_COLOR},
                    {'title': 'Moderate Wasting', 'type': 'moderate_wasting', 'color': MODERATE_WASTING_COLOR},
                    {'title': 'Overall Wasting', 'type': 'wasting', 'color': WASTING_COLOR},
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

    return get_country_table(simple_data, str(data_year.astype(int)))


@app.callback(
    Output('country-map', 'children'),
    [Input('country-dropdown', 'value')])
def generate_country_map(selected_iso_code):
    return html.Div(
        [html.Img(src='https://reliefweb.int/sites/reliefweb.int/files/resources/{0}_ocha_500px.png'.format(
            selected_iso_code.lower()),
            style={'height': '400',
                   'boxShadow': '1px 1px 5px #999',
                   'border': 'solid 1px #EFEFEF',  # ddd;
                   'padding': '5px'
                   }
        )],
        style={
            'display': 'flex',
            'align': 'middle',
            'flexDirection': 'row',
            'justifyContent': 'center'
        }
    )


@app.callback(
    Output('relief-web-data', 'children'),
    [Input('country-dropdown', 'value')])
def get_relief_web_data(selected_iso_code):
    country_data = relief_web_data[relief_web_data['crisis_iso3'] == selected_iso_code].sort_values('figure_name')
    if len(country_data) == 0:
        return ''
    return html.Div(
        [html.H3('Relief Web Crisis App Data'),
         dash_table.DataTable(
             data=country_data.to_dict('records'),
             columns=[{"name": i, "id": i} for i in ['figure_name', 'figure_value', 'figure_date', 'figure_source']],
             row_selectable=False,
             editable=False,
             id='reliefweb-datatable'
         )])


@app.callback(
    Output('country-chart', 'figure'),
    [Input('country-dropdown', 'value')])
def update_plan_funding_chart(selected_iso_code):
    df = detailed_country_data[detailed_country_data['iso_code'] == selected_iso_code]
    un_subregion = df['UN_subregion'].values[0]
    un_subregion_wasting = who_wasting_data[who_wasting_data['UN_subregion'] == un_subregion]
    un_subregion_stunting = who_stunting_data[who_stunting_data['UN_subregion'] == un_subregion]
    un_subregion_stunting_under_2016 = un_subregion_stunting[un_subregion_stunting['year'] <= 2016]
    un_subregion_stunting_over_2016 = un_subregion_stunting[un_subregion_stunting['year'] >= 2016]

    un_subregion_wasting_trace = go.Scatter(
        x=un_subregion_wasting['year'],
        y=un_subregion_wasting['mean'],
        name='Wasting for {}'.format(un_subregion),
        marker=dict(
            color=WASTING_COLOR,
            line=dict(
                color=WASTING_COLOR,
                width=1.5)
        ),
        error_y=dict(
            type='data',
            symmetric=False,
            color=WASTING_COLOR,
            thickness=2.5,
            width=5,
            array=un_subregion_wasting['upper'] - un_subregion_wasting['mean'],
            arrayminus=un_subregion_wasting['mean'] - un_subregion_wasting['lower']
        )
    )

    un_subregion_stunting_trace = go.Scatter(
        x=un_subregion_stunting_under_2016['year'],
        y=un_subregion_stunting_under_2016['mean'],
        name='Stunting for {}'.format(un_subregion),
        marker=dict(
            color='#B0DEB2',
            line=dict(
                color='#B0DEB2',
                width=1.5)
        ),
        error_y=dict(
            type='data',
            symmetric=False,
            color='#B0DEB2',
            thickness=2.5,
            width=5,
            array=un_subregion_stunting_under_2016['upper'] - un_subregion_stunting_under_2016['mean'],
            arrayminus=un_subregion_stunting_under_2016['mean'] - un_subregion_stunting_under_2016['lower']
        )
    )

    un_subregion_stunting_trace_proj = go.Scatter(
        x=un_subregion_stunting_over_2016['year'],
        y=un_subregion_stunting_over_2016['mean'],
        name='Stunting projection for {}'.format(un_subregion),
        line=dict(
            shape='linear',
            dash='longdash'
        ),
        marker=dict(
            color='#B0DEB2',
            line=dict(
                color='#B0DEB2',
                width=1.5)
        ),
        error_y=dict(
            type='data',
            symmetric=False,
            color='#B0DEB2',
            thickness=2.5,
            width=5,
            array=un_subregion_stunting_over_2016['upper'] - un_subregion_stunting_over_2016['mean'],
            arrayminus=un_subregion_stunting_over_2016['mean'] - un_subregion_stunting_over_2016['lower']
        )
    )

    wasting_trace = go.Scatter(
        y=df[df['wasting'] > 0]['wasting'],  # negative values mean data not found
        x=df[df['wasting'] > 0]['year'],
        fill='tozeroy',
        line=dict(
            shape='linear',
            dash='longdash'
        ),
        marker=dict(
            color=WASTING_COLOR,
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        name='Wasting',
    )

    stunting_trace = go.Scatter(
        y=df[df['stunting'] > 0]['stunting'],  # negative values mean data not found
        x=df[df['stunting'] > 0]['year'],
        marker=dict(
            color=STUNTING_COLOR,
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        name='Stunting'
    )

    moderate_trace = go.Scatter(
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

    severe_trace = go.Scatter(
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
        'data': [wasting_trace, severe_trace, moderate_trace, stunting_trace, un_subregion_wasting_trace,
                 un_subregion_stunting_trace, un_subregion_stunting_trace_proj],
        'layout': go.Layout(
            barmode='overlay',
            showlegend=True,
            title='Malnutrition evolution',
        )

    }


@app.callback(
    Output('intermediate-funding-buffer', 'children'),
    [Input('country-dropdown', 'value'),
     Input('year-slider', 'value')])
def fill_intermediate_buffer(selected_iso_code, selected_year):
    country_funding_by_orga = fts_api.get_country_funding_by_orga(selected_iso_code, selected_year)
    data = fts_api.get_country_funding_for_year(selected_iso_code, selected_year)
    result = {'country_funding': country_funding_by_orga,
              'plans_funding': data}
    return json.dumps(result)


@app.callback(
    Output('country-funding', 'children'),
    [Input('intermediate-funding-buffer', 'children')])
def generate_funding_info(funding_data):
    data = json.loads(funding_data)['country_funding']
    if data['total_funded'] == 0:
        return ''

    return html.Div([
        html.H3('Nutrition funding details in the country'),
        html.P('Total funded for nutrition: {0}$'.format(format(data['total_funded'], ',')))
    ])


@app.callback(
    Output('funding-chart-sankey', 'children'),
    [Input('intermediate-funding-buffer', 'children')])
def generate_funding_chart_sankey(funding_data):
    data = json.loads(funding_data)['country_funding']
    funding_total = data['total_funded']
    if funding_total == 0:
        return ''
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

    return dcc.Graph(id='chart-sankey',
                     figure={
                         'data': [trace1],
                         'layout': go.Layout(
                             title='Funding source and destination for Nutrition(10 largest)'
                         )

                     })


@app.callback(
    Output('funding-chart-progress', 'children'),
    [Input('intermediate-funding-buffer', 'children')])
def generate_funding_chart_progress(funding_data):
    data = json.loads(funding_data)['plans_funding']
    if len(data['plans']) == 0:
        return ''
    trace1 = go.Bar(
        y=data['total_funded'],
        x=data['plans'],
        text=data['percentages'],
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

    return dcc.Graph(id='chart-progress',
                     figure={
                         'data': [trace1, trace2],
                         'layout': go.Layout(
                             barmode='overlay',
                             title='Funding progress for the country\'s emergency plans (Nutrition)'
                         )

                     })


@app.callback(
    Output('reports-list', 'children'),
    [Input('country-dropdown', 'value')])
def update_reports_list(iso_code):
    reports = reliefweb_api.get_reports_for_country(iso_code)
    if not reports:
        return ''
    images = [html.A(children=[
        html.Img(
            src=report['thumbnail'],
            style={'height': '180px',
                   'padding': '3',
                   'marginRight': 40,
                   'marginLeft': 40,
                   'boxShadow': '10px 10px 5px 0px #656565',
                   'background': '#FFF'}
        ),
        html.P(report['title'][0:50], style={'font-size': 'small', 'text-align': 'center'})
    ],
        href=report['file'],
        target='_blank')
        for report in reports]
    return html.Div([
        html.H3('Humanitarian Reports'),
        html.Div(children=images, style={
            'display': 'flex',
            'align': 'middle',
            'flexDirection': 'row',
            'justifyContent': 'center'
        })])


@app.callback(
    Output('wfp-funding-chart', 'children'),
    [Input('country-dropdown', 'value')])
def update_funding_chart_wfp(iso_code):
    return get_funding_chart_by_orga(iso_code, 'wfp')


@app.callback(
    Output('unicef-funding-chart', 'children'),
    [Input('country-dropdown', 'value')])
def update_funding_chart_unicef(iso_code):
    return get_funding_chart_by_orga(iso_code, 'unicef')


def get_funding_chart_by_orga(iso_code, organization):
    data = fts_api.get_country_funding_for_organization(iso_code, organization)
    if len(data['funding_source']) == 0:
        return ''
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
    return dcc.Graph(id=organization + '-chart-progress',
                     figure={
                         'data': [trace],
                         'layout': go.Layout(
                             title='Who is funding {0} (for Nutrition)'.format(organization.upper())
                         )

                     })
