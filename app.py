import dash

from datasources import hdx_connect, scrap_wfp_tender, who_connect

app = dash.Dash(external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css',
                                      'https://codepen.io/chriddyp/pen/brPBPO.css',
                                      'https://use.fontawesome.com/releases/v5.0.8/css/solid.css',
                                      'https://use.fontawesome.com/releases/v5.0.8/css/fontawesome.css'
                                      ])
app.title = 'Nutriset - Market Monitor'
print('Fetching Data from HDX')
hdx_connect.main()
print('Fetching Data from WHO')
who_connect.main()
print('Scraping WFP Tender Awards data from WFP website')
scrap_wfp_tender.main()
server = app.server

app.config.suppress_callback_exceptions = True
