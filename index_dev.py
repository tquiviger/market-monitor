import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output

from app import app
from apps import wfp#country, map, datatable, wfp, funding
from datasources.hdx_connect import get_jme_dataset

server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id="header", children=[
        html.Img(src='https://www.nutriset.fr/public/images/nutriset-logo.svg',
                 style={"height": "80px", "margin-right": "10px", "vertical-align": "middle"}),
        html.Div([html.H2('Market Monitoring')], className='twelve columns'),
    ], className='row', style={"display": "flex", "align-items": "center"}),
    dcc.Tabs(
        tabs=[
            {'label': 'Malnutrition Map', 'value': 'map'},
            {'label': 'Datatable', 'value': 'datatable'},
            {'label': 'Plans funding', 'value': 'funding'},
            {'label': 'Country Data', 'value': 'country'},
            {'label': 'WFP', 'value': 'wfp'}
        ],
        value='wfp',
        id='tabs'
    ),
    html.Div(id='page-content', className='container'),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),  # DONT DELETE ME
], style={"font-family": "Raleway,'helvetica neue',helvetica,sans-serif"}

)


@app.callback(Output('page-content', 'children'),
              [Input('tabs', 'value')])
def display_page(value):
    
    if value == 'wfp':
        return wfp.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
