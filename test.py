import requests
import pandas as pd
import streamlit as st
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

# Replace with your Canvas API token and base URL
API_TOKEN = 'YOUR_API_TOKEN'
BASE_URL = 'https://kepler.instructure.com/api/v1'

# Set headers for authentication
headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

# Cache to store student names to reduce API calls
student_name_cache = {}

# Function to fetch all courses
def fetch_all_courses():
    courses = []
    url = f'{BASE_URL}/accounts/1/courses?per_page=100'
    
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            courses_page = response.json()
            courses.extend(courses_page)
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
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None
        else:
            st.error(f"Error fetching grades: {response.status_code}")
            break

    return grades

# Function to fetch student names (with caching)
def fetch_student_name(student_id):
    if student_id in student_name_cache:
        return student_name_cache[student_id]
    
    url = f'{BASE_URL}/users/{student_id}/profile'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        name = response.json().get('name', 'Unknown')
        student_name_cache[student_id] = name
        return name
    else:
        return 'Unknown'

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
                student_name = fetch_student_name(student_id)  # Fetch student name with caching
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

# Function to filter courses based on the number of students
def filter_courses_by_student_count(courses):
    valid_courses = []

    # Using ThreadPoolExecutor to speed up fetching data for multiple courses
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_course = {executor.submit(format_gradebook, course['id']): course for course in courses}

        for future in future_to_course:
            course = future_to_course[future]
            course_id = course['id']
            course_name = course['name']

            try:
                df_gradebook = future.result()  # Get gradebook for the course
                if not df_gradebook.empty:
                    # Count unique students in the gradebook
                    student_count = df_gradebook['Student ID'].nunique()

                    # Only keep courses with more than 2 students
                    if student_count > 2:
                        valid_courses.append(course)
            except Exception as e:
                st.error(f"Error processing course {course_name}: {e}")

    return valid_courses

# Streamlit display function to show grades for selected course
def display_course_grades():
    # Fetch all courses
    courses = fetch_all_courses()

    # Filter courses with more than 2 students
    valid_courses = filter_courses_by_student_count(courses)

    st.title("Select a Course to View Grades")

    if not valid_courses:
        st.write("No courses with more than 2 participants found.")
        return

    # Display course names in a dropdown
    course_options = {course['name']: course['id'] for course in valid_courses}
    selected_course_name = st.selectbox("Choose a course", list(course_options.keys()))
    
    # Get the selected course ID
    selected_course_id = course_options[selected_course_name]

    # Fetch and display the gradebook for the selected course
    df_gradebook = format_gradebook(selected_course_id)
    
    # Only display courses that have grades
    if not df_gradebook.empty:
        st.header(f"Course: {selected_course_name} (ID: {selected_course_id})")
        st.dataframe(df_gradebook)
    else:
        st.write(f"No grades found for {selected_course_name}.")

# Streamlit app starts here
if __name__ == "__main__":
    display_course_grades()
