from fastapi import APIRouter
import mysql.connector 
import os
import logging
from pydantic import BaseModel
from positions import Position


router = APIRouter()
@router.get("/ShouldEnterPosition", tags=["algo"])
async def should_enter_position(symbol: str):
    # TODO send request to the algo server to get the answer
    # answer is a boolean and timeout_seconds and stop_lose_price and exit_price
    pass


