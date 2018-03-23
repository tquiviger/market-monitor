import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output

from app import app
from apps import country, map, datatable, wfp, funding
from hdx_connect import get_jme_dataset

server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.Div([html.H1('Market Monitor')], className='four columns', style={'text-align': 'left'}),
        html.Div([
            html.P('HDX Data updated on : {}'.format(get_jme_dataset().get_dataset_date()))], className='eight columns',
            style={'text-align': 'right', 'margin-top': '10'})
    ], className='row'),
    dcc.Tabs(
        tabs=[
            {'label': 'Malnutrition Map', 'value': 'map'},
            {'label': 'Datatable', 'value': 'datatable'},
            {'label': 'Plans funding', 'value': 'funding'},
            {'label': 'Country Data', 'value': 'country'},
            {'label': 'WFP', 'value': 'wfp'}
        ],
        value='map',
        id='tabs'
    ),
    html.Div(id='page-content'),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
])


@app.callback(Output('page-content', 'children'),
              [Input('tabs', 'value')])
def display_page(value):
    if value == 'datatable':
        return datatable.layout
    elif value == 'country':
        return country.layout
    elif value == 'map':
        return map.layout
    elif value == 'funding':
        return funding.layout
    elif value == 'wfp':
        return wfp.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
