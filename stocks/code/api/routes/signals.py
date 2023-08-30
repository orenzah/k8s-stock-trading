import mysql.connector
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


@router.get("/ShouldEnterPosition", tags=["signals"])
async def should_enter_position(symbol: str):
    # TODO send request to the algo server to get the answer
    # answer is a boolean and timeout_seconds and stop_lose_price and exit_price
    pass
