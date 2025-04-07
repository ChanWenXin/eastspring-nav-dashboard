import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Setup
st.set_page_config(layout='wide')
st.title("🌍 Eastspring NAV Dashboard")
st.markdown("All NAVs are normalized to USD using April 2025 exchange rates.")

# Load clean dataframe
df1 = pd.read_csv("C:\\udemy\\web scraping in python with beautifulsoup and selenium\\eastspring_funds_nav_draft2.csv", index_col=0)

#Clean the DF
# Approximate exchange rates to USD (as of April 2025)
currency_to_usd = {
    'USD': 1.00,
    'SGD': 0.74,
    'EUR': 1.08,
    'JPY': 0.0066,
    'GBP': 1.25,
    'AUD': 0.66,
    'CNH': 0.14,
    'HKD': 0.13,
    'NZD': 0.60
}

# Create a new column 'NAV (USD)' by converting NAV to USD using exchange rates
def convert_to_usd(row):
    currency = row['Currency']
    nav = row['NAV']
    rate = currency_to_usd.get(currency, 1.0)  # default to 1.0 if currency not found
    return nav * rate

df1['NAV (USD)'] = df1.apply(convert_to_usd, axis=1)
df1

# Sidebar filters (optional)
currencies = df1["Currency"].unique().tolist()
selected_currencies = st.sidebar.multiselect("Select Currencies", currencies, default=currencies)

df1_filtered = df1[df1["Currency"].isin(selected_currencies)]

# --- Section 1: Data Overview ---
st.header("📋 Fund Overview (Normalized to USD)")
st.dataframe(df1_filtered)

# --- Section 2: Average NAV by Currency ---
st.header("💵 Average NAV (USD) by Currency")
nav_avg = df1_filtered.groupby("Currency")["NAV (USD)"].mean().sort_values(ascending=False)

fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.barplot(x=nav_avg.index, y=nav_avg.values, palette="viridis", ax=ax1)
ax1.set_title("Average NAV (USD) by Currency")
ax1.set_ylabel("Average NAV (USD)")
ax1.set_xlabel("Currency")
st.pyplot(fig1)

# --- Section 3: NAV Volatility by Currency ---
st.header("📊 NAV Volatility by Currency")
nav_std = df1_filtered.groupby("Currency")["NAV (USD)"].std().sort_values(ascending=False)

fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.barplot(x=nav_std.index, y=nav_std.values, palette="rocket", ax=ax2)
ax2.set_title("NAV Volatility (Standard Deviation)")
ax2.set_ylabel("Standard Deviation (USD)")
ax2.set_xlabel("Currency")
st.pyplot(fig2)

# --- Section 4: Not Updated Funds ---
st.header("⚠️ Funds Not Updated (≠ 04 Apr 2025)")
outdated_funds = df1[df1["NAV Date"] != "2025-04-04"].reset_index(drop=True)
st.warning(f"{len(outdated_funds)} fund(s) have not updated their NAV on 04 Apr 2025.")
st.dataframe(outdated_funds)