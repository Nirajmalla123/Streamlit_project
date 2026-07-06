import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Expense Dashboard",
    page_icon="💰",
    layout="wide"
)

# Connect to database
conn = sqlite3.connect("Expenses.db")

# Read data
df = pd.read_sql_query("SELECT * FROM expenses", conn)

st.title("💰 Expense Tracker Dashboard")

# ---------------- Sidebar ----------------

st.sidebar.header("Filters")

selected_month = st.sidebar.selectbox(
    "Select Month",
    ["All"] + sorted(df["MONTH"].unique().tolist())
)

selected_category = st.sidebar.selectbox(
    "Select Category",
    ["All"] + sorted(df["CATEGORY"].unique().tolist())
)

# ---------------- Filter Data ----------------

filtered_df = df.copy()

if selected_month != "All":
    filtered_df = filtered_df[
        filtered_df["MONTH"] == selected_month
    ]

if selected_category != "All":
    filtered_df = filtered_df[
        filtered_df["CATEGORY"] == selected_category
    ]




total_expense = filtered_df["EXPENSE"].sum()
average_expense = filtered_df["EXPENSE"].mean()

if filtered_df.empty:
    top_category = "No Data"
else:
    top_category = (
        filtered_df.groupby("CATEGORY")["EXPENSE"]
        .sum()
        .idxmax()
    )

col1, col2, col3 = st.columns(3)

col1.metric(
    "💰 Total Expense",
    f"Rs {total_expense:,.2f}"
)

col2.metric(
    "📊 Average Expense",
    f"Rs {average_expense:,.2f}"
)

col3.metric(
    "🏆 Top Category",
    top_category
)




st.dataframe(filtered_df)


# adding charts

st.subheader("📊 Expense Distribution by Category")

if not filtered_df.empty:

    category_data = (
        filtered_df.groupby("CATEGORY")["EXPENSE"]
        .sum()
    )

    fig, ax = plt.subplots(figsize=(6,6))

    ax.pie(
        category_data,
        labels=category_data.index,
        autopct="%1.1f%%",
        startangle=90
    )

    ax.set_title("Expenses by Category")

    st.pyplot(fig)

else:
    st.warning("No data available.")


st.subheader("📈 Monthly Expenses")

if not filtered_df.empty:

    monthly = (
        filtered_df.groupby("MONTH")["EXPENSE"]
        .sum()
    )

    st.bar_chart(monthly)



st.subheader("📉 Expense Trend")

if not filtered_df.empty:

    daily = (
        filtered_df.groupby("DATE")["EXPENSE"]
        .sum()
    )

    st.line_chart(daily)


conn.close()