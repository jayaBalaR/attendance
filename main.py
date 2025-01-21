import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Database setup
def init_db():
    # Create the SQL connection to pets_db as specified in your secrets file.
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    # Attendance table
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        status TEXT,
                        date TEXT)''')
    # Fees table
    cursor.execute('''CREATE TABLE IF NOT EXISTS fees (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        fees_to_pay REAL)''')
    conn.commit()
    conn.close()

# Function to populate names from an Excel file
def load_names_from_excel():
    # Assume the Excel file is named 'students.xlsx' with a 'name' column
    df = pd.read_excel('students.xlsx')
    return df['Name'].tolist()

# Initialize database
init_db()

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
    date = st.date_input("Select Date", value=datetime.today(), format="DD/MM/YYYY")
    status = st.radio("Attendance Status", ["Present", "Absent"])

    if st.button("Submit Attendance"):
        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO attendance (name, status, date) VALUES (?, ?, ?)", (name, status, date.strftime('%d/%m/%Y')))
        conn.commit()
        conn.close()
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
            conn = sqlite3.connect("attendance.db")
            cursor = conn.cursor()
            fees_results = []

            for _, row in df.iterrows():
                cursor.execute("SELECT COUNT(*) FROM attendance WHERE name = ? AND status = 'Present'", (row['Name'],))
                present_days = cursor.fetchone()[0]
                daily_fees = row['Monthly Fees'] / 30  # Assuming 30 days in a month
                fees_to_pay = daily_fees * present_days

                # Save calculated fees to the database
                cursor.execute("INSERT INTO fees (name, fees_to_pay) VALUES (?, ?)", (row['Name'], fees_to_pay))

                fees_results.append({
                    "Name": row['Name'],
                    "Fees to Pay": round(fees_to_pay, 2)
                })

            conn.commit()
            conn.close()

            # Display calculated fees
            fees_df = pd.DataFrame(fees_results)
            st.write("Calculated Fees")
            st.dataframe(fees_df)

st.sidebar.info("Developed for tracking student attendance and fees.")
