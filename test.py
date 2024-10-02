import requests
import pandas as pd
import streamlit as st

# Replace with your Canvas API token and base URL
API_TOKEN = '1941~FXJZ2tYC2DTWQr923eFTaXy473rK73A4KrYkT3uVy7WeYV9fyJQ4khH4MAGEH3Tf'
BASE_URL = 'https://kepler.instructure.com/api/v1'

# Set headers for authentication
headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

# Function to fetch all terms
def fetch_terms():
    url = f'{BASE_URL}/accounts/1/terms'
    response = requests.get(url, headers=headers)
    st.write(f"Fetching terms: {response.status_code}")
    return response.json().get('enrollment_terms', []) if response.status_code == 200 else []

# Function to fetch all courses from the account based on term
def fetch_courses_by_term(term_id):
    url = f'{BASE_URL}/accounts/1/courses'
    params = {'enrollment_term_id': term_id}
    response = requests.get(url, headers=headers, params=params)
    st.write(f"Fetching courses for term {term_id}: {response.status_code}")
    return response.json() if response.status_code == 200 else []

# Function to fetch assignment groups for a course
def fetch_assignment_groups(course_id):
    url = f'{BASE_URL}/courses/{course_id}/assignment_groups'
    response = requests.get(url, headers=headers)
    st.write(f"Fetching assignment groups for course {course_id}: {response.status_code}")
    return response.json() if response.status_code == 200 else []

# Function to fetch assignments in each group
def fetch_assignments(course_id, group_id):
    url = f'{BASE_URL}/courses/{course_id}/assignment_groups/{group_id}/assignments'
    response = requests.get(url, headers=headers)
    st.write(f"Fetching assignments for group {group_id} in course {course_id}: {response.status_code}")
    return response.json() if response.status_code == 200 else []

# Function to fetch student submissions for an assignment
def fetch_grades(course_id, assignment_id):
    url = f'{BASE_URL}/courses/{course_id}/assignments/{assignment_id}/submissions'
    response = requests.get(url, headers=headers)
    st.write(f"Fetching grades for assignment {assignment_id} in course {course_id}: {response.status_code}")
    return response.json() if response.status_code == 200 else []

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
                grade = submission.get('score', 0)
                grade = grade if grade is not None else 0
                percentage = (grade / assignment_max_score) * 100 if assignment_max_score > 0 else 0

                gradebook.append({
                    'Student ID': student_id,
                    'Assignment Group': group_name,
                    'Group Weight': group_weight,
                    'Assignment Name': assignment_name,
                    'Grade': grade,
                    'Max Score': assignment_max_score,
                    'Percentage': round(percentage, 2)
                })
    
    df = pd.DataFrame(gradebook)
    
    if df.empty:
        st.write("No grades found.")
    else:
        st.write("Gradebook Data:")
        st.write(df)

    return df

# Streamlit display function to show courses and their grades based on term
def display_all_courses_grades():
    # Step 1: Select a term
    terms = fetch_terms()
    if terms:
        term_options = {term['name']: term['id'] for term in terms}
        selected_term = st.selectbox("Select a term:", list(term_options.keys()))
        term_id = term_options[selected_term]
    else:
        st.error("No terms found or access denied.")
        return
    
    # Step 2: Fetch courses for the selected term
    courses = fetch_courses_by_term(term_id)
    st.title(f"Course Grades for Term: {selected_term}")
    
    # Step 3: Display all courses fetched
    for course in courses:
        course_id = course['id']
        course_name = course['name']
        st.header(f"Course: {course_name} (ID: {course_id})")
        
        # Fetch and display the gradebook for each course
        df_gradebook = format_gradebook(course_id)
        st.write(df_gradebook)

# Streamlit app starts here
if __name__ == "__main__":
    display_all_courses_grades()
