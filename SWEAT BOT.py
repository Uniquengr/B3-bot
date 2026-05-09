import websocket
import json
import datetime
import os
import time

url = "wss://stream.bybit.com/v5/public/spot"

position = None
buy_price = None
last_price = None

balance = 10000
trade_count = 0
max_trades = 10
change_percent = None
new_percentage = None


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def on_open(ws):
    print("Connected")

    ws.send(json.dumps({
        "op": "subscribe",
        "args": ["publicTrade.SWEATUSDT"]
    }))


def on_message(ws, message):
    global position, buy_price, last_price, balance, trade_count
    global change_percent, new_percentage

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

    # ✅ FIX: initialize new_percentage before comparison
    if new_percentage is None:
        new_percentage = change_percent
        last_price = price
        return

    clear_screen()

    print("OBOL BOT")
    print(f"Price: {price}")
    print(f"Change %: {change_percent:.4f}")
    print(f"Position: {position}")
    print(f"Balance: {balance}")
    print(f"Trades: {trade_count}")

    # 🟢 BUY
    if position is None and change_percent > new_percentage:
        print("BUY")
        position = "bought"
        buy_price = price
        new_percentage = change_percent

    # 🔴 SELL
    elif position == "bought":
        drop = change_percent = ((price - last_price) / last_price) * 100


        if drop <= -1:
            print("SELL")

            profit = price - buy_price
            balance += profit
            trade_count += 1

            position = None
            buy_price = None

            if trade_count >= max_trades:
                ws.close()

    last_price = price


def on_error(ws, error):
    print("Error:", error)


def on_close(ws, code, msg):
    print("Closed. Restarting...")
    time.sleep(3)
    start()


def start():
    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever()


start()