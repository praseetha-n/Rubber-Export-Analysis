
import streamlit as st


def show_overview(df):

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

    st.divider()
