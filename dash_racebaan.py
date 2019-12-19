# %%
'''
TODO
- Realtime naar 15 minuten vanaf nu
- click event ipv hoverevent

DONE
- Zelfde vrachtwagen minder vaak meetellen --> gemiddelde per punt
- verschillende zooms --> van segment naar wegniveau en linkerbaan/rechterbaan
- Resetten of niet na actie
- Alleen data in graph bekijken. Hoge zoom niveaus dus alleen lokale data
- Naar CSS kijken
- Daily or hourly mode
- Buttons etc op de goede plek
- Bootstrap components
- Nederlands of engels? --> Nederlands
- Stresstest --> bij 250.000 records werkt het nog steeds best prima
- Monitoring mode with https://dash.plot.ly/live-updates
- denken over einddatum
- dynamic layout
- maxzoom=12 --> is er niet, nu laat ie een lege kaart zien
- click event ipv hoverevent

'''
# %%
import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.graph_objs as go

from dash_project_functions import get_color, get_linewidth, determine_bbox, read_input_csv

# Set paths/filenames etc
filename = 'ADRoutput.csv'

# Read csv file
# First read is done here, some variables are extracted from this
# Afterwards, updated every minute in def update_data
df = read_input_csv(filename)

# converting to json format
df_json = df.to_json(date_format='iso', orient='split')

# Get first and last timestamp, in order to get first and last dates and times
# First from the data and last is current time
mn = min(df['timestamp'])
mx = pd.to_datetime(datetime.datetime.now())

# Zoom pixel distance curve
# Fit on zoom levels and meter/pixel values as specified by:
# https://docs.mapbox.com/help/glossary/zoom-level/
# Values for lat of 50 (middle between 40 and 60)
ZOOM_CURVE = np.poly1d(np.polyfit([8, 9, 10, 11, 12], [193.5, 96.5, 48.5, 24, 12.5], 3))

START_LON=df.loc[df.first_valid_index(),'lon']
START_LAT=df.loc[df.first_valid_index(),'lat']

# %%
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport",
         "content": "width=device-width, initial-scale=1.0"}
    ],
)

