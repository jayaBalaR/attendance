import streamlit as st
import json
import pandas as pd
from datetime import datetime


# Streamlit App
st.title("Student Attendance and Fees Tracker")

# Tab selection
tabs = st.tabs(["Calculate Fees (End of Month)"])

# Tab 1: Mark Attendance
with tabs[0]:


# Tab 2: Calculate Fees
with tabs[1]:
    st.header("Calculate Monthly Fees")

    # Enable tab only at the end of the month
    today = datetime.today()
    if today.day != 30 and today.day != 31:  # Example condition for end-of-month
        st.warning("This feature is only enabled at the end of the month.")
    else:
        # Display table for fee calculation
        df = pd.DataFrame({
            "Name": names,
            "Email": [f"{name.lower().replace(' ', '.')}@example.com" for name in names],
            "Monthly Fees": [st.number_input(f"Monthly Fees for {name}", min_value=0.0) for name in names]
        })

        if st.button("Calculate Fees"):
            # Load attendance data
            with open("attendance.json", "r") as f:
                attendance_data = json.load(f)

            fees_results = []

            for _, row in df.iterrows():
                # Count present days
                present_days = sum(1 for record in attendance_data if record['name'] == row['Name'] and record['status'] == 'Present')
                daily_fees = row['Monthly Fees'] / 30  # Assuming 30 days in a month
                fees_to_pay = daily_fees * present_days

                # Append calculated fees
                fees_results.append({
                    "name": row['Name'],
                    "fees_to_pay": round(fees_to_pay, 2)
                })

            # Save fees data to JSON
            with open("fees.json", "w") as f:
                json.dump(fees_results, f, indent=4)

            # Display calculated fees
            fees_df = pd.DataFrame(fees_results)
            st.write("Calculated Fees")
            st.dataframe(fees_df)

st.sidebar.info("Developed for tracking student attendance and fees.")
