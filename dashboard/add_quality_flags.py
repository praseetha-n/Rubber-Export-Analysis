
import re
import pandas as pd

# Load the existing cleaned dataset
df = pd.read_csv("output/cleaned_exports.csv", dtype={"HS_CODE": str})

# 1. Flag the three records identified for manual review
suspect_rows = [1569, 3170, 3805]
df["QTY_SUSPECT"] = df["SOURCE_ROW"].isin(suspect_rows)

# 2. Flag unit-price outliers relative to each HS code median
df["HS_MEDIAN_PER_KG"] = (
    df.groupby("HS_CODE")["UNIT_VALUE_LKR_PER_KG"].transform("median")
)

df["RATIO_TO_MEDIAN"] = (
    df["UNIT_VALUE_LKR_PER_KG"] / df["HS_MEDIAN_PER_KG"]
)

df["UNIT_PRICE_OUTLIER"] = (
    (df["RATIO_TO_MEDIAN"] < 0.1) |
    (df["RATIO_TO_MEDIAN"] > 10)
)

# 3. Check whether a number in the description matches QTY
def qty_matches_description(row):
    numbers = [
        int(n.replace(",", ""))
        for n in re.findall(
            r"\d[\d,]*",
            str(row["PRODUCT_DESCRIPTION_11"])
        )
        if n.replace(",", "").isdigit()
    ]

    return any(
        n >= 100 and abs(n - row["QTY"]) < 0.5
        for n in numbers
    )

df["DESCRIPTION_QTY_MATCH"] = df.apply(
    qty_matches_description,
    axis=1
)

# Save as a separate file; do not overwrite the cleaned dataset
output_path = "output/quality_flagged_exports.csv"
df.to_csv(output_path, index=False)

# Summary
print("=== QUALITY FLAGS SUMMARY ===")
print("Total records:", len(df))
print("QTY_SUSPECT:", df["QTY_SUSPECT"].sum())
print("UNIT_PRICE_OUTLIER:", df["UNIT_PRICE_OUTLIER"].sum())
print("DESCRIPTION_QTY_MATCH:", df["DESCRIPTION_QTY_MATCH"].sum())

print("\n=== THREE MANUAL REVIEW RECORDS ===")
cols = [
    "SOURCE_ROW", "SUPPLIER_NAME", "PRODUCT_DESCRIPTION_11",
    "QTY", "VALUE_LKR", "QTY_SUSPECT",
    "UNIT_PRICE_OUTLIER", "DESCRIPTION_QTY_MATCH"
]
print(df[df["QTY_SUSPECT"]][cols].to_string(index=False))

print("\nSaved:", output_path)
