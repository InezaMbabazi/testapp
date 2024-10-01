import streamlit as st
import pandas as pd

# Sample data for storing users and applications (in a real scenario, this should be a database)
user_data = pd.DataFrame(columns=["Username", "Password"])
scholarship_applications = pd.DataFrame(columns=["Username", "Scholarship"])

# Function to check if username already exists
def check_user_exists(username):
    return username in user_data["Username"].values

# Function to authenticate user
def authenticate_user(username, password):
    if check_user_exists(username):
        stored_password = user_data[user_data["Username"] == username]["Password"].values[0]
        return stored_password == password
    return False

# Function to apply for scholarship
def apply_for_scholarship(username):
    st.write(f"User {username} is applying for a scholarship.")
    scholarship = st.text_input("Enter scholarship name:")
    if st.button("Submit application"):
        if scholarship:
            new_application = {"Username": username, "Scholarship": scholarship}
            global scholarship_applications
            scholarship_applications = pd.concat([scholarship_applications, pd.DataFrame([new_application])], ignore_index=True)
            st.success("Application submitted successfully!")
        else:
            st.error("Please enter a valid scholarship name.")

# Main function
def main():
    st.title("Scholarship Application System")

    # Sidebar for user actions
    menu = ["Create Account", "Login", "View Applications"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Create Account":
        st.subheader("Create a new account")
        new_username = st.text_input("Enter Username")
        new_password = st.text_input("Enter Password", type="password")

        if st.button("Create Account"):
            if not check_user_exists(new_username):
                new_row = {"Username": new_username, "Password": new_password}
                global user_data
                user_data = pd.concat([user_data, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Account created successfully!")
            else:
                st.error("Username already exists. Please choose a different one.")

    elif choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate_user(username, password):
                st.success(f"Welcome {username}!")
                apply_for_scholarship(username)
            else:
                st.error("Invalid username or password.")

    elif choice == "View Applications":
        st.subheader("Scholarship Applications")
        st.write(scholarship_applications)

if __name__ == "__main__":
    main()
