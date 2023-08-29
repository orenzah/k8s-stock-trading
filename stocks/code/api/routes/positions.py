from fastapi import APIRouter
import mysql.connector 
import os
import logging
from pydantic import BaseModel

class Position(BaseModel):
    id: int | None = None
    entry_datetime: str | None = None
    entry_price: float
    exit_price: float
    shares: int
    symbol: str
    active: bool | None = None
    timeout_seconds: int
    stop_lose_price: float
    
logger = logging.getLogger("mysql.connector")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s- %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler("cpy.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler) 

router = APIRouter()
def open_connection(database: str):
    cnx = mysql.connector.connect(user=os.environ['MYSQL_USER'], password=os.environ['MYSQL_PASSWORD'],
                                    host=os.environ['MYSQL_HOST'],
                                    database=database)
    return cnx

def close_connection(cnx):
    cnx.close()


def get_positions(cnx):
    cursor = cnx.cursor()
    query = ("SELECT * FROM state")
    cursor.execute(query)
    positions = []
    for (id, entry_datetime, entry_price, exit_price, shares, symbol, active, timeout_seconds ,stop_lose_price) in cursor:
        position = {
            "id": id,
            "entry_datetime": entry_datetime,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "shares": shares,
            "symbol": symbol,
            "active": active,
            "timeout_seconds": timeout_seconds,
            "stop_lose_price": stop_lose_price
        }
        positions.append(position)
    cursor.close()
    return positions

def get_position_by_id(cnx, id):
    cursor = cnx.cursor()
    query = ("SELECT * FROM state WHERE id = %s")
    cursor.execute(query, (id,))
    position = {}
    for (id, entry_datetime, entry_price, exit_price, shares, symbol, active, stop_lose_price) in cursor:
        position = {
            "id": id,
            "entry_datetime": entry_datetime,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "shares": shares,
            "symbol": symbol,
            "active": active,
            "timeout_seconds": timeout_seconds,
            "stop_lose_price": stop_lose_price
        }
    cursor.close()
    return position

def insert_state(position):    
    cnx = open_connection('positions')
    cursor = cnx.cursor()
    query = ("INSERT INTO state "
            "(entry_price, exit_price, shares, symbol, timeout_seconds, stop_lose_price)"
            "VALUES (%s, %s, %s, %s, %s)")
    data = ( position.entry_price, position.exit_price, position.shares, position.symbol, position.timeout_seconds ,position.stop_lose_price)
    cursor.execute(query, data)
    lastrowid = cursor.lastrowid
    cnx.commit()
    cursor.close()
    close_connection(cnx)
    return lastrowid    
    
def wrapper_get_positions():
    cnx = open_connection('positions')
    positions = get_positions(cnx)
    close_connection(cnx)
    return positions

def wrapper_get_positions_by_id(id):
    cnx = open_connection('positions')
    position = get_position_by_id(cnx, id)
    close_connection(cnx)
    return position

### Routes ###

@router.get("/List", tags=["positions"])
async def list_positions():
    # Get all positions
    positions = wrapper_get_positions()
    logging.debug(positions)
    return {"positions": positions}

@router.get("/ID/{id}", tags=["positions"])
async def get_id(id: int):
    # Get position by id
    position = wrapper_get_positions_by_id(id)    
    logging.debug(position)
    return {"id": id, "position": position}

@router.post("/Create", tags=["positions"])
async def create_position(position: Position):
    # Create a new position     
    row_id = insert_state(position)
    position.id = row_id
    if position.active is None:
        position.active = True
    logging.debug(row_id)
    logging.debug(position)
    return {"id": row_id ,"position": position}

@router.put("/Update", tags=["positions"])
async def update_position(position: Position):
    # Update a position
    logging.debug(position)
    return {"position": position}

@router.delete("/Delete", tags=["positions"])
async def delete_position(position: Position):
    # Delete a position
    logging.debug(position)
    return {"position": position}

