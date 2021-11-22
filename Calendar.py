import datetime

import icalendar
import pandas as pd
import recurring_ical_events
import requests


def get_events_ics(names, urls, start, end, verbose=True):
    start_time = datetime.datetime.now()
    assert len(names) == len(urls), AssertionError("Different sizes of 'names' and 'urls' parameters")

    sd = datetime.datetime(start[0], start[1], start[2], 00, 00, 00, 0)
    ed = datetime.datetime(end[0], end[1], end[2], 23, 59, 59, 0)

    calendars = [icalendar.Calendar.from_ical(requests.get(url).text) for url in urls]
    recurrent = [(name, event) for cal, name in zip(calendars, names)
                 for event in recurring_ical_events.of(cal).between(sd, ed)]

    # Find events
    events = [component[1] for component in recurrent if component[1].name == 'VEVENT']
    names = [component[0] for component in recurrent if component[1].name == 'VEVENT']

    df = pd.DataFrame()
    df['Event'] = [event.get('summary') for event in events]
    df['Calendar'] = [name for name in names]
    df['Date'] = [event.get('dtstart') for event in events]
    df['End Date'] = [event.get('dtend') for event in events]
    df['Week'] = [ev_start.dt.date().isocalendar()[1] for ev_start in df['Date']]
    df['Month'] = [f"{(ev_start.dt.date().month, ev_start.dt.date().year)}" for ev_start in df['Date']]
    df['Day'] = [f"{(ev_start.dt.date().day, ev_start.dt.date().month, ev_start.dt.date().year)}"
                 for ev_start in df['Date']]
    df['Duration'] = [(end.dt - start.dt).seconds/3600 for end, start in zip(df['End Date'], df['Date'])]

    if len(df) > 0:
        df['Date'] = pd.to_datetime([dt.dt.date() for dt in df['Date']])
        df = df.sort_values('Date')
        if verbose:
            print(f"Events extracted from {len(calendars)} calendars in {datetime.datetime.now() - start_time} seconds")
        return df

    else:
        if verbose:
            print(f"No events found between {start} and {end}")
