import requests 
import pandas as pd
import streamlit as st

# Replace with your Canvas API token and base URL
API_TOKEN = 'your_token_here'
BASE_URL = 'https://kepler.instructure.com/api/v1'

# Set headers for authentication
headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

# Function to fetch root accounts
def fetch_root_accounts():
    url = f'{BASE_URL}/accounts'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching root accounts: {response.status_code}")
        return []

# Function to fetch all subaccounts
def fetch_all_subaccounts(root_account_id):
    subaccounts = []
    url = f'{BASE_URL}/accounts/{root_account_id}/subaccounts?per_page=100'
    
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            subaccounts_page = response.json()
            subaccounts.extend(subaccounts_page)
            # Handle pagination if next page exists
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None
        else:
            st.error(f"Error fetching subaccounts: {response.status_code}")
            break
    return subaccounts

# Streamlit display function to show courses and their grades
def display_courses_grades_by_subaccount():
    # Fetch the root accounts first
    root_accounts = fetch_root_accounts()

    if not root_accounts:
        st.error("No root accounts found.")
        return
    
    # Assuming the first account is the root account
    root_account_id = root_accounts[0]['id']

    subaccounts = fetch_all_subaccounts(root_account_id)

    # Ensure subaccounts are not empty
    if not subaccounts:
        st.error("No subaccounts found.")
        return
    
    st.title("Course Grades by Subaccount")
    
    # Display subaccounts for selection
    subaccount_options = {subaccount['name']: subaccount['id'] for subaccount in subaccounts}
    
    # Handle empty subaccount options
    if not subaccount_options:
        st.error("No subaccount options available.")
        return

    selected_subaccount_name = st.selectbox("Select Subaccount", list(subaccount_options.keys()))
    
    # Ensure the selected subaccount name is valid
    if selected_subaccount_name not in subaccount_options:
        st.error("Invalid subaccount selected.")
        return

    selected_subaccount_id = subaccount_options[selected_subaccount_name]

    # Here you can proceed to fetch and display courses by subaccount
    st.write(f"Selected Subaccount ID: {selected_subaccount_id}")

# Streamlit app starts here
if __name__ == "__main__":
    display_courses_grades_by_subaccount()
