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

# Function to fetch all terms
def fetch_all_terms():
    url = f'{BASE_URL}/accounts/1/terms'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('enrollment_terms', [])
    return []

# Function to fetch all courses for a specific term
def fetch_courses_for_term(term_id):
    url = f'{BASE_URL}/courses?enrollment_term_id={term_id}'
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

# Function to fetch student names
def fetch_student_name(student_id):
    url = f'{BASE_URL}/users/{student_id}/profile'
    response = requests.get(url, headers=headers)
    return response.json()['name'] if response.status_code == 200 else 'Unknown'

# Function to format gradebook data
def format_gradebook(course_id):
    gradebook = []
    assignment_groups = fetch_assignment_groups(course_id)
    
    for group in assignment_groups:
        group_name = group['name']
        group_weight = group['group_weight']
        
        assignments = fetch_assignments(course_id, group['id'])
        for assignment in assignments:
            assignment_name = assignment['name']
            assignment_max_score = assignment.get('points_possible', 0)  # Handle missing points
            
            grades = fetch_grades(course_id, assignment['id'])
            for submission in grades:
                student_id = submission['user_id']
                student_name = fetch_student_name(student_id)
                grade = submission.get('score', 0) or 0
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
    if not df.empty:
        df = df.groupby(['Student ID', 'Student Name', 'Assignment Group', 'Assignment Name', 'Group Weight']).mean()
    return df

# Streamlit function to display courses and grades for a selected term
def display_courses_by_term():
    st.title("Course Grades by Term")

    # Fetch all terms
    terms = fetch_all_terms()

    if not terms:
        st.error("No terms found or access denied.")
        return

    # Allow the user to select a term
    term_names = {term['id']: term['name'] for term in terms}
    selected_term_id = st.selectbox("Select a Term", options=list(term_names.keys()), format_func=lambda x: term_names[x])

    if selected_term_id:
        courses = fetch_courses_for_term(selected_term_id)
        
        if not courses:
            st.warning(f"No courses found for the term '{term_names[selected_term_id]}'.")
            return

        # Display all courses in the selected term
        for course in courses:
            course_id = course['id']
            course_name = course['name']
            st.header(f"Course: {course_name} (ID: {course_id})")

            # Fetch and display the gradebook for the course
            df_gradebook = format_gradebook(course_id)
            st.write(df_gradebook)

# Streamlit app starts here
if __name__ == "__main__":
    display_courses_by_term()
