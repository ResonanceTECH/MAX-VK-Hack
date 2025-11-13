import httpx
from icalendar import Calendar
from io import BytesIO
from fastapi import HTTPException
from app.services.event_service import process_events
from app.config.settings import SEARCH_URL
import logging

logger = logging.getLogger(__name__)

# Настройка таймаутов для HTTP запросов
TIMEOUT = httpx.Timeout(
    connect=30.0,  # Таймаут подключения
    read=60.0,     # Таймаут чтения
    write=30.0,   # Таймаут записи
    pool=30.0     # Таймаут получения соединения из пула
)


async def fetch_all_events(query: str = None):
    params = {"match": query} if query else {}
    events_by_calname = {}

    while True:
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                search_response = await client.get(SEARCH_URL, params=params)
                search_response.raise_for_status()
                search_data = search_response.json()
        except httpx.ConnectTimeout:
            logger.error(f"Таймаут подключения к {SEARCH_URL}")
            raise HTTPException(
                status_code=504,
                detail="Внешний сервис расписания недоступен. Попробуйте позже."
            )
        except httpx.ReadTimeout:
            logger.error(f"Таймаут чтения ответа от {SEARCH_URL}")
            raise HTTPException(
                status_code=504,
                detail="Внешний сервис расписания не отвечает. Попробуйте позже."
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка от {SEARCH_URL}: {e}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Ошибка при получении расписания: {e.response.status_code}"
            )
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе к {SEARCH_URL}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при получении расписания: {str(e)}"
            )

        if not search_data.get("data"):
            raise HTTPException(status_code=404, detail="Расписание не найдено")

        for item in search_data["data"]:
            ical_link = item.get("iCalLink")
            if ical_link:
                try:
                    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                        ical_response = await client.get(ical_link)
                        ical_response.raise_for_status()
                except httpx.ConnectTimeout:
                    logger.warning(f"Таймаут подключения к {ical_link}, пропускаем")
                    continue
                except httpx.ReadTimeout:
                    logger.warning(f"Таймаут чтения ответа от {ical_link}, пропускаем")
                    continue
                except httpx.HTTPStatusError as e:
                    logger.warning(f"HTTP ошибка от {ical_link}: {e}, пропускаем")
                    continue
                except Exception as e:
                    logger.warning(f"Ошибка при загрузке {ical_link}: {e}, пропускаем")
                    continue

                try:
                    calendar = Calendar.from_ical(BytesIO(ical_response.content).read())
                    calname = str(calendar.get("X-WR-CALNAME")) if calendar.get("X-WR-CALNAME") else None
                    if calname:
                        events = process_events(calendar)
                        if calname not in events_by_calname:
                            events_by_calname[calname] = []
                        events_by_calname[calname].extend(events["events"])
                except Exception as e:
                    logger.warning(f"Ошибка при обработке календаря {ical_link}: {e}, пропускаем")
                    continue

        next_page_token = search_data.get("nextPageToken")
        if not next_page_token:
            break
        params["pageToken"] = next_page_token

    return events_by_calname


async def get_schedule(query: str = None):
    events_by_calname = await fetch_all_events(query)
    return {"events_by_calname": events_by_calname}
