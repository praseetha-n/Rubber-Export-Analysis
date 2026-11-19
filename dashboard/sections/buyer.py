
import streamlit as st
import pandas as pd
import plotly.express as px


def show_buyer_analysis(df, total_value):

    st.divider()
    st.header("Buyer Analysis")

    st.caption(
        "Buyer analysis is based on BUYER_CORE, an approximate "
        "standardised grouping. It does not confirm legal entity identity."
    )

    buyer_data = df.copy()

    buyer_data["BUYER_CORE"] = (
        buyer_data["BUYER_CORE"]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
        .fillna("Missing Buyer")
    )

    buyer_analysis = (
        buyer_data.groupby("BUYER_CORE", as_index=False)
        .agg(
            Export_Value=("VALUE_LKR", "sum"),
            Transactions=("SOURCE_ROW", "count"),
            Supplier_Count=("SUPPLIER_NAME", "nunique"),
            Destination_Count=("COUNTRY_OF_DESTINATION", "nunique"),
            Full_Name_Variants=("BUYER_FULL", "nunique")
        )
        .sort_values("Export_Value", ascending=False)
    )

    buyer_analysis["Value_Share"] = (
        buyer_analysis["Export_Value"] / total_value * 100
        if total_value > 0 else 0
    )

    buyer_analysis["Cumulative_Share"] = (
        buyer_analysis["Value_Share"].cumsum()
    )

    top5_buyers = buyer_analysis.head(5)
    top10_buyers = buyer_analysis.head(10)

    top5_buyer_share = (
        top5_buyers["Export_Value"].sum() / total_value * 100
        if total_value > 0 else 0
    )

    top10_buyer_share = (
        top10_buyers["Export_Value"].sum() / total_value * 100
        if total_value > 0 else 0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Buyer Groups",
        f"{len(buyer_analysis):,}"
    )

    col2.metric(
        "Top 5 Buyer Contribution",
        f"{top5_buyer_share:.2f}%"
    )

    col3.metric(
        "Top 10 Buyer Contribution",
        f"{top10_buyer_share:.2f}%"
    )

    st.subheader("Top 10 Buyers by Export Value")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("**Buyer Export Value Ranking**")

        buyer_bar_data = top10_buyers.sort_values(
            "Export_Value",
            ascending=True
        )

        fig_buyer_bar = px.bar(
            buyer_bar_data,
            x="Export_Value",
            y="BUYER_CORE",
            orientation="h",
            text="Value_Share",
            labels={
                "Export_Value": "Export Value (LKR)",
                "BUYER_CORE": "Buyer",
                "Value_Share": "Value Share (%)"
            }
        )

        fig_buyer_bar.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
            cliponaxis=False
        )

        fig_buyer_bar.update_layout(
            height=550,
            xaxis_title="Export Value (LKR)",
            yaxis_title="Buyer",
            xaxis=dict(
                tickformat=",.0f",
                rangemode="tozero"
            ),
            margin=dict(
                l=20,
                r=65,
                t=40,
                b=60
            )
        )

        st.plotly_chart(
            fig_buyer_bar,
            use_container_width=True
        )

    with col2:

        st.markdown("**Top 10 Buyer Contribution**")

        fig_buyer_pie = px.pie(
            top10_buyers,
            names="BUYER_CORE",
            values="Export_Value",
            hole=0.45
        )

        fig_buyer_pie.update_traces(
            textposition="inside",
            textinfo="percent",
            hovertemplate=(
                "Buyer: %{label}<br>"
                "Export Value: LKR %{value:,.0f}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            )
        )

        fig_buyer_pie.update_layout(
            height=550,
            legend=dict(
                title="Buyer",
                font=dict(size=9)
            )
        )

        st.plotly_chart(
            fig_buyer_pie,
            use_container_width=True
        )

    st.divider()

    st.subheader("Buyer Performance Details")

    display_buyer = buyer_analysis.copy()

    display_buyer["Export_Value"] = (
        display_buyer["Export_Value"]
        .map(lambda x: f"LKR {x:,.0f}")
    )

    display_buyer["Value_Share"] = (
        display_buyer["Value_Share"]
        .map(lambda x: f"{x:.2f}%")
    )

    display_buyer["Cumulative_Share"] = (
        display_buyer["Cumulative_Share"]
        .map(lambda x: f"{x:.2f}%")
    )

    display_buyer = display_buyer.rename(
        columns={
            "BUYER_CORE": "Buyer",
            "Export_Value": "Export Value",
            "Transactions": "Transactions",
            "Supplier_Count": "Supplier Count",
            "Destination_Count": "Destination Countries",
            "Full_Name_Variants": "Full Name Variants",
            "Value_Share": "Value Share",
            "Cumulative_Share": "Cumulative Share"
        }
    )

    st.dataframe(
        display_buyer,
        use_container_width=True,
        hide_index=True
    )
