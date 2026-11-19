import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 70)
pd.set_option("display.max_rows", 200)

FILE = "data/2026 RUBBER EX SEP.xlsx"
major = pd.read_excel(FILE, sheet_name="MAJOR REPORT")
major.columns = [c.strip().replace("_ ", "_") for c in major.columns]
TOTAL_VALUE = major["VALUE_LKR"].sum()

# Display/checking columns only. Nothing is merged or changed in the data.
major["SUPPLIER_FULL"] = major["SUPPLIER_MAME"].str.replace(r"\s*\n\s*", " | ", regex=True).str.strip()
major["SUPPLIER_CORE"] = major["SUPPLIER_MAME"].str.split("\n").str[0].str.strip()

print("Unique full supplier strings :", major["SUPPLIER_FULL"].nunique())
print("Unique first-line names      :", major["SUPPLIER_CORE"].nunique())

# A) Does one first-line name have several full versions?
g = major.groupby("SUPPLIER_CORE").agg(
    full_versions=("SUPPLIER_FULL", "nunique"),
    tins=("TIN_NUMB", "nunique"),
    rows=("VALUE_LKR", "size"),
    value=("VALUE_LKR", "sum"),
)
multi = g[g["full_versions"] > 1].sort_values("value", ascending=False)
print("\n=== A) First-line names with more than one full version ===")
print("Count:", len(multi))
print(multi.head(15))

# B) Same first-line name but different TINs (would mean DIFFERENT companies)
print("\n=== B) First-line names with more than one TIN ===")
print(g[g["tins"] > 1])

# C) TIN coverage per supplier
cov = major.groupby("SUPPLIER_FULL").agg(
    rows=("VALUE_LKR", "size"),
    rows_missing_tin=("TIN_NUMB", lambda s: s.isna().sum()),
    value=("VALUE_LKR", "sum"),
)
never = cov[cov["rows_missing_tin"] == cov["rows"]]
partial = cov[(cov["rows_missing_tin"] > 0) & (cov["rows_missing_tin"] < cov["rows"])]
print("\n=== C) TIN coverage ===")
print("Suppliers never having a TIN  :", len(never), "| value share:", f"{never['value'].sum()/TOTAL_VALUE:.2%}")
print("Suppliers with TIN on some rows only:", len(partial), "| value share:", f"{partial['value'].sum()/TOTAL_VALUE:.2%}")
print("\nTop 8 'partial' suppliers by value:")
print(partial.sort_values("value", ascending=False).head(8))

# D) Samson's own position in the data
samson = major[major["SUPPLIER_CORE"].str.contains("SAMSON", case=False, na=False)]
print("\n=== D) Rows where supplier name contains 'SAMSON' ===")
print(samson.groupby("SUPPLIER_FULL")["VALUE_LKR"].agg(["size", "sum"]))
print("Share of total value:", f"{samson['VALUE_LKR'].sum()/TOTAL_VALUE:.2%}")