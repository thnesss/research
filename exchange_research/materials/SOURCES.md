# Источники данных:

В данном файле собраны основные источники, использованные для формирования выборки бирж, сбора исходных данных, проведения количественного анализа и подготовки итоговых аналитических выводов.

Исходные значения находятся в файле [`../data/Exchanges.xlsx`](../data/Exchanges.xlsx), расчеты и обработка данных представлены в Jupyter Notebook в папке [`../notebooks`](../notebooks/).

> **Важно:** часть показателей, использованных в исследовании, является динамической. Значения Average Bid-Ask Spread, количества торговых инструментов, комиссий, Trust Score и торговых объемов могут изменяться с течением времени. В исследовании использовались значения, актуальные на момент сбора данных. Поэтому текущие значения на страницах источников могут отличаться от значений, зафиксированных в Excel.

---

# 1. Криптовалютные биржи

## 1.1. Total Trading Volume

### CoinMarketCap — Crypto Exchange Monthly Report, June 2026

**Источник:**  
https://coinmarketcap.com/events/crypto-exchange-monthly-report-june-2026/

**Раздел:** `Total Volume by Exchange — Spot + Derivatives, USD billions`

В отчете представлены данные по совокупному объему Spot + Derivatives для Binance, OKX, Bybit, Gate, MEXC, Bitget, HTX, Coinbase / Deribit и Crypto.com.

### Hyperliquid

**Источник:** ASXN Hyperliquid Screener  
https://hyperscreener.asxn.xyz/home

### Другие площадки

Для площадок, отсутствующих в основном отчете CoinMarketCap, использовались страницы соответствующих бирж на CoinGecko и дополнительные рыночные источники.

**CoinGecko — Exchanges:**  
https://www.coingecko.com/en/exchanges

В эту группу входят Bitfinex, Kraken, BingX и другие площадки из исходной выборки.

---

## 1.2. Trust Score

### CoinGecko — Exchange Ranking

**Источник:**  
https://www.coingecko.com/en/exchanges

**Методология Trust Score:**  
https://support.coingecko.com/hc/en-us/articles/36442561461657-Trust-Score-Methodology

Для децентрализованных площадок, для которых сопоставимый Trust Score отсутствовал, в исходной таблице указано `N/A`.

---

## 1.3. Average Bid-Ask Spread

### CoinGecko

**Основной источник:**  
https://www.coingecko.com/en/exchanges

Показатель Average Bid-Ask Spread собирался со страниц соответствующих бирж на CoinGecko. На странице каждой площадки CoinGecko публикует статистику ликвидности, включая показатель среднего Bid-Ask Spread.
Значения были зафиксированы на момент проведения исследования.

Примеры прямых страниц:

**Binance:**  
https://www.coingecko.com/en/exchanges/binance

**Bybit:**  
https://www.coingecko.com/en/exchanges/bybit_spot

**OKX:**  
https://www.coingecko.com/en/exchanges/okx

**MEXC:**  
https://www.coingecko.com/en/exchanges/mexc

**Gate:**  
https://www.coingecko.com/en/exchanges/gate

**HTX:**  
https://www.coingecko.com/en/exchanges/htx

**Bitget:**  
https://www.coingecko.com/en/exchanges/bitget

**Coinbase:**  
https://www.coingecko.com/en/exchanges/coinbase-exchange

**Crypto.com:**  
https://www.coingecko.com/en/exchanges/crypto_com

**Bitfinex:**  
https://www.coingecko.com/en/exchanges/bitfinex

**Kraken:**  
https://www.coingecko.com/en/exchanges/kraken

**BingX:**  
https://www.coingecko.com/en/exchanges/bingx

---

## 1.4. Base Maker Fee / Base Taker Fee

### Binance

**Trading Fees:**  
https://www.binance.com/en/fee/trading

### Bybit

**Spot Trading Fees Explained:**  
https://www.bybit.com/en/help-center/article/Bybit-Spot-Fees-Explained

### OKX

**Trading Fee Rules:**  
https://www.okx.com/en-eu/help/trading-fee-rules-faq

### MEXC

**Trading Fees:**  
https://www.mexc.com/fee

### Gate

**VIP Levels & Trading Fees:**  
https://www.gate.com/fee

### HTX

**Fee Rates:**  
https://www.htx.com/en-us/fee/

### Bitget

**Spot Trading Fees:**  
https://www.bitget.com/support/articles/12560603820584

### Coinbase

**Advanced Trade Fees:**  
https://help.coinbase.com/en/coinbase/trading-and-funding/advanced-trade/advanced-trade-fees

### Crypto.com

**Fees & Limits:**  
https://crypto.com/exchange/document/fees-limits

### Bitfinex

**Trading Fees:**  
https://www.bitfinex.com/fees/

### Kraken

**Maker and Taker Fees:**  
https://support.kraken.com/hc/articles/360000526126-what-are-maker-and-taker-fees-

### Hyperliquid

**Официальная документация по комиссиям:**  
https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees

---

## 1.5. Number of Trading Instruments

### CoinGecko

**Основной источник:**  
https://www.coingecko.com/en/exchanges

В количественном анализе использовался срез данных, зафиксированный на момент их сбора.

Примеры прямых страниц:

