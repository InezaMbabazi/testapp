import requests
import pandas as pd
import streamlit as st

# Ensure this token is correct and has the required permissions
API_TOKEN = '1941~YfMDLMGz2ZRWRvcWZBG8k7yctAXvfxnGMwCrF3cVJGBzhVKDCvUWDhPeVeDXnaMz'
BASE_URL = 'https://kepler.instructure.com/api/v1'
COURSE_URL_TEMPLATE = 'https://kepler.instructure.com/courses/{}'

headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

def fetch_all_courses():
    url = f'{BASE_URL}/courses'
    params = {
        'per_page': 100
    }
    courses = []
    
    while url:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            courses_page = response.json()
            courses.extend(courses_page)

            # Check for pagination
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None
        else:
            st.error(f"Error fetching courses: {response.status_code}")
            break

    return courses

def display_courses():
    st.title("Canvas Courses")

    courses = fetch_all_courses()

    if courses:
        course_list = [(course['id'], course['name']) for course in courses]

        df_courses = pd.DataFrame(course_list, columns=['Course ID', 'Course Name'])
        df_courses['Course URL'] = df_courses['Course ID'].apply(lambda x: COURSE_URL_TEMPLATE.format(x))

        st.dataframe(df_courses)

        for index, row in df_courses.iterrows():
            st.write(f"Course Name: {row['Course Name']}, Course URL: {row['Course URL']}")
    else:
        st.write("No courses found or access denied.")

if __name__ == "__main__":
    display_courses()
