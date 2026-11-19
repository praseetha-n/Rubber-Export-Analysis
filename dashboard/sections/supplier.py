
import streamlit as st
import plotly.express as px


def show_supplier_analysis(df, total_value):

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

    st.divider()
