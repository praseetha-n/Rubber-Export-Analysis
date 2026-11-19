
import pandas as pd

# Load quality-flagged data
df = pd.read_csv("output/quality_flagged_exports.csv")

# Supplier-level aggregation
supplier = (
    df.groupby("SUPPLIER_NAME")
    .agg(
        TRANSACTIONS=("SOURCE_ROW", "count"),
        EXPORT_VALUE_LKR=("VALUE_LKR", "sum"),
        REPORTED_QTY=("QTY", "sum"),
        UNIQUE_BUYERS=("BUYER_CORE", "nunique"),
        DESTINATION_COUNTRIES=("COUNTRY_OF_DESTINATION", "nunique")
    )
    .reset_index()
)

# Average value per transaction
supplier["AVG_VALUE_PER_TRANSACTION_LKR"] = (
    supplier["EXPORT_VALUE_LKR"] / supplier["TRANSACTIONS"]
)

# Contribution to total exports
total_value = supplier["EXPORT_VALUE_LKR"].sum()

supplier["VALUE_SHARE_%"] = (
    supplier["EXPORT_VALUE_LKR"] / total_value * 100
)

# Rank suppliers by export value
supplier = supplier.sort_values(
    "EXPORT_VALUE_LKR",
    ascending=False
).reset_index(drop=True)

supplier["RANK"] = supplier.index + 1

# Cumulative contribution
supplier["CUMULATIVE_SHARE_%"] = (
    supplier["VALUE_SHARE_%"].cumsum()
)

# Display top 20
print("\n========== TOP 20 SUPPLIERS ==========")

cols = [
    "RANK",
    "SUPPLIER_NAME",
    "TRANSACTIONS",
    "EXPORT_VALUE_LKR",
    "VALUE_SHARE_%",
    "CUMULATIVE_SHARE_%",
    "UNIQUE_BUYERS",
    "DESTINATION_COUNTRIES"
]

print(supplier[cols].head(20).to_string(index=False))

# Concentration summary
print("\n========== SUPPLIER CONCENTRATION ==========")

for n in [5, 10, 20]:
    share = supplier.head(n)["VALUE_SHARE_%"].sum()
    print(f"Top {n} suppliers contribution: {share:.2f}%")

# Save full supplier analysis
supplier.to_csv("output/eda_supplier_analysis.csv", index=False)

print("\nSaved: output/eda_supplier_analysis.csv")
