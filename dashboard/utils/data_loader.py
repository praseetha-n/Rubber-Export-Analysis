
import streamlit as st
import pandas as pd


# =========================================
# LOAD DATA
# =========================================

@st.cache_data
def load_data():
    return pd.read_csv("output/quality_flagged_exports.csv")


# =========================================
# PREPARE DATA
# =========================================

def prepare_data():

    df = load_data().copy()

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

    return df


# =========================================
# EXCLUDE EARTHFORM PRIVATE LTD
# =========================================

def exclude_earthform(df):

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

    filtered_df = df.loc[~earthform_mask].copy()

    return filtered_df, len(excluded_rows), excluded_value
