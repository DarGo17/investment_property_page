import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prophet import Prophet
import joblib
import requests
from datetime import datetime

# =================== Load Model and Data ==========================
model = joblib.load('prophet_model.pkl')
combined_df = joblib.load('combined_df.pkl')  # Should include Date, price, MORTGAGE30US
forecast = model.predict(model.make_future_dataframe(periods=120, freq='M'))  # Generate full future forecast

# =================== RentCast API Setup ==========================
API_KEY = "bc87829e1d2d4ee68dcbb775c90b598a"
VALUE_URL = "https://api.rentcast.io/v1/avm/value"
HEADERS = {"X-Api-Key": API_KEY}

def fetch_property_value(address):
    params = {"address": address}
    response = requests.get(VALUE_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Value API Error {response.status_code}: {response.text}")
        return None

# =================== Streamlit UI ==========================
st.set_page_config(page_title="Forecast vs RentCast Comparison", layout="wide")
st.title("🏡 Address-Based Home Value vs Forecast Comparison")

tab1, tab2 = st.tabs(["📈 Forecast Explorer", "🏷️ Address Comparison"])

# =================== TAB 1: Prophet Forecast Viewer ==========================
with tab1:
    st.subheader("📉 Full Model Forecast Viewer")

    months_to_predict = st.slider("Forecast Months Ahead", 1, 120, 12)
    min_date = forecast['ds'].min()
    max_date = forecast['ds'].max()
    date_range = st.date_input("Select Date Range to View", [min_date, max_date])

    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    forecast_filtered = forecast[(forecast['ds'] >= start_date) & (forecast['ds'] <= end_date)]

    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(forecast_filtered['ds'], forecast_filtered['yhat'], label="Forecast")
    ax1.fill_between(forecast_filtered['ds'], forecast_filtered['yhat_lower'], forecast_filtered['yhat_upper'],
                     color='blue', alpha=0.2, label="Uncertainty")
    ax1.set_title("Fayetteville Home Price Forecast")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Price ($)")
    ax1.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig1)

# =================== TAB 2: Address Comparison ==========================
with tab2:
    st.subheader("📍 Compare Property Value with Forecast on Custom Date")

    address = st.text_input("Enter Property Address", "3821 Hargis St, Austin, TX 78723")
    forecast_min = forecast['ds'].min()
    forecast_max = forecast['ds'].max()

    date_input = st.date_input("Select Forecast Date", forecast_max, min_value=forecast_min, max_value=forecast_max)

    if address and date_input:
        value_data = fetch_property_value(address)

        if value_data:
            rentcast_price = value_data.get("price")
            st.metric("🏷️ RentCast Estimated Value", f"${rentcast_price:,.0f}")

            selected_date = pd.to_datetime(date_input)

            # Find closest forecasted date
            closest_row = forecast.iloc[(forecast['ds'] - selected_date).abs().argsort()[:1]]
            model_price = closest_row['yhat'].values[0]
            model_date = closest_row['ds'].values[0]

            st.metric("📈 Forecasted Value on Selected Date", f"${model_price:,.0f}")
            diff_pct = 100 * (rentcast_price - model_price) / model_price

            if diff_pct > 0:
                st.success(f"🏠 The property appears **overvalued** by {diff_pct:.2f}% compared to the model.")
            else:
                st.info(f"💸 The property appears **undervalued** by {abs(diff_pct):.2f}% compared to the model.")

            # Plot forecast from selected date forward
            st.markdown("### 🔮 Forecast from Selected Date")
            filtered_forecast = forecast[forecast['ds'] >= selected_date]

            fig2, ax2 = plt.subplots(figsize=(10, 4))
            ax2.plot(filtered_forecast['ds'], filtered_forecast['yhat'], label="Forecast")
            ax2.fill_between(filtered_forecast['ds'], filtered_forecast['yhat_lower'], filtered_forecast['yhat_upper'], color='blue', alpha=0.2)
            ax2.axhline(y=rentcast_price, color='r', linestyle='--', label="RentCast Value")
            ax2.set_xlabel("Date")
            ax2.set_ylabel("Price ($)")
            ax2.set_title("Forecast vs RentCast Value")
            ax2.legend()
            st.pyplot(fig2)

# =================== Optional CSV Download ==========================
st.markdown("---")
csv = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_csv(index=False)
st.download_button(label="📥 Download Full Forecast CSV", data=csv, file_name='forecast.csv', mime='text/csv')
