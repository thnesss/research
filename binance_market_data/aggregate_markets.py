from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

BINANCE_FILES = {
    ("BTC", "spot"): "btcusdt_spot_raw.csv",
    ("BTC", "perp"): "btcusdt_usdm_futures_raw.csv",
    ("ETH", "spot"): "ethusdt_spot_raw.csv",
    ("ETH", "perp"): "ethusdt_usdm_futures_raw.csv",
}

SPB_PERP_RE = re.compile(r"(?P<id>\d+);(?P<symbol>[^;]+);(?P<description>[^;]+);(?P<bid>[^;]+);(?P<ask>[^;]+);(?P<unknown1>[^;]+);(?P<bid_qty>[^;]+);(?P<ask_qty>[^;]+);(?P<unknown2>[^;]+);(?P<source_time_1>[^;]+);(?P<source_time_2>[^;]+);(?P<message_type>[^;]+);(?P<resource_type>[^;]+);(?P<channel>[^;]+)$")
SPB_INDEX_RE = re.compile(r"(?P<symbol>[^;]+);(?P<price>[^;]+);(?P<source_time_1>[^;]+);(?P<source_time_2>[^;]+);(?P<blank1>[^;]*);(?P<blank2>[^;]*);(?P<kind>[^;]+)$")
PREFIX_RE = re.compile(r"^\[(?P<receive_iso>[^ ]+) (?P<receive_ms>\d+)\]\s+(?P<body>.*)$")


def comma_float(value: str) -> float:
    return float(value.replace(",", "."))


def parse_utc(value: str | None) -> pd.Timestamp | None:
    if value is None:
        return None
    ts = pd.Timestamp(value)
    return ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")


def read_binance(path: Path, market: str, start: pd.Timestamp | None, end: pd.Timestamp | None) -> pd.DataFrame:
    usecols = ["receive_time_ms", "bid_price", "bid_qty", "ask_price", "ask_qty"]
    if market == "perp":
        usecols = ["event_time_ms", *usecols]

    parts: list[pd.DataFrame] = []
    for chunk in pd.read_csv(path, usecols=usecols, chunksize=500_000):
        time_col = "event_time_ms" if market == "perp" else "receive_time_ms"
        ts = pd.to_datetime(chunk[time_col], unit="ms", utc=True)
        mask = pd.Series(True, index=chunk.index)
        if start is not None:
            mask &= ts >= start
        if end is not None:
            mask &= ts <= end
        if not mask.any():
            continue

        out = chunk.loc[mask, ["bid_price", "bid_qty", "ask_price", "ask_qty"]].copy()
        out.insert(0, "timestamp", pd.Series(ts.loc[mask].array, index=out.index))
        parts.append(out)

    if not parts:
        return pd.DataFrame(columns=["timestamp", "bid", "bid_qty", "ask", "ask_qty"])

    df = pd.concat(parts, ignore_index=True)
    df = df.rename(columns={
        "bid_price": "bid",
        "ask_price": "ask",
    })
    df = df.sort_values("timestamp")
    return df


def read_spb_perp(path: Path, start: pd.Timestamp | None, end: pd.Timestamp | None) -> pd.DataFrame:
    rows = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as fh:
        for line in fh:
            prefix = PREFIX_RE.match(line.strip())
            if not prefix:
                continue
            ts = pd.to_datetime(int(prefix.group("receive_ms")), unit="ms", utc=True)
            if start is not None and ts < start:
                continue
            if end is not None and ts > end:
                continue
            match = SPB_PERP_RE.match(prefix.group("body"))
            if not match:
                continue
            d = match.groupdict()
            try:
                rows.append({
                    "timestamp": ts,
                    "bid": comma_float(d["bid"]),
                    "ask": comma_float(d["ask"]),
                    "bid_qty_raw": comma_float(d["bid_qty"]),
                    "ask_qty_raw": comma_float(d["ask_qty"]),
                })
            except ValueError:
                continue
    return pd.DataFrame(rows).sort_values("timestamp") if rows else pd.DataFrame(
        columns=["timestamp", "bid", "ask", "bid_qty_raw", "ask_qty_raw"]
    )


def read_spb_index(path: Path, start: pd.Timestamp | None, end: pd.Timestamp | None) -> pd.DataFrame:
    rows = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as fh:
        for line in fh:
            prefix = PREFIX_RE.match(line.strip())
            if not prefix:
                continue
            ts = pd.to_datetime(int(prefix.group("receive_ms")), unit="ms", utc=True)
            if start is not None and ts < start:
                continue
            if end is not None and ts > end:
                continue
            match = SPB_INDEX_RE.match(prefix.group("body"))
            if not match:
                continue
            d = match.groupdict()
            try:
                rows.append({"timestamp": ts, "price": comma_float(d["price"])})
            except ValueError:
                continue
    return pd.DataFrame(rows).sort_values("timestamp") if rows else pd.DataFrame(columns=["timestamp", "price"])


