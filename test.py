import streamlit as st
import pandas as pd

# Initialize user data (in a real system, this would be loaded from a database or CSV)
users = {'username': ['user1', 'user2'], 'password': ['pass1', 'pass2']}
user_data = pd.DataFrame(users)

# Store applications
applications = []

# Function to check login credentials
def check_credentials(username, password):
    if (user_data['username'] == username).any() and (user_data['password'] == password).any():
        return True
    else:
        return False

# Main Streamlit app
def main():
    st.title("Scholarship Application System")

    # User registration or login
    choice = st.sidebar.selectbox("Choose action", ["Login", "Register"])
    
    if choice == "Register":
        st.subheader("Create a new account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        
        if st.button("Register"):
            if new_user and new_password:
                new_row = {'username': new_user, 'password': new_password}
                global user_data
                user_data = user_data.append(new_row, ignore_index=True)
                st.success("Account created successfully!")
            else:
                st.warning("Please fill in both fields.")

    elif choice == "Login":
        st.subheader("Login to your account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if check_credentials(username, password):
                st.success(f"Welcome {username}!")

                # Scholarship application form
                st.subheader("Apply for a scholarship")
                full_name = st.text_input("Full Name")
                email = st.text_input("Email")
                essay = st.text_area("Why do you deserve the scholarship?")
                
                if st.button("Submit Application"):
                    application = {'Full Name': full_name, 'Email': email, 'Essay': essay}
                    applications.append(application)
                    st.success("Your application has been submitted!")
            else:
                st.error("Invalid username or password")

if __name__ == '__main__':
    main()
