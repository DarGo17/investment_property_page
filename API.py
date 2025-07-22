import streamlit as st
import requests
import json
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Configuration
API_KEY = "bc87829e1d2d4ee68dcbb775c90b598a"
VALUE_URL = "https://api.rentcast.io/v1/avm/value"
RENT_URL = "https://api.rentcast.io/v1/avm/rent/long-term"
MAX_PULLS = 50
COUNTER_FILE = "pull_counter.json"

headers = {
    "X-Api-Key": API_KEY
}

# Load or initialize pull counter
def load_counter():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            data = json.load(f)
            return data.get("remaining", MAX_PULLS)
    else:
        return MAX_PULLS

def save_counter(remaining):
    with open(COUNTER_FILE, "w") as f:
        json.dump({"remaining": remaining}, f)

def fetch_property_value(address):
    params = {"address": address}
    response = requests.get(VALUE_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Value API Error {response.status_code}: {response.text}")
        return None

def fetch_rent_estimate(address):
    params = {"address": address}
    response = requests.get(RENT_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Rent API Error {response.status_code}: {response.text}")
        return None

# Simulate historical data for value/rent trends (since RentCast doesn't provide directly)
def generate_trend(current_value, growth_rate=0.03, years=10):
    dates = [datetime.now() - timedelta(days=365 * i) for i in reversed(range(years))]
    values = [current_value / ((1 + growth_rate) ** (years - i - 1)) for i in range(years)]
    return pd.DataFrame({'Year': [d.year for d in dates], 'Value': values})

def main():
    st.title("🏡 Property Valuation & Rent Insights Dashboard")

    remaining_pulls = load_counter()
    st.sidebar.markdown(f"### API Calls Remaining: **{remaining_pulls}**")

    address = st.text_input("Enter Full Property Address", "3821 Hargis St, Austin, TX 78723")

    if st.button("Analyze Property"):
        if remaining_pulls <= 0:
            st.error("❌ Monthly API pull limit reached (50). Wait until next month.")
            return

        if not address.strip():
            st.warning("⚠️ Please enter a valid address.")
            return

        st.info(f"📡 Fetching data for **{address}**...")

        value_data = fetch_property_value(address)
        rent_data = fetch_rent_estimate(address)

        st.markdown("---")

        # Display in Tabs
        tab1, tab2, tab3 = st.tabs(["🏠 Current Valuation", "📊 Trends Over 10 Years", "📄 Raw API Responses"])

        with tab1:
            if value_data:
                price = value_data.get("price")
                price_low = value_data.get("priceRangeLow")
                price_high = value_data.get("priceRangeHigh")

                st.subheader("🏷️ Property Value")
                st.metric("Current Estimated Value", f"${price:,.0f}")
                st.caption(f"Value Range: ${price_low:,.0f} - ${price_high:,.0f}")

            if rent_data:
                rent = rent_data.get("rent")
                rent_low = rent_data.get("rentRangeLow")
                rent_high = rent_data.get("rentRangeHigh")

                st.subheader("💰 Expected Monthly Rent")
                st.metric("Current Rent Estimate", f"${rent:,.0f} /mo")
                st.caption(f"Rent Range: ${rent_low:,.0f} - ${rent_high:,.0f}")

        with tab2:
            st.subheader("📈 Historical Trends (Simulated)")
            if value_data and rent_data:
                # Simulated historical data
                value_trend = generate_trend(price, growth_rate=0.035)
                rent_trend = generate_trend(rent, growth_rate=0.025)

                # Plot
                st.markdown("#### Home Value Over Last 10 Years")
                st.line_chart(value_trend.set_index('Year'))

                st.markdown("#### Rent Estimate Over Last 10 Years")
                st.line_chart(rent_trend.set_index('Year'))

                st.caption("Note: Historical trends are modeled based on assumed average appreciation rates.")

            else:
                st.warning("Not enough data to generate trends.")

        with tab3:
            st.subheader("📄 Raw API Responses")
            st.markdown("**Property Value API Response:**")
            st.json(value_data)

            st.markdown("**Rent Estimate API Response:**")
            st.json(rent_data)

        # Decrement counter and save
        remaining_pulls -= 1
        save_counter(remaining_pulls)
        st.sidebar.markdown(f"### API Calls Remaining: **{remaining_pulls}**")

if __name__ == "__main__":
    main()
