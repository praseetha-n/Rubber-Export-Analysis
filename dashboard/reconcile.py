
import re
from pathlib import Path
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 60)

FILE = "data/2026 RUBBER EX SEP.xlsx"
OUTPUT = Path("output/reconciliation_checks.csv")

# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def fix_cols(df):
    df.columns = [
        str(c).strip().replace("_ ", "_")
        for c in df.columns
    ]

    return df.rename(columns={
        "Sum of QTY": "QTY",
        "Sum of VALUE_LKR": "VALUE_LKR"
    })


def norm(x):
    if pd.isna(x):
        return ""

    return re.sub(r"\s+", "", str(x)).upper()


def add_keys(df):
    df = df.copy()

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce")
    df["VALUE_LKR"] = pd.to_numeric(
        df["VALUE_LKR"], errors="coerce"
    )

    df["HS_K"] = (
        pd.to_numeric(df["HS_CODE"], errors="coerce")
        .astype("Int64")
        .astype(str)
    )

    df["SUP_K"] = df["SUPPLIER_MAME"].map(norm)
    df["BUY_K"] = df["BUYER_NAME"].map(norm)
    df["CTRY_K"] = df["COUNTRY_OF_DESTINATION"].map(norm)

    if "MONTH" in df.columns:
        df["MONTH_K"] = (
            df["MONTH"].astype(str).str.strip().str.upper()
        )

    return df


# --------------------------------------------------
# Comparison function
# --------------------------------------------------

all_results = []


def compare(a, b, keys, label_a, label_b, show=5):

    ga = a.groupby(keys, dropna=False)[
        ["QTY", "VALUE_LKR"]
    ].sum().add_suffix("_" + label_a)

    gb = b.groupby(keys, dropna=False)[
        ["QTY", "VALUE_LKR"]
    ].sum().add_suffix("_" + label_b)

    joined = ga.join(gb, how="outer").fillna(0)

    value_diff = (
        joined["VALUE_LKR_" + label_a]
        - joined["VALUE_LKR_" + label_b]
    ).abs()

    qty_diff = (
        joined["QTY_" + label_a]
        - joined["QTY_" + label_b]
    ).abs()

    bad = joined[
        (value_diff > 0.5) | (qty_diff > 0.01)
    ]

    print(
        f"{label_a} vs {label_b} by {keys}: "
        f"{len(joined)} groups compared, "
        f"{len(bad)} differ"
    )

    all_results.append({
        "Comparison": f"{label_a} vs {label_b}",
        "Grouping": " + ".join(keys),
        "Groups_Compared": len(joined),
        "Differences": len(bad),
        "Status": "PASS" if len(bad) == 0 else "CHECK"
    })

    if len(bad):
        print(bad.head(show).to_string())


# --------------------------------------------------
# Load original workbook
# --------------------------------------------------

major = add_keys(
    fix_cols(
        pd.read_excel(FILE, sheet_name="MAJOR REPORT")
    )
)

summ_raw = fix_cols(
    pd.read_excel(
        FILE,
        sheet_name="SUMMARY REPORT",
        header=2
    )
)

rank_raw = fix_cols(
    pd.read_excel(
        FILE,
        sheet_name="RANK REPORT",
        header=2
    )
)


# --------------------------------------------------
# SUMMARY REPORT processing
# --------------------------------------------------

hs_txt = summ_raw["HS_CODE"].astype(str)

is_total = hs_txt.str.contains("Total", na=False)
is_grand = hs_txt.str.contains("Grand", na=False)

grand = summ_raw[is_grand]
sub = summ_raw[is_total & ~is_grand].copy()

summ = summ_raw[~is_total].copy()

for col in [
    "HS_CODE",
    "SUPPLIER_MAME",
    "BUYER_NAME"
]:
    summ[col] = summ[col].ffill()

summ = add_keys(summ).dropna(
    subset=["VALUE_LKR"]
)

print("\n=== SUMMARY STRUCTURE ===")

print("Total rows found:", int(is_total.sum()))
print("Detail rows kept:", len(summ))

if len(grand):
    print(
        "Grand Total:",
        "QTY", grand["QTY"].iloc[0],
        "| VALUE", grand["VALUE_LKR"].iloc[0]
    )


# SUMMARY subtotal validation

sub_tbl = sub.assign(
    HS_K=sub["HS_CODE"].astype(str).str.extract(r"(\d+)")[0]
).set_index("HS_K")[["QTY", "VALUE_LKR"]]

det_tbl = summ.groupby("HS_K")[
    ["QTY", "VALUE_LKR"]
].sum()

chk = sub_tbl.join(
    det_tbl,
    lsuffix="_subtotal",
    rsuffix="_detail"
)

chk["value_diff"] = (
    chk["VALUE_LKR_subtotal"]
    - chk["VALUE_LKR_detail"]
)

chk["qty_diff"] = (
    chk["QTY_subtotal"]
    - chk["QTY_detail"]
).round(3)

