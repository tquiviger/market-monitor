from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

from app import app
from apps import country, map, datatable

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Tabs(
        tabs=[
            {'label': 'Malnutrition Map', 'value': 'map'},
            {'label': 'Datatable', 'value': 'datatable'},
            {'label': 'Country Data', 'value': 'country'}
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
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
