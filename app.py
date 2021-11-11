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
GOAL = {
    'PhD': 8,
    'MITACS': 8,
    'elementslab': 10,
    'Green Network Planning': 5,
    'UPAL': 1,
    'Portfolio': 2
}

chart_template = dict(
    layout=go.Layout(
        title_font=dict(family="Roboto", size=20),
        font=dict(family='Roboto Light'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=10, t=10, b=35),
        legend=dict(orientation="h"),
    ),
)
text_style = {'height': '20%', 'text-align': 'left', 'position': 'relative', 'top': '20%',
              'font-size': 'x-large', 'font-weight': 'bold', 'font-family': 'Roboto', 'color': 'gray'}

app = dash.Dash(external_stylesheets=[dbc.themes.YETI])
app.layout = \
    html.Div(style={"height": "100vh"}, children=[
        dbc.Row(class_name='h-50', children=[
            html.Div(style={"height": "5vh"}),
            dbc.Col(width=9, style={"height": "100%"}, children=[
                dcc.Graph(id='stacked_bars', style={"height": "100%"}),
            ]),
            dbc.Col(width=3, style={"height": "100%"}, children=[
                dcc.Graph(id='sunburst_chart', style={"height": "80%"}),
            ])
        ]),
        dbc.Row(class_name='h-50', children=[
            html.Div(style={"height": "5vh"}),
            dbc.Col(width=5, style={"height": "80%"}, children=[
                dcc.Graph(id='radar_chart', style={"height": "100%"})
            ]),
            dbc.Col(width=5, style={"height": "80%"}, children=[
                dcc.Graph(id='calendar_rank', style={"height": "100%"}),
            ]),
            dbc.Col(width=2, style={"height": "80%"}, children=[
                dcc.Dropdown(id='agg_by', style={"width": "66%"}, options=[{'label': 'Week', 'value': 'Week'}],
                             value='Week'),
                html.Div(id='daily_average', style=text_style),
                html.Div(id='weekly_average', style=text_style),
            ])
        ])
    ])


@app.callback(
    Output(component_id='stacked_bars', component_property='figure'),
    Output(component_id='sunburst_chart', component_property='figure'),
    Output(component_id='calendar_rank', component_property='figure'),
    Output(component_id='radar_chart', component_property='figure'),
    Output(component_id='daily_average', component_property='children'),
    Output(component_id='weekly_average', component_property='children'),
    [Input(component_id='agg_by', component_property='value')]
)
def update_output_div(agg_by):
    events_raw = get_events_from_calendars(CALENDARS)
    events = events_raw.sort_values(agg_by).groupby([agg_by, 'Calendar'], as_index=False).sum()
    events['Theme'] = events['Calendar'].replace(THEMES)
    events['Time'] = 'Time'
    events['Goal'] = events['Calendar'].replace(GOAL)
    events['Change'] = (events['Duration'] - events['Goal'])/events['Goal']
    cal_events = events.groupby('Calendar', as_index=False).sum().sort_values('Duration', ascending=False)
    cal_events['Week'] = events.groupby('Calendar', as_index=False).count()['Week']
    total = f"{int(events['Duration'].sum())}h"

    # Pie chart
    sun = px.sunburst(events, labels='Calendar', path=['Time', 'Calendar', 'Theme'], values='Duration',
                      color='Calendar', template=chart_template, color_discrete_map=COLORS)
    sun.update_traces(insidetextorientation='horizontal')
    pie = px.pie(events, names='Calendar', values='Duration', color='Calendar',
                 template=chart_template, color_discrete_map=COLORS)
    pie.update_layout(showlegend=False, annotations=[dict(text=total, x=0.5, y=0.5, font_size=30, showarrow=False)])
    pie.update_traces(hole=0.8)

    # Stacked bar chart
    bars = px.bar(events, x='Week', y='Duration', color='Calendar',
                  template=chart_template, color_discrete_map=COLORS)
    bars.update_traces(marker={"opacity": 0.4})

    # Calendar rank
    rank = px.bar(cal_events, x='Duration', y='Calendar', color='Calendar',
                  template=chart_template, color_discrete_map=COLORS)
    rank.update_layout(showlegend=False, margin=dict(l=120, r=10, t=10, b=35))
    rank.update_traces(marker={"opacity": 0.4})

    # Box plot
    box = px.box(events, x='Calendar', y='Change', color='Calendar',
                 template=chart_template, color_discrete_map=COLORS)

    # Polar chart
    events['Week'] = [f"W{int(w)}" for w in events['Week']]
    for week in events['Week'].unique():
        events.loc[len(events), ['Calendar', 'Change', 'Week']] = ['Benchmark', 1, week]
    events = events.sort_values('Week')
    radar = px.line_polar(events, r='Change', theta='Week', color='Calendar', line_close=True,
                          template=chart_template, color_discrete_map=COLORS, title="Benchmark")
    radar.update_layout(showlegend=False, margin=dict(l=40, r=40, t=80, b=40))
    radar.update_traces(marker={'opacity': 0.4})

    d_average = f"{int(events['Duration'].sum()/len(events_raw['Date'].unique()))}h/day"
    w_average = f"{(int(events['Duration'].sum()/len(events_raw['Date'].unique()))) * 5}h/week"
    return bars, pie, rank, box, d_average, w_average


if __name__ == '__main__':
    app.run_server(debug=False, host='localhost', port=9050)
