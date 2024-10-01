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
    url = f'{BASE_URL}/terms'
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else []

# Function to fetch courses for a specific term
def fetch_courses_by_term(term_id):
    courses = []
    url = f'{BASE_URL}/terms/{term_id}/courses?per_page=100'
    
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            courses_page = response.json()
            courses.extend(courses_page)
            # Handle pagination if next page exists
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None
        else:
            st.error(f"Error fetching courses: {response.status_code}")
            break
    return courses

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
    grades = []
    url = f'{BASE_URL}/courses/{course_id}/assignments/{assignment_id}/submissions?per_page=100'

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            grades_page = response.json()
            grades.extend(grades_page)
            # Handle pagination
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None
        else:
            st.error(f"Error fetching grades: {response.status_code}")
            break

    return grades

# Function to fetch student names
def fetch_student_name(student_id):
    url = f'{BASE_URL}/users/{student_id}/profile'
    response = requests.get(url, headers=headers)
    return response.json().get('name', 'Unknown') if response.status_code == 200 else 'Unknown'

# Function to calculate percentage grades and format data
def format_gradebook(course_id):
    gradebook = []
    assignment_groups = fetch_assignment_groups(course_id)
    
    for group in assignment_groups:
        group_name = group['name']
        group_weight = group.get('group_weight', 0)  # Handle missing group weight

        assignments = fetch_assignments(course_id, group['id'])
        for assignment in assignments:
            assignment_name = assignment['name']
            assignment_max_score = assignment.get('points_possible', 0)  # Default to 0 if not present

            grades = fetch_grades(course_id, assignment['id'])
            for submission in grades:
                student_id = submission['user_id']
                student_name = fetch_student_name(student_id)  # Fetch student name
                grade = submission.get('score', 0)  # Handle missing grades

                # Ensure grades are numeric
                grade = float(grade) if grade is not None else 0
                assignment_max_score = float(assignment_max_score) if assignment_max_score is not None else 0

                # Calculate percentage
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
        # Group by student and assignment group
        df = df.groupby(['Student ID', 'Student Name', 'Assignment Group', 'Assignment Name', 'Group Weight']).mean().reset_index()
    
    return df

# Streamlit display function to show courses and their grades for a selected term
def display_courses_grades_for_term():
    terms = fetch_all_terms()
    term_options = {term['name']: term['id'] for term in terms}
    
    # Add a dropdown for selecting a term
    selected_term = st.selectbox("Select a Term", list(term_options.keys()))

    if selected_term:
        term_id = term_options[selected_term]
        courses = fetch_courses_by_term(term_id)
        st.title(f"Course Grades for Term: {selected_term}")

        # Display all courses fetched
        for course in courses:
            course_id = course['id']
            course_name = course['name']
            course_code = course.get('course_code', 'N/A')  # Fetch course code

            # Fetch and display the gradebook
            df_gradebook = format_gradebook(course_id)
            
            # Only display courses that have grades
            if not df_gradebook.empty:
                st.header(f"Course: {course_name} (ID: {course_id})")
                st.write(f"**Course Code:** {course_code}")  # Display course code
                st.dataframe(df_gradebook)
            else:
                st.write(f"No grades found for {course_name}.")

# Streamlit app starts here
if __name__ == "__main__":
    display_courses_grades_for_term()