app.layout = html.Div(
    children=[
        html.Div(
            id="body",
            # className="container scalable",
            children=[
                html.Div(
                    className="two columns",
                    id="left-column",
                    children=[
                        # Two breaks to get it on the save level
                        # as the graph block
                        html.Br(),
                        html.Br(),
                        # Group to select the mode of the graph
                        dbc.FormGroup([
                            dbc.Label('Kies een mode: '),
                            dbc.RadioItems(
                                id='mode',
                                options=[{'label': i, 'value': i} for i in ['Realtime', 'Alles']],
                                value='Alles',
                                labelStyle={'display': 'inline-block'},
                                )
                            ]),
                        html.Br(),
                        # Group to select the GEVI codes
                        dbc.FormGroup([
                            dbc.Label('Kies GEVI codes: '),
                            dcc.Dropdown(
                                id='gevi_selector',
                                options=[{'label': i, 'value': i} for i in np.sort(df['gevi'].unique())],
                                multi=True,
                                value=[]),
                            ]),
                        html.Br(),
                        dbc.FormGroup(
                            id='date_formgroup',
                            children=[
                                dbc.Label('Kies start en eind datum:'),
                                dcc.DatePickerSingle(
                                    id="start_date",
                                    min_date_allowed=datetime.datetime(
                                        mn.year, mn.month, mn.day),
                                    max_date_allowed=datetime.datetime(
                                        mx.year, mx.month, mx.day),
                                    initial_visible_month=datetime.datetime(
                                        mn.year, mn.month, mn.day),
                                    date=datetime.datetime(
                                        mn.year, mn.month, mn.day),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                ),
                                dcc.DatePickerSingle(
                                    id="end_date",
                                    min_date_allowed=datetime.datetime(
                                        mn.year, mn.month, mn.day),
                                    max_date_allowed=datetime.datetime(
                                        mx.year, mx.month, mx.day),
                                    initial_visible_month=datetime.datetime(
                                        mx.year, mx.month, mx.day),
                                    date=datetime.datetime(
                                        mx.year, mx.month, mx.day),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                    ),
                                ],
                            ),
                        html.Br(),
                        # Checkboxes to determine the filtering
                        dbc.FormGroup([
                            dbc.Label('Kies filter detail:'),
                            dbc.Checklist(
                                id='filteroptions',
                                options=[
                                    {"label": "Gemiddeld dagelijks patroon", "value": 'daily'},
                                    {"label": "Alleen specifieke uren", "value": 'hourly'},
                                    ],
                                labelStyle={'display': 'inline-block'},
                                value=[]
                                )
                            ]),
                        html.Br(),
                        dbc.FormGroup(
                            id='hour_formgroup',
                            children=[
                                dbc.Label('Uren tussen:'),
                                dcc.RangeSlider(
                                    id='hour-slider',
                                    count=1,
                                    min=0,
                                    max=24,
                                    step=1,
                                    marks={i: '{}:00'.format(i) for i in range(0, 28, 4)},
                                    value=[0, 24]
                                    ),
                                html.Br(),
                                ], style={"display": "none"}
                            ),
                        dbc.FormGroup([
                            dcc.Interval(
                                id='interval-component',
                                interval=60*1000, # in milliseconds, every minute
                                n_intervals=0
                                )
                            ]),
                        ],
                    style={'marginLeft': '1em'}
                    ),
                html.Div(
                    className="nine columns",
                    children=[
                        html.H2(
                            id="banner-title",
                            children=[
                                html.A(
                                    "Intensiteit van vrachtwagens met gevaarlijke stoffen over de Nederlandse snelwegen",
                                    href="https://github.com/Killaars/CBS3",
                                    style={
                                        "text-decoration": "none",
                                        "color": "inherit",
                                    },
                                )
                            ],
                        ),
                        html.Div(children=[
                            dcc.Graph(id='mapbox_graph',
                                      clickData={'points': [{'lat': START_LAT, 'lon': START_LON}]},
                                      hoverData={'points': [{'lat': START_LAT, 'lon': START_LON}]},
                                      relayoutData={'mapbox.zoom': 6.5},
                                      )
                            ],
                            style={'width': '69%', 'display': 'inline-block', 'padding': '0 20'}
                            ),
                        html.Div(children=[
                            dcc.Graph(id='timeseries')],
                            style={'display': 'inline-block', 'width': '29%', 'vertical-align': 'top'}
                            ),
                        ]
                    ),
                ]
            ),
        # Hidden div inside the app that stores the refreshed data
        # Updated every minute
        html.Div(id='refreshed_data', style={'display': 'none'}),
        # Hidden div inside the app that stores the filtered data
        html.Div(id='filtered_data',
                 style={'display': 'none'}),
        ]
    )


