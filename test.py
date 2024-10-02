import requests 
import pandas as pd
import streamlit as st

# Replace with your Canvas API token and base URL
API_TOKEN = '1941~YfMDLMGz2ZRWRvcWZBG8k7yctAXvfxnGMwCrF3cVJGBzhVKDCvUWDhPeVeDXnaMz'
BASE_URL = 'https://kepler.instructure.com/api/v1'

# Set headers for authentication
headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

# Function to fetch all courses from the account
def fetch_all_courses():
    url = f'{BASE_URL}/accounts/1/courses'
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else []

# Function to fetch assignment groups for a course
def fetch_assignment_groups(course_id):
    url = f'{BASE_URL}/courses/{course_id}/assignment_groups'
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else []

# Function to fetch assignments in each group
def fetch_assignments(course_id, group_id):
    url = f'{BASE_URL}/courses/{course_id}/assignment_groups/{group_id}/assignments'
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else []

# Function to fetch student submissions for an assignment
def fetch_grades(course_id, assignment_id):
    url = f'{BASE_URL}/courses/{course_id}/assignments/{assignment_id}/submissions'
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else []

# Function to fetch student info (including ID) based on their email
def fetch_student_by_email(email):
    url = f'{BASE_URL}/accounts/1/users'
    params = {'search_term': email}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        users = response.json()
        if users:
            return users[0]  # Assuming the first user is the correct one
    return None

# Function to fetch student names
def fetch_student_name(student_id):
    url = f'{BASE_URL}/users/{student_id}/profile'
    response = requests.get(url, headers=headers)
    return response.json()['name'] if response.status_code == 200 else 'Unknown'

# Function to calculate percentage grades and format data, filtered by student email
def format_gradebook(course_id, student_email):
    gradebook = []
    
    # Fetch student based on email
    student = fetch_student_by_email(student_email)
    
    if not student:
        st.error(f"No student found with email {student_email}")
        return pd.DataFrame()  # Return empty DataFrame

    student_id = student['id']
    assignment_groups = fetch_assignment_groups(course_id)
    
    for group in assignment_groups:
        group_name = group['name']
        group_weight = group['group_weight']
        
        assignments = fetch_assignments(course_id, group['id'])
        for assignment in assignments:
            assignment_name = assignment['name']
            assignment_max_score = assignment['points_possible']

            grades = fetch_grades(course_id, assignment['id'])
            for submission in grades:
                # Only process if the submission belongs to the selected student
                if submission['user_id'] == student_id:
                    grade = submission.get('score', 0)
                    grade = grade if grade is not None else 0
                    percentage = (grade / assignment_max_score) * 100 if assignment_max_score > 0 else 0

                    gradebook.append({
                        'Student ID': student_id,
                        'Student Name': student['name'],
                        'Assignment Group': group_name,
                        'Group Weight': group_weight,
                        'Assignment Name': assignment_name,
                        'Grade': grade,
                        'Max Score': assignment_max_score,
                        'Percentage': round(percentage, 2)
                    })
    
    df = pd.DataFrame(gradebook)

    # Debugging: Print the DataFrame structure and check columns
    print("Gradebook DataFrame:\n", df.head())  # First few rows for debugging
    print("Columns in DataFrame:", df.columns)  # Print column names

    # Group by student and assignment groups if all columns are present
    if all(col in df.columns for col in ['Student ID', 'Assignment Group', 'Assignment Name', 'Group Weight']):
        df = df.groupby(['Student ID', 'Student Name', 'Assignment Group', 'Assignment Name', 'Group Weight']).mean()
    else:
        print("Missing one or more columns required for grouping.")
    
    return df

# Streamlit display function to show courses and their grades based on student email
def display_all_courses_grades():
    student_email = st.text_input("Enter student email:")
    
    if student_email:
        courses = fetch_all_courses()
        st.title("Course Grades by Student Email")

        # Display all courses fetched
        for course in courses:
            course_id = course['id']
            course_name = course['name']
            st.header(f"Course: {course_name} (ID: {course_id})")

            # Fetch and display the gradebook filtered by student email
            df_gradebook = format_gradebook(course_id, student_email)
            st.write(df_gradebook)

# Streamlit app starts here
if __name__ == "__main__":
    display_all_courses_grades()
