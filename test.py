import requests
import pandas as pd
import streamlit as st

# Replace with your actual Canvas API token
API_TOKEN = 'your_canvas_api_token'
BASE_URL = 'https://kepler.instructure.com/api/v1'
COURSE_URL_TEMPLATE = 'https://kepler.instructure.com/courses/{}'

# Set headers for the API request
headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

# Function to fetch all courses
def fetch_all_courses():
    url = f'{BASE_URL}/courses'
    params = {
        'per_page': 100  # Fetch up to 100 courses per request
    }
    courses = []
    
    while url:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            courses_page = response.json()
            courses.extend(courses_page)

            # Check if there's a 'next' link in the response headers for pagination
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None
        else:
            st.error(f"Error fetching courses: {response.status_code}")
            break

    return courses

# Streamlit app to display courses
def display_courses():
    st.title("Canvas Courses")

    # Fetch all courses
    courses = fetch_all_courses()

    if courses:
        # Create a list of tuples with course ID and name
        course_list = [(course['id'], course['name']) for course in courses]

        # Create a DataFrame for display
        df_courses = pd.DataFrame(course_list, columns=['Course ID', 'Course Name'])

        # Add a column with course URLs
        df_courses['Course URL'] = df_courses['Course ID'].apply(lambda x: COURSE_URL_TEMPLATE.format(x))

        # Display the DataFrame
        st.dataframe(df_courses)

        # Optionally, display as a list
        for index, row in df_courses.iterrows():
            st.write(f"Course Name: {row['Course Name']}, Course URL: {row['Course URL']}")
    else:
        st.write("No courses found or access denied.")

# Run the Streamlit app
if __name__ == "__main__":
    display_courses()
