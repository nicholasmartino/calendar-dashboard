import datetime

import icalendar
import pandas as pd
import recurring_ical_events
import requests


def get_events_ics(url, start, end):
    cal = icalendar.Calendar.from_ical(requests.get(url).text)
    sd = datetime.datetime(start[0], start[1], start[2], 00, 00, 00, 0)
    ed = datetime.datetime(end[0], end[1], end[2], 23, 59, 59, 0)
    recurrent = recurring_ical_events.of(cal).between(sd, ed)

    df = pd.DataFrame()
    for component in recurrent: # + cal.walk():
        if component.name == 'VEVENT':
            ev_start = component.get('dtstart').dt
            ev_end = component.get('dtend').dt

            if (ev_start.date() > sd.date()) and (ev_end.date() < ed.date()):
                l = len(df)
                df.loc[l, 'Date'] = ev_start.date()
                df.loc[l, 'Week'] = ev_start.isocalendar()[1]
                df.loc[l, 'Event'] = component.get('summary')
                df.loc[l, 'Duration'] = (ev_end - ev_start).seconds/3600

    if len(df) > 0:
        df['Date'] = pd.to_datetime(df['Date'])
        print(df.groupby(['Date', 'Event']).sum().loc[:, 'Duration'])
        print(f"Total: {df['Duration'].sum()} hours")
        return df


def get_events_from_calendars(calendars):
    df = pd.DataFrame()
    for name in calendars.keys():
        df_cal = get_events_ics(
            url=calendars[name],
            start=(2021, 9, 1),
            end=(2021, 12, 31)
        )
        if df_cal is not None:
            df_cal['Calendar'] = name
            df = pd.concat([df, df_cal])
    df = df[df['Week'] <= datetime.datetime.now().isocalendar()[1]]
    return df
