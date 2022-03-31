# -*- coding: utf-8 -*-
from dash import dcc
from dash import html
import pandas as pd
import plotly.graph_objs as go
import randomcolor

from api import fts_api
from conf import nutriset_config
from utils import csv_reader, functions

rand_color = randomcolor.RandomColor()

suppliers = [
    {'name': 'NUTRISET', 'color': nutriset_config.NUTRISET_COLOR},
    {'name': 'EDESIA', 'color': '#48C9B0'},
    {'name': 'HILINA', 'color': '#45B39D'},
    {'name': 'JB', 'color': '#52BE80'},
    {'name': 'NUTRIVITA', 'color': '#58D68D'},
    {'name': 'COMPACT', 'color': '#F4D03F'},
    {'name': 'DIVA', 'color': '#F5B041'},
    {'name': 'INSTA', 'color': '#EB984E'},
    {'name': 'ISMAIL', 'color': '#DC7633'},
    {'name': 'MANA', 'color': '#CD6155'},
    {'name': 'OKI', 'color': '#CD6155'},
    {'name': 'DEVESH', 'color': '#CD6155'},
    {'name': 'INNOFASO', 'color': '#CD6155'},
    {'name': 'STA', 'color': '#CD6155'},
]


def get_funds_dataframe_for_orga(organization):
    flows = fts_api.get_nutrition_funding_for_orga(organization)['flows']
    x = []
    y = []
    z = []
    for flow in flows:
        x.append(flow['date'])
        y.append(flow['amountUSD'])
        z.append(flow['status'])
    return pd.DataFrame(data={
        'date': x,
        'amount': y,
        'status': z,
        'organization': organization})


def get_month(row):
    if row['date'].month < 10:
        return str(row['date'].year) + '-0' + str(row['date'].month)
    else:
        return str(row['date'].year) + '-' + str(row['date'].month)


def get_year(row):
    return str(row['date'].year)


def get_market_share(row):
    return "{0:.1f}".format(row.amount_usd / row.year_total * 100)


def get_aggregate_date(row):
    if row['date'].month == 1 and row['date'].week == 52:
        return str(row['date'].year) + '-01'
    else:
        return str(row['date'].year) + '-' + str(row['date'].week)


def generate_flow_history_chart():
    # Funds data
    wfp = get_funds_dataframe_for_orga('wfp')
    wfp: pd.DataFrame = wfp.astype(dtype={"date": "datetime64[ns]",
                                          "amount": "int64",
                                          "status": "str",
                                          "organization": "str"})

    if not wfp.empty:
        wfp['aggregate_date'] = wfp.apply(get_month, axis=1)
        wfp['year'] = wfp.apply(get_year, axis=1)
        wfp = wfp[wfp['year'] >= '2015']

        wfp: pd.DataFrame = wfp.groupby(by=['organization', 'year', 'aggregate_date'])[
            'amount'].sum().reset_index()

        wfp = wfp.sort_values('aggregate_date')

        funding_trace = go.Bar(
            x=wfp['aggregate_date'],
            y=wfp['amount'],
            marker=dict(
                color='#1aa3ff'
            ),
            name='Funding'
        )
    else:
        funding_trace = []

    # Tender data
    tender = csv_reader.get_wfp_tender_awards()
    tender = tender[tender['date'] >= '2015-01']

    tender: pd.DataFrame = tender.groupby(by=['date'])['amount_usd'].sum().reset_index()
    tender['date'] = pd.to_datetime(tender['date'], format='%Y/%m')
    tender_trace = go.Bar(
        x=tender['date'],
        y=tender['amount_usd'],
        marker=dict(
            color=nutriset_config.WASTING_COLOR
        ),
        name='Tender'
    )

    return [funding_trace, tender_trace]


def generate_market_shares_chart():
    # Tender data
    tender = csv_reader.get_wfp_tender_awards()
    tender: pd.DataFrame = tender.groupby(by=['year', 'supplier'])['amount_usd'].sum().reset_index()

    year_cumul = (
        tender.groupby(by=['year'])['amount_usd'].sum().reset_index().rename(columns={'amount_usd': 'year_total'}))
    tender = pd.merge(tender, year_cumul, how='left', on=['year'])
    tender['market_share'] = tender.apply(get_market_share, axis=1)

    traces = []

    for supplier in suppliers:
        tenders_for_year = tender[tender['supplier'] == supplier['name']]
        bar_text = ''
        if supplier['name'] == 'NUTRISET':
            bar_text = tenders_for_year.market_share + ' %'
        traces.append(
            go.Bar(
                x=tenders_for_year.year,
                y=tenders_for_year.market_share,
                textposition='auto',
                text=bar_text,
                name=supplier['name'],
                marker=dict(
                    color=supplier['color']),
            ))
    return traces


