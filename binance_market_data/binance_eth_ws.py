import websocket
import json
import csv
import ssl
import certifi
import queue
import threading
import time
from datetime import datetime, timezone

FILE_NAME = "eth_bookticker_queue_test.csv"

data_queue = queue.Queue()
latest_data = None


def writer_worker():
    with open(FILE_NAME, "a", newline="") as file:
        writer = csv.writer(file)

        while True:
            row = data_queue.get()

            if row is None:
                break

            writer.writerow(row)
            data_queue.task_done()


def on_message(ws, message):
    global latest_data

    data = json.loads(message)

    receive_time_ms = int(
        datetime.now(timezone.utc).timestamp() * 1000
    )

    latency_ms = receive_time_ms - data["E"]

    latest_data = {
        "bid": data["b"],
        "bid_qty": data["B"],
        "ask": data["a"],
        "ask_qty": data["A"],
        "latency": latency_ms
    }

    row = [
        data["E"],
        receive_time_ms,
        latency_ms,
        data["T"],
        data["u"],
        data["s"],
        data["b"],
        data["B"],
        data["a"],
        data["A"]
    ]

    data_queue.put(row)


def console_worker():
    while True:
        if latest_data is not None:
            now = datetime.now().strftime("%H:%M:%S")

            print(
                f"{now} | "
                f"BID: {latest_data['bid']} "
                f"({latest_data['bid_qty']} ETH) | "
                f"ASK: {latest_data['ask']} "
                f"({latest_data['ask_qty']} ETH) | "
                f"LATENCY: {latest_data['latency']} ms | "
                f"QUEUE: {data_queue.qsize()}"
            )

        time.sleep(1)


def on_error(ws, error):
    print("ERROR:", error)


def on_close(ws, close_status_code, close_msg):
    print("Connection closed")


def on_open(ws):
    print("Connected to Binance Futures")


try:
    with open(FILE_NAME, "x", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "event_time_ms",
            "receive_time_ms",
            "latency_ms",
            "transaction_time_ms",
            "update_id",
            "symbol",
            "bid_price",
            "bid_qty",
            "ask_price",
            "ask_qty"
        ])
except FileExistsError:
    pass


writer_thread = threading.Thread(
    target=writer_worker,
    daemon=True
)
writer_thread.start()


console_thread = threading.Thread(
    target=console_worker,
    daemon=True
)
console_thread.start()


url = "wss://fstream.binance.com/ws/ethusdt@bookTicker"

while True:
    try:
        ws = websocket.WebSocketApp(
            url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )

        ws.run_forever(
            sslopt={
                "cert_reqs": ssl.CERT_REQUIRED,
                "ca_certs": certifi.where()
            }
        )

    except Exception as e:
        print("WebSocket exception:", e)

    print("Reconnecting in 5 seconds...")
    time.sleep(5)
