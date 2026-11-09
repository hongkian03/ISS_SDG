"""
plot_gdp.py
-----------
Reads gdp.xlsx and plots Vietnam's annual growth rate of real GDP per capita
(SDG 8.1.1) over 2000–2023.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

XLSX_PATH = "gdp.xlsx"
SHEET = "Record format"

df = pd.read_excel(XLSX_PATH, sheet_name=SHEET)
df = df[["TimePeriod", "Value"]].dropna().sort_values("TimePeriod")
df["TimePeriod"] = df["TimePeriod"].astype(int)

fig, ax = plt.subplots(figsize=(12, 5))

ax.bar(
    df["TimePeriod"],
    df["Value"],
    color=["#d32f2f" if v < 0 else "#1565c0" for v in df["Value"]],
    edgecolor="white",
    linewidth=0.5,
    zorder=3,
)
ax.plot(df["TimePeriod"], df["Value"], color="#ffa000", linewidth=1.8,
        marker="o", markersize=4, zorder=4, label="Annual growth rate")

ax.axhline(0, color="black", linewidth=0.8, linestyle="--", zorder=2)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
ax.set_xticks(df["TimePeriod"])
ax.set_xticklabels(df["TimePeriod"], rotation=45, ha="right", fontsize=9)
ax.grid(axis="y", linestyle=":", linewidth=0.7, alpha=0.7, zorder=0)

ax.set_title(
    "Vietnam – Annual Growth Rate of Real GDP per Capita\n"
    "SDG Indicator 8.1.1 (2000–2023)",
    fontsize=13, fontweight="bold", pad=14,
)
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Growth Rate (%)", fontsize=11)
ax.legend(fontsize=9)

plt.tight_layout()
output_path = "gdp_growth_vietnam.png"
plt.savefig(output_path, dpi=150)
print(f"Plot saved to {output_path}")
plt.show()
