import requests
import pandas as pd
import streamlit as st

# Replace with your Canvas API token
API_TOKEN = '1941~YfMDLMGz2ZRWRvcWZBG8k7yctAXvfxnGMwCrF3cVJGBzhVKDCvUWDhPeVeDXnaMz'
BASE_URL = 'https://kepler.instructure.com/api/v1'

# Set headers for authentication
headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

# Function to fetch all courses for the user
def fetch_courses():
    url = f'{BASE_URL}/courses'
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
def fetch_student_name(user_id):
    url = f'{BASE_URL}/users/{user_id}/profile'
    response = requests.get(url, headers=headers)
    return response.json()['name'] if response.status_code == 200 else 'Unknown'

# Function to calculate percentage grades and format data
def format_gradebook():
    gradebook = []
    courses = fetch_courses()  # Fetch all courses for the user
    
    # For each course, fetch the course name and its assignment groups
    for course in courses:
        course_id = course['id']
        course_name = course['name']
        
        assignment_groups = fetch_assignment_groups(course_id)
        
        # For each assignment group, fetch assignments and their weights
        for group in assignment_groups:
            group_name = group['name']
            group_weight = group['group_weight']
            
            assignments = fetch_assignments(course_id, group['id'])
            for assignment in assignments:
                assignment_name = assignment['name']
                assignment_max_score = assignment['points_possible']

                # Fetch student grades for each assignment
                grades = fetch_grades(course_id, assignment['id'])
                for submission in grades:
                    student_id = submission['user_id']
                    student_name = fetch_student_name(student_id)  # Fetch the student's name
                    grade = submission.get('score', 0)  # Fetch grade; default to 0 if missing or None

                    # Ensure grade is not None and handle missing values
                    grade = grade if grade is not None else 0

                    # Calculate percentage for this assignment
                    percentage = (grade / assignment_max_score) * 100 if assignment_max_score > 0 else 0

                    # Append data for display
                    gradebook.append({
                        'Course Name': course_name,  # Add the course name here
                        'Student ID': student_id,
                        'Student Name': student_name,
                        'Assignment Group': group_name,
                        'Group Weight': group_weight,
                        'Assignment Name': assignment_name,
                        'Grade': grade,
                        'Max Score': assignment_max_score,
                        'Percentage': round(percentage, 2)
                    })

    # Create DataFrame and display the gradebook
    df = pd.DataFrame(gradebook)
    
    return df

# Example Usage
df_gradebook = format_gradebook()

# Save the DataFrame to CSV and display in Streamlit
st.title("Canvas Gradebook")

# Display the DataFrame
st.dataframe(df_gradebook)

# Save to CSV
csv_file_path = 'gradeapi.csv'
df_gradebook.to_csv(csv_file_path, index=False)

st.write(f"Gradebook saved to: {csv_file_path}")
