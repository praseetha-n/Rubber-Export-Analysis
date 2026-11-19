
import streamlit as st
import pandas as pd
import plotly.express as px


# =========================================
# PAGE CONFIGURATION
# =========================================

st.set_page_config(
    page_title="Rubber Export Analysis",
    page_icon="📊",
    layout="wide"
)


# =========================================
# LOAD DATA
# =========================================

@st.cache_data
def load_data():
    return pd.read_csv("output/quality_flagged_exports.csv")


df = load_data()


# =========================================
# DATA PREPARATION
# =========================================

df["VALUE_LKR"] = pd.to_numeric(
    df["VALUE_LKR"],
    errors="coerce"
).fillna(0)

df["SOURCE_ROW"] = pd.to_numeric(
    df["SOURCE_ROW"],
    errors="coerce"
)

df["MONTH_NUM"] = pd.to_numeric(
    df["MONTH_NUM"],
    errors="coerce"
)


# =========================================
# EXCLUDE EARTHFORM PRIVATE LTD
# =========================================

earthform_mask = (
    df["SUPPLIER_NAME"]
    .astype("string")
    .str.strip()
    .str.casefold()
    .eq("earthform private ltd")
    .fillna(False)
)

excluded_rows = df.loc[earthform_mask]

excluded_value = excluded_rows["VALUE_LKR"].sum()

df = df.loc[~earthform_mask].copy()

st.info(
    f"EARTHFORM PRIVATE LTD excluded from analysis: "
    f"{len(excluded_rows):,} transactions | "
    f"LKR {excluded_value:,.2f} export value"
)


# =========================================
# DASHBOARD HEADER
# =========================================

st.title("Rubber Export Performance Dashboard")

st.caption(
    "January – September 2026 | Management Overview"
)

st.divider()


# =========================================
# SECTION 1 - KEY PERFORMANCE INDICATORS
# =========================================

st.header("Key Performance Indicators")

total_value = df["VALUE_LKR"].sum()

total_transactions = len(df)

total_suppliers = df["SUPPLIER_NAME"].nunique()

total_buyers = df["BUYER_CORE"].nunique()

total_countries = df["COUNTRY_OF_DESTINATION"].nunique()

total_hs = df["HS_CODE"].nunique()


col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Export Value",
    f"LKR {total_value / 1_000_000_000:.2f} B"
)

col2.metric(
    "Total Transactions",
    f"{total_transactions:,}"
)

col3.metric(
    "Unique Suppliers",
    f"{total_suppliers:,}"
)


col4, col5, col6 = st.columns(3)

col4.metric(
    "Buyer Records",
    f"{total_buyers:,}"
)

col5.metric(
    "Destination Countries",
    f"{total_countries:,}"
)

col6.metric(
    "HS Code Categories",
    f"{total_hs:,}"
)


st.info(
    "Export value is used as the primary performance measure. "
    "Quantity figures require further verification."
)


# =========================================
# SECTION 2 - MONTHLY EXPORT PERFORMANCE
# =========================================

st.divider()

st.header("Monthly Export Performance")


monthly = (
    df.groupby(["MONTH_NUM", "MONTH"], as_index=False)
    .agg(
        Export_Value=("VALUE_LKR", "sum"),
        Transactions=("SOURCE_ROW", "count")
    )
    .sort_values("MONTH_NUM")
)


col1, col2 = st.columns(2)


with col1:

    st.subheader("Monthly Export Value")

    fig_monthly_value = px.bar(
        monthly,
        x="MONTH",
        y="Export_Value",
        labels={
            "MONTH": "Month",
            "Export_Value": "Export Value (LKR)"
        }
    )

    fig_monthly_value.update_traces(
        texttemplate="LKR %{y:,.0f}",
        textposition="outside",
        cliponaxis=False
    )

    fig_monthly_value.update_layout(
        height=450,
        xaxis_title="Month",
        yaxis_title="Export Value (LKR)"
    )

    st.plotly_chart(
        fig_monthly_value,
        use_container_width=True
    )


