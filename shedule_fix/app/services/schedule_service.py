import httpx
from icalendar import Calendar
from io import BytesIO
from fastapi import HTTPException
from app.services.event_service import process_events
from app.config.settings import SEARCH_URL


async def fetch_all_events(query: str = None):
    params = {"match": query} if query else {}
    events_by_calname = {}

    while True:
        async with httpx.AsyncClient() as client:
            search_response = await client.get(SEARCH_URL, params=params)
            search_data = search_response.json()

        if not search_data.get("data"):
            raise HTTPException(status_code=404, detail="Расписание не найдено")

        for item in search_data["data"]:
            ical_link = item.get("iCalLink")
            if ical_link:
                async with httpx.AsyncClient() as client:
                    ical_response = await client.get(ical_link)

                calendar = Calendar.from_ical(BytesIO(ical_response.content).read())
                calname = str(calendar.get("X-WR-CALNAME")) if calendar.get("X-WR-CALNAME") else None
                if calname:
                    events = process_events(calendar)
                    if calname not in events_by_calname:
                        events_by_calname[calname] = []
                    events_by_calname[calname].extend(events["events"])

        next_page_token = search_data.get("nextPageToken")
        if not next_page_token:
            break
        params["pageToken"] = next_page_token

    return events_by_calname


async def get_schedule(query: str = None):
    events_by_calname = await fetch_all_events(query)
    return {"events_by_calname": events_by_calname}
