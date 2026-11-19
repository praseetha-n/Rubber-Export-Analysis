
import streamlit as st
import pandas as pd
import plotly.express as px


def get_main_product(series):

    descriptions = series.dropna()

    if descriptions.empty:
        return "Description unavailable"

    return descriptions.value_counts().index[0]


def show_product_analysis(df, total_value):

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
        .str.strip(" - ,/")
    )

    hs_data.loc[
        hs_data["PRODUCT_NAME"].str.fullmatch(
            r"[\d\s.,%/-]*",
            na=False
        ),
        "PRODUCT_NAME"
    ] = pd.NA

    hs_data.loc[
        hs_data["PRODUCT_NAME"].str.fullmatch(
            r"(?i)(?:OF\s*)?(?:PCS?|PIECES?|SHEETS?|ROLLS?|SETS?|PAIRS?|BOXES?|PACKS?|BAGS?|UNITS?|KG|KGS|GMS|GRAMS?|METERS?|METRES?)+",
            na=False
        ),
        "PRODUCT_NAME"
    ] = pd.NA

    hs_data["PRODUCT_NAME"] = (
        hs_data["PRODUCT_NAME"].replace("", pd.NA)
    )

    # -----------------------------------------
    # 5.3 FIND MAIN PRODUCT DESCRIPTION
    # -----------------------------------------

    product_lookup = (
        hs_data.groupby("HS_CODE_DISPLAY")["PRODUCT_NAME"]
        .apply(get_main_product)
        .reset_index(name="Main_Product")
    )

    # -----------------------------------------
    # 5.3.1 STATIC PRODUCT NAME CORRECTIONS
    # -----------------------------------------

    static_hs_mapping = {
        "40169990": "OTHERS",
        "40082900": "RUBBER BAND"
    }

    product_lookup["Main_Product"] = (
        product_lookup["HS_CODE_DISPLAY"]
        .map(static_hs_mapping)
        .fillna(product_lookup["Main_Product"])
    )

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

    # -----------------------------------------
    # 5.4 AGGREGATE HS CODE PERFORMANCE
    # -----------------------------------------

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

    # -----------------------------------------
    # 5.5 CALCULATE CONTRIBUTION
    # -----------------------------------------

    if total_value > 0:

        hs_analysis["Value_Share"] = (
            hs_analysis["Export_Value"] / total_value * 100
        )

    else:

        hs_analysis["Value_Share"] = 0

    hs_analysis["Cumulative_Share"] = (
        hs_analysis["Value_Share"].cumsum()
    )

    # -----------------------------------------
    # 5.6 DISPLAY HS CODE ANALYSIS
    # -----------------------------------------

    if hs_analysis.empty:

        st.warning(
            "No HS Code data available for analysis."
        )

        return

    top3_hs_share = (
        hs_analysis.head(3)["Export_Value"].sum()
        / total_value * 100
        if total_value > 0 else 0
    )

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

