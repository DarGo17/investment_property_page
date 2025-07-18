import streamlit as st
import numpy as np

st.title('Real Estate Investment Valuation Tool')

# User Inputs
purchase_price = st.number_input('Purchase Price ($)', value=1000000)
down_payment_percent = st.number_input('Down Payment (%)', min_value=0.0, max_value=100.0, value=20.0)
interest_rate = st.number_input('Interest Rate (%)', min_value=0.0, max_value=20.0, value=6.5)
loan_term_years = st.number_input('Loan Term (Years)', min_value=1, max_value=40, value=30)
annual_rent_income = st.number_input('Annual Rental Income ($)', value=120000)
annual_operating_expenses = st.number_input('Annual Operating Expenses ($)', value=40000)

payment_type = st.radio('Payment Type', ['Fully Amortized', 'Interest Only'])

# Calculations
down_payment = purchase_price * (down_payment_percent / 100)
loan_amount = purchase_price - down_payment
monthly_interest_rate = interest_rate / 100 / 12
total_payments = loan_term_years * 12

if payment_type == 'Fully Amortized':
    if monthly_interest_rate == 0:
        monthly_payment = loan_amount / total_payments
    else:
        monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate)**total_payments) / ((1 + monthly_interest_rate)**total_payments - 1)
else:
    monthly_payment = loan_amount * monthly_interest_rate  # Interest only

annual_debt_service = monthly_payment * 12
net_operating_income = annual_rent_income - annual_operating_expenses
cash_flow_before_tax = net_operating_income - annual_debt_service
monthly_cash_flow = cash_flow_before_tax / 12
cash_on_cash_return = (cash_flow_before_tax / down_payment) * 100 if down_payment > 0 else np.nan
cap_rate = (net_operating_income / purchase_price) * 100

# Output
st.header("Investment Summary")
st.write(f"Loan Amount: ${loan_amount:,.2f}")
st.write(f"Monthly Debt Payment ({payment_type}): ${monthly_payment:,.2f}")
st.write(f"Annual Debt Service: ${annual_debt_service:,.2f}")
st.write(f"Net Operating Income (NOI): ${net_operating_income:,.2f}")
st.write(f"Annual Cash Flow Before Tax: ${cash_flow_before_tax:,.2f}")

st.markdown("---")
st.subheader("Monthly Cash Flow")
if monthly_cash_flow >= 0:
    st.markdown(f"<h3 style='color:green;'>${monthly_cash_flow:,.2f} Positive Cash Flow</h3>", unsafe_allow_html=True)
else:
    st.markdown(f"<h3 style='color:red;'>${monthly_cash_flow:,.2f} Negative Cash Flow</h3>", unsafe_allow_html=True)

st.write(f"Cap Rate: {cap_rate:.2f}%")
st.write(f"Cash on Cash Return: {cash_on_cash_return:.2f}%")
