from fastapi import FastAPI
from routes import binance_stock, positions, signals, symbol

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
# Include the routers
app.include_router(positions.router, prefix="/Positions", tags=["positions"])
app.include_router(signals.router, prefix="/Signals", tags=["signals"])
app.include_router(symbol.router, prefix="/Symbols", tags=["symbols"])
app.include_router(binance_stock.router, prefix="/Stocks", tags=["stocks"])