@app.callback(Output('refreshed_data', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_data(n_intervals):
    '''
    Check the file for new data every minute
    '''
    new_df = read_input_csv(filename)
    return new_df.to_json(date_format='iso', orient='split')


@app.callback(Output('hour_formgroup', 'style'),
              [Input('filteroptions', 'value')])
def show_hours(filteroptions):
    '''
    Only show hourly if it makes sense
    '''
    if 'hourly' in filteroptions:
        to_return = {}
    else:
        to_return = {'display': 'none'}
    return to_return


@app.callback(
    Output('filtered_data', 'children'),
    [Input('mode', 'value'),
     Input('gevi_selector', 'value'),
     Input('start_date', 'date'),
     Input('end_date', 'date'),
     Input('mapbox_graph', 'relayoutData'),
     Input('filteroptions', 'value'),
     Input('hour-slider', 'value'),
     Input('refreshed_data', 'children'),
     ])
def filter_data(selected_mode,
                selected_gevi,
                start_date,
                end_date,
                relayoutdata,
                filteroptions,
                hourslider,
                jsonified_refreshed_data):
    '''
    Filter data callback
    Reads refreshed data given by update_data
    Filters and stores the df as json, other graphs can use it as input
    '''
    # Load data from hidden div, if possible
    try:
        dff = pd.read_json(jsonified_refreshed_data, orient='split')
    except:
        dff = pd.read_json(df_json, orient='split')

    # Realtime
    if selected_mode == 'Realtime':
        timecutoff = datetime.datetime.now() - datetime.timedelta(minutes=15)
        filtered_df = dff[dff['timestamp'] >= timecutoff]

    # Aggregated
    if selected_mode == 'Alles':
        filtered_df = dff.copy()

        # Daily filtering --> between or equal to start/end date
        filtered_df = filtered_df[(filtered_df['timestamp'] >= start_date) &
                                  (filtered_df['timestamp'] <= end_date)]

        # Hourly filtering --> Between certain hours, irrespective of date
        if 'hourly' in filteroptions:
            index = pd.DatetimeIndex(filtered_df['timestamp'])
            begin_time = '%s:00' % (hourslider[0])
            end_time = '%s:00' % (hourslider[1])
            if hourslider[1] == 24:
                end_time = '23:59'
            filtered_df = filtered_df.iloc[index.indexer_between_time(begin_time, end_time)]

    # Filter gevi codes based on selection
    if len(selected_gevi) > 0:
        filtered_df = filtered_df[filtered_df['gevi'].isin(selected_gevi)]

        return filtered_df.to_json(date_format='iso', orient='split')


# Update main figure callback
@app.callback(
    Output('mapbox_graph', 'figure'),
    [Input('filtered_data', 'children'),
     Input('mapbox_graph', 'relayoutData'),
     ])
def update_figure(jsonified_filtered_data, relayoutdata):
    '''
    Builds mapbox graph graph. Uses filtered data from filter_data.
    Calculates intensity for the road pieces and determines color and
    linewidth based on this
    '''

    # Add default zoom if not present in relayoutData
    if 'mapbox.zoom' not in relayoutdata:
        relayoutdata['mapbox.zoom'] = 6.5
    print(relayoutdata)
    # Load data from hidden div, if possible
    try:
        dff = pd.read_json(jsonified_filtered_data, orient='split')
    except:
        dff = pd.read_json(df_json, orient='split')
        
    plot_data = [go.Scattermapbox(lat=[dff.loc[dff.first_valid_index(),'lat']],
                             lon=[dff.loc[dff.first_valid_index(),'lon']],
                              mode='markers',
                              text=len(df),
                              marker=dict(size=10,
                                             color='#000000',
                                             showscale=False)
                             )]

    # Returns plot_data as data part of plotly graph and filled layout
    return {
        "data": plot_data,
        "layout": dict(
            # autosize = True,
            height=800,
            legend=dict(orientation="h"),
            plot_bgcolor="#1E1E1E", paper_bgcolor="#1E1E1E",
            font=dict(color="#d8d8d8"),
            hovermode="closest",
            margin=dict(l=0, r=0, t=0, b=0),
            # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            mapbox=dict(
                uirevision='no reset of zoom',
                # bearing = 0,
                center=dict(
                    lon=dff.loc[dff.first_valid_index(),'lon'],
                    lat=dff.loc[dff.first_valid_index(),'lat']),
                style="open-street-map",
                # pitch = 0,
                zoom=6.7,
            )
        )
    }


@app.callback(
        Output('timeseries', 'figure'),
        [Input('filtered_data', 'children'),
         Input('mapbox_graph', 'clickData'),
         Input('filteroptions', 'value'),
         ])
def timeseries_graph(jsonified_filtered_data, clickdata, filteroptions):
    '''
    Builds timeseries graph. Uses clickData to select camera point and filtered data from filter_data
    '''
    # Load data from hidden div, if possible
    try:
        dff = pd.read_json(jsonified_filtered_data, orient='split')
    except:
        dff = pd.read_json(df_json, orient='split')
    lat = np.round(clickdata['points'][0]['lat'], 4)
    lon = np.round(clickdata['points'][0]['lon'], 4)

    # Build timeseries for location
    timeseries_to_plot = dff[(dff['lat'] == lat) & (dff['lon'] == lon)].copy()
    
    # Maak 1-hot zodat elke code een bar krijgt
    timeseries_to_plot = dff[['gevi','road']]
    timeseries_to_plot = pd.get_dummies(timeseries_to_plot['gevi'])
    timeseries_to_plot['road'] = dff['road']
    
    # Grouperen op timestamp 
    timeseries_to_plot = timeseries_to_plot.groupby(timeseries_to_plot['road']).sum()
    timeseries_to_plot.index.names = ['index']    


    # store it as data variable for the plot
    data = [{'x': timeseries_to_plot.index, 'y':timeseries_to_plot[column], 'type': 'bar', 'name': column, 'showlegend': True} for column in timeseries_to_plot.columns]

    layout = dict(
                title='Tijdserie voor locatie %s, %s' % (lat, lon),
                plot_bgcolor="#1E1E1E", paper_bgcolor="#1E1E1E",
                font=dict(color="#d8d8d8"),
                xaxis=dict(title='Aantal vrachtwagens per weghelft')
                )


    return {
        'data': data,
        'layout': layout
        }


app.run_server(debug=True)