print("\nSUMMARY subtotal validation:")
print(chk[["value_diff", "qty_diff"]])


# --------------------------------------------------
# RANK REPORT processing
# --------------------------------------------------

is_tot_r = (
    rank_raw["HS_CODE"].astype(str).str.contains(
        "Total", na=False
    )
    |
    rank_raw["UOM"].astype(str).str.contains(
        "Total", na=False
    )
)

rank = rank_raw[~is_tot_r].copy()

# Forward-fill all hierarchical label columns.
# Blank cells represent the previous group's label.

rank_label_cols = [
    "UOM",
    "PRODUCT_DESCRIPTION_11",
    "BUYER_NAME",
    "COUNTRY_OF_DESTINATION",
    "GOODSDESC",
    "SUPPLIER_MAME",
    "TIN_NUMB",
    "YEAR",
    "HS_CODE"
]

print("\n=== RANK FORWARD-FILL ===")

for col in rank_label_cols:

    before = rank[col].isna().sum()

    rank[col] = rank[col].ffill()

    after = rank[col].isna().sum()

    print(
        f"{col}: blanks before={before}, "
        f"after={after}"
    )

rank = add_keys(rank).dropna(
    subset=["VALUE_LKR"]
)

print("\n=== RANK STRUCTURE ===")

print("Total rows removed:", int(is_tot_r.sum()))
print("Detail rows kept:", len(rank))

print(
    "MAJOR rows:", len(major),
    "| RANK detail rows:", len(rank),
    "| Difference:", len(major) - len(rank)
)


# --------------------------------------------------
# Overall totals
# --------------------------------------------------

print("\n=== OVERALL TOTALS ===")

for name, df in [
    ("MAJOR", major),
    ("SUMMARY", summ),
    ("RANK", rank)
]:

    print(
        f"{name:8s} "
        f"QTY {df['QTY'].sum():,.3f} "
        f"| VALUE {df['VALUE_LKR'].sum():,.0f}"
    )


# --------------------------------------------------
# Reconciliation comparisons
# --------------------------------------------------

print("\n=== MAJOR vs SUMMARY ===")

compare(
    major, summ,
    ["HS_K"],
    "MAJOR", "SUMMARY"
)

compare(
    major, summ,
    ["SUP_K"],
    "MAJOR", "SUMMARY"
)

compare(
    major, summ,
    ["HS_K", "SUP_K", "BUY_K", "CTRY_K"],
    "MAJOR", "SUMMARY"
)


print("\n=== MAJOR vs RANK ===")

compare(
    major, rank,
    ["HS_K"],
    "MAJOR", "RANK"
)

compare(
    major, rank,
    ["MONTH_K"],
    "MAJOR", "RANK"
)

compare(
    major, rank,
    ["MONTH_K", "HS_K"],
    "MAJOR", "RANK"
)

compare(
    major, rank,
    ["SUP_K"],
    "MAJOR", "RANK"
)

compare(
    major, rank,
    ["BUY_K"],
    "MAJOR", "RANK"
)

compare(
    major, rank,
    ["CTRY_K"],
    "MAJOR", "RANK"
)

compare(
    major, rank,
    ["HS_K", "SUP_K", "BUY_K", "CTRY_K", "MONTH_K"],
    "MAJOR", "RANK"
)


# --------------------------------------------------
# Why does RANK have fewer rows?
# --------------------------------------------------

print("\n=== RANK ROW DIFFERENCE INVESTIGATION ===")

major_grain = major.groupby([
    "YEAR",
    "MONTH_K",
    "HS_K",
    "SUP_K",
    "BUY_K",
    "CTRY_K"
]).size()

rank_grain = rank.groupby([
    "YEAR",
    "MONTH_K",
    "HS_K",
    "SUP_K",
    "BUY_K",
    "CTRY_K"
]).size()

print("MAJOR unique groups:", len(major_grain))
print("RANK unique groups:", len(rank_grain))

print(
    "MAJOR duplicate grouping combinations:",
    int((major_grain > 1).sum())
)

print(
    "RANK duplicate grouping combinations:",
    int((rank_grain > 1).sum())
)

# Compare complete available pivot dimensions

full_keys = [
    "UOM",
    "PRODUCT_DESCRIPTION_11",
    "BUYER_NAME",
    "COUNTRY_OF_DESTINATION",
    "GOODSDESC",
    "SUPPLIER_MAME",
    "TIN_NUMB",
    "YEAR",
    "HS_CODE",
    "MONTH"
]

print("\nRANK grouping dimensions:")
print(full_keys)

print(
    "Note: RANK may aggregate MAJOR rows "
    "sharing identical pivot dimensions."
)


# --------------------------------------------------
# Save reconciliation results
# --------------------------------------------------

results_df = pd.DataFrame(all_results)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

results_df.to_csv(OUTPUT, index=False)

print("\n=== RECONCILIATION SUMMARY ===")
print(results_df.to_string(index=False))

print("\nResults saved to:", OUTPUT)
print("\nReconciliation script completed.")
