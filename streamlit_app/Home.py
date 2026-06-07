import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Payment Instruction Parser", layout="wide")
st.title("Payment Instruction Parser")

uploaded_file = st.file_uploader("Upload a payment email", type=["txt", "eml"])

left, right = st.columns([1, 2])

with left:
    st.subheader("Intake")
    if uploaded_file:
        st.caption(uploaded_file.name)
        if st.button("Extract payment instructions", type="primary"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "text/plain")}
            with st.spinner("Extracting structured payment fields..."):
                response = requests.post(f"{API_BASE_URL}/payments/extract", files=files, timeout=90)
            if response.ok:
                st.session_state["latest_result"] = response.json()
                st.success("Extraction complete")
            else:
                st.error(response.json().get("detail", response.text))

with right:
    st.subheader("Extracted Fields")
    result = st.session_state.get("latest_result")
    if result:
        payments = result.get("payments", [])
        if payments:
            st.dataframe(payments, use_container_width=True, hide_index=True)
        else:
            st.info("No payment instructions found.")
    else:
        st.info("Upload a .txt or .eml payment email to begin.")

st.divider()
st.subheader("Recent Extractions")
try:
    history_response = requests.get(f"{API_BASE_URL}/payments", timeout=15)
    if history_response.ok:
        st.dataframe(history_response.json(), use_container_width=True, hide_index=True)
    else:
        st.caption("History is unavailable.")
except requests.RequestException:
    st.caption("Start the FastAPI service to view extraction history.")
