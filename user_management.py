import datetime

import pandas as pd
import streamlit as st

from utils import (load_credentials,
                   save_credentials)


# Add user modal
def add_user_modal():
    with st.form("add_user_form"):
        st.write("### Add New User")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["voice", "email", "admin", "collections"])
        has_admin_access = st.checkbox("Has Super Admin Access")
        empid = st.text_input("Employee ID")
        dob = st.date_input(
            "Date of Birth",
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today(),
        )

        if st.form_submit_button("Add User"):
            credentials = load_credentials()

            if username in credentials:
                st.error("User already exists!")
            else:
                credentials[username] = {
                    "password": password,
                    "role": role,
                    "has_admin_access": has_admin_access,
                    "empid": empid,
                    "dob": str(dob),
                }
                save_credentials(credentials)
                st.success("User added successfully!")
                st.rerun()  # ✅ Updated rerun


# Delete user function
def delete_user(username):
    credentials = load_credentials()
    if username in credentials:
        del credentials[username]
        save_credentials(credentials)
        st.success(f"User {username} deleted successfully!")
        st.rerun()  # ✅ Updated rerun


# Update users function
def update_users(edited_df, original_credentials):
    updated_credentials = original_credentials.copy()
    changes_made = False

    for index, row in edited_df.iterrows():
        old_username = row["Original Username"]
        new_username = row["Username"]

        new_data = {
            "password": row["Password"],
            "role": row["Role"],
            "empid": row["EmpID"],
            "has_admin_access": row["Has Admin Access"],
            "dob": row["DOB"]
        }

        if old_username in updated_credentials:
            if (
                updated_credentials[old_username]["password"] != new_data["password"]
                or updated_credentials[old_username]["role"] != new_data["role"]
                or updated_credentials[old_username]["empid"] != new_data["empid"]
                or updated_credentials[old_username]["has_admin_access"]
                != new_data["has_admin_access"]
                or updated_credentials[old_username]["dob"] != new_data["dob"]
            ):
                changes_made = True
                updated_credentials[old_username] = new_data

        if old_username != new_username:
            changes_made = True
            updated_credentials[new_username] = updated_credentials.pop(old_username)

    if changes_made:
        save_credentials(updated_credentials)
        st.success("User data updated successfully!")
        st.rerun()  # ✅ Updated rerun

# User management UI
def user_management():
    st.title("User Management")
    credentials = load_credentials()

    add_user_modal()
    st.write("### User List")

    if credentials:
        user_list = [
            {
                "Original Username": username,
                "Username": username,
                "Password": details["password"],
                "Role": details["role"],
                "EmpID": details["empid"],
                "Has Admin Access": details["has_admin_access"],
                "DOB": details["dob"],
                "Delete": False,
            }
            for username, details in credentials.items()
        ]

        df = pd.DataFrame(user_list)
        edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="user_table")

        if st.button("Save Changes"):
            update_users(edited_df, credentials)

        users_to_delete = edited_df[edited_df["Delete"] == True]
        if not users_to_delete.empty:
            for index, row in users_to_delete.iterrows():
                delete_user(row["Original Username"])
            st.rerun()  # ✅ Updated rerun

    else:
        st.write("No users found.")

    st.markdown("<hr>", unsafe_allow_html=True)



# Run the user management UI
if __name__ == "__main__":
    user_management()