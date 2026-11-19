import re
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 55)
pd.set_option("display.max_rows", 100)

df = pd.read_csv("output/cleaned_exports.csv", dtype={"HS_CODE": str})
TOTAL_QTY = df["QTY"].sum()
TOTAL_VALUE = df["VALUE_LKR"].sum()

# ---- 1) unit price outliers, compared with the HS code's own median ----
df["HS_MEDIAN_PER_KG"] = df.groupby("HS_CODE")["UNIT_VALUE_LKR_PER_KG"].transform("median")
df["RATIO_TO_MEDIAN"] = (df["UNIT_VALUE_LKR_PER_KG"] / df["HS_MEDIAN_PER_KG"]).round(3)

print("Median LKR/kg by HS code:")
print(df.groupby("HS_CODE")["UNIT_VALUE_LKR_PER_KG"].median().round(1))

low = df[df["RATIO_TO_MEDIAN"] < 0.1]
high = df[df["RATIO_TO_MEDIAN"] > 10]
print("\n=== 1) Unit price outliers (below 1/10 or above 10x the HS median) ===")
print("Rows too low :", len(low), "| Rows too high:", len(high))
out = pd.concat([low, high])
print("Their QTY share  :", f"{out['QTY'].sum() / TOTAL_QTY:.2%}")
print("Their VALUE share:", f"{out['VALUE_LKR'].sum() / TOTAL_VALUE:.2%}")
cols = ["SOURCE_ROW", "MONTH", "SUPPLIER_NAME", "COUNTRY_OF_DESTINATION", "HS_CODE",
        "PRODUCT_DESCRIPTION_11", "QTY", "VALUE_LKR", "UNIT_VALUE_LKR_PER_KG", "RATIO_TO_MEDIAN"]
print("\nLowest unit price rows:")
print(low.sort_values("RATIO_TO_MEDIAN").head(15)[cols].to_string())
print("\nHighest unit price rows:")
print(high.sort_values("RATIO_TO_MEDIAN", ascending=False).head(15)[cols].to_string())

# ---- 2) QTY exactly equals a number written in the description ----
def qty_matches_description(row):
    nums = [int(n.replace(",", "")) for n in re.findall(r"\d[\d,]*", str(row["PRODUCT_DESCRIPTION_11"]))
            if n.replace(",", "").isdigit()]
    return any(n >= 100 and abs(n - row["QTY"]) < 0.5 for n in nums)

df["QTY_EQUALS_DESC_NUMBER"] = df.apply(qty_matches_description, axis=1)
m = df[df["QTY_EQUALS_DESC_NUMBER"]]
print("\n=== 2) Rows where QTY equals a number in the description (maybe a piece count) ===")
print("Rows:", len(m), "| QTY share:", f"{m['QTY'].sum() / TOTAL_QTY:.2%}",
      "| VALUE share:", f"{m['VALUE_LKR'].sum() / TOTAL_VALUE:.2%}")
print(m.sort_values("VALUE_LKR", ascending=False).head(10)[cols[:9]].to_string())

# ---- 3) buyer names to review ----
print("\n=== 3) Buyer names to review ===")
rev = pd.read_csv("output/buyer_review_top40.csv")
targets = ["SE", "DACHSER FRANCE CONTRACT LOGISTICS P", "ID GROUP", "SAS ID GROUP"]
for _, r in rev[rev["BUYER_CORE"].isin(targets)].iterrows():
    print("\n>>", r["BUYER_CORE"], "| rows:", r["rows"], "| share %:", r["share_%"])
    print("   countries:", r["countries"])
    for v in str(r["full_versions"]).split(" ## ")[:6]:
        print("   -", v)