import pandas as pd

FILES = [
    "btcusdt_spot_raw.csv",
    "btcusdt_usdm_futures_raw.csv",
    "ethusdt_spot_raw.csv",
    "ethusdt_usdm_futures_raw.csv",
]

CHUNK_SIZE = 500_000

for filename in FILES:
    print("\n" + "=" * 70)
    print(filename)
    print("=" * 70)

    total_rows = 0
    bad_quotes = 0
    zero_prices = 0
    missing_values = 0
    duplicate_update_ids = 0
    non_monotonic_updates = 0
    non_monotonic_time = 0

    first_time = None
    last_time = None
    previous_update_id = None
    previous_time = None

    for chunk in pd.read_csv(filename, chunksize=CHUNK_SIZE):
        total_rows += len(chunk)

        missing_values += chunk.isna().sum().sum()

        bad_quotes += (chunk["bid_price"] >= chunk["ask_price"]).sum()

        zero_prices += (
            (chunk["bid_price"] <= 0)
            | (chunk["ask_price"] <= 0)
        ).sum()

        duplicate_update_ids += chunk["update_id"].duplicated().sum()

        update_diff = chunk["update_id"].diff()
        non_monotonic_updates += (update_diff <= 0).sum()

        if previous_update_id is not None:
            if chunk["update_id"].iloc[0] <= previous_update_id:
                non_monotonic_updates += 1

        previous_update_id = chunk["update_id"].iloc[-1]

        time_col = (
            "event_time_ms"
            if "event_time_ms" in chunk.columns
            else "receive_time_ms"
        )

        if first_time is None:
            first_time = chunk[time_col].iloc[0]

        last_time = chunk[time_col].iloc[-1]

        time_diff = chunk[time_col].diff()
        non_monotonic_time += (time_diff < 0).sum()

        if previous_time is not None:
            if chunk[time_col].iloc[0] < previous_time:
                non_monotonic_time += 1

        previous_time = chunk[time_col].iloc[-1]

    print("Строк:", total_rows)
    print("Пропусков:", missing_values)
    print("bid >= ask:", bad_quotes)
    print("Нулевых/отрицательных цен:", zero_prices)
    print("Повторяющихся update_id:", duplicate_update_ids)
    print("Нарушений порядка update_id:", non_monotonic_updates)
    print("Нарушений порядка времени:", non_monotonic_time)

    if first_time is not None:
        print("Начало:", pd.to_datetime(first_time, unit="ms", utc=True))
        print("Конец:", pd.to_datetime(last_time, unit="ms", utc=True))
