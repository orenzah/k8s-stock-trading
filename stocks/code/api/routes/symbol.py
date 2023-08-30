import os

import mysql.connector
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


def open_connection(database: str):
    cnx = mysql.connector.connect(user=os.environ['MYSQL_USER'], password=os.environ['MYSQL_PASSWORD'],
                                  host=os.environ['MYSQL_HOST'],
                                  database=database)
    return cnx


def close_connection(cnx):
    cnx.close()


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
