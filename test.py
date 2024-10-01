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

# Function to fetch all terms from the account
def fetch_all_terms():
    url = f'{BASE_URL}/accounts/1/terms'
    response = requests.get(url, headers=headers)
    
    # Check if the response is successful
    if response.status_code == 200:
        terms = response.json().get('enrollment_terms', [])
        return terms if terms else []
    else:
        st.error(f"Error fetching terms: {response.status_code} - {response.text}")
        return []

# Function to fetch all courses for a specific term
def fetch_all_courses(term_id=None):
    url = f'{BASE_URL}/accounts/1/courses'
    params = {'enrollment_term_id': term_id} if term_id else {}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json() if response.json() else []
    else:
        st.error(f"Error fetching courses: {response.status_code} - {response.text}")
        return []

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

# Function to fetch student names
def fetch_student_name(student_id):
    url = f'{BASE_URL}/users/{student_id}/profile'
    response = requests.get(url, headers=headers)
    return response.json()['name'] if response.status_code == 200 else 'Unknown'

# Function to calculate percentage grades and format data
def format_gradebook(course_id):
    gradebook = []
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
                student_id = submission['user_id']
                student_name = fetch_student_name(student_id)  # Fetch student name
                grade = submission.get('score', 0)
                grade = grade if grade is not None else 0
                
                percentage = (grade / assignment_max_score) * 100 if assignment_max_score > 0 else 0

                gradebook.append({
                    'Student ID': student_id,
                    'Student Name': student_name,
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

# Streamlit display function to show terms, courses, and their grades
def display_all_courses_grades():
    # Fetch all terms
    terms = fetch_all_terms()
    
    if terms:
        # Extract term names and IDs
        term_options = {term['name']: term['id'] for term in terms}
        
        # Allow user to select a term
        selected_term_name = st.selectbox('Select a Term', list(term_options.keys()))
        selected_term_id = term_options[selected_term_name]
        
        # Fetch and display courses for the selected term
        st.title(f"Course Grades for Term: {selected_term_name}")
        courses = fetch_all_courses(selected_term_id)
        
        if courses:
            for course in courses:
                course_id = course['id']
                course_name = course['name']
                st.header(f"Course: {course_name} (ID: {course_id})")
                
                # Fetch and display the gradebook
                df_gradebook = format_gradebook(course_id)
                st.write(df_gradebook)
        else:
            st.warning("No courses found for this term.")
    else:
        st.error("No terms found or access denied.")

# Streamlit app starts here
if __name__ == "__main__":
    display_all_courses_grades()
