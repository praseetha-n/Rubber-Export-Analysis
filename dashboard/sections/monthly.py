
import streamlit as st
import plotly.express as px


def show_monthly_analysis(df):

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

    st.divider()
