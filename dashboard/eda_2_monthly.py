
import pandas as pd

# Load quality-flagged data
df = pd.read_csv("output/quality_flagged_exports.csv")

# Monthly aggregation
monthly = (
    df.groupby(["MONTH_NUM", "MONTH"])
    .agg(
        TRANSACTIONS=("SOURCE_ROW", "count"),
        EXPORT_VALUE_LKR=("VALUE_LKR", "sum"),
        REPORTED_QTY=("QTY", "sum")
    )
    .reset_index()
    .sort_values("MONTH_NUM")
)

# Overall total
total_value = monthly["EXPORT_VALUE_LKR"].sum()

# Average export value per transaction
monthly["AVG_VALUE_PER_TRANSACTION_LKR"] = (
    monthly["EXPORT_VALUE_LKR"] / monthly["TRANSACTIONS"]
)

# Monthly contribution
monthly["VALUE_SHARE_%"] = (
    monthly["EXPORT_VALUE_LKR"] / total_value * 100
)

# Month-on-month value change
monthly["MOM_CHANGE_%"] = (
    monthly["EXPORT_VALUE_LKR"].pct_change() * 100
)

# Cumulative export value
monthly["CUMULATIVE_VALUE_LKR"] = (
    monthly["EXPORT_VALUE_LKR"].cumsum()
)

# Rounding for display
monthly["VALUE_SHARE_%"] = monthly["VALUE_SHARE_%"].round(2)
monthly["MOM_CHANGE_%"] = monthly["MOM_CHANGE_%"].round(2)
monthly["AVG_VALUE_PER_TRANSACTION_LKR"] = (
    monthly["AVG_VALUE_PER_TRANSACTION_LKR"].round(2)
)

print("\n========== MONTHLY EXPORT ANALYSIS ==========")
print(monthly.to_string(index=False))

# Highest and lowest month
highest = monthly.loc[monthly["EXPORT_VALUE_LKR"].idxmax()]
lowest = monthly.loc[monthly["EXPORT_VALUE_LKR"].idxmin()]

print("\n========== KEY FINDINGS ==========")
print(
    f"Highest month: {highest['MONTH']} "
    f"| LKR {highest['EXPORT_VALUE_LKR']:,.0f}"
)
print(
    f"Lowest month: {lowest['MONTH']} "
    f"| LKR {lowest['EXPORT_VALUE_LKR']:,.0f}"
)

# Save
monthly.to_csv("output/eda_monthly_analysis.csv", index=False)

print("\nSaved: output/eda_monthly_analysis.csv")