with col2:

    st.subheader("Monthly Transaction Count")

    fig_monthly_transactions = px.line(
        monthly,
        x="MONTH",
        y="Transactions",
        markers=True,
        text="Transactions",
        labels={
            "MONTH": "Month",
            "Transactions": "Transaction Count"
        }
    )

    fig_monthly_transactions.update_traces(
        textposition="top center",
        line=dict(width=3),
        marker=dict(size=9)
    )

    fig_monthly_transactions.update_layout(
        height=450,
        xaxis_title="Month",
        yaxis_title="Number of Transactions"
    )

    st.plotly_chart(
        fig_monthly_transactions,
        use_container_width=True
    )


# =========================================
# SECTION 3 - SUPPLIER PERFORMANCE
# =========================================

st.divider()

st.header("Supplier Performance")


supplier = (
    df.groupby("SUPPLIER_NAME", as_index=False)
    .agg(
        Export_Value=("VALUE_LKR", "sum"),
        Transactions=("SOURCE_ROW", "count"),
        Buyers=("BUYER_CORE", "nunique"),
        Destinations=("COUNTRY_OF_DESTINATION", "nunique")
    )
    .sort_values("Export_Value", ascending=False)
)

supplier["Value_Share"] = (
    supplier["Export_Value"] / total_value * 100
    if total_value > 0 else 0
)

top10_suppliers = supplier.head(10)

top10_supplier_share = (
    top10_suppliers["Export_Value"].sum()
    / total_value * 100
    if total_value > 0 else 0
)


col1, col2 = st.columns(2)

col1.metric(
    "Total Suppliers",
    f"{len(supplier):,}"
)

col2.metric(
    "Top 10 Supplier Contribution",
    f"{top10_supplier_share:.2f}%"
)


col1, col2 = st.columns(2)


with col1:

    st.subheader("Top 10 Suppliers by Export Value")

    fig_supplier_bar = px.bar(
        top10_suppliers.sort_values("Export_Value"),
        x="Export_Value",
        y="SUPPLIER_NAME",
        orientation="h",
        labels={
            "Export_Value": "Export Value (LKR)",
            "SUPPLIER_NAME": "Supplier"
        }
    )

    fig_supplier_bar.update_layout(
        height=550,
        xaxis_title="Export Value (LKR)",
        yaxis_title="Supplier"
    )

    st.plotly_chart(
        fig_supplier_bar,
        use_container_width=True
    )


with col2:

    st.subheader("Top 10 Supplier Contribution")

    fig_supplier_pie = px.pie(
        top10_suppliers,
        names="SUPPLIER_NAME",
        values="Export_Value",
        hole=0.45
    )

    fig_supplier_pie.update_layout(
        height=550
    )

    st.plotly_chart(
        fig_supplier_pie,
        use_container_width=True
    )


st.subheader("Supplier Performance Details")

display_supplier = supplier.copy()

display_supplier["Export_Value"] = (
    display_supplier["Export_Value"]
    .map(lambda x: f"LKR {x:,.0f}")
)

display_supplier["Value_Share"] = (
    display_supplier["Value_Share"]
    .map(lambda x: f"{x:.2f}%")
)

st.dataframe(
    display_supplier,
    use_container_width=True,
    hide_index=True
)


# =========================================
# SECTION 4 - DESTINATION COUNTRY ANALYSIS
# =========================================

st.divider()

st.header("Destination Country Analysis")


destination = (
    df.groupby("COUNTRY_OF_DESTINATION", as_index=False)
    .agg(
        Export_Value=("VALUE_LKR", "sum"),
        Transactions=("SOURCE_ROW", "count"),
        Suppliers=("SUPPLIER_NAME", "nunique"),
        Buyers=("BUYER_CORE", "nunique")
    )
    .sort_values("Export_Value", ascending=False)
)


destination["Value_Share"] = (
    destination["Export_Value"] / total_value * 100
    if total_value > 0 else 0
)

destination["Cumulative_Share"] = (
    destination["Value_Share"].cumsum()
)


top5_countries = destination.head(5)

top10_countries = destination.head(10)

top5_share = (
    top5_countries["Export_Value"].sum()
    / total_value * 100
    if total_value > 0 else 0
)

top10_share = (
    top10_countries["Export_Value"].sum()
    / total_value * 100
    if total_value > 0 else 0
)


