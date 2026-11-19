
import pandas as pd

# Load data
df = pd.read_csv("output/quality_flagged_exports.csv")

# Group by HS Code
hs = (
    df.groupby("HS_CODE")
    .agg(
        TRANSACTIONS=("SOURCE_ROW", "count"),
        EXPORT_VALUE_LKR=("VALUE_LKR", "sum"),
        REPORTED_QTY=("QTY", "sum"),
        SUPPLIER_COUNT=("SUPPLIER_NAME", "nunique"),
        DESTINATION_COUNT=("COUNTRY_OF_DESTINATION", "nunique")
    )
    .reset_index()
    .sort_values("EXPORT_VALUE_LKR", ascending=False)
)

# Calculate value contribution
total_value = df["VALUE_LKR"].sum()

hs["VALUE_SHARE_%"] = (
    hs["EXPORT_VALUE_LKR"] / total_value * 100
).round(2)

hs["CUMULATIVE_SHARE_%"] = (
    hs["VALUE_SHARE_%"].cumsum()
).round(2)

# Display results
print("\n========== HS CODE PERFORMANCE ==========")
print(hs.to_string(index=False))

# Top category concentration
print("\n========== HS CODE CONCENTRATION ==========")
print("Top 2 HS Codes share:",
      hs.head(2)["VALUE_SHARE_%"].sum(), "%")

print("Top 3 HS Codes share:",
      hs.head(3)["VALUE_SHARE_%"].sum(), "%")

print("Total HS Codes:", len(hs))

# Save
hs.to_csv("output/eda_hs_analysis.csv", index=False)

print("\nSaved: output/eda_hs_analysis.csv")

