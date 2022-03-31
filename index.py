import getopt
import sys

from dash import html, dcc, dash_table, Input, Output

from app import app
from apps import about, country, funding, map, raw, wfp

server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id="header", children=[
        html.Img(src='https://www.nutriset.fr/public/images/nutriset-logo.svg',
                 style={"height": "80px", "margin-right": "10px", "vertical-align": "middle"}),
        html.Div([html.H2('Market Monitoring')], className='twelve columns'),
    ], className='row', style={"display": "flex", "align-items": "center"}),
    dcc.Tabs(
        children=[
            dcc.Tab(label= 'Malnutrition Map', value= 'map'),
            dcc.Tab(label= 'Raw Data', value= 'raw'),
            dcc.Tab(label= 'Country Data', value= 'country'),
            dcc.Tab(label= 'WFP', value= 'wfp'),
            dcc.Tab(label= 'Plans funding', value= 'funding'),
            dcc.Tab(label= 'About', value= 'about')
        ],
        value='map',
        id='tabs'
    ),
    html.Div(id='page-content', className='container'),
    html.Div(dash_table.DataTable(data=[{}]), style={'display': 'none'}),  # DONT DELETE ME
], style={"font-family": "Montserrat,sans-serif"}

)


@app.callback(Output('page-content', 'children'),
              [Input('tabs', 'value')])
def display_page(value):
    if value == 'raw':
        return raw.layout
    elif value == 'country':
        return country.layout
    elif value == 'map':
        return map.layout
    elif value == 'funding':
        return funding.layout
    elif value == 'wfp':
        return wfp.layout
    elif value == 'about':
        return about.layout
    else:
        return '404'


if __name__ == '__main__':
    debug = False
    usage = 'index.py  [-d]'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d")
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("-d", "--debug"):
            print('Debug Mode')
            debug = True

    app.run_server(debug=debug)
