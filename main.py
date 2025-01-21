import streamlit as st
import json
import pandas as pd
from datetime import datetime

# Initialize JSON files
def init_json():
    try:
        with open("attendance.json", "r") as f:
            json.load(f)
    except FileNotFoundError:
        with open("attendance.json", "w") as f:
            json.dump([], f)

    try:
        with open("fees.json", "r") as f:
            json.load(f)
    except FileNotFoundError:
        with open("fees.json", "w") as f:
            json.dump([], f)

# Function to populate names from an Excel file
def load_names_from_excel():
    # Assume the Excel file is named 'students.xlsx' with a 'name' column
    df = pd.read_excel('students.xlsx')
    return df['name'].tolist()

# Initialize JSON files
init_json()

# Load names from Excel
names = load_names_from_excel()

# Streamlit App
st.title("Student Attendance and Fees Tracker")

# Tab selection
tabs = st.tabs(["Mark Attendance", "Calculate Fees (End of Month)"])

# Tab 1: Mark Attendance
with tabs[0]:
    st.header("Mark Attendance")

    # Attendance form
    name = st.selectbox("Select Student Name", names)
    date = st.date_input("Select Date", value=datetime.today(), format="DD/MM/YY")
    status = st.radio("Attendance Status", ["Present", "Absent"])

    if st.button("Submit Attendance"):
        # Load existing attendance data
        with open("attendance.json", "r") as f:
            attendance_data = json.load(f)

        # Append new record
        attendance_data.append({
            "name": name,
            "status": status,
            "date": date.strftime('%d/%m/%Y')
        })

        # Save updated data
        with open("attendance.json", "w") as f:
            json.dump(attendance_data, f, indent=4)

        st.success("Attendance recorded successfully!")

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
