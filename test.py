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
    print(f"Courses API Response: {response.status_code}, {response.text}")  # Print response details
    if response.status_code == 200:
        courses = response.json()
        print(f"Fetched {len(courses)} courses.")
        return courses
    else:
        print(f"Failed to fetch courses. Status code: {response.status_code}")
        return []

# Function to fetch assignment groups for a course
def fetch_assignment_groups(course_id):
    url = f'{BASE_URL}/courses/{course_id}/assignment_groups'
    response = requests.get(url, headers=headers)
    print(f"Assignment Groups API Response for course {course_id}: {response.status_code}, {response.text}")  # Print response
    return response.json() if response.status_code == 200 else []

# Function to fetch assignments in each group
def fetch_assignments(course_id, group_id):
    url = f'{BASE_URL}/courses/{course_id}/assignment_groups/{group_id}/assignments'
    response = requests.get(url, headers=headers)
    print(f"Assignments API Response for group {group_id}: {response.status_code}, {response.text}")  # Print response
    return response.json() if response.status_code == 200 else []

# Function to fetch student submissions for an assignment
def fetch_grades(course_id, assignment_id):
    url = f'{BASE_URL}/courses/{course_id}/assignments/{assignment_id}/submissions'
    response = requests.get(url, headers=headers)
    print(f"Grades API Response for assignment {assignment_id}: {response.status_code}, {response.text}")  # Print response
    return response.json() if response.status_code == 200 else []

# Function to fetch student names
def fetch_student_name(user_id):
    url = f'{BASE_URL}/users/{user_id}/profile'
    response = requests.get(url, headers=headers)
    print(f"Student Name API Response for user {user_id}: {response.status_code}, {response.text}")  # Print response
    return response.json()['name'] if response.status_code == 200 else 'Unknown'

# Function to calculate percentage grades and format data
def format_gradebook():
    gradebook = []
    courses = fetch_courses()  # Fetch all courses for the user
    
    if len(courses) == 0:
        print("No courses fetched. Exiting.")
        return pd.DataFrame()  # Return empty DataFrame if no courses found
    
    # For each course, fetch the course name and its assignment groups
    for course in courses:
        course_id = course['id']
        course_name = course['name']
        print(f"Processing course: {course_name} (ID: {course_id})")
        
        assignment_groups = fetch_assignment_groups(course_id)
        if len(assignment_groups) == 0:
            print(f"No assignment groups found for course: {course_name}.")
            continue
        
        # For each assignment group, fetch assignments and their weights
        for group in assignment_groups:
            group_name = group['name']
            group_weight = group['group_weight']
            
            assignments = fetch_assignments(course_id, group['id'])
            if len(assignments) == 0:
                print(f"No assignments found in group: {group_name}.")
                continue
            
            for assignment in assignments:
                assignment_name = assignment['name']
                assignment_max_score = assignment['points_possible']

                # Fetch student grades for each assignment
                grades = fetch_grades(course_id, assignment['id'])
                if len(grades) == 0:
                    print(f"No grades found for assignment: {assignment_name}.")
                    continue
                
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

# Check if any data was fetched
if df_gradebook.empty:
    print("No gradebook data available.")
else:
    # Display the DataFrame in Streamlit
    st.title("Canvas Gradebook")
    st.dataframe(df_gradebook)

    # Save to CSV
    csv_file_path = 'gradeapi.csv'
    df_gradebook.to_csv(csv_file_path, index=False)

    st.write(f"Gradebook saved to: {csv_file_path}")