def generate_tenders_chart():
    # Tender data
    tender = csv_reader.get_wfp_tender_awards()
    tender: pd.DataFrame = tender.groupby(by=['year', 'supplier'])['amount'].sum().reset_index()

    year_cumul = (tender.groupby(by=['year'])['amount'].sum().reset_index().rename(columns={'amount': 'year_total'}))
    tender = pd.merge(tender, year_cumul, how='left', on=['year'])
    tender['market_share'] = tender.apply(get_market_share, axis=1)

    traces = []
    for supplier in tender.supplier.unique():
        tenders_for_year = tender[tender['supplier'] == supplier]
        traces.append(
            go.Bar(
                x=tenders_for_year.year,
                y=tenders_for_year.market_share,
                name=supplier
            ))

    return traces


def generate_sankey_chart():
    data = fts_api.get_wfp_funding()
    funding_total = data['total_funded']
    i = 1
    sources = []
    targets = []
    values = []
    colors = ["black"]
    labels = ['WFP']
    link_labels = []
    for funding_source in sorted(data['funding_source'], key=lambda x: x['totalFunding'], reverse=True)[:15]:
        sources.append(i)
        targets.append(0)
        values.append(funding_source['totalFunding'])
        labels.append(funding_source['name'])
        link_labels.append('{:02.2f}%'.format(funding_source['totalFunding'] / funding_total * 100))
        colors.append(rand_color.generate(hue='orange')[0])
        i = i + 1
    for funding_dest in sorted(data['funding_destination'], key=lambda x: x['totalFunding'], reverse=True)[:15]:
        sources.append(0)
        targets.append(i)
        values.append(funding_dest['totalFunding'])
        labels.append(funding_dest['name'])
        link_labels.append('{:02.2f}%'.format(funding_dest['totalFunding'] / funding_total * 100))
        colors.append(rand_color.generate(hue='blue')[0])
        i = i + 1
    trace = go.Sankey(
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

    return trace


def get_style(supplier):
    if supplier == 'NUTRISET':
        return {'color': nutriset_config.NUTRISET_COLOR, 'font-weight': 'bolder'}
    else:
        return {}


def get_color(product_tye):
    if product_tye == 'severe_wasting':
        return nutriset_config.SEVERE_WASTING_COLOR
    elif product_tye == 'moderate_wasting':
        return nutriset_config.MODERATE_WASTING_COLOR
    elif product_tye == 'stunting':
        return nutriset_config.STUNTING_COLOR
    return '#000'


def display_original_amount(tender):
    if tender['original_currency'] != 'USD':
        return functions.format_number(tender['original_amount']) + ' ' + tender['original_currency']
    else:
        return ''


def get_tenders_table():
    return html.Table([
        html.Tbody([html.Tr([
            html.Th(tender['date']),
            html.Td(tender['tender_id']),
            html.Td(tender['supplier'], style=get_style(tender['supplier'])),
            html.Td(tender['product'], style={'color': get_color(tender['product_type'])}),
            html.Td(functions.format_number(tender['amount_usd']) + ' USD'),
            html.Td(display_original_amount(tender)),
            html.Td(tender['destination'])
        ]) for index, tender in
            csv_reader
                .get_wfp_tender_awards()
                .sort_values(['date'], ascending=False)
                .iterrows()], style={
            'display': 'block',
            'height': '500px',
            'overflow-y': 'scroll',
            'overflow-x': 'hidden'})
    ], style={'font-size': 'x-small'})


layout = html.Div([
    html.Div([
        dcc.Graph(
            id='market-shares',
            figure={
                'data': generate_market_shares_chart(),
                'layout': go.Layout(
                    barmode='relative',
                    title='WFP Market shares of RUF suppliers'
                )

            })
    ], className='twelve columns'),
    html.Div([
        html.H4('Tender Awards for WFP RUF suppliers 2012-2022'),
        get_tenders_table(),
        dcc.Graph(
            id='funding-chart-history',
            figure={
                'data': generate_flow_history_chart(),
                'layout': go.Layout(
                    height=772,
                    title='Nutrition Funding history'
                )

            })
    ], className='twelve columns'),
    html.Div([
        dcc.Graph(
            id='funding-chart-wfp-sankey',
            figure={
                'data': [generate_sankey_chart()],
                'layout': go.Layout(
                    height=772,
                    title='WFP Funding source and destination (15 largest)'
                )

            })

    ], className='twelve columns'),
    html.Div([
        html.H4('WFP Market Prices Explorer'),
        html.Iframe(
            width=900,
            height=500,
            src='//data.humdata.org/widget/WFP?type=WFP&datastore_id=bd88a565-bf6f-4827-b07b-fb3a65bbb01a&data_link_url=https%3A%2F%2Fdata.humdata.org%2Fdataset%2Fwfp-food-prices&embedded=true&title=Food+Market+Prices')

    ])
])
