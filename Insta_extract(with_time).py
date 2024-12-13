import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
import pytz

# Path to your ChromeDriver
driver_path = "/opt/anaconda3/bin/chromedriver"

# Start Selenium WebDriver using Service
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# Instagram Login Credentials
username = "goldengoosesaintso"
password = "garyoakpoke123"

# Open Instagram login page
driver.get("https://www.instagram.com/accounts/login/")
time.sleep(5)  # Wait for the login page to load

# Enter username
username_input = driver.find_element(By.NAME, "username")
username_input.send_keys(username)

# Enter password
password_input = driver.find_element(By.NAME, "password")
password_input.send_keys(password)

# Submit the login form
password_input.send_keys(Keys.RETURN)
time.sleep(5)  # Wait for the main page to load after login

# Initialize results list
results = []

# Load Instagram profile URLs from the CSV file
#file_path = "/Users/ggsantos/Documents/Data_Python_folder/pandas_projects/Instagram_Data/Instagram_data_1 - Insta_Usernames_Cleaned.csv.csv"
#file_path = "/Users/ggsantos/Documents/Data_Python_folder/pandas_projects/Instagram_Data/Missing_Data_1.75 - Sheet1.csv"
#file_path = "/Users/ggsantos/Documents/Data_Python_folder/pandas_projects/Instagram_Data/Missing_Data_1.75 - Sheet1 - Missing_Data_1.75 - Sheet1.csv.csv"
file_path = "/Users/ggsantos/Documents/Data_Python_folder/pandas_projects/Missing_Data_2 - Missing_Data_1.75 - Sheet1.csv"
#file_path = "/Users/ggsantos/Documents/Data_Python_folder/pandas_projects/Instagram_Data/Insta_Data_3 - Sheet1.csv"
profile_urls = pd.read_csv(file_path).iloc[:, 0]  # First column contains profile URLs


# Function to extract data for a reel
def extract_reel_data(reel_url):
    try:
        driver.get(reel_url)
        time.sleep(3)

        # Extract likes
        try:
            likes_element = driver.find_element(By.XPATH, "//span[contains(text(), 'likes')]")
            likes_text = likes_element.text
            likes = int(likes_text.split()[0].replace(",", ""))
        except Exception:
            likes = None

        # Extract comments and replies
        try:
            usernames = driver.find_elements(By.XPATH, "//a[@role='link' and contains(@href, '/')]")
            comments = len(usernames)

            reply_elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'View replies')]")
            replies = sum([int(reply.text.split('(')[1].split(')')[0]) for reply in reply_elements])

            raw_replies = comments + replies
        except Exception:
            comments, replies, raw_replies = None, None, None

        # Extract video length
        try:
            video_element = driver.find_element(By.TAG_NAME, "video")
            video_length = driver.execute_script("return arguments[0].duration;", video_element)
        except Exception:
            video_length = None

        # Extract date and time, and convert to EST
        try:
            time_element = driver.find_element(By.XPATH, "//time")
            datetime_value = time_element.get_attribute("datetime")
            dt_utc = datetime.fromisoformat(datetime_value.replace("Z", "+00:00"))
            est = pytz.timezone("US/Eastern")
            dt_est = dt_utc.astimezone(est)
            post_time_est = dt_est.strftime("%H:%M:%S")
            month = dt_est.strftime("%B")
            day_of_month = dt_est.day
            year = dt_est.year
            cumulative_date = dt_est.strftime("%Y-%m-%d")
            day_of_week = dt_est.strftime("%A")
        except Exception:
            post_time_est, month, day_of_month, year, cumulative_date, day_of_week = (None, None, None, None, None, None)

        return (likes, comments, replies, raw_replies, video_length, post_time_est, 
                month, day_of_month, year, cumulative_date, day_of_week)
    except Exception as e:
        print(f"Failed to extract reel data for {reel_url}: {e}")
        return (None, None, None, None, None, None, None, None, None, None, None)

# Process profiles and reels
for profile_url in profile_urls:
    try:
        driver.get(profile_url)
        time.sleep(5)

        # Find all reel elements on the first page
        reel_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/reel/')]")
        reel_urls = [reel.get_attribute('href') for reel in reel_elements[:12]]

        # Ensure we always have 12 URLs, filling missing with placeholders
        while len(reel_urls) < 12:
            reel_urls.append(None)

        # Process each reel URL
        for index, reel_url in enumerate(reel_urls):
            if reel_url is not None:
                data = extract_reel_data(reel_url)
            else:
                data = (None, None, None, None, None, None, None, None, None, None, None)

            (likes, comments, replies, raw_replies, video_length, post_time_est,
             month, day_of_month, year, cumulative_date, day_of_week) = data

            results.append({
                "Profile URL": profile_url,
                "Post ID": reel_url.split('/')[-2] if reel_url else None,
                "Reel URL": reel_url,
                "Likes": likes,
                "Comments": comments,
                "Replies": replies,
                "Raw Replies": raw_replies,
                "Video Length (seconds)": video_length,
                "Post Time (EST)": post_time_est,
                "Month": month,
                "Day of Month": day_of_month,
                "Year": year,
                "Cumulative Date": cumulative_date,
                "Day of Week": day_of_week
            })
    except Exception as e:
        print(f"Failed for Profile URL: {profile_url}, Error: {e}")

# Quit the driver
driver.quit()

# Save results
results_df = pd.DataFrame(results)
output_file = "/Users/ggsantos/Documents/Data_Python_folder/pandas_projects/Instagram_Data/Insta_Missing_from_First_12.csv"
results_df.to_csv(output_file, index=False)
print(f"Scraping complete. Results saved to {output_file}")