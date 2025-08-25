from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
import httpx

app = FastAPI(title="ETH Data API (Coinbase public market)")

PUBLIC_BASE = "https://api.coinbase.com/api/v3/brokerage/market"

class CandleResp(BaseModel):
    candles: list

@app.get("/candles", response_model=CandleResp)
async def candles(product_id: str = "ETH-USD",
                  granularity: str = "ONE_MINUTE",
                  lookback_minutes: int = 300):
    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=lookback_minutes)
    url = f"{PUBLIC_BASE}/products/{product_id}/candles"
    params = {
        "start": int(start.timestamp()),
        "end": int(end.timestamp()),
        "granularity": granularity,
        "limit": 350,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params, headers={"cache-control": "no-cache"})
        r.raise_for_status()
        return r.json()

@app.get("/ticker")
async def ticker(product_id: str = "ETH-USD"):
    url = f"{PUBLIC_BASE}/products/{product_id}/ticker"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, headers={"cache-control": "no-cache"})
        r.raise_for_status()
        return r.json()
