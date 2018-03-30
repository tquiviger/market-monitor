# -*- coding: utf-8 -*-
import dash_html_components as html

from datasources import hdx_connect

layout = html.Div(children=[

    html.H4('Data Sources : '),
    html.P([
        html.A('Humanitarian Data Exchange',
               href='https://data.humdata.org/dataset/'
                    'child-malnutrition-joint-country-dataset-unicef-who-world-bank-group-2017'),
        ' (Data updated on: {})'.format(hdx_connect.get_jme_dataset().get_dataset_date())]),
    html.P(
        html.A('FTS',
               href='https://fts.unocha.org/')),
    html.P([
        html.A('Relief Web',
               href='https://reliefweb.int/'),
        ' (Data updated on: {})'.format(hdx_connect.get_reliefweb_dataset().get_dataset_date())]),
    html.P(
        html.A('WFP Tender Awards',
               href='https://www.wfp.org/procurement/food-tender-awards')),

], className='twelve columns')
