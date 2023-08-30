from fastapi import FastAPI
import os
import importlib
import logging
from routes import positions, algo, symbols

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}    
# Include the routers
app.include_router(positions.router, prefix="/Positions", tags=["positions"])
app.include_router(algo.router, prefix="/Algo", tags=["algo"])
app.include_router(symbols.router, prefix="/Symbols", tags=["symbols"])
