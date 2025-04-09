import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests

# Setup
st.set_page_config(layout='wide')
st.title("🌍 Eastspring NAV Dashboard")
st.markdown("All NAVs are normalized to USD using April 2025 exchange rates.")

# Load clean dataframe
df1 = pd.read_csv("eastspring_funds_nav_draft2.csv", index_col=0)

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
st.header("⚠️ Funds Not Updated (≠ 08 Apr 2025)")
outdated_funds = df1[df1["NAV Date"] != "2025-04-08"].reset_index(drop=True)
st.warning(f"{len(outdated_funds)} fund(s) have not updated their NAV on 08 Apr 2025.")
st.dataframe(outdated_funds)

# === Prepare webhook message ===
if not outdated_funds.empty:
    fund_list_text = "\n".join(
        f"- {row['Fund name']}: NAV = {row['NAV']} ({row['NAV Date']})"
        for _, row in outdated_funds.iterrows()
    )

    teams_message = {
        "title": "⚠️ Funds Not Updated - NAV Alert",
        "text": f"{len(outdated_funds)} fund(s) have not updated their NAV for 08 Apr 2025:\n\n{fund_list_text}"
    }

    # === Replace this with your actual Teams webhook URL ===
    webhook_url = "https://szmschoolo.webhook.office.com/webhookb2/08ec0457-dcd4-4270-80f9-c0efd3078ede@b8288e74-2c7b-4331-93fd-aed4d2b09add/IncomingWebhook/f744a98bbe6a47d48c6fb54054e0b55a/b208173a-863b-4704-ac6e-b4e4e8a217cc/V283b-LipgVvFGXHbDY4u9CehZxYmsfpzsnaOgWY7v7kk1"

    # === Send to Microsoft Teams ===
    response = requests.post(
        webhook_url,
        json={"text": teams_message["text"]}
    )

    # Streamlit status
    if response.status_code == 200:
        st.success("🔔 Alert sent to Teams successfully.")
    else:
        st.error(f"❌ Failed to send alert. Status code: {response.status_code}")
