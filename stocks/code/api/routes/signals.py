import mysql.connector
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class QueryEnter(BaseModel):
    symbol: str
    entry_datetime: str # date format: 2021-01-01 00:00:00       
    

@router.post("/ShouldEnterPosition", tags=["signals"])
async def should_enter_position(query: QueryEnter):
    symbol = query.symbol
    entry_datetime = query.entry_datetime
    
    # TODO send request to the algo server to get the answer
    # answer is a boolean and timeout_seconds and stop_lose_price and exit_price
    pass
