from flask import Flask
from threading import Thread
import websocket
import json
import os
import time

# ---------------- WEB SERVER FOR RENDER ----------------

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0", port=10000)

Thread(target=run_web).start()

# ---------------- BOT SETTINGS ----------------

url = "wss://stream.bybit.com/v5/public/spot"

position = None
buy_price = None
last_price = None

balance = 10000
trade_count = 0
max_trades = 10

# ---------------- CLEAR SCREEN ----------------

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

# ---------------- CONNECT ----------------

def on_open(ws):
    print("Connected")

    ws.send(json.dumps({
        "op": "subscribe",
        "args": ["publicTrade.B3USDT"]
    }))

# ---------------- RECEIVE DATA ----------------

def on_message(ws, message):
    global position
    global buy_price
    global last_price
    global balance
    global trade_count

    data = json.loads(message)

    if "data" not in data:
        return

    trade = data["data"][0]

    price = trade.get("p")

    if price is None:
        return

    price = float(price)

    if last_price is None:
        last_price = price
        return

    change_percent = ((price - last_price) / last_price) * 100

    clear_screen()

    print("B3 BOT")
    print(f"Price: {price}")
    print(f"Change %: {change_percent:.4f}")
    print(f"Position: {position}")
    print(f"Balance: {balance}")
    print(f"Trades: {trade_count}")

    # BUY
    if position is None and change_percent > 0:
        print("BUY")

        position = "bought"
        buy_price = price

    # SELL
    elif position == "bought":

        drop = ((price - last_price) / last_price) * 100

        if drop <= -1:
            print("SELL")

            profit = price - buy_price

            balance += profit

            trade_count += 1

            position = None
            buy_price = None

            print(f"Profit: {profit}")

            if trade_count >= max_trades:
                print("MAXIMUM TRADES REACHED")
                ws.close()

    last_price = price

# ---------------- ERROR ----------------

def on_error(ws, error):
    print("Error:", error)

# ---------------- CLOSE ----------------

def on_close(ws, code, msg):
    print("Closed. Restarting...")

    time.sleep(3)

    start()

# ---------------- START ----------------

def start():

    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever()

# ---------------- RUN ----------------

start()