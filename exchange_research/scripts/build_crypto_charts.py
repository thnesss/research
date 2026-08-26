from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "figures"
OUTPUT.mkdir(exist_ok=True)

# Вклады рассчитаны в notebook как normalized value × criterion weight × 100.
components = pd.DataFrame(
    {
        "Биржа": ["Binance", "MEXC", "OKX", "Gate", "Bybit"],
        "Объём торгов": [35.0000, 8.2277, 14.7309, 8.2520, 9.4303],
        "Trust Score": [30.0, 27.0, 30.0, 30.0, 27.0],
        "Комиссия": [16.0, 16.0, 16.0, 16.0, 16.0],
        "Количество инструментов": [6.6139, 15.0, 5.3454, 11.7221, 3.5636],
    }
).set_index("Биржа")

colors = ["#31688e", "#35b779", "#fde725", "#9e9ac8"]
axis = components.plot(
    kind="barh",
    stacked=True,
    figsize=(11, 6),
    color=colors,
    width=0.72,
)
axis.invert_yaxis()
axis.set_title("Из чего складывается количественная оценка TOP-5")
axis.set_xlabel("Вклад критерия в Final Score, баллы")
axis.set_ylabel("")
axis.grid(axis="x", alpha=0.25)
axis.legend(loc="lower right", frameon=False)
totals = components.sum(axis=1)
for row, total in enumerate(totals):
    axis.text(total + 0.7, row, f"{total:.2f}", va="center")
plt.tight_layout()
plt.savefig(OUTPUT / "crypto_score_components.png", dpi=180, bbox_inches="tight")
plt.close()

quantitative = {
    "Binance": 1,
    "MEXC": 2,
    "OKX": 3,
    "Gate": 4,
    "Bybit": 5,
    "Bitget": 6,
}
expert = {
    "Binance": 1,
    "OKX": 2,
    "Bybit": 3,
    "Bitget": 4,
    "Gate": 5,
    "MEXC": 6,
}

fig, axis = plt.subplots(figsize=(10, 6))
for exchange in quantitative:
    q_rank = quantitative[exchange]
    e_rank = expert[exchange]
    axis.plot([0, 1], [q_rank, e_rank], marker="o", linewidth=1.8)
    axis.text(-0.03, q_rank, exchange, ha="right", va="center")
    axis.text(1.03, e_rank, exchange, ha="left", va="center")
axis.set_xlim(-0.35, 1.35)
axis.set_ylim(6.5, 0.5)
axis.set_xticks([0, 1], ["Количественная модель", "Мой экспертный итог"])
axis.set_yticks(range(1, 7))
axis.set_ylabel("Место")
axis.set_title("Как изменился TOP после экспертной проверки")
axis.grid(axis="y", alpha=0.25)
for side in ("top", "right", "bottom"):
    axis.spines[side].set_visible(False)
plt.tight_layout()
plt.savefig(OUTPUT / "crypto_ranking_comparison.png", dpi=180, bbox_inches="tight")
plt.close()