col1, col2, col3 = st.columns(3)

col1.metric(
    "Destination Countries",
    f"{len(destination):,}"
)

col2.metric(
    "Top 5 Country Contribution",
    f"{top5_share:.2f}%"
)

col3.metric(
    "Top 10 Country Contribution",
    f"{top10_share:.2f}%"
)


col1, col2 = st.columns(2)


with col1:

    st.subheader("Top 10 Destination Countries")

    fig_country_bar = px.bar(
        top10_countries.sort_values("Export_Value"),
        x="Export_Value",
        y="COUNTRY_OF_DESTINATION",
        orientation="h",
        labels={
            "Export_Value": "Export Value (LKR)",
            "COUNTRY_OF_DESTINATION": "Destination Country"
        }
    )

    fig_country_bar.update_layout(
        height=550,
        xaxis_title="Export Value (LKR)",
        yaxis_title="Country"
    )

    st.plotly_chart(
        fig_country_bar,
        use_container_width=True
    )


with col2:

    st.subheader("Top 10 Destination Contribution")

    fig_country_pie = px.pie(
        top10_countries,
        names="COUNTRY_OF_DESTINATION",
        values="Export_Value",
        hole=0.45
    )

    fig_country_pie.update_layout(
        height=550
    )

    st.plotly_chart(
        fig_country_pie,
        use_container_width=True
    )


st.subheader("Destination Country Performance Details")

display_destination = destination.copy()

display_destination["Export_Value"] = (
    display_destination["Export_Value"]
    .map(lambda x: f"LKR {x:,.0f}")
)

display_destination["Value_Share"] = (
    display_destination["Value_Share"]
    .map(lambda x: f"{x:.2f}%")
)

display_destination["Cumulative_Share"] = (
    display_destination["Cumulative_Share"]
    .map(lambda x: f"{x:.2f}%")
)

st.dataframe(
    display_destination,
    use_container_width=True,
    hide_index=True
)


# =========================================
# SECTION 5 - HS CODE / PRODUCT ANALYSIS
# =========================================

st.divider()

st.header("HS Code / Product Analysis")


# -----------------------------------------
# 5.1 PREPARE HS CODE DATA
# -----------------------------------------

hs_data = df.copy()

hs_data["HS_CODE_DISPLAY"] = (
    hs_data["HS_CODE"]
    .astype("string")
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
    .replace("", pd.NA)
    .fillna("Missing HS Code")
)


# -----------------------------------------
# 5.2 CLEAN PRODUCT DESCRIPTIONS
# -----------------------------------------

hs_data["PRODUCT_NAME"] = (
    hs_data["PRODUCT_DESCRIPTION_11"]
    .astype("string")
    .str.upper()
    .str.strip()
)

# Remove quantity and packaging information
hs_data["PRODUCT_NAME"] = (
    hs_data["PRODUCT_NAME"]
    .str.replace(
        r"\bOF\s*\d+(?:[.,]\d+)?\s*%?(?=\s|$)",
        "",
        regex=True
    )
    .str.replace(
        r"\b\d+(?:[.,]\d+)?\s*(?:%|PERCENT|PCS?|PIECES?|SHEETS?|ROLLS?|SETS?|PAIRS?|BOXES?|PACKS?|BAGS?|UNITS?|KG|KGS|GMS|GRAMS?|METERS?|METRES?)(?=\s|$)",
        "",
        regex=True
    )
    .str.replace(
        r"\s+OF\s*$",
        "",
        regex=True
    )
    .str.replace(
        r"\s+",
        " ",
        regex=True
    )
    .str.strip(" -,/")
)


# Remove descriptions containing only numbers or symbols
hs_data.loc[
    hs_data["PRODUCT_NAME"].str.fullmatch(
        r"[\d\s.,%/-]*",
        na=False
    ),
    "PRODUCT_NAME"
] = pd.NA


