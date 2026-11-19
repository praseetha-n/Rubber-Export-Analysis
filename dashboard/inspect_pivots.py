import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", 28)

FILE = "data/2026 RUBBER EX SEP.xlsx"

for sheet in ["SUMMARY REPORT", "RANK REPORT"]:
    # header=None: read the sheet exactly as it looks, nothing treated as a header
    raw = pd.read_excel(FILE, sheet_name=sheet, header=None)
    print("\n" + "=" * 90)
    print(sheet, "| shape (rows, columns):", raw.shape)

    print("\nFirst 25 rows:")
    print(raw.head(25).to_string())

    print("\nLast 6 rows:")
    print(raw.tail(6).to_string())

    # rows that contain the word 'total' anywhere (subtotals / grand total)
    mask = raw.apply(lambda r: r.astype(str).str.contains("total", case=False, na=False).any(), axis=1)
    print("\nRows containing 'total':", int(mask.sum()))
    print(raw[mask].head(8).to_string())