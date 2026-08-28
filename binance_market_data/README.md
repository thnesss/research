# Binance Market Data Collector

Сбор market data Binance через WebSocket.

Сборщик данных универсален. Один скрипт используется для разных инструментов и типов рынка. Они определяются автоматически при запуске программы.

## Какие рынки поддерживаются?

-Spot

-USD-M Futures

## Структура проекта

- `binance_collector.py` — универсальный сборщик market data

- `config.py` — настройки WebSocket-адресов для разных рынков

- `samples/` — небольшие примеры собранных данных

- `requirements.txt` — дополнительные Python-библиотеки

Полные raw CSV-файлы в GitHub не загружаются из-за большого объёма данных.

## Данные в CSV

Формат raw CSV зависит от типа рынка.

### Spot

Для каждого обновления `bookTicker` сохраняются:

- `receive_time_ms` — время получения сообщения программой на локальном компьютере, в миллисекундах.
- `update_id` — идентификатор обновления order book.
- `symbol` — торговый инструмент.
- `bid_price` — лучшая текущая цена покупки, Best Bid.
- `bid_qty` — объём по лучшей цене покупки.
- `ask_price` — лучшая текущая цена продажи, Best Ask.
- `ask_qty` — объём по лучшей цене продажи.

Пример:

[BTCUSDT Spot sample](samples/btcusdt_spot_sample.csv)

### USDⓈ-M Futures

Для каждого обновления `bookTicker` сохраняются:

- `event_time_ms` — время события на стороне Binance, в миллисекундах.
- `receive_time_ms` — время получения сообщения программой на локальном компьютере, в миллисекундах.
- `transaction_time_ms` — время транзакции на стороне Binance, в миллисекундах.
- `update_id` — идентификатор обновления order book.
- `symbol` — торговый инструмент.
- `bid_price` — лучшая текущая цена покупки, Best Bid.
- `bid_qty` — объём по лучшей цене покупки.
- `ask_price` — лучшая текущая цена продажи, Best Ask.
- `ask_qty` — объём по лучшей цене продажи.

Пример:

[BTCUSDT USDⓈ-M Futures sample](samples/btcusdt_usdm_futures_sample.csv)

### Расчётные показатели 

Расчётные показатели, например latency, в raw CSV не сохраняются.

## Как работает сбор

Для получения данных используется публичный WebSocket Binance `bookTicker`.

При запуске передаются два параметра:

1. тип рынка;
2. торговый инструмент.

Примеры запуска:

BTCUSDT Spot:

`python3 binance_collector.py spot btcusdt`

ETHUSDT Spot:

`python3 binance_collector.py spot ethusdt`

BTCUSDT USDⓈ-M Futures:

`python3 binance_collector.py usdm_futures btcusdt`

ETHUSDT USDⓈ-M Futures:

`python3 binance_collector.py usdm_futures ethusdt`

API-ключ для получения этих публичных market data не требуется.

## Архитектура

Настройки WebSocket-адресов для разных рынков вынесены в `config.py`.

Общая логика подключения, получения сообщений, очереди, записи в CSV и переподключения находится в одном `binance_collector.py`.

Схема работы:

Binance WebSocket  
↓  
`on_message`  
↓  
parser рынка  
↓  
`queue`  
↓  
`writer_worker`  
↓  
CSV

## Очередь записи

Полученные WebSocket-сообщения помещаются в очередь `queue`.

Отдельный поток `writer_worker` забирает строки из очереди и записывает их в CSV.

Получение новых WebSocket-сообщений не зависит напрямую от скорости записи данных на диск.

Размер очереди выводится в Terminal и используется для контроля работы сборщика.

## Автоматическое переподключение

Если WebSocket-соединение закрывается, программа автоматически пытается подключиться снова через несколько секунд.

## Установка

Для работы необходим Python 3.

Дополнительные библиотеки:

- `websocket-client`
- `certifi`

Установка зависимостей:

`pip install -r requirements.txt`

## Остановка

Для остановки сбора используется:

`Control + C`

В текущей версии при остановке во время автоматического переподключения иногда может потребоваться повторное нажатие `Control + C`.

## Хранение данных

В репозитории хранятся:

- исходный код;
- настройки;
- документация;
- небольшие sample-файлы.

## Визуализация данных

Отдельный Jupyter Notebook с графиками и сравнением инструментов:

[Открыть market_visualizations.ipynb](market_visualizations.ipynb)

В ноутбуке представлены:
- Binance BTC Spot vs Perpetual
- Binance ETH Spot vs Perpetual
- SPB BTC Perpetual vs Index
- SPB ETH Perpetual vs Index
