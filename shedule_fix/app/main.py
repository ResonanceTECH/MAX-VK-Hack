from fastapi import FastAPI
from app.services.schedule_service import get_schedule

app = FastAPI(
    root_path="/api2"  # Указываем префикс для работы за nginx прокси
)


@app.get("/schedule_1")
async def schedule_endpoint(query: str = None):
    return await get_schedule(query)
