from fastapi import APIRouter
import mysql.connector 
import os
import logging
from pydantic import BaseModel
from positions import Position


router = APIRouter()


def get_symbols():
    cnx = open_connection("stocks")
    cursor = cnx.cursor()
    query = ("SELECT * FROM symbols")
    cursor.execute(query)
    symbols = []
    for (id, symbol) in cursor:
        symbols.append(symbol)
    cursor.close()
    close_connection(cnx)
    return symbols


@router.get("/List", tags=["symbol"])
async def list_supported_symbols():
    return get_symbols()    


