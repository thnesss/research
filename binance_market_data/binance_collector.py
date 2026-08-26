# Универсальный сборщик данных для Binance.
# Один и тот же код используется для разных торговых инструментов.

import websocket
import json
import csv
import ssl
import certifi
import queue
import threading
import time
import sys

from datetime import datetime, timezone
from config import MARKET_URLS

# При запуске передаем два параметра: тип рынка и торговый инструмент.
# Примеры:
# python3 binance_collector.py usdm_futures btcusdt
# python3 binance_collector.py spot btcusdt

if len(sys.argv) < 3:
    print(
        "Укажите рынок и инструмент: "
        "Например: python3 binance_collector.py futures btcusdt"
    )
    sys.exit()

market_type = sys.argv[1].lower()
symbol = sys.argv[2].lower()

# Проверяем, что такой тип рынка есть в настройках.
if market_type not in MARKET_URLS:
    print(f"Неизвестный рынок: {market_type}")
    print(f"Доступные рынки: {', '.join(MARKET_URLS.keys())}")
    sys.exit()

# Берем нужный WebSocket-адрес из config.py.
base_url = MARKET_URLS[market_type]

# Формируем адрес потока bookTicker для выбранного рынка и инструмента.
url = f"{base_url}{symbol}@bookTicker"

# Имя файла формируется автоматически.
FILE_NAME = f"{symbol}_{market_type}_raw.csv"

# Очередь разделяет получение WebSocket-сообщений и запись данных в CSV.
data_queue = queue.Queue()

# Последняя полученная котировка хранится для вывода состояния в Terminal.
latest_data = None


def writer_worker():
    """
    Забирает строки из очереди и записывает их в CSV.
    """

    with open(FILE_NAME, "a", newline="") as file:
        writer = csv.writer(file)

        while True:
            row = data_queue.get()

            if row is None:
                break

            writer.writerow(row)
            data_queue.task_done()
