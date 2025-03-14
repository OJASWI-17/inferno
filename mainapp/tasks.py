from celery import shared_task
import pandas as pd
import json
import redis
from channels.layers import get_channel_layer
import asyncio
from mainapp.models import StockDetail

# Redis Connection
redis_conn = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Path to CSV file
CSV_FILE_PATH = r"C:\infernoproject\stocktracker\stockproject\mainapp\multi_stock_data.csv"
df = pd.read_csv(CSV_FILE_PATH)

# Track index for each stock
stock_indices = {ticker: 0 for ticker in df["ticker"].unique()}

def fetch_stock_data_from_csv(selected_stocks):
    """Fetch stock data from CSV and store in Redis in a standardized format."""
    global stock_indices
    data = {}

    for ticker in selected_stocks:
        stock_data = df[df["ticker"] == ticker]
        index = stock_indices.get(ticker, 0)
        if index >= len(stock_data):
            index = 0

        row = stock_data.iloc[index]
        stock_indices[ticker] = index + 1  # Move index forward

        # Standardized data format
        stock_entry = {
            "time": row["date"],  # Ensure this is a string or timestamp
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": int(row["volume"]),
        }

        # Store data in Redis
        redis_key = f"candlestick_data:{ticker}"
        history = redis_conn.get(redis_key)
        if history:
            history = json.loads(history)
            history.append(stock_entry)
            if len(history) > 100:  # Keep only last 100 candles
                history.pop(0)
        else:
            history = [stock_entry]

        redis_conn.set(redis_key, json.dumps(history))
        data[ticker] = stock_entry

    return data

@shared_task
def update_stock(selected_stocks=None):
    """Fetch stock data, store in Redis, and send WebSocket updates."""
    if selected_stocks is None:
        selected_stocks = list(StockDetail.objects.values_list("stock", flat=True))

    if not selected_stocks:
        print("No stocks selected.")
        return

    data = fetch_stock_data_from_csv(selected_stocks)
    print("Updated Stock Data:", data)

    # Send update to WebSocket
    channel_layer = get_channel_layer()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(channel_layer.group_send("stock_track", {
        "type": "send_stock_update",
        "message": data,
    }))
    loop.close()