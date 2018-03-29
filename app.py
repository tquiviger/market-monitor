import dash

from datasources import hdx_connect, scrap_wfp_tender

app = dash.Dash()
print('Fetching JME data from hdx')
hdx_connect.main()
print('Scraping WFP Tender Awards data from WFP website')
scrap_wfp_tender.main()
server = app.server
app.config.suppress_callback_exceptions = True
app.css.append_css({
    'external_url': ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                     'https://codepen.io/chriddyp/pen/brPBPO.css',
                     'https://use.fontawesome.com/releases/v5.0.8/css/solid.css',
                     'https://use.fontawesome.com/releases/v5.0.8/css/fontawesome.css'
                     ]
})
