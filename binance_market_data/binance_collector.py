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

# Заголовки raw CSV для каждого типа рынка.
CSV_HEADERS = {
    "spot": [
        "receive_time_ms",
        "update_id",
        "symbol",
        "bid_price",
        "bid_qty",
        "ask_price",
        "ask_qty"
    ],

    "usdm_futures": [
        "event_time_ms",
        "receive_time_ms",
        "transaction_time_ms",
        "update_id",
        "symbol",
        "bid_price",
        "bid_qty",
        "ask_price",
        "ask_qty"
    ]
}

# Очередь разделяет получение WebSocket-сообщений и запись данных в CSV.
data_queue = queue.Queue()

# Последняя полученная котировка хранится для вывода состояния в Terminal.
latest_data = None

def writer_worker():
    """
    Забирает строки из очереди и записывает их в CSV.
    Заголовок создается только для нового пустого файла.
    """

    with open(FILE_NAME, "a", newline="") as file:
        writer = csv.writer(file)

        # Если файл новый и пустой, записываем названия колонок.
        if file.tell() == 0:
            writer.writerow(CSV_HEADERS[market_type])

        while True:
            row = data_queue.get()

            # None используется как сигнал остановки writer-потока.
            if row is None:
                data_queue.task_done()
                break

            writer.writerow(row)
            data_queue.task_done()

def parse_usdm_futures_message(data, receive_time_ms):
    """
    Преобразует сообщение USD-M Futures bookTicker
    в строку для raw CSV.
    """

    return [
        data["E"],          # время события на Binance
        receive_time_ms,   # время получения сообщения нашим компьютером
        data["T"],          # время транзакции на Binance
        data["u"],          # ID обновления order book
        data["s"],          # торговый инструмент
        data["b"],          # best bid price
        data["B"],          # best bid quantity
        data["a"],          # best ask price
        data["A"]           # best ask quantity
    ]


def parse_spot_message(data, receive_time_ms):
    """
    Преобразует сообщение Spot bookTicker
    в строку для raw CSV.
    """

    return [
        receive_time_ms,   # время получения сообщения нашим компьютером
        data["u"],          # ID обновления order book
        data["s"],          # торговый инструмент
        data["b"],          # best bid price
        data["B"],          # best bid quantity
        data["a"],          # best ask price
        data["A"]           # best ask quantity
    ]

# Для каждого типа рынка указываем функцию, которая умеет разбирать его сообщения.
MESSAGE_PARSERS = {
    "spot": parse_spot_message,
    "usdm_futures": parse_usdm_futures_message
}


def on_message(ws, message):
    """
    Получает новое WebSocket-сообщение от Binance
    и передает его нужному парсеру.
    """

    global latest_data

    # Binance присылает данные в JSON, которые мы превращаем в Python-словарь
    data = json.loads(message)

    # Фиксируем время, в которое пришло сообщение
    receive_time_ms = int(
        datetime.now(timezone.utc).timestamp() * 1000
    )

    # Выбираем нужный парсер по типу рынка.
    parser = MESSAGE_PARSERS[market_type]

    # Парсер превращает сообщение Binance в строку для raw CSV.
    row = parser(data, receive_time_ms)

    # Эти данные нужны только для отображения последней котировки в Terminal.
    latest_data = {
        "symbol": data["s"],
        "bid": data["b"],
        "bid_qty": data["B"],
        "ask": data["a"],
        "ask_qty": data["A"]
    }

    # Передаем строку в очередь на запись.
    data_queue.put(row)

def on_open(ws):
    """
    Вызывается после успешного подключения к Binance.
    """

    print(f"Подключено: {market_type} | {symbol.upper()}")


def on_error(ws, error):
    """
    Выводит ошибку WebSocket.
    """

    print(f"WebSocket error: {error}")


def on_close(ws, close_status_code, close_msg):
    """
    Вызывается при закрытии WebSocket-соединения.
    """

    print("Соединение закрыто.")

def console_worker():
    """
    Раз в секунду показывает последнюю котировку
    и размер очереди записи.
    """

    while True:
        if latest_data is not None:
            print(
                f"{latest_data['symbol']} | "
                f"BID: {latest_data['bid']} | "
                f"ASK: {latest_data['ask']} | "
                f"QUEUE: {data_queue.qsize()}"
            )

        time.sleep(1)

def run_collector():
    """
    Запускает запись CSV, вывод состояния в Terminal
    и WebSocket-подключение к Binance.
    """

    # Отдельный поток записывает данные из очереди в CSV.
    writer_thread = threading.Thread(
        target=writer_worker,
        daemon=True
    )
    writer_thread.start()

    # Отдельный поток раз в секунду показывает состояние сборщика.
    console_thread = threading.Thread(
        target=console_worker,
        daemon=True
    )
    console_thread.start()

    try:
        while True:
            print(f"Подключение к: {url}")

            # Создаем WebSocket-клиент и передаем ему callback-функции.
            ws = websocket.WebSocketApp(
                url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )

            # Запускаем соединение.
            ws.run_forever(
                sslopt={
                    "cert_reqs": ssl.CERT_REQUIRED,
                    "ca_certs": certifi.where()
                }
            )

            # Если соединение оборвалось, ждем 5 секунд и подключаемся снова.
            print("Повторное подключение через 5 секунд...")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nСбор данных остановлен пользователем.")

        # Ждем, пока очередь полностью запишется в CSV.
        data_queue.join()

        # None сообщает writer_worker, что работу можно завершать.
        data_queue.put(None)

        writer_thread.join()


# Этот блок выполняется только при прямом запуске файла.
if __name__ == "__main__":
    run_collector()
