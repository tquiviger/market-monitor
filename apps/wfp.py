# -*- coding: utf-8 -*-
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import api
import randomcolor

rand_color = randomcolor.RandomColor()


def generate_flow_history_chart():
    flows = api.get_all_nut_and_fs_funding('wfp')['flows']
    x = []
    y = []

    for flow in flows:
        x.append(flow['date'])
        y.append(flow['amountUSD'])

    trace1 = go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=dict(
            line=dict(
                color='rgb(8,48,107)',
                width=1.5)
        ),
        name='Moderate Wasting'
    )

    flows = api.get_all_nut_and_fs_funding('unicef')['flows']
    x = []
    y = []

    for flow in flows:
        x.append(flow['date'])
        y.append(flow['amountUSD'])

    trace2 = go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=dict(
            line=dict(
                color='#ff9900',
                width=1.5)
        ),
        name='Moderate Wasting'
    )

    return [trace1, trace2]


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
    # html.Div([
    #     dcc.Graph(
    #         id='funding-chart-history',
    #         figure={
    #             'data': generate_flow_history_chart(),
    #             'layout': go.Layout(
    #                 yaxis=dict(
    #                     type='log',
    #                     autorange=True
    #                 ),
    #                 width=1118,
    #                 height=772,
    #                 title='Nutrition and Food Security Funding for 2018'
    #             )
    #
    #         })
    #
    # ], className='eight columns'),
    html.Div([
        dcc.Graph(
            id='funding-chart-wfp-sankey',
            figure={
                'data': [generate_sankey_chart()],
                'layout': go.Layout(
                    width=1200,
                    height=772,
                    title='WFP Funding source and destination (20 largest)'
                )

            })

    ], className='eight columns'),
    html.Div([
        html.Iframe(
            width="1200px",
            height="500px",
            src='//data.humdata.org/widget/WFP?type=WFP&datastore_id=bd88a565-bf6f-4827-b07b-fb3a65bbb01a&data_link_url=https%3A%2F%2Fdata.humdata.org%2Fdataset%2Fwfp-food-prices&embedded=true&title=Food+Market+Prices')

    ], className='twelve columns')
], className='row')
