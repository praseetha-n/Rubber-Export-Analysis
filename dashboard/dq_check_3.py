import re
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 80)
pd.set_option("display.max_rows", 200)

FILE = "data/2026 RUBBER EX SEP.xlsx"
major = pd.read_excel(FILE, sheet_name="MAJOR REPORT")
major.columns = [c.strip().replace("_ ", "_") for c in major.columns]
TOTAL_VALUE = major["VALUE_LKR"].sum()

def core_name(s):
    first = str(s).split("\n")[0].upper()
    first = re.sub(r"^\s*(M/S\.?|MESSRS\.?)\s*", "", first)   # remove M/S prefix
    first = re.sub(r"[^A-Z0-9 ]", " ", first)                 # punctuation -> space
    return re.sub(r"\s+", " ", first).strip()

# Checking columns only; the data itself is not changed or merged
major["BUYER_FULL"] = major["BUYER_NAME"].str.replace(r"\s*\n\s*", " | ", regex=True).str.strip()
major["BUYER_CORE"] = major["BUYER_NAME"].apply(core_name)

print("=== BUYERS ===")
print("Unique full buyer strings        :", major["BUYER_FULL"].nunique())
print("Unique first-line names (cleaned):", major["BUYER_CORE"].nunique())

g = major.groupby("BUYER_CORE").agg(
    full_versions=("BUYER_FULL", "nunique"),
    countries=("COUNTRY_OF_DESTINATION", "nunique"),
    rows=("VALUE_LKR", "size"),
    value=("VALUE_LKR", "sum"),
).sort_values("value", ascending=False)
g["share_%"] = (g["value"] / TOTAL_VALUE * 100).round(2)

print("\nTop 15 buyers by value (first-line name):")
print(g.head(15))

print("\nTop 5 / top 10 buyer share of value:",
      f"{g.head(5)['value'].sum()/TOTAL_VALUE:.1%} /",
      f"{g.head(10)['value'].sum()/TOTAL_VALUE:.1%}")
print("Buyers appearing in only 1 row    :", (g["rows"] == 1).sum())

print("\nSame first-line name written with several full versions (top 8):")
multi = g[g["full_versions"] > 1]
print("Count:", len(multi))
print(multi.head(8))

print("\nSame first-line name in more than one country (top 8):")
print(g[g["countries"] > 1].head(8))

print("\n=== HS CODES ===")
hs = major.groupby("HS_CODE").agg(rows=("VALUE_LKR", "size"),
                                   qty_kg=("QTY", "sum"),
                                   value=("VALUE_LKR", "sum"))
hs["share_%"] = (hs["value"] / TOTAL_VALUE * 100).round(2)
print(hs.sort_values("value", ascending=False))

print("\nMost common product description for each HS code:")
for code, sub in major.groupby("HS_CODE"):
    print(code, "->", sub["PRODUCT_DESCRIPTION_11"].value_counts().head(2).index.tolist())

print("\n=== COUNTRIES ===")
print(sorted(major["COUNTRY_OF_DESTINATION"].unique()))