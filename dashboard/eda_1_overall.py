
import pandas as pd

# Load quality-flagged dataset
df = pd.read_csv("output/quality_flagged_exports.csv")

# -------------------------------
# 1. BASIC KPIs
# -------------------------------
total_records = len(df)
total_value = df["VALUE_LKR"].sum()
reported_qty = df["QTY"].sum()

unique_suppliers = df["SUPPLIER_NAME"].nunique()
unique_buyers = df["BUYER_CORE"].nunique()
unique_countries = df["COUNTRY_OF_DESTINATION"].nunique()
unique_hs_codes = df["HS_CODE"].nunique()

# -------------------------------
# 2. QUANTITY QUALITY INDICATORS
# -------------------------------
suspect_mask = df["QTY_SUSPECT"].astype(bool)

suspect_qty = df.loc[suspect_mask, "QTY"].sum()
quantity_excluding_flagged = reported_qty - suspect_qty

suspect_qty_share = (
    suspect_qty / reported_qty * 100
    if reported_qty else 0
)

# -------------------------------
# 3. MONTHLY PERFORMANCE
# -------------------------------
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

monthly["VALUE_SHARE_%"] = (
    monthly["EXPORT_VALUE_LKR"] / total_value * 100
).round(2)

monthly["TRANSACTION_SHARE_%"] = (
    monthly["TRANSACTIONS"] / total_records * 100
).round(2)

# -------------------------------
# 4. OVERALL KPI TABLE
# -------------------------------
kpis = pd.DataFrame({
    "KPI": [
        "Reporting Period",
        "Total Transactions",
        "Total Export Value (LKR)",
        "Reported Quantity (KGM)",
        "Quantity Flagged for Review (KGM)",
        "Quantity Flagged for Review (%)",
        "Quantity Excluding Flagged Records (KGM)",
        "Unique Suppliers",
        "Unique Buyers",
        "Destination Countries",
        "HS Codes"
    ],
    "Value": [
        "January - September 2026",
        total_records,
        total_value,
        reported_qty,
        suspect_qty,
        round(suspect_qty_share, 2),
        quantity_excluding_flagged,
        unique_suppliers,
        unique_buyers,
        unique_countries,
        unique_hs_codes
    ]
})

# -------------------------------
# 5. DISPLAY RESULTS
# -------------------------------
print("\n========== OVERALL EXPORT PERFORMANCE ==========")
print(kpis.to_string(index=False))

print("\n========== MONTHLY PERFORMANCE ==========")
print(monthly.to_string(index=False))

# -------------------------------
# 6. SAVE OUTPUTS
# -------------------------------
kpis.to_csv("output/eda_overall_kpis.csv", index=False)
monthly.to_csv("output/eda_overall_monthly.csv", index=False)

print("\nSaved:")
print("output/eda_overall_kpis.csv")
print("output/eda_overall_monthly.csv")
