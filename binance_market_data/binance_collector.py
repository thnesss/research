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
from config import FUTURES_BASE_URL

# Инструмент передается при запуске программы.

if len(sys.argv) < 2:
    print("Укажите инструмент. Например: python3 binance_collector.py btcusdt")
    sys.exit()

symbol = sys.argv[1].lower()

# Формируем WebSocket URL для выбранного инструмента.
url = f"{FUTURES_BASE_URL}{symbol}@bookTicker"

# Каждый инструмент записывается в отдельный CSV.
FILE_NAME = f"{symbol}_futures_raw.csv"

