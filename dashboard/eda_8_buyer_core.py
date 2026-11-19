
import pandas as pd

df = pd.read_csv("output/quality_flagged_exports.csv")

buyers = (
    df.groupby("BUYER_CORE")
    .agg(
        TRANSACTIONS=("SOURCE_ROW", "count"),
        EXPORT_VALUE_LKR=("VALUE_LKR", "sum"),
        SUPPLIER_COUNT=("SUPPLIER_NAME", "nunique"),
        DESTINATION_COUNT=("COUNTRY_OF_DESTINATION", "nunique"),
        FULL_NAME_VARIANTS=("BUYER_FULL", "nunique")
    )
    .reset_index()
    .sort_values("EXPORT_VALUE_LKR", ascending=False)
)

total_value = df["VALUE_LKR"].sum()

buyers["VALUE_SHARE_%"] = (
    buyers["EXPORT_VALUE_LKR"] / total_value * 100
).round(2)

buyers["CUMULATIVE_SHARE_%"] = (
    buyers["VALUE_SHARE_%"].cumsum()
).round(2)

print("\n========== TOP 20 BUYER CORE ANALYSIS ==========")
print(buyers.head(20).to_string(index=False))

print("\n========== BUYER CORE CONCENTRATION ==========")
print("Unique buyer core records:", len(buyers))
print("Top 5 share:",
      buyers.head(5)["VALUE_SHARE_%"].sum(), "%")
print("Top 10 share:",
      buyers.head(10)["VALUE_SHARE_%"].sum(), "%")

print("\n========== BUYER NAME VARIATIONS ==========")
print(
    buyers[buyers["FULL_NAME_VARIANTS"] > 1]
    .head(20)
    .to_string(index=False)
)

buyers.to_csv("output/eda_buyer_core_analysis.csv", index=False)

print("\nSaved: output/eda_buyer_core_analysis.csv")
