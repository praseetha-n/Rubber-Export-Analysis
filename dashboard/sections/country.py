
import streamlit as st
import plotly.express as px


def show_country_analysis(df, total_value):

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

    st.divider()
