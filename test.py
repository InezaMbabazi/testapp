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

# Function to fetch all courses from the account
def fetch_all_courses():
    url = f'{BASE_URL}/accounts/1/courses'
    response = requests.get(url, headers=headers)
    st.write(f"Fetching all courses: {response.status_code}")
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

# Function to fetch student info based on their name
def fetch_students_by_name(name):
    url = f'{BASE_URL}/accounts/1/users'
    params = {'search_term': name}
    response = requests.get(url, headers=headers, params=params)
    st.write(f"Searching for student with name '{name}': {response.status_code}")
    if response.status_code == 200:
        st.write(f"Response: {response.json()}")  # Print out the response for debugging
        return response.json()
    st.error(f"Failed to fetch students for name '{name}'. Status code: {response.status_code}")
    return []

# Function to fetch student names
def fetch_student_name(student_id):
    url = f'{BASE_URL}/users/{student_id}/profile'
    response = requests.get(url, headers=headers)
    return response.json()['name'] if response.status_code == 200 else 'Unknown'

# Function to calculate percentage grades and format data, filtered by student name
def format_gradebook(course_id, student_name):
    gradebook = []
    
    # Fetch student based on name
    students = fetch_students_by_name(student_name)
    
    if not students:
        st.error(f"No students found with name {student_name}")
        return pd.DataFrame()  # Return empty DataFrame
    
    # If multiple students match the name, allow the user to select
    if len(students) > 1:
        student_options = {f"{student['name']} (ID: {student['id']})": student['id'] for student in students}
        selected_student = st.selectbox("Select a student:", list(student_options.keys()))
        student_id = student_options[selected_student]
    else:
        student = students[0]
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
    
    if df.empty:
        st.write(f"No grades found for student {student_name}")
    else:
        st.write("Gradebook Data:")
        st.write(df)

    return df

# Streamlit display function to show courses and their grades based on student name
def display_all_courses_grades():
    student_name = st.text_input("Enter student name:")
    
    if student_name:
        courses = fetch_all_courses()
        st.title("Course Grades by Student Name")

        # Display all courses fetched
        for course in courses:
            course_id = course['id']
            course_name = course['name']
            st.header(f"Course: {course_name} (ID: {course_id})")

            # Fetch and display the gradebook filtered by student name
            df_gradebook = format_gradebook(course_id, student_name)
            st.write(df_gradebook)

# Streamlit app starts here
if __name__ == "__main__":
    display_all_courses_grades()
