# -*- coding: utf-8 -*-
from dash import html, dash_table

from utils import csv_reader

jme_data = csv_reader.get_simple_jme()
tender_awards_data = csv_reader.get_wfp_tender_awards().sort_values(['date'], ascending=False)

layout = html.Div(children=[
    html.H4(children='Joint Malnutrition Estimate Data'),

    html.Div([
        html.Div([
            dash_table.DataTable(
                data=jme_data.to_dict('records'),
                columns=[{"name": i, "id": i} for i in ['iso_code', 'country_name', 'UN_subregion', 'UN_region', 'year',
                         'severe_wasting', 'moderate_wasting', 'wasting', 'stunting', 'overweight', 'underweight',
                         'under5']],
                id='raw-datatable'
            )], className='twelve columns')
    ], className='row'),

    html.H4(children='WFP Tender Awards'),

    html.Div([
        html.Div([
            dash_table.DataTable(
                data=tender_awards_data.to_dict('records'),
                columns=[{"name": i, "id": i} for i in['date', 'supplier', 'product', 'amount_usd', 'tender_id', 'original_currency',
                         'original_amount', 'destination']],
                id='tender-datatable'
            )], className='twelve columns'),
    ], className='row')

])
