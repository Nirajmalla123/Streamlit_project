import streamlit as st
import sqlite3 as sql
import pandas as pd
from datetime import datetime

# ----------------------------
# Database Connection
# ----------------------------
conn = sql.connect("Expenses.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    MONTH TEXT NOT NULL,
    EXPENSE REAL NOT NULL,
    CATEGORY TEXT NOT NULL,
    REMARKS TEXT,
    DATE TEXT NOT NULL
)
""")

conn.commit()

# ----------------------------
# Functions
# ----------------------------

def add_expense(month, expense, category, remarks):
    date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        """
        INSERT INTO expenses(MONTH, EXPENSE, CATEGORY, REMARKS, DATE)
        VALUES (?, ?, ?, ?, ?)
        """,
        (month, expense, category, remarks, date)
    )

    conn.commit()


def show_expenses():
    cursor.execute("SELECT * FROM expenses ORDER BY DATE DESC")
    return cursor.fetchall()


def delete_expense(record_id):
    cursor.execute("DELETE FROM expenses WHERE ID=?", (record_id,))
    conn.commit()


def export_csv():
    df = pd.read_sql_query("SELECT * FROM expenses ORDER BY DATE", conn)
    df.to_csv("expenses.csv", index=False)
    return df


# ----------------------------
# Streamlit UI
# ----------------------------

st.set_page_config(page_title="Expense Tracker", layout="wide")

st.title("💰 Expense Tracker")

# ----------------------------
# Input Form
# ----------------------------

months = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

categories = [
    "Food",
    "Bills",
    "Travel",
    "Clothes",
    "Other"
]

with st.form("expense_form"):

    col1, col2 = st.columns(2)

    with col1:
        month = st.selectbox("Select Month", months)

    with col2:
        expense = st.number_input(
            "Expense (Rs.)",
            min_value=0.0,
            step=1.0
        )

    category = st.selectbox("Category", categories)

    remarks = st.text_input("Remarks")

    submitted = st.form_submit_button("Save Expense")

    if submitted:

        if expense <= 0:
            st.error("Expense must be greater than 0.")

        else:
            add_expense(month, expense, category, remarks)
            st.success("Expense Added Successfully!")
            st.rerun()

# ----------------------------
# Show Expenses
# ----------------------------

rows = show_expenses()

if rows:

    df = pd.DataFrame(
        rows,
        columns=[
            "ID",
            "Month",
            "Expense",
            "Category",
            "Remarks",
            "Date"
        ]
    )

    total = df["Expense"].sum()

    st.subheader(f"Total Expense : Rs. {total:.2f}")

    st.dataframe(
        df,
        use_container_width=True
    )

    # ------------------------
    # Delete Record
    # ------------------------

    st.subheader("Delete Expense")

    record = st.selectbox(
        "Select Record ID",
        df["ID"]
    )

    if st.button("Delete"):

        delete_expense(record)
        st.success("Record Deleted Successfully!")
        st.rerun()

    # ------------------------
    # Export CSV
    # ------------------------

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="expenses.csv",
        mime="text/csv"
    )

else:
    st.info("No expenses found.")

# ----------------------------
# Close Database
# ----------------------------

conn.close()