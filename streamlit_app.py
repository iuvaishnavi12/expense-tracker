# streamlit_app.py
# ExpensePulse - Real-Time Expense Tracker with Reports & Budget Alerts

import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------ CONSTANTS ------------------
COLUMNS = ["Date", "Category", "Description", "Amount"]
CATEGORIES = ["Food", "Transport", "Education", "Entertainment", "Shopping", "Others"]

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="ExpensePulse", layout="centered")

st.markdown("""
<h1 style="margin-bottom:0;">ExpensePulse</h1>
<p style="color:#9aa0a6; margin-top:4px;">
Smart expense tracking & spending insights
</p>
""", unsafe_allow_html=True)

st.divider()

# ------------------ SESSION STATE ------------------
def init_session_state():
    if "expenses" not in st.session_state:
        st.session_state.expenses = pd.DataFrame(columns=COLUMNS)

init_session_state()

# ------------------ SIDEBAR: ADD EXPENSE ------------------
def sidebar_add_expense():
    st.sidebar.header("➕ Add New Expense")

    date = st.sidebar.date_input("Date", datetime.today())
    category = st.sidebar.selectbox("Category", CATEGORIES)
    description = st.sidebar.text_input("Description")
    amount = st.sidebar.number_input("Amount (₹)", min_value=0.0, step=1.0)

    if st.sidebar.button("Add Expense"):
        if amount <= 0:
            st.sidebar.error("Amount must be greater than 0")
            return
        if not description.strip():
            st.sidebar.error("Description cannot be empty")
            return

        new_expense = {
            "Date": date,
            "Category": category,
            "Description": description,
            "Amount": amount,
        }

        st.session_state.expenses = pd.concat(
            [st.session_state.expenses, pd.DataFrame([new_expense])],
            ignore_index=True,
        )

        st.sidebar.success("Expense added successfully")

sidebar_add_expense()

# ------------------ EXPENSE LIST ------------------
def show_expense_list():
    st.subheader("📋 Expense List")
    st.dataframe(st.session_state.expenses, use_container_width=True)

show_expense_list()

# ------------------ OVERALL SUMMARY ------------------
def overall_summary():
    st.subheader("📊 Overall Expense Summary")

    if st.session_state.expenses.empty:
        st.info("No expenses added yet")
        return

    total = st.session_state.expenses["Amount"].sum()
    st.metric("💸 Total Expense", f"₹ {total:.2f}")

    category_summary = (
        st.session_state.expenses.groupby("Category")["Amount"].sum()
    )
    st.bar_chart(category_summary)

overall_summary()

# ------------------ MONTHLY REPORT & BUDGET ------------------
def monthly_report():
    if st.session_state.expenses.empty:
        return

    st.divider()
    st.subheader("📅 Monthly Expense Report")

    df = st.session_state.expenses.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    selected_month = st.selectbox(
        "Select Month",
        sorted(df["Month"].unique())
    )

    monthly_df = df[df["Month"] == selected_month]
    monthly_total = monthly_df["Amount"].sum()

    st.metric("💰 Monthly Expense", f"₹ {monthly_total:.2f}")

    monthly_category = monthly_df.groupby("Category")["Amount"].sum()
    st.bar_chart(monthly_category)

    # -------- Budget Alert --------
    st.divider()
    st.subheader("🚨 Monthly Budget Alert")

    budget = st.number_input(
        "Set Monthly Budget (₹)",
        min_value=0.0,
        step=500.0,
        value=5000.0
    )

    if budget > 0:
        usage_percent = (monthly_total / budget) * 100

        if monthly_total > budget:
            st.error(
                f"❌ Budget Exceeded!\n\n"
                f"Spent ₹{monthly_total:.2f} / Budget ₹{budget:.2f}"
            )
        elif usage_percent >= 80:
            st.warning(
                f"⚠️ Warning! You have used {usage_percent:.1f}% of your budget."
            )
        else:
            st.success(
                f"✅ You are within budget. Used {usage_percent:.1f}%."
            )

    # -------- Smart Suggestions --------
    st.subheader("💡 Spending Suggestions")

    highest_category = monthly_category.idxmax()
    highest_amount = monthly_category.max()

    st.info(
        f"📌 Highest spending category: "
        f"**{highest_category} (₹{highest_amount:.2f})**"
    )

    if highest_category in ["Shopping", "Entertainment"]:
        st.warning("Consider reducing non-essential expenses next month.")

monthly_report()

# ------------------ FOOTER ------------------
st.markdown("---")
st.caption("Built with ❤️ using Python & Streamlit")
