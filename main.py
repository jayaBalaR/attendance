import streamlit as st
import pymongo
import pandas as pd
from datetime import datetime

# MongoDB Atlas connection setup
def init_mongodb():
    connection_string = st.secrets["mongo"]["connection_string"]
    client = pymongo.MongoClient(connection_string, connect=False, serverSelectionTimeoutMS=5000)
    db = client["attendance_db"]
    return db

# Function to populate names from an Excel file
def load_names_from_excel():
    # Assume the Excel file is named 'students.xlsx' with a 'name' column
    df = pd.read_excel('students.xlsx')
    return df['Name'].tolist()

# Initialize MongoDB connection
db = init_mongodb()
attendance_collection = db["attendance"]
fees_collection = db["fees"]

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

    # Ensure attendance is only for today or future dates
    if date < datetime.today().date():
        st.error("You can only submit attendance for today or future dates.")
    else:
        status = st.radio("Attendance Status", ["Present", "Absent"])
    
        if st.button("Submit Attendance"):
            # Insert new record into MongoDB
            attendance_record = {
                "name": name,
                "status": status,
                "date": date.strftime('%d/%m/%Y')
            }
            attendance_collection.insert_one(attendance_record)
    
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
            fees_results = []

            for _, row in df.iterrows():
                # Count present days from MongoDB
                present_days = attendance_collection.count_documents({"name": row['Name'], "status": "Present"})
                daily_fees = row['Monthly Fees'] / 30  # Assuming 30 days in a month
                fees_to_pay = daily_fees * present_days

                # Append calculated fees
                fees_results.append({
                    "name": row['Name'],
                    "fees_to_pay": round(fees_to_pay, 2)
                })

                # Insert or update fees record in MongoDB
                fees_collection.update_one(
                    {"name": row['Name']},
                    {"$set": {"fees_to_pay": round(fees_to_pay, 2)}},
                    upsert=True
                )

            # Display calculated fees
            fees_df = pd.DataFrame(fees_results)
            st.write("Calculated Fees")
            st.dataframe(fees_df)

st.sidebar.info("Developed for tracking student attendance and fees.")
