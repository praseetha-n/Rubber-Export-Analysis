
import pandas as pd

# Load data
df = pd.read_csv("output/quality_flagged_exports.csv")

# Analyse destination countries
country = (
    df.groupby("COUNTRY_OF_DESTINATION")
    .agg(
        TRANSACTIONS=("SOURCE_ROW", "count"),
        EXPORT_VALUE_LKR=("VALUE_LKR", "sum"),
        SUPPLIER_COUNT=("SUPPLIER_NAME", "nunique"),
        BUYER_COUNT=("BUYER_CORE", "nunique")
    )
    .reset_index()
    .sort_values("EXPORT_VALUE_LKR", ascending=False)
)

# Calculate export value contribution
total_value = df["VALUE_LKR"].sum()

country["VALUE_SHARE_%"] = (
    country["EXPORT_VALUE_LKR"] / total_value * 100
).round(2)

country["CUMULATIVE_SHARE_%"] = (
    country["VALUE_SHARE_%"].cumsum()
).round(2)

# Display top 20 countries
print("\n========== TOP 20 DESTINATION COUNTRIES ==========")
print(country.head(20).to_string(index=False))

# Top 5 and Top 10 contribution
print("\n========== COUNTRY CONCENTRATION ==========")
print("Top 5 countries share:",
      country.head(5)["VALUE_SHARE_%"].sum(), "%")

print("Top 10 countries share:",
      country.head(10)["VALUE_SHARE_%"].sum(), "%")

print("Total destination countries:", len(country))

# Save complete country analysis
country.to_csv("output/eda_country_analysis.csv", index=False)

print("\nSaved: output/eda_country_analysis.csv")
