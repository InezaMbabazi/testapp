import requests
import pandas as pd

# Set up your Canvas API token and base URL
API_TOKEN = '1941~YfMDLMGz2ZRWRvcWZBG8k7yctAXvfxnGMwCrF3cVJGBzhVKDCvUWDhPeVeDXnaMz'
BASE_URL = 'https://kepler.instructure.com/api/v1'

# Define headers for authorization
headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

# Function to fetch all courses using pagination
def fetch_all_courses():
    url = f'{BASE_URL}/courses'
    params = {
        'per_page': 100  # Number of courses per page
    }
    courses = []
    
    while url:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            # Add current page courses to the list
            courses.extend(response.json())
            
            # Check if there's a next page
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None  # Stop if no more pages
        else:
            print(f"Error fetching courses: {response.status_code}")
            break
    
    return courses

# Fetch all courses and store them in a DataFrame
def fetch_courses_to_dataframe():
    courses = fetch_all_courses()
    
    if courses:
        # Convert the courses list to a pandas DataFrame
        df = pd.DataFrame(courses)
        return df
    else:
        print("No courses found.")
        return pd.DataFrame()

# Main execution
if __name__ == "__main__":
    df_courses = fetch_courses_to_dataframe()
    
    # Print the DataFrame or display it using Streamlit or other tools
    print(df_courses)