**Binance:**  
https://www.coingecko.com/en/exchanges/binance

**Bybit:**  
https://www.coingecko.com/en/exchanges/bybit_spot

**OKX:**  
https://www.coingecko.com/en/exchanges/okx

**MEXC:**  
https://www.coingecko.com/en/exchanges/mexc

**Gate:**  
https://www.coingecko.com/en/exchanges/gate

**HTX:**  
https://www.coingecko.com/en/exchanges/htx

**Bitget:**  
https://www.coingecko.com/en/exchanges/bitget

**Coinbase:**  
https://www.coingecko.com/en/exchanges/coinbase-exchange

**Crypto.com:**  
https://www.coingecko.com/en/exchanges/crypto_com

**Bitfinex:**  
https://www.coingecko.com/en/exchanges/bitfinex

**Kraken:**  
https://www.coingecko.com/en/exchanges/kraken

**BingX:**  
https://www.coingecko.com/en/exchanges/bingx

---

## 1.6. Децентрализованные биржи

### CoinGecko — Decentralized Derivatives Exchanges

**Источник:**  
https://www.coingecko.com/en/exchanges/derivatives/decentralized

Использовался для формирования и дополнительной проверки выборки децентрализованных деривативных площадок.

### Hyperliquid

**ASXN Hyperliquid Screener:**  
https://hyperscreener.asxn.xyz/home

Использовался как дополнительный источник статистики по Hyperliquid.

### Aster

**CoinGecko — Aster:**  
https://www.coingecko.com/en/exchanges/aster-spot

### Lighter

**CoinGecko — Lighter:**  
https://www.coingecko.com/en/exchanges/lighter

### PancakeSwap

**CoinGecko — PancakeSwap:**  
https://www.coingecko.com/en/exchanges/pancakeswap-v3-bsc

---

## 1.7. Дополнительный источник по рынку криптодеривативов

### CoinGlass — 2026 H1 Cryptocurrency Derivatives Market Report

**Источник:**  
https://www.coinglass.com/learn/2026h1-market-report-en

---

# 2. Традиционные биржи деривативов

## 2.1. YTD Trading Volume

### Futures Industry Association (FIA) — ETD Tracker

**Источник:**  
https://www.fia.org/fia/etd-tracker

**Раздел:** `Volume by Exchange`


---

## 2.2. YTD Volume Change

### Futures Industry Association (FIA) — ETD Tracker

**Источник:**  
https://www.fia.org/fia/etd-tracker

**Раздел:** `Volume by Exchange`

---

## 2.3. Trust Score традиционных бирж

Для традиционных бирж показатель Trust Score не был взят из внешнего рейтинга.

Он был сформирован экспертно в рамках исследования как дополнительная оценка надежности, зрелости и устойчивости торговой площадки.

---

## 4.1. CME Group

**Markets:**  
https://www.cmegroup.com/markets.html

Использовано для анализа ассортимента деривативов и классов активов CME.

CME предоставляет рынки деривативов на процентные ставки, фондовые индексы, валюты, энергоресурсы, металлы, сельскохозяйственные товары и криптоактивы.

---

## 4.2. National Stock Exchange of India (NSE)

**Derivatives Market:**  
https://www.nseindia.com/market-data/derivatives-market

Использовано для дополнительной проверки структуры рынка деривативов NSE.

---

## 4.3. Eurex

**Markets:**  
https://www.eurex.com/ex-en/markets

**Product Overview:**  
https://www.eurex.com/ex-en/markets/productSearch

Использовано для анализа ассортимента европейских деривативов и роли Eurex на европейском рынке.

---

## 4.4. ICE Futures Europe

**ICE Futures Europe:**  
https://www.ice.com/futures-europe

Использовано для анализа специализации площадки, в частности ее роли на международном рынке энергетических деривативов.

---

## 4.5. Nasdaq PHLX

**Nasdaq Options Markets:**  
https://www.nasdaqtrader.com/Trader.aspx?id=Options

Использовано для проверки специализации Nasdaq PHLX на рынке опционов.

---

# 5. Источники для дополнительной оценки криптовалютных бирж

При формировании итогового аналитического TOP-5 учитывались не только результаты Final Score, но и дополнительные характеристики площадок.

## Binance

**Proof of Reserves:**  
https://www.binance.com/en/proof-of-reserves

**Trading Fees:**  
https://www.binance.com/en/fee/trading

---

## OKX

**Proof of Reserves:**  
https://www.okx.com/proof-of-reserves

**Trading Fee Rules:**  
https://www.okx.com/en-eu/help/trading-fee-rules-faq

---

## Bybit

**Proof of Reserves:**  
https://www.bybit.com/en/proof-of-reserves

**Spot Trading Fees:**  
https://www.bybit.com/en/help-center/article/Bybit-Spot-Fees-Explained

---

## Bitget

**Proof of Reserves:**  
https://www.bitget.com/proof-of-reserves

**Protection Fund:**  
https://www.bitget.com/protection-fund

**Spot Trading Fees:**  
https://www.bitget.com/support/articles/12560603820584

---

## Gate

**Proof of Reserves:**  
https://www.gate.com/proof-of-reserves

**Trading Fees:**  
https://www.gate.com/fee

---
