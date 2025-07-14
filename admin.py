import streamlit as st
import requests
import time as t
import os
import pandas as pd
from db_conn import get_db_connection
from datetime import date
from utils import load_credentials
from streamlit_lottie import st_lottie
from io import StringIO


today = date.today()

# --- Helper Functions ---

def load_lottie_url(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def fetch_employee_ledger(emp_id):
    conn = get_db_connection()
    query = f'''
        SELECT
            date, emp_id, emp_name, department,
            transaction_type, transaction_method, amount, remarks,
            CASE WHEN transaction_type = 'Amount Given' THEN amount ELSE 0 END AS amount_given,
            CASE WHEN transaction_type = 'Amount Recovered' THEN amount ELSE 0 END AS amount_recovered,
            SUM(CASE WHEN transaction_type = 'Amount Given' THEN amount ELSE -amount END)
                OVER (PARTITION BY emp_id ORDER BY date, id) AS running_balance
        FROM advance_transactions
        WHERE emp_id = %s
        ORDER BY date, id;
    '''
    cursor = conn.cursor()
    cursor.execute(query, (emp_id))
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_department_ledger(dept):
    conn = get_db_connection()
    query = f'''
        SELECT
            emp_id, emp_name, department,
            SUM(CASE WHEN transaction_type = 'Amount Given' THEN amount ELSE 0 END) AS total_advance,
            SUM(CASE WHEN transaction_type = 'Amount Recovered' THEN amount ELSE 0 END) AS total_recovery,
            SUM(CASE WHEN transaction_type = 'Amount Given' THEN amount ELSE -amount END) AS balance
        FROM advance_transactions
        WHERE department = %s
        GROUP BY emp_id, emp_name, department;
    '''
    cursor = conn.cursor()
    cursor.execute(query, (dept))
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_date_range_ledger(start_date, end_date):
    conn = get_db_connection()
    query = f'''
        SELECT
            date, emp_id, emp_name, department,
            transaction_type, transaction_method, amount, remarks,
            CASE WHEN transaction_type = 'Amount Given' THEN amount ELSE 0 END AS amount_given,
            CASE WHEN transaction_type = 'Amount Recovered' THEN amount ELSE 0 END AS amount_recovered,
            SUM(CASE WHEN transaction_type = 'Amount Given' THEN amount ELSE -amount END)
                OVER (PARTITION BY emp_id ORDER BY date, id) AS running_balance
        FROM advance_transactions
        WHERE date BETWEEN %s AND %s
        ORDER BY date, id;
    '''
    cursor = conn.cursor()
    cursor.execute(query, (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_month_summary():
    conn = get_db_connection()
    query = f'''
        SELECT DATE_FORMAT(date, '%Y-%m') AS month,
            SUM(CASE WHEN transaction_type = 'Amount Given' THEN amount ELSE 0 END) AS total_advance,
            SUM(CASE WHEN transaction_type = 'Amount Recovered' THEN amount ELSE 0 END) AS total_recovery
        FROM advance_transactions
        GROUP BY month
        ORDER BY month DESC;
    '''
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_full_ledger():
    conn = get_db_connection()
    query = '''
        SELECT
            date, emp_id, emp_name, department,
            transaction_type, transaction_method, amount, remarks,
            CASE WHEN transaction_type = 'Amount Given' THEN amount ELSE 0 END AS amount_given,
            CASE WHEN transaction_type = 'Amount Recovered' THEN amount ELSE 0 END AS amount_recovered,
            SUM(CASE WHEN transaction_type = 'Amount Given' THEN amount ELSE -amount END)
                OVER (PARTITION BY emp_id ORDER BY date, id) AS running_balance
        FROM advance_transactions
        ORDER BY date, id;
    '''
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

# Fetch user data (remains largely the same, no S3 interaction here)
def fetch_user_data(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT customer_id, loanid, codes AS "issue/codes", remarks AS "Remarks/notes", agents, timestamp, 'collection' AS source
    FROM collection_loan_tracker
    WHERE customer_id = %s
    UNION ALL
    SELECT customer_id, Loan_ID, issue AS "issue/codes", remark AS "Remarks/notes", agents, timestamp, channel AS source
    FROM cx_support_ticket
    WHERE customer_id = %s
    ORDER BY timestamp ASC;
    """
    cursor.execute(query, (user_id, user_id))
    rows = cursor.fetchall()
    conn.close()
    return rows

def download_data(start_date, end_date, modules):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Convert the list to a tuple and ensure each value is quoted as a string
    formatted_modules = tuple(f"'{module}'" for module in modules)

    # Format the tuple for the SQL query
    if len(formatted_modules) == 1:
        formatted_tuple = f"({formatted_modules[0]})"  # Single value
    else:
        formatted_tuple = str(formatted_modules) # tuple format for SQL 'IN' clause

    # Build the SQL query with the correct number of placeholders
    query = f"""
    SELECT *
    FROM cx_support_ticket
    WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'
    AND (channel in {formatted_tuple} or channel is Null);
    """

    # Execute the query, passing the start date, end date, and the modules list
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def insert_transaction(data):
    conn = get_db_connection()
    if conn is None:
        st.error("❌ Could not connect to the database.")
        return False

    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO advance_transactions (
                emp_name, emp_id, date, amount, transaction_type,
                transaction_method, department, remarks
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, data)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"❌ Failed to insert: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Admin Module
def admin_module():
    st.title("Advance Management Portal 💵")
    st.write("You can add new advance transaction entry here!")

    today = date.today()
    validation_errors = {}

    with st.form("add_transaction", clear_on_submit=True):
        st.markdown("<h5>Add New Transaction:</h5>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            emp_name = st.text_input("Employee Name*", key="emp_name",placeholder="Enter Employee Name")
        with col2:
            emp_id = st.text_input("Employee ID*", key="emp_id", placeholder="Enter Employee ID").upper()

        col1, col2 = st.columns(2)
        with col1:
            txn_date = st.date_input("Date*", value=today, max_value=today, key="txn_date")
        with col2:
            amount = st.text_input("Amount(₹)*", placeholder="00", key="amount")

        col1, col2 = st.columns(2)
        with col1:
            transaction_type = st.selectbox("Transaction Type*", 
                options=["Amount Given", "Amount Recovered"], 
                index=None, 
                placeholder="Select transaction type...", 
                key="txn_type")
        with col2:
            transaction_method = st.selectbox("Transaction Method*", 
                options=["Salary", "Cash", "Bank Transfer"], 
                index=None, 
                placeholder="Select transaction method...", 
                key="txn_method")

        col1, col2 = st.columns(2)
        with col1:
            department = st.selectbox("Department*", 
                options=["HR", "A", "B", "C", "D"], 
                index=None, 
                placeholder="Select department...", 
                key="dept")
        with col2:
            remarks = st.text_input("Remarks", placeholder="Enter your remarks...", key="remarks")

        submitted = st.form_submit_button("↪ Add Transaction", type="primary", use_container_width=True)

        if submitted:
            validation_errors["emp_name"] = not emp_name
            validation_errors["emp_id"] = not emp_id
            validation_errors["amount"] = not amount
            validation_errors["transaction_type"] = transaction_type is None
            validation_errors["transaction_method"] = transaction_method is None
            validation_errors["department"] = department is None

            if any(validation_errors.values()):
                # error_container = st.empty()
                # error_container.error("🚨 Please fill all required fields marked with *")
                # t.sleep()
                # error_container.empty()
                st.toast("🚨Please fill all required fields marked with *")
            else:
                if remarks == "":
                    remarks = "No Remarks Updated by user"
                # Prepare data tuple
                data = (
                    emp_name,
                    emp_id,
                    txn_date,
                    float(amount),
                    transaction_type,
                    transaction_method,
                    department,
                    remarks
                )
                success = insert_transaction(data)
                if success:
                    st.success("✅ Transaction submitted successfully!")

    # Highlight unfilled fields with red border (CSS)
    st.markdown("""
    <style>
    input:placeholder-shown:invalid, select:invalid {
        border: 2px solid red !important;
    }
    </style>
    """, unsafe_allow_html=True)


    st.markdown("<hr>",unsafe_allow_html=True)

    st.title("Advance Report Fetcher 💼")

    report_type = st.radio("Select the type of report you want to fetch", [
        "Employee-wise Ledger",
        "Department-wise Ledger",
        "Date-wise Ledger",
        "Month-wise Summary",
        "Full Ledger"
    ], captions=[
        "Shows running balance of selected employee",
        "Shows department-wise outstanding and recovery",
        "Shows transactions in a date range",
        "Shows monthly aggregated summary",
        "Full transaction history"
    ], horizontal=True)

    emp_id = dept = None
    start_date = end_date = None

    if report_type == "Employee-wise Ledger":
        emp_id = st.text_input("Enter Employee ID", placeholder="e.g., EMP001")

    elif report_type == "Department-wise Ledger":
        dept = st.selectbox("Select Department", ["HR", "Finance", "Operations"])

    elif report_type in ["Date-wise Ledger", "Month-wise Summary"]:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From Date", max_value=date.today())
        with col2:
            end_date = st.date_input("To Date", max_value=date.today())

    if st.button("📥 Fetch Report"):
        with st.spinner("Fetching data..."):
            if report_type == "Employee-wise Ledger" and emp_id:
                rows = fetch_employee_ledger(emp_id)
            elif report_type == "Department-wise Ledger" and dept:
                rows = fetch_department_ledger(dept)
            elif report_type == "Date-wise Ledger" and start_date and end_date:
                rows = fetch_date_range_ledger(start_date, end_date)
            elif report_type == "Month-wise Summary" and start_date and end_date:
                rows = fetch_month_summary()
            elif report_type == "Full Ledger":
                rows = fetch_full_ledger()
            else:
                st.warning("Please fill in all required filters.")
                rows = []

        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df)
        else:
            st.info("No records found.")


    st.markdown("<br><br><br><br>",unsafe_allow_html=True)
