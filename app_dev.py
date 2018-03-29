import dash

app = dash.Dash()
server = app.server
app.config.suppress_callback_exceptions = True
app.css.append_css({
    'external_url': ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                     'https://codepen.io/chriddyp/pen/brPBPO.css',
                     'https://use.fontawesome.com/releases/v5.0.8/css/solid.css',
                     'https://use.fontawesome.com/releases/v5.0.8/css/fontawesome.css'
                     ]
})