def quote_features(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    valid = (out["bid"] > 0) & (out["ask"] > 0) & (out["ask"] > out["bid"])
    out = out.loc[valid].copy()
    out["mid"] = (out["bid"] + out["ask"]) / 2
    out["spread"] = out["ask"] - out["bid"]
    out["spread_pct"] = out["spread"] / out["mid"] * 100
    return out


def last_per_second(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.set_index("timestamp").sort_index()
    return out.resample("1s").last().dropna(how="all")


def prefix_columns(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    return df.rename(columns={c: f"{prefix}_{c}" for c in df.columns})


def build_asset(asset: str, binance_dir: Path, spb_dir: Path, start: pd.Timestamp | None, end: pd.Timestamp | None) -> tuple[pd.DataFrame, dict]:
    spot = quote_features(read_binance(binance_dir / BINANCE_FILES[(asset, "spot")], "spot", start, end))
    bperp = quote_features(read_binance(binance_dir / BINANCE_FILES[(asset, "perp")], "perp", start, end))

    perp_glob = f"*_{asset}USDperpA_*.log"
    index_symbol = f"I{asset}USD"
    index_glob = f"{index_symbol}_{index_symbol}_*.log"
    spb_perp_path = next(iter(sorted(spb_dir.glob(perp_glob))), None)
    spb_index_path = next(iter(sorted(spb_dir.glob(index_glob))), None)
    if spb_perp_path is None or spb_index_path is None:
        raise FileNotFoundError(f"SPB files for {asset} not found in {spb_dir}")

    sperp = quote_features(read_spb_perp(spb_perp_path, start, end))
    sindex = read_spb_index(spb_index_path, start, end)

    streams = {
        "binance_spot": last_per_second(spot),
        "binance_perp": last_per_second(bperp),
        "spb_perp": last_per_second(sperp),
        "spb_index": last_per_second(sindex),
    }

    starts = [x.index.min() for x in streams.values() if not x.empty]
    ends = [x.index.max() for x in streams.values() if not x.empty]
    if len(starts) != 4 or len(ends) != 4:
        raise ValueError(f"One or more {asset} streams are empty in selected interval")

    overlap_start = max(starts)
    overlap_end = min(ends)
    if overlap_start > overlap_end:
        raise ValueError(f"No common time overlap for {asset}")

    grid = pd.date_range(overlap_start.floor("s"), overlap_end.floor("s"), freq="1s", tz="UTC")
    merged = pd.DataFrame(index=grid)

    for name in ("binance_spot", "binance_perp", "spb_perp"):
        aligned = streams[name].reindex(grid).ffill(limit=5)
        merged = merged.join(prefix_columns(aligned, name), how="left")
    aligned_index = streams["spb_index"].reindex(grid).ffill(limit=90)
    merged = merged.join(prefix_columns(aligned_index, "spb_index"), how="left")

    merged["binance_basis_pct"] = (
        (merged["binance_perp_mid"] - merged["binance_spot_mid"])
        / merged["binance_spot_mid"] * 100
    )
    merged["spb_basis_pct"] = (
        (merged["spb_perp_mid"] - merged["spb_index_price"])
        / merged["spb_index_price"] * 100
    )
    merged["perp_mid_diff_pct_vs_binance"] = (
        (merged["spb_perp_mid"] - merged["binance_perp_mid"])
        / merged["binance_perp_mid"] * 100
    )
    merged["spot_vs_spb_index_pct"] = (
        (merged["spb_index_price"] - merged["binance_spot_mid"])
        / merged["binance_spot_mid"] * 100
    )

    report = {
        "asset": asset,
        "overlap_start": overlap_start.isoformat(),
        "overlap_end": overlap_end.isoformat(),
        "seconds_on_grid": len(merged),
        "raw_rows_selected": {
            "binance_spot": len(spot),
            "binance_perp": len(bperp),
            "spb_perp": len(sperp),
            "spb_index": len(sindex),
        },
        "complete_seconds": int(merged[[
            "binance_spot_mid", "binance_perp_mid", "spb_perp_mid", "spb_index_price"
        ]].notna().all(axis=1).sum()),
    }
    merged.index.name = "timestamp"
    return merged.reset_index(), report


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate Binance Spot/Futures and SPB perpetual/index market data to a common 1-second grid.")
    parser.add_argument("--binance-dir", type=Path, required=True, help="Directory with four Binance *_raw.csv files")
    parser.add_argument("--spb-dir", type=Path, required=True, help="Directory with SPB perpetual and index .log files")
    parser.add_argument("--output-dir", type=Path, default=Path("aggregated"))
    parser.add_argument("--start", type=str, default=None, help="UTC start, e.g. 2026-08-26T14:00:00Z")
    parser.add_argument("--end", type=str, default=None, help="UTC end, e.g. 2026-08-26T20:00:00Z")
    args = parser.parse_args()

    start = parse_utc(args.start)
    end = parse_utc(args.end)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    reports = []
    for asset in ("BTC", "ETH"):
        aggregated, report = build_asset(asset, args.binance_dir, args.spb_dir, start, end)
        output = args.output_dir / f"{asset.lower()}_aggregated_1s.csv"
        aggregated.to_csv(output, index=False)
        reports.append(report)
        print(f"{asset}: {len(aggregated):,} rows -> {output}")
        print(f"  overlap: {report['overlap_start']} .. {report['overlap_end']}")
        print(f"  complete seconds: {report['complete_seconds']:,}")

    report_path = args.output_dir / "aggregation_report.json"
    report_path.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Report -> {report_path}")


if __name__ == "__main__":
    main()
