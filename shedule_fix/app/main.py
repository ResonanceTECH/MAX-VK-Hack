from fastapi import FastAPI
from app.services.schedule_service import get_schedule

app = FastAPI()


@app.get("/schedule_1")
async def schedule_endpoint(query: str = None):
    return await get_schedule(query)
