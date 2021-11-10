import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from Calendar import *

CALENDARS = {
    'PhD': 'https://outlook.live.com/owa/calendar/00000000-0000-0000-0000-000000000000/d13b4415-57b7-4152-89ef-6f707880cccd/cid-59D903F0133C1A64/calendar.ics',
    'MITACS': 'https://outlook.live.com/owa/calendar/00000000-0000-0000-0000-000000000000/de8b5359-dacc-4030-a70e-f8cb020cdc7a/cid-59D903F0133C1A64/calendar.ics',
    'Green Network Planning': 'https://outlook.live.com/owa/calendar/00000000-0000-0000-0000-000000000000/9121c110-4043-49ef-a0ce-3018a3670c1f/cid-59D903F0133C1A64/calendar.ics',
    'UPAL': 'https://outlook.live.com/owa/calendar/00000000-0000-0000-0000-000000000000/666b5775-d4a8-48f8-bb5b-b08bdfa9c2cc/cid-59D903F0133C1A64/calendar.ics',
    'elementslab': 'https://outlook.live.com/owa/calendar/8fd2720a-5774-41df-90e9-fa8ff7cc3cbf/1b14feb2-a841-4f74-ae70-496436c6da96/cid-59D903F0133C1A64/calendar.ics',
    'Portfolio': 'https://outlook.live.com/owa/calendar/00000000-0000-0000-0000-000000000000/491714b4-dc60-421d-9cf7-cb2f1eaf2b0f/cid-59D903F0133C1A64/calendar.ics',
}
COLORS = {
    'PhD': 'cadetblue',
    'MITACS': 'teal',
    'Green Network Planning': 'mediumseagreen',
    'UPAL': 'Lime',
    'elementslab': 'gold',
    'Portfolio': 'mediumpurple',
}
THEMES = {
    'PhD': 'Research',
    'MITACS': 'Research',
    'elementslab': 'Research',
    'Green Network Planning': 'Teaching',
    'UPAL': '',
    'Portfolio': ''
}
chart_template = dict(
    layout=go.Layout(
        title_font=dict(family="Rockwell", size=24),
        font=dict(family='Roboto Light'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=10, t=10, b=35),
    ),
)

app = dash.Dash(external_stylesheets=[dbc.themes.YETI])
app.layout = dbc.Container(style={"height": "100vh"}, children=[
    html.Div([], style={"height": "5vh"}),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='agg_by', options=[{'label': 'Week', 'value': 'Week'}], value='Week'),
        ], width=2),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='stacked_bars'),
            dbc.Row([
                dcc.Graph(id='spider_chart'),
                dbc.Col([

                ])
            ])
        ], width=9),
        dbc.Col([
            dcc.Graph(id='sunburst_chart'),
            dcc.Graph(id='calendar_rank')
        ], width=3)
    ]),
])


@app.callback(
    Output(component_id='stacked_bars', component_property='figure'),
    Output(component_id='sunburst_chart', component_property='figure'),
    Output(component_id='calendar_rank', component_property='figure'),
    [Input(component_id='agg_by', component_property='value')]
)
def update_output_div(agg_by):
    events = get_events_from_calendars(CALENDARS)
    events = events.sort_values(agg_by).groupby([agg_by, 'Calendar'], as_index=False).sum()
    events['Theme'] = events['Calendar'].replace(THEMES)
    events['Time'] = 'Time'

    #
    sun = px.sunburst(events, labels='Calendar', path=['Time', 'Calendar', 'Theme'], values='Duration',
                      template=chart_template, color='Calendar', color_discrete_map=COLORS)
    sun.update_traces(insidetextorientation='horizontal')

    #
    bars = px.bar(events, x='Week', y='Duration', color='Calendar', template=chart_template, color_discrete_map=COLORS)
    bars.update_traces(overwrite=False, marker={"opacity": 0.4})

    #
    rank = px.bar(events.groupby('Calendar', as_index=False).sum().sort_values('Duration'),
                  x='Duration', y='Calendar', color='Calendar', template=chart_template, color_discrete_map=COLORS)
    rank.update_layout(showlegend=False)
    return bars, sun, rank


if __name__ == '__main__':
    app.run_server(debug=False, host='localhost', port=9050)
