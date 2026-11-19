import pandas as pd

FILE = "data/2026 RUBBER EX SEP.xlsx"

major = pd.read_excel(FILE, sheet_name="MAJOR REPORT")

# Clean column names in memory only (original Excel is not changed):
# remove spaces after underscores, e.g. "VALUE_ LKR" -> "VALUE_LKR"
major.columns = [c.strip().replace("_ ", "_") for c in major.columns]
print("Columns:", list(major.columns))

print("\nTotals:")
print("Total QTY      :", round(major["QTY"].sum(), 3))
print("Total VALUE_LKR:", round(major["VALUE_LKR"].sum(), 0))

print("\nUnit of measure counts:")
print(major["UOM"].value_counts(dropna=False))

print("\nYears / months present (with row counts):")
print(major.groupby(["YEAR", "MONTH"]).size())

print("\nUnique values (raw, before any cleaning):")
for col in ["SUPPLIER_MAME", "BUYER_NAME", "COUNTRY_OF_DESTINATION", "HS_CODE", "TIN_NUMB"]:
    print(f"{col:25s}", major[col].nunique())

print("\nExact duplicate rows:", major.duplicated().sum())