# Remove descriptions that only contain quantity/unit terms
hs_data.loc[
    hs_data["PRODUCT_NAME"].str.fullmatch(
        r"(?i)(?:OF\s*)?(?:PCS?|PIECES?|SHEETS?|ROLLS?|SETS?|PAIRS?|BOXES?|PACKS?|BAGS?|UNITS?|KG|KGS|GMS|GRAMS?|METERS?|METRES?)+",
        na=False
    ),
    "PRODUCT_NAME"
] = pd.NA


# Remove empty descriptions
hs_data["PRODUCT_NAME"] = (
    hs_data["PRODUCT_NAME"].replace("", pd.NA)
)


# =========================================
# 5.3 FIND MAIN PRODUCT DESCRIPTION
# =========================================

def get_main_product(series):

    descriptions = series.dropna()

    if descriptions.empty:
        return "Description unavailable"

    return descriptions.value_counts().index[0]


product_lookup = (
    hs_data.groupby("HS_CODE_DISPLAY")["PRODUCT_NAME"]
    .apply(get_main_product)
    .reset_index(name="Main_Product")
)


# =========================================
# 5.3.1 STATIC PRODUCT NAME CORRECTIONS
# =========================================

# Confirmed HS Code to product name mappings
static_hs_mapping = {
    "40169990": "OTHERS",
    "40082900": "RUBBER BAND"
}

product_lookup["Main_Product"] = (
    product_lookup["HS_CODE_DISPLAY"]
    .map(static_hs_mapping)
    .fillna(product_lookup["Main_Product"])
)


# Identify gasket records using the original description
gasket_mask = (
    hs_data["PRODUCT_DESCRIPTION_11"]
    .astype("string")
    .str.upper()
    .str.contains(
        "UNHARDENED VULCANISED RUBBER BASED PRODUCTS",
        na=False
    )
)

gasket_codes = (
    hs_data.loc[gasket_mask, "HS_CODE_DISPLAY"]
    .dropna()
    .astype(str)
    .unique()
)

product_lookup.loc[
    product_lookup["HS_CODE_DISPLAY"].isin(gasket_codes),
    "Main_Product"
] = "GASKETS"


# =========================================
# 5.4 AGGREGATE HS CODE PERFORMANCE
# =========================================

hs_analysis = (
    hs_data.groupby("HS_CODE_DISPLAY", as_index=False)
    .agg(
        Export_Value=("VALUE_LKR", "sum"),
        Transactions=("SOURCE_ROW", "count"),
        Suppliers=("SUPPLIER_NAME", "nunique")
    )
    .merge(
        product_lookup,
        on="HS_CODE_DISPLAY",
        how="left"
    )
    .sort_values(
        "Export_Value",
        ascending=False
    )
)


# =========================================
# 5.5 CALCULATE CONTRIBUTION
# =========================================

if total_value > 0:

    hs_analysis["Value_Share"] = (
        hs_analysis["Export_Value"] / total_value * 100
    )

else:

    hs_analysis["Value_Share"] = 0


hs_analysis["Cumulative_Share"] = (
    hs_analysis["Value_Share"].cumsum()
)


# =========================================
# 5.6 DISPLAY HS CODE ANALYSIS
# =========================================

