# -*- coding: utf-8 -*-
import datetime

import dash_html_components as html

from datasources import hdx_connect

layout = html.Div(children=[

    html.H4('Data Sources'),
    html.Table([
        html.Thead([
            html.Tr([
                html.Th('Dataset'),
                html.Th('Source'),
                html.Th('Type'),
                html.Th('Files'),
                html.Th('Last Update')
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td('Joint Malnutrition Estimate (UNICEF, WB, WHO)'),
                html.Td(html.A('Humanitarian Data Exchange',
                               href='https://data.humdata.org/', target='_blank')),
                html.Td('CSV File'),
                html.Td(html.A('https://data.humdata.org/dataset/'
                               'child-malnutrition-joint-country-dataset-unicef-who-world-bank-group-2017',
                               href='https://data.humdata.org/dataset/'
                                    'child-malnutrition-joint-country-dataset-unicef-who-world-bank-group-2017',
                               target='_blank')),
                html.Td(hdx_connect.get_jme_dataset().get_dataset_date())
            ]),
            html.Tr([
                html.Td('Relief Web Data'),
                html.Td(html.A('Humanitarian Data Exchange',
                               href='https://data.humdata.org/', target='_blank')),
                html.Td('CSV File'),
                html.Td(html.A('https://data.humdata.org/dataset/'
                               'reliefweb-crisis-app-data',
                               href='https://data.humdata.org/dataset/'
                                    'reliefweb-crisis-app-data',
                               target='_blank')),
                html.Td(hdx_connect.get_reliefweb_dataset().get_dataset_date())
            ]),
            html.Tr([
                html.Td('Relief Web Reports'),
                html.Td(html.A('Relief Web API',
                               href='https://reliefweb.int/help/api', target='_blank')),
                html.Td('API'),
                html.Td('N/A'),
                html.Td(datetime.datetime.now().strftime("%Y-%m-%d"))
            ]),

            html.Tr([
                html.Td('Fundings'),
                html.Td(html.A('FTS',
                               href='https://fts.unocha.org/content/fts-public-api', target='_blank')),
                html.Td('API'),
                html.Td('N/A'),
                html.Td(datetime.datetime.now().strftime("%Y-%m-%d"))
            ]),
            html.Tr([
                html.Td('WFP Tender Awards'),
                html.Td(html.A('WFP Tender Awards',
                               href='https://www.wfp.org/procurement/food-tender-awards', target='_blank')),
                html.Td('Webpage'),
                html.Td('N/A'),
                html.Td('Unknown')
            ])
        ])
    ], style={'font-size': 'small'}),

], className='twelve columns')
