
import pandas as pd

# Load data
df = pd.read_csv("output/quality_flagged_exports.csv")

# Identify top 10 suppliers by total export value
top10 = (
    df.groupby("SUPPLIER_NAME")["VALUE_LKR"]
    .sum()
    .nlargest(10)
    .index
)

# Filter top 10 supplier records
top_df = df[df["SUPPLIER_NAME"].isin(top10)].copy()

# Monthly supplier performance
monthly = (
    top_df.groupby(["MONTH_NUM", "MONTH", "SUPPLIER_NAME"])
    .agg(
        TRANSACTIONS=("SOURCE_ROW", "count"),
        EXPORT_VALUE_LKR=("VALUE_LKR", "sum")
    )
    .reset_index()
    .sort_values(["MONTH_NUM", "EXPORT_VALUE_LKR"],
                 ascending=[True, False])
)

# Calculate each supplier's contribution within its month
monthly_total = (
    df.groupby("MONTH_NUM")["VALUE_LKR"]
    .sum()
    .rename("MONTH_TOTAL_VALUE")
)

monthly = monthly.join(
    monthly_total,
    on="MONTH_NUM"
)

monthly["MONTH_VALUE_SHARE_%"] = (
    monthly["EXPORT_VALUE_LKR"] /
    monthly["MONTH_TOTAL_VALUE"] * 100
).round(2)

# Display results
print("\n========== TOP 10 SUPPLIERS - MONTHLY PERFORMANCE ==========")

print(
    monthly.to_string(index=False)
)

# Pivot table for easier comparison
pivot = monthly.pivot(
    index="SUPPLIER_NAME",
    columns="MONTH",
    values="EXPORT_VALUE_LKR"
).fillna(0)

print("\n========== SUPPLIER MONTHLY EXPORT VALUE ==========")
print(pivot.to_string())

# Save results
monthly.to_csv(
    "output/eda_supplier_monthly.csv",
    index=False
)

pivot.to_csv(
    "output/eda_supplier_monthly_pivot.csv"
)

print("\nSaved:")
print("output/eda_supplier_monthly.csv")
print("output/eda_supplier_monthly_pivot.csv")
