import requests
import pandas as pd

# Replace with your Canvas API token
API_TOKEN = '1941~YfMDLMGz2ZRWRvcWZBG8k7yctAXvfxnGMwCrF3cVJGBzhVKDCvUWDhPeVeDXnaMz'
BASE_URL = 'https://kepler.instructure.com/api/v1'
ACCOUNT_ID = 1  # Assuming you are fetching courses from account 1

# Set headers for authentication
headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

# Fetch all courses for the account
def fetch_courses(account_id):
    url = f'{BASE_URL}/accounts/{account_id}/courses'
    response = requests.get(url, headers=headers)
    
    # Check for errors in the API response
    if response.status_code != 200:
        print(f"Error fetching courses: {response.status_code}, {response.text}")
        return []
    
    courses = response.json()
    
    # Check if any courses were fetched
    if len(courses) == 0:
        print("No courses available or token does not have access to any courses.")
    else:
        print(f"Fetched {len(courses)} courses.")
    
    return courses

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

# Fetch student submissions for an assignment
def fetch_grades(course_id, assignment_id):
    url = f'{BASE_URL}/courses/{course_id}/assignments/{assignment_id}/submissions'
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else []

# Format the gradebook for a specific course
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
    df = df.groupby(['Student ID', 'Assignment Group', 'Assignment Name', 'Group Weight']).mean()
    
    return df

# Example usage: Fetch all courses and display their gradebook
def display_all_courses_grades():
    courses = fetch_courses(ACCOUNT_ID)
    
    if not courses:
        print("No courses found.")
        return
    
    for course in courses:
        course_id = course['id']
        course_name = course['name']
        
        print(f"\nCourse ID: {course_id}, Course Name: {course_name}")
        df_gradebook = format_gradebook(course_id)
        print(df_gradebook)

# Call the function to display grades for all courses
display_all_courses_grades()
