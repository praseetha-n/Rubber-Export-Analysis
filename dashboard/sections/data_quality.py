
import streamlit as st
import pandas as pd
import plotly.express as px


def show_data_quality(df):

    st.divider()
    st.header("Data Quality Overview")

    # -----------------------------------------
    # 1. DATA QUALITY SUMMARY
    # -----------------------------------------

    total_records = len(df)

    missing_tin = (
        df["TIN_MISSING"].fillna(False).astype(bool).sum()
        if "TIN_MISSING" in df.columns else 0
    )

    duplicate_records = (
        df["IS_EXTRA_DUPLICATE"].fillna(False).astype(bool).sum()
        if "IS_EXTRA_DUPLICATE" in df.columns else 0
    )

    qty_suspect = (
        df["QTY_SUSPECT"].fillna(False).astype(bool).sum()
        if "QTY_SUSPECT" in df.columns else 0
    )

    unit_price_outlier = (
        df["UNIT_PRICE_OUTLIER"].fillna(False).astype(bool).sum()
        if "UNIT_PRICE_OUTLIER" in df.columns else 0
    )

    description_qty_match = (
        df["DESCRIPTION_QTY_MATCH"].fillna(False).astype(bool).sum()
        if "DESCRIPTION_QTY_MATCH" in df.columns else 0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Records", f"{total_records:,}")
    col2.metric("Missing TIN Records", f"{missing_tin:,}")
    col3.metric("Extra Duplicate Records", f"{duplicate_records:,}")

    col1, col2, col3 = st.columns(3)

    col1.metric("Quantity Review Flags", f"{qty_suspect:,}")
    col2.metric("Unit Price Outliers", f"{unit_price_outlier:,}")
    col3.metric("Description / Quantity Flags", f"{description_qty_match:,}")

    # -----------------------------------------
    # 2. DATA QUALITY FLAG SUMMARY
    # -----------------------------------------

    st.subheader("Data Quality Flag Summary")

    flag_summary = pd.DataFrame({
        "Quality Check": [
            "Missing TIN",
            "Extra Exact Duplicates",
            "Suspicious Quantity",
            "Unit Price Outlier",
            "Description / Quantity Match"
        ],
        "Flagged Records": [
            missing_tin,
            duplicate_records,
            qty_suspect,
            unit_price_outlier,
            description_qty_match
        ]
    })

    fig_flags = px.bar(
        flag_summary,
        x="Quality Check",
        y="Flagged Records",
        text="Flagged Records",
        labels={
            "Quality Check": "Quality Check",
            "Flagged Records": "Number of Records"
        }
    )

    fig_flags.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    fig_flags.update_layout(
        height=450,
        xaxis_title="Quality Check",
        yaxis_title="Number of Records"
    )

    st.plotly_chart(
        fig_flags,
        use_container_width=True
    )

    # -----------------------------------------
    # 3. QUALITY FLAG INTERPRETATION
    # -----------------------------------------

    st.subheader("Quality Review Notes")

    st.info(
        "These flags identify records that may require further review. "
        "They do not automatically confirm data errors."
    )

    st.warning(
        "Suspicious quantity records and unit price outliers "
        "have been retained without changing the original values."
    )

    st.caption(
        "Exact duplicate records are retained because they have not "
        "been confirmed as erroneous transactions."
    )

    # -----------------------------------------
    # 4. FLAGGED RECORD DETAILS
    # -----------------------------------------

    st.subheader("Flagged Record Details")

    available_flag_columns = [
        col for col in [
            "TIN_MISSING",
            "IS_EXTRA_DUPLICATE",
            "QTY_SUSPECT",
            "UNIT_PRICE_OUTLIER",
            "DESCRIPTION_QTY_MATCH"
        ]
        if col in df.columns
    ]

    if available_flag_columns:

        selected_flags = st.multiselect(
            "Select quality checks to inspect",
            options=available_flag_columns,
            default=[
                col for col in [
                    "QTY_SUSPECT",
                    "UNIT_PRICE_OUTLIER",
                    "DESCRIPTION_QTY_MATCH"
                ]
                if col in available_flag_columns
            ]
        )

        if selected_flags:

            flagged_mask = pd.Series(
                False,
                index=df.index
            )

            for column in selected_flags:

                flagged_mask |= (
                    df[column]
                    .fillna(False)
                    .astype(bool)
                )

            flagged_records = df.loc[flagged_mask].copy()

            display_columns = [
                col for col in [
                    "SOURCE_ROW",
                    "MONTH",
                    "SUPPLIER_NAME",
                    "BUYER_CORE",
                    "COUNTRY_OF_DESTINATION",
                    "HS_CODE",
                    "PRODUCT_DESCRIPTION_11",
                    "QTY",
                    "UNIT_VALUE_LKR_PER_KG",
                    "VALUE_LKR"
                ]
                if col in flagged_records.columns
            ]

            st.caption(
                f"Records requiring review: {len(flagged_records):,}"
            )

            st.dataframe(
                flagged_records[display_columns],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("Select at least one quality check to view records.")

    else:

        st.warning(
            "No quality flag columns were found in the dataset."
        )

    st.divider()
