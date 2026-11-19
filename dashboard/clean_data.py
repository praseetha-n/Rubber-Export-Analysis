import re
from pathlib import Path
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", 45)

FILE = "data/2026 RUBBER EX SEP.xlsx"
OUT = Path("output")
OUT.mkdir(exist_ok=True)

raw = pd.read_excel(FILE, sheet_name="MAJOR REPORT")
raw.columns = [c.strip().replace("_ ", "_") for c in raw.columns]
df = raw.copy()

def one_line(s):
    return re.sub(r"\s*\n\s*", " | ", str(s)).strip()

def first_line(s):
    return str(s).split("\n")[0].strip()

def core_buyer(s):
    t = first_line(s).upper()
    t = re.sub(r"^\s*(M/S\.?|MESSRS\.?)\s*", "", t)
    t = re.sub(r"[^A-Z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

# traceability: Excel row number (header assumed in row 1)
df["SOURCE_ROW"] = df.index + 2

# months
months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
df["MONTH"] = df["MONTH"].str.strip().str.upper()
df["MONTH_NUM"] = df["MONTH"].map({m: i + 1 for i, m in enumerate(months)})

# names (originals kept in one-line form; nothing merged)
df["SUPPLIER_NAME"] = df["SUPPLIER_MAME"].apply(first_line)
df["SUPPLIER_FULL"] = df["SUPPLIER_MAME"].apply(one_line)
df["BUYER_CORE"] = df["BUYER_NAME"].apply(core_buyer)
df["BUYER_FULL"] = df["BUYER_NAME"].apply(one_line)

# flags and helper columns (no rows removed)
df["TIN_NUMB"] = df["TIN_NUMB"].astype("string").str.strip()
df["TIN_MISSING"] = df["TIN_NUMB"].isna()
df["IS_EXTRA_DUPLICATE"] = raw.duplicated(keep="first")   # computed on original columns
df["HS_CODE"] = df["HS_CODE"].astype(str)
df["UNIT_VALUE_LKR_PER_KG"] = (df["VALUE_LKR"] / df["QTY"]).where(df["QTY"] > 0).round(2)

# validation: stop immediately if anything is off
TOTAL_VALUE = df["VALUE_LKR"].sum()
assert len(df) == 4129, "row count changed"
assert abs(df["QTY"].sum() - 37163153.936) < 0.001, "QTY total changed"
assert TOTAL_VALUE == 27572919808, "VALUE total changed"
assert df["MONTH_NUM"].notna().all(), "unknown month found"
print("VALIDATION PASSED: 4,129 rows | QTY and VALUE totals match")

cols = ["SOURCE_ROW", "YEAR", "MONTH", "MONTH_NUM", "TIN_NUMB", "SUPPLIER_NAME",
        "SUPPLIER_FULL", "BUYER_CORE", "BUYER_FULL", "COUNTRY_OF_DESTINATION",
        "HS_CODE", "GOODSDESC", "PRODUCT_DESCRIPTION_11", "UOM", "QTY", "VALUE_LKR",
        "UNIT_VALUE_LKR_PER_KG", "TIN_MISSING", "IS_EXTRA_DUPLICATE"]
df = df[cols]
df.to_csv(OUT / "cleaned_exports.csv", index=False, encoding="utf-8-sig")
df.to_excel(OUT / "cleaned_exports.xlsx", index=False)
print("Saved: output/cleaned_exports.csv and output/cleaned_exports.xlsx")

# buyer review file (open in Excel and check manually)
rev = (df.groupby("BUYER_CORE")
         .agg(rows=("VALUE_LKR", "size"),
              value=("VALUE_LKR", "sum"),
              countries=("COUNTRY_OF_DESTINATION", lambda s: " ; ".join(sorted(s.unique()))),
              full_versions=("BUYER_FULL", lambda s: " ## ".join(sorted(s.unique()))))
         .sort_values("value", ascending=False).head(40))
rev["share_%"] = (rev["value"] / TOTAL_VALUE * 100).round(2)
rev.to_csv(OUT / "buyer_review_top40.csv", encoding="utf-8-sig")
print("Saved: output/buyer_review_top40.csv")

# look at the HS 40169100 quantity anomaly
print("\nUnit value by HS code (LKR per kg):")
uv = df.groupby("HS_CODE").agg(qty_kg=("QTY", "sum"), value=("VALUE_LKR", "sum"))
uv["LKR_per_kg"] = (uv["value"] / uv["qty_kg"]).round(1)
print(uv.sort_values("qty_kg", ascending=False))

print("\nTop 10 rows by QTY:")
show = ["SOURCE_ROW", "MONTH", "SUPPLIER_NAME", "COUNTRY_OF_DESTINATION", "HS_CODE",
        "PRODUCT_DESCRIPTION_11", "QTY", "VALUE_LKR", "UNIT_VALUE_LKR_PER_KG"]
print(df.sort_values("QTY", ascending=False).head(10)[show].to_string())