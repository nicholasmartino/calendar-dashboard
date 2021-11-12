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
    'TA': 'https://outlook.live.com/owa/calendar/00000000-0000-0000-0000-000000000000/9121c110-4043-49ef-a0ce-3018a3670c1f/cid-59D903F0133C1A64/calendar.ics',
    'UPAL': 'https://outlook.live.com/owa/calendar/00000000-0000-0000-0000-000000000000/666b5775-d4a8-48f8-bb5b-b08bdfa9c2cc/cid-59D903F0133C1A64/calendar.ics',
    'elementslab': 'https://outlook.live.com/owa/calendar/8fd2720a-5774-41df-90e9-fa8ff7cc3cbf/1b14feb2-a841-4f74-ae70-496436c6da96/cid-59D903F0133C1A64/calendar.ics',
    'Portfolio': 'https://outlook.live.com/owa/calendar/00000000-0000-0000-0000-000000000000/491714b4-dc60-421d-9cf7-cb2f1eaf2b0f/cid-59D903F0133C1A64/calendar.ics',
}
COLORS = {
    'PhD': 'cadetblue',
    'MITACS': 'teal',
    'TA': 'mediumseagreen',
    'UPAL': 'Lime',
    'elementslab': 'gold',
    'Portfolio': 'mediumpurple',
}
THEMES = {
    'PhD': 'Research',
    'MITACS': 'Research',
    'elementslab': 'Research',
    'TA': 'Teaching',
    'UPAL': '',
    'Portfolio': ''
}
GOAL = {
    'PhD': 8,
    'MITACS': 8,
    'elementslab': 10,
    'TA': 5,
    'UPAL': 1,
    'Portfolio': 2
}

chart_template = dict(
    layout=go.Layout(
        title_font=dict(family="Roboto", size=20),
        font=dict(family='Roboto Light'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=10, t=10, b=35),
        legend=dict(orientation="h"),
    ),
)
text_style = {'height': '20%', 'text-align': 'left', 'position': 'relative', 'top': '20%',
              'font-size': 'x-large', 'font-weight': 'bold', 'font-family': 'Roboto', 'color': 'gray'}
agg_op = [{'label': 'Day', 'value': 'd'}, {'label': 'Week', 'value': 'w'}, {'label': 'Month', 'value': 'm'}]
ts_op = [{'label': l, 'value': v} for l, v in {'YTD': 'ytd', 'Quarter': 'q', '7 Days': '7d', '30 Days': '30d'}.items()]

app = dash.Dash(external_stylesheets=[dbc.themes.YETI])
app.layout = \
    html.Div(style={"height": "98vh", "width": "98vw"}, children=[
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
            dbc.Col(width=4, style={"height": "80%"}, children=[
                dcc.Graph(id='calendar_rank', style={"height": "100%"}),
            ]),
            dbc.Col(width=3, style={"height": "80%"}, children=[
                dbc.Row([
                    dbc.Col([
                        dcc.Dropdown(id='time_scale', options=ts_op, value='ytd'),
                    ]),
                    dbc.Col([
                        dcc.Dropdown(id='agg_by', options=agg_op, value='w'),
                    ]),
                ]),
                dbc.Row(style={'height': '90%'}, children=[
                    dcc.Graph(id='funnel_chart'),
                ]),
            ])
        ])
    ])


@app.callback(
    Output(component_id='stacked_bars', component_property='figure'),
    Output(component_id='sunburst_chart', component_property='figure'),
    Output(component_id='calendar_rank', component_property='figure'),
    Output(component_id='radar_chart', component_property='figure'),
    Output(component_id='funnel_chart', component_property='figure'),
    [Input(component_id='agg_by', component_property='value'),
     Input(component_id='time_scale', component_property='value')]
)
def update_output_div(agg_by, ts):

    if ts == 'q':
        start = (datetime.datetime.now().year, 9, 1)
        end = (datetime.datetime.now().year, 12, 31)
    elif ts == '7d':
        start = datetime.datetime.now().date() - datetime.timedelta(7)
        start = (start.year, start.month, start.day)
        end = (datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
    elif ts == '30d':
        start = datetime.datetime.now().date() - datetime.timedelta(30)
        start = (start.year, start.month, start.day)
        end = (datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
    else:
        start = (datetime.datetime.now().year, 1, 1)
        end = (datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)

    events_raw = get_events_ics(names=[k for k in CALENDARS.keys()], urls=[u for u in CALENDARS.values()],
                                start=start, end=end)
    agg_by = [i['label'] for i in agg_op if i['value'] == agg_by][0]
    grouped = events_raw.groupby([agg_by, 'Calendar'], as_index=False)
    events = grouped.sum()
    events['Date'] = grouped.agg({'Date': 'first'})['Date']
    events['Theme'] = events['Calendar'].replace(THEMES)
    events['Time'] = 'Time'

    events = events.sort_values('Date').reset_index(drop=True)
    cal_events = events.copy().groupby('Calendar', as_index=False).sum().sort_values('Duration', ascending=False)
    cal_events[agg_by] = events.copy().groupby('Calendar', as_index=False).count()[agg_by]
    total = f"{int(events['Duration'].sum())}h"

    # Pie chart
    sun = px.sunburst(events, labels='Calendar', path=['Time', 'Calendar', 'Theme'], values='Duration',
                      color='Calendar', template=chart_template, color_discrete_map=COLORS)
    sun.update_traces(insidetextorientation='horizontal')
    pie = px.pie(events, names='Calendar', values='Duration', color='Calendar',
                 template=chart_template, color_discrete_map=COLORS)
    pie.update_layout(showlegend=False, annotations=[dict(text=f"<b>{total}</b>", x=0.5, y=0.5, font_size=50,
                                                          font_family="Roboto", font_color="gray", showarrow=False)])
    pie.update_traces(hole=0.8)

    # Stacked bar chart
    if agg_by == 'Day':
        x = 'Date'
    else:
        x = agg_by
    bars = px.bar(events, x=x, y='Duration', color='Calendar',
                  template=chart_template, color_discrete_map=COLORS)
    bars.update_traces(marker={"opacity": 0.4})

    # Calendar rank
    rank = px.bar(cal_events, x='Duration', y='Calendar', color='Calendar',
                  template=chart_template, color_discrete_map=COLORS)
    rank.update_layout(showlegend=False, margin=dict(l=120, r=10, t=10, b=35))
    rank.update_traces(marker={"opacity": 0.4})

    # Box plot
    box_df = events_raw.groupby(['Week', 'Calendar'], as_index=False).agg({'Week': 'mean', 'Duration': 'sum'})
    box_df['Goal'] = box_df['Calendar'].replace(GOAL)
    box_df['Change'] = (box_df['Duration']/box_df['Goal']) - 1
    box = px.box(box_df, x='Calendar', y='Change', color='Calendar',
                 template=chart_template, color_discrete_map=COLORS)
    box.update_layout(showlegend=False)

    # Funnel chart
    d_average = events['Duration'].sum()/len(events_raw['Date'].unique())
    w_average = events['Duration'].sum()/len(events_raw['Week'].unique())
    m_average = events['Duration'].sum()/len(events_raw['Month'].unique())
    data = pd.DataFrame(dict(
        number=[m_average, w_average, d_average],
        name=['Monthly', 'Weekly', 'Daily']
    ))
    data['number'] = data['number'].astype(int)
    fun = px.funnel(data, x='number', y='name', template=chart_template) #, color='Calendar', color_discrete_map=COLORS)
    return bars, pie, rank, box, fun


if __name__ == '__main__':
    app.run_server(debug=False, host='localhost', port=9050)
