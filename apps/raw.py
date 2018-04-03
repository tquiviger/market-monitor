# -*- coding: utf-8 -*-
import dash_html_components as html
import dash_table_experiments as dt

from utils import csv_reader

jme_data = csv_reader.get_simple_jme()
tender_awards_data = csv_reader.get_wfp_tender_awards().sort_values(['date'], ascending=False)

layout = html.Div(children=[
    html.H4(children='Joint Malnutrition Estimate Data'),

    html.Div([
        html.Div([
            dt.DataTable(
                rows=jme_data.to_dict('records'),
                columns=['iso_code', 'country_name', 'UN_subregion', 'UN_region',
                         'severe_wasting', 'moderate_wasting', 'wasting', 'stunting', 'overweight', 'underweight',
                         'under5'],
                row_selectable=True,
                filterable=True,
                sortable=True,
                selected_row_indices=[],
                id='raw-datatable'
            )], className='twelve columns')
    ], className='row'),

    html.H4(children='WFP Tender Awards'),

    html.Div([
        html.Div([
            dt.DataTable(
                rows=tender_awards_data.to_dict('records'),
                columns=['date', 'supplier', 'product', 'amount_usd', 'tender_id', 'original_currency',
                         'original_amount', 'destination'],
                row_selectable=False,
                filterable=True,
                sortable=True,
                editable=False,
                selected_row_indices=[],
                id='tender-datatable'
            )], className='twelve columns'),
    ], className='row')

])
