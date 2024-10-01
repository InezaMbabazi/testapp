import requests
import pandas as pd
import streamlit as st

# Replace with your Canvas API token
API_TOKEN = '1941~YfMDLMGz2ZRWRvcWZBG8k7yctAXvfxnGMwCrF3cVJGBzhVKDCvUWDhPeVeDXnaMz'
BASE_URL = 'https://kepler.instructure.com/api/v1'
ACCOUNT_ID = 1  # Account ID as per the screenshot

# Set headers for authentication
headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

# Function to fetch all courses in the account
def fetch_all_courses():
    url = f'{BASE_URL}/accounts/{ACCOUNT_ID}/courses'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching courses: {response.status_code}")
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

# Function to format gradebook data for a course
def format_gradebook(course_id):
    gradebook = []
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
                grade = submission.get('score', 0)  # Fetch grade; default to 0 if missing or None
                
                # Ensure grade is not None and handle missing values
                grade = grade if grade is not None else 0
                
                # Calculate percentage for this assignment
                percentage = (grade / assignment_max_score) * 100 if assignment_max_score > 0 else 0

                # Append data for display
                gradebook.append({
                    'Student ID': student_id,
                    'Assignment Group': group_name,
                    'Group Weight': group_weight,
                    'Assignment Name': assignment_name,
                    'Grade': grade,
                    'Max Score': assignment_max_score,
                    'Percentage': round(percentage, 2)
                })
    
    # Create DataFrame and display the gradebook
    df = pd.DataFrame(gradebook)
    
    if not df.empty:
        # Group by student and assignment groups
        df = df.groupby(['Student ID', 'Assignment Group', 'Assignment Name', 'Group Weight']).mean().reset_index()
    return df

# Streamlit app to display the grades for all courses
def display_all_courses_grades():
    st.title("All Courses and Grades")
    
    # Fetch all courses
    courses = fetch_all_courses()

    if courses:
        for course in courses:
            st.subheader(f"Course: {course['name']} (ID: {course['id']})")
            
            # Fetch and display the gradebook for this course
            df_gradebook = format_gradebook(course['id'])
            
            if not df_gradebook.empty:
                st.write(df_gradebook)
            else:
                st.write("No grades available for this course.")
    else:
        st.write("No courses available.")

# Main execution
if __name__ == "__main__":
    display_all_courses_grades()
