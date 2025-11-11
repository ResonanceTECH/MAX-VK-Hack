from app.models.events import Event
from app.utils.date_utils import format_time, get_week_parity, DAYS_OF_WEEK
from datetime import datetime
import pytz


def process_events(calendar):
    events = []
    for component in calendar.walk():
        if component.name == "VEVENT":
            start_dt = component.get("DTSTART").dt
            end_dt = component.get("DTEND").dt

            if isinstance(start_dt, datetime) and isinstance(end_dt, datetime):
                start_dt = start_dt.astimezone(pytz.timezone("Europe/Moscow"))
                end_dt = end_dt.astimezone(pytz.timezone("Europe/Moscow"))

                event = Event(
                    summary=str(component.get("SUMMARY")),
                    start=format_time(start_dt),
                    end=format_time(end_dt),
                    day_of_week=DAYS_OF_WEEK[start_dt.weekday()],
                    description=str(component.get("DESCRIPTION")),
                    location=str(component.get("LOCATION")),
                    week_parity=get_week_parity(start_dt)
                )
                events.append(event)

    return {"events": events}
