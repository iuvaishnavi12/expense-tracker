# streamlit_app.py
# Real-Time Expense Tracker with Monthly Reports & Budget Alerts

import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Expense Tracker", layout="centered")

st.markdown("""
<h1 style="margin-bottom:0;">ExpensePulse</h1>
<p style="color:#9aa0a6; margin-top:4px;">
Smart expense tracking & spending insights
</p>
""", unsafe_allow_html=True)

st.divider()



# ------------------ SESSION STATE ------------------
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(
        columns=["Date", "Category", "Description", "Amount"]
    )

# ------------------ SIDEBAR ------------------
st.sidebar.header("➕ Add New Expense")

date = st.sidebar.date_input("Date", datetime.today())
category = st.sidebar.selectbox(
    "Category",
    ["Food", "Transport", "Education", "Entertainment", "Shopping", "Others"],
)
description = st.sidebar.text_input("Description")
amount = st.sidebar.number_input("Amount (₹)", min_value=0.0, step=1.0)

if st.sidebar.button("Add Expense"):
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
    st.sidebar.success("Expense Added Successfully")

# ------------------ EXPENSE LIST ------------------
st.subheader("📋 Expense List")
st.dataframe(st.session_state.expenses, use_container_width=True)

# ------------------ OVERALL SUMMARY ------------------
st.subheader("📊 Overall Expense Summary")

if not st.session_state.expenses.empty:
    total_expense = st.session_state.expenses["Amount"].sum()
    st.metric("💸 Total Expense", f"₹ {total_expense:.2f}")

    category_summary = st.session_state.expenses.groupby("Category")["Amount"].sum()
    st.bar_chart(category_summary)
else:
    st.info("No expenses added yet")

# ------------------ MONTHLY REPORT ------------------
if not st.session_state.expenses.empty:
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

    # ------------------ BUDGET LIMIT ALERTS ------------------
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

    # ------------------ SMART SUGGESTIONS ------------------
    st.subheader("💡 Spending Suggestions")

    highest_category = monthly_category.idxmax()
    highest_amount = monthly_category.max()

    st.info(
        f"📌 Highest spending category: **{highest_category} (₹{highest_amount:.2f})**"
    )

    if highest_category in ["Shopping", "Entertainment"]:
        st.warning("Try reducing non-essential spending next month.")

# ------------------ FOOTER ------------------
st.markdown("---")
st.caption("Built with ❤️ using Python & Streamlit")

