import requests
import pandas as pd
import streamlit as st

# Your trusty API token and Canvas base URL
API_TOKEN = '1941~YfMDLMGz2ZRWRvcWZBG8k7yctAXvfxnGMwCrF3cVJGBzhVKDCvUWDhPeVeDXnaMz'
BASE_URL = 'https://kepler.instructure.com/api/v1'

# Setting up the authentication headers
headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

# Fetch all courses for the selected term
def fetch_all_courses(term_id):
    url = f'{BASE_URL}/accounts/1/courses?enrollment_term_id={term_id}'
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else []

# Fetch all terms so we can filter courses by term
def fetch_all_terms():
    url = f'{BASE_URL}/accounts/1/terms'
    response = requests.get(url, headers=headers)
    return response.json()['enrollment_terms'] if response.status_code == 200 else []

# Fetch assignment groups for a course
def fetch_assignment_groups(course_id):
    url = f'{BASE_URL}/courses/{course_id}/assignment_groups'
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else []

# Fetch assignments in each group
def fetch_assignments(course_id, group_id):
    url = f'{BASE_URL}/courses/{course_id}/assignment_groups/{group_id}/assignments'
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else []

# Fetch student submissions (grades) for an assignment
def fetch_grades(course_id, assignment_id):
    url = f'{BASE_URL}/courses/{course_id}/assignments/{assignment_id}/submissions'
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else []

# Fetch student names
def fetch_student_name(student_id):
    url = f'{BASE_URL}/users/{student_id}/profile'
    response = requests.get(url, headers=headers)
    return response.json()['name'] if response.status_code == 200 else 'Unknown'

# Format the gradebook data
# Format the gradebook data
def format_gradebook(course_id):
    gradebook = []
    assignment_groups = fetch_assignment_groups(course_id)
    
    for group in assignment_groups:
        group_name = group['name']
        group_weight = group['group_weight']
        
        assignments = fetch_assignments(course_id, group['id'])
        for assignment in assignments:
            assignment_name = assignment['name']
            assignment_max_score = assignment.get('points_possible', 0)  # Default to 0 if missing or None

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


# Streamlit display function to show courses and their grades
def display_all_courses_grades():
    # Fetch all terms first
    terms = fetch_all_terms()
    
    if terms:
        term_options = {term['name']: term['id'] for term in terms}
        selected_term = st.selectbox("Select a Term", list(term_options.keys()))
        
        if selected_term:
            term_id = term_options[selected_term]
            courses = fetch_all_courses(term_id)
            
            # Display all courses fetched for the term
            if courses:
                st.title(f"Course Grades for Term: {selected_term}")

                for course in courses:
                    course_id = course['id']
                    course_name = course['name']
                    st.header(f"Course: {course_name} (ID: {course_id})")

                    # Fetch and display the gradebook for this course
                    df_gradebook = format_gradebook(course_id)
                    st.write(df_gradebook)
            else:
                st.write("No courses found for this term.")
    else:
        st.write("No terms found.")

# Streamlit app starts here
if __name__ == "__main__":
    display_all_courses_grades()
