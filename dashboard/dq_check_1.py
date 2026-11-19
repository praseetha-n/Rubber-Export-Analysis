import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 60)

FILE = "data/2026 RUBBER EX SEP.xlsx"
major = pd.read_excel(FILE, sheet_name="MAJOR REPORT")
major.columns = [c.strip().replace("_ ", "_") for c in major.columns]

orig_cols = list(major.columns)
TOTAL_VALUE = major["VALUE_LKR"].sum()
TOTAL_QTY = major["QTY"].sum()

# Display-only helper: put multi-line names on one line (does NOT merge names)
major["SUPPLIER_1LINE"] = major["SUPPLIER_MAME"].str.replace(r"\s*\n\s*", " | ", regex=True)

# ---------- CHECK 1: duplicates ----------
print("=== CHECK 1: DUPLICATES ===")
extra = major[major.duplicated(keep="first")]
print("Extra duplicate rows        :", len(extra))
print("Their QTY (kg)              :", round(extra["QTY"].sum(), 3),
      f"({extra['QTY'].sum() / TOTAL_QTY:.2%} of total)")
print("Their VALUE_LKR             :", extra["VALUE_LKR"].sum(),
      f"({extra['VALUE_LKR'].sum() / TOTAL_VALUE:.2%} of total)")

group_sizes = major.groupby(orig_cols, dropna=False).size()
print("\nHow many times each repeated row appears (2 = appears twice):")
print(group_sizes[group_sizes > 1].value_counts())

print("\nDuplicates by month:")
print(extra.groupby("MONTH").size())

print("\nTop 10 duplicate rows by value:")
cols = ["MONTH", "SUPPLIER_1LINE", "COUNTRY_OF_DESTINATION", "HS_CODE", "QTY", "VALUE_LKR"]
print(extra.sort_values("VALUE_LKR", ascending=False).head(10)[cols].to_string())

# ---------- CHECK 2: supplier names vs TIN ----------
print("\n=== CHECK 2: SUPPLIER NAME vs TIN ===")
with_tin = major.dropna(subset=["TIN_NUMB"]).copy()
with_tin["TIN_NUMB"] = with_tin["TIN_NUMB"].astype(str).str.strip()

names_per_tin = with_tin.groupby("TIN_NUMB")["SUPPLIER_1LINE"].nunique()
print("TINs that appear with more than one supplier name:", (names_per_tin > 1).sum())
print(names_per_tin[names_per_tin > 1].sort_values(ascending=False).head(10))

tins_per_name = with_tin.groupby("SUPPLIER_1LINE")["TIN_NUMB"].nunique()
print("\nSupplier names that appear with more than one TIN:", (tins_per_name > 1).sum())

# ---------- CHECK 3: missing TIN ----------
print("\n=== CHECK 3: MISSING TIN ===")
no_tin = major[major["TIN_NUMB"].isna()]
print("Rows with no TIN        :", len(no_tin))
print("Their VALUE_LKR         :", no_tin["VALUE_LKR"].sum(),
      f"({no_tin['VALUE_LKR'].sum() / TOTAL_VALUE:.2%} of total)")
print("Distinct supplier names :", no_tin["SUPPLIER_1LINE"].nunique())
print("\nTop 8 suppliers with missing TIN (by value):")
print(no_tin.groupby("SUPPLIER_1LINE")["VALUE_LKR"].sum()
      .sort_values(ascending=False).head(8))