if not hs_analysis.empty:

    top3_hs_share = (
        hs_analysis.head(3)["Export_Value"].sum()
        / total_value * 100
        if total_value > 0 else 0
    )


    # -----------------------------------------
    # KPI CARDS
    # -----------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "HS Code Categories",
        f"{len(hs_analysis):,}"
    )

    col2.metric(
        "Top 3 HS Code Contribution",
        f"{top3_hs_share:.2f}%"
    )

    col3.metric(
        "Highest Exporting HS Code",
        str(hs_analysis.iloc[0]["HS_CODE_DISPLAY"])
    )


    # -----------------------------------------
    # 5.7 CONSISTENT COLOUR MAPPING
    # -----------------------------------------

    hs_codes = sorted(
        hs_analysis["HS_CODE_DISPLAY"].unique()
    )

    colour_palette = [
        "#2563EB",
        "#F97316",
        "#16A34A",
        "#9333EA",
        "#0891B2",
        "#DC2626",
        "#CA8A04",
        "#DB2777",
        "#475569",
        "#0D9488"
    ]

    hs_color_map = {
        code: colour_palette[i % len(colour_palette)]
        for i, code in enumerate(hs_codes)
    }


    # -----------------------------------------
    # 5.8 CHARTS
    # -----------------------------------------

    st.subheader("HS Code Export Performance")

    col1, col2 = st.columns(2)


    # -----------------------------------------
    # BAR CHART - HS CODE ONLY
    # -----------------------------------------

    with col1:

        st.markdown("**Export Value by HS Code**")

        chart_data = hs_analysis.sort_values(
            "Export_Value",
            ascending=True
        )

        fig_hs_bar = px.bar(
            chart_data,
            x="Export_Value",
            y="HS_CODE_DISPLAY",
            orientation="h",
            color="HS_CODE_DISPLAY",
            color_discrete_map=hs_color_map,
            text="Value_Share",
            labels={
                "Export_Value": "Export Value (LKR)",
                "HS_CODE_DISPLAY": "HS Code",
                "Value_Share": "Value Share (%)"
            }
        )

        fig_hs_bar.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
            cliponaxis=False,
            showlegend=False
        )

        fig_hs_bar.update_layout(
            height=550,
            showlegend=False,
            xaxis_title="Export Value (LKR)",
            yaxis_title="HS Code",
            xaxis=dict(
                tickformat=",.0f",
                rangemode="tozero"
            ),
            yaxis=dict(
                type="category",
                automargin=True
            ),
            margin=dict(
                l=30,
                r=65,
                t=40,
                b=65
            )
        )

        st.plotly_chart(
            fig_hs_bar,
            use_container_width=True
        )


    # -----------------------------------------
    # PIE CHART - HS CODE AND PRODUCT KEY
    # -----------------------------------------

    with col2:

        st.markdown("**HS Code Contribution Distribution**")

        hs_analysis["PIE_LABEL"] = (
            hs_analysis["HS_CODE_DISPLAY"]
            + " - "
            + hs_analysis["Main_Product"]
        )

        fig_hs_pie = px.pie(
            hs_analysis,
            names="PIE_LABEL",
            values="Export_Value",
            color="HS_CODE_DISPLAY",
            color_discrete_map=hs_color_map,
            hole=0.45
        )

        fig_hs_pie.update_traces(
            domain=dict(
                x=[0, 0.67],
                y=[0, 1]
            ),
            textposition="inside",
            textinfo="percent",
            hovertemplate=(
                "HS Code / Product: %{label}<br>"
                "Export Value: LKR %{value:,.0f}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            )
        )

        fig_hs_pie.update_layout(
            height=550,
            showlegend=True,
            legend=dict(
                title="HS Code / Product",
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=0.70,
                font=dict(size=9),
                itemsizing="constant"
            ),
            margin=dict(
                l=5,
                r=5,
                t=40,
                b=35
            )
        )

        st.plotly_chart(
            fig_hs_pie,
            use_container_width=True
        )


    # -----------------------------------------
    # 5.9 HS CODE REFERENCE GUIDE
    # -----------------------------------------

    st.divider()

    st.subheader("HS Code Reference Guide")

    st.caption(
        "Product descriptions are derived from the dataset and "
        "corrected using the specified HS Code mappings. "
        "They are not verified official Customs descriptions."
    )

    reference_table = hs_analysis[
        [
            "HS_CODE_DISPLAY",
            "Main_Product",
            "Transactions",
            "Export_Value",
            "Value_Share"
        ]
    ].copy()

    reference_table = reference_table.rename(
        columns={
            "HS_CODE_DISPLAY": "HS Code (Key)",
            "Main_Product": "Main Product Description",
            "Transactions": "Transactions",
            "Export_Value": "Export Value (LKR)",
            "Value_Share": "Value Share (%)"
        }
    )

    reference_table["Export Value (LKR)"] = (
        reference_table["Export Value (LKR)"]
        .map(lambda x: f"LKR {x:,.0f}")
    )

    reference_table["Value Share (%)"] = (
        reference_table["Value Share (%)"]
        .map(lambda x: f"{x:.2f}%")
    )

    st.dataframe(
        reference_table,
        use_container_width=True,
        hide_index=True
    )

else:

    st.warning(
        "No HS Code data available for analysis."
    )
