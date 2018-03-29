# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import randomcolor

import api
from conf import nutriset_config
from utils import csv_reader

rand_color = randomcolor.RandomColor()


def get_funds_dataframe_for_orga(organization):
    flows = api.get_funding_for_orga_and_cluster(organization, 9)['flows']
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

    wfp['aggregate_date'] = wfp.apply(get_month, axis=1)
    wfp['year'] = wfp.apply(get_year, axis=1)
    wfp = wfp[wfp['year'] >= '2015']

    wfp: pd.DataFrame = wfp.groupby(by=['organization', 'year', 'aggregate_date'])[
        'amount'].sum().reset_index()

    wfp = wfp.sort_values('aggregate_date')
    wfp['year_cumul'] = wfp.groupby(by=['organization', 'year'])['amount'].apply(lambda x: x.cumsum())

    # Tender data
    tender = csv_reader.get_wfp_tender_awards()
    tender = tender[tender['date'] >= '2015-01']

    tender: pd.DataFrame = tender.groupby(by=['date', 'product_type'])['amount'].sum().reset_index()

    funding_trace = go.Bar(
        x=wfp['aggregate_date'],
        y=wfp['amount'],
        marker=dict(
            color='#1aa3ff'
        ),
        name='Funding'
    )

    cumul_trace = go.Scatter(
        x=wfp['aggregate_date'],
        y=wfp['year_cumul'],
        line=dict(
            dash='longdash'
        ),
        marker=dict(
            color='#005c99'
        ),
        name='Funding - Cumul Paid'
    )

    tender_sam = tender[tender['product_type'] == 'severe_wasting']
    tender_mam = tender[tender['product_type'] == 'moderate_wasting']
    tender_stunting = tender[tender['product_type'] == 'stunting']

    tender_trace_sam = go.Bar(
        x=tender_sam['date'],
        y=tender_sam['amount'],
        marker=dict(
            color=nutriset_config.SEVERE_WASTING_COLOR
        ),
        name='Tender - SAM'
    )

    tender_trace_mam = go.Bar(
        x=tender_mam['date'],
        y=tender_mam['amount'],
        marker=dict(
            color=nutriset_config.MODERATE_WASTING_COLOR
        ),
        name='Tender - SAM'
    )

    tender_trace_stunting = go.Bar(
        x=tender_stunting['date'],
        y=tender_stunting['amount'],
        marker=dict(
            color=nutriset_config.STUNTING_COLOR
        ),
        name='Tender - Stunting'
    )

    return [funding_trace, cumul_trace, tender_trace_sam, tender_trace_mam, tender_trace_stunting]


def generate_sankey_chart():
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
        dcc.Graph(
            id='funding-chart-history',
            figure={
                'data': generate_flow_history_chart(),
                'layout': go.Layout(
                    width=1000,
                    height=772,

                    title='Nutrition and Food Security Funding history'
                )

            })
    ], className='twelve columns'),
    html.Div([
        dcc.Graph(
            id='funding-chart-wfp-sankey',
            figure={
                'data': [generate_sankey_chart()],
                'layout': go.Layout(
                    width=1000,
                    height=772,
                    title='WFP Funding source and destination (20 largest)'
                )

            })

    ], className='twelve columns'),
    html.Div([
        html.Iframe(
            width=1000,
            height=500,
            src='//data.humdata.org/widget/WFP?type=WFP&datastore_id=bd88a565-bf6f-4827-b07b-fb3a65bbb01a&data_link_url=https%3A%2F%2Fdata.humdata.org%2Fdataset%2Fwfp-food-prices&embedded=true&title=Food+Market+Prices')

    ])
], className='row twelve columns')
