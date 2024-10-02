import requests
import pandas as pd
import streamlit as st
from datetime import datetime

# Replace with your Canvas API token and base URL
API_TOKEN = '1941~FXJZ2tYC2DTWQr923eFTaXy473rK73A4KrYkT3uVy7WeYV9fyJQ4khH4MAGEH3Tf'
BASE_URL = 'https://kepler.instructure.com/api/v1'

# Set headers for authentication
headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

# Function to fetch all courses
def fetch_all_courses():
    courses = []
    url = f'{BASE_URL}/accounts/1/courses?per_page=100'
    
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

# Streamlit display function to show courses and their grades
def display_all_courses_grades():
    courses = fetch_all_courses()
    st.title("Course Grades with Grades")

    # Define the date threshold
    date_threshold = datetime.strptime("2024-05-01", "%Y-%m-%d")

    # Display all courses fetched
    for course in courses:
        course_id = course['id']
        course_name = course['name']
        course_code = course.get('course_code', 'N/A')  # Fetch course code
        start_at = course.get('start_at')

        if start_at:
            try:
                course_start_date = datetime.strptime(start_at, "%Y-%m-%dT%H:%M:%SZ")
                # Only process courses that start after the date threshold
                if course_start_date > date_threshold:
                    # Fetch and display the gradebook
                    df_gradebook = format_gradebook(course_id)
                    
                    # Only display courses that have grades
                    if not df_gradebook.empty:
                        st.header(f"Course: {course_name} (ID: {course_id})")
                        st.write(f"**Course Code:** {course_code}")  # Display course code
                        st.dataframe(df_gradebook)
                    else:
                        st.write(f"No grades found for {course_name}.")
            except ValueError:
                st.error(f"Error parsing start date for course {course_name} (ID: {course_id}).")

# Streamlit app starts here
if __name__ == "__main__":
    display_all_courses_grades()
