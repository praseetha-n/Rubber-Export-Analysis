
import streamlit as st

from utils.data_loader import prepare_data, exclude_earthform

from utils.data_loader import prepare_data, exclude_earthform
from sections.overview import show_overview
from sections.monthly import show_monthly_analysis
from sections.supplier import show_supplier_analysis
from sections.country import show_country_analysis
from sections.product import show_product_analysis
from sections.buyer import show_buyer_analysis
from sections.data_quality import show_data_quality

# =========================================
# PAGE CONFIGURATION
# =========================================

st.set_page_config(
    page_title="Rubber Export Analysis",
    page_icon="📊",
    layout="wide"
)


# =========================================
# LOAD AND PREPARE DATA
# =========================================

df = prepare_data()


# =========================================
# EXCLUDE EARTHFORM PRIVATE LTD
# =========================================

df, excluded_count, excluded_value = exclude_earthform(df)

st.info(
    f"EARTHFORM PRIVATE LTD excluded from analysis: "
    f"{excluded_count:,} transactions | "
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

show_overview(df)

total_value = df["VALUE_LKR"].sum()

# =========================================
# SECTION 2 - MONTHLY EXPORT PERFORMANCE
# =========================================

show_monthly_analysis(df)
# =========================================
# SECTION 3 - SUPPLIER PERFORMANCE
# =========================================

show_supplier_analysis(df, total_value)

# =========================================
# SECTION 4 - DESTINATION COUNTRY ANALYSIS
# =========================================

show_country_analysis(df, total_value)

# =========================================
# SECTION 5 - HS CODE / PRODUCT ANALYSIS
# =========================================

show_product_analysis(df, total_value)

# =========================================
# SECTION 6 - BUYER ANALYSIS
# =========================================

show_buyer_analysis(df, total_value)

# =========================================
# SECTION 7 - DATA QUALITY OVERVIEW
# =========================================

show_data_quality(df)