import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random
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
time.sleep(5)

# Enter username
username_input = driver.find_element(By.NAME, "username")
username_input.send_keys(username)

# Enter password
password_input = driver.find_element(By.NAME, "password")
password_input.send_keys(password)

# Submit the login form
password_input.send_keys(Keys.RETURN)
time.sleep(5)

# Load Instagram profile URLs from the CSV file
file_path = "/Users/ggsantos/Documents/Data_Python_folder/pandas_projects/Instagram_Data/Insta_Usernames_Cleaned - Insta_Usernames_Cleaned_3.csv.csv"
profile_urls = pd.read_csv(file_path).iloc[:, 0]

# Function to convert follower count (handles K and M abbreviations)
def convert_follower_count(follower_text):
    multiplier = 1
    if "K" in follower_text:
        multiplier = 1000
        follower_text = follower_text.replace("K", "")
    elif "M" in follower_text:
        multiplier = 1000000
        follower_text = follower_text.replace("M", "")
    return int(float(follower_text) * multiplier)

# Define the function to extract data
def extract_data_and_followers(profile_url):
    try:
        driver.get(profile_url)
        time.sleep(random.uniform(3, 7))  # Random delay to avoid rate limits

        # Extract followers count
        try:
            followers_element = driver.find_element(By.XPATH, "//a[contains(@href, '/followers')]/span")
            followers_text = followers_element.get_attribute("title")  # Extract full number
            if followers_text:
                followers_count = int(followers_text.replace(",", ""))
            else:
                followers_text = followers_element.text
                followers_count = convert_follower_count(followers_text)
        except Exception as e:
            followers_count = None
            print(f"Error extracting followers for {profile_url}: {e}")

        # Extract reel data
        try:
            reel_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/reel/')]")
            reel_urls = [reel.get_attribute('href') for reel in reel_elements[:12]]
        except Exception as e:
            reel_urls = []
            print(f"Error extracting reels for {profile_url}: {e}")

        # Pad reel URLs if fewer than 12
        while len(reel_urls) < 12:
            reel_urls.append(None)

        # Return the followers count and reel URLs
        return {
            "Profile URL": profile_url,
            "Followers": followers_count,
            "Reel URLs": reel_urls
        }

    except Exception as e:
        print(f"Error processing {profile_url}: {e}")
        return {
            "Profile URL": profile_url,
            "Followers": None,
            "Reel URLs": []
        }

# Initialize results list
results = []

# Process each profile URL
for i, profile_url in enumerate(profile_urls):
    results.append(extract_data_and_followers(profile_url))
    
    # Save intermediate results every 10 profiles
    if (i + 1) % 10 == 0:
        temp_file = "/Users/ggsantos/Documents/Data_Python_folder/pandas_projects/Instagram_Data/Temp_Profile_Data_With_Followers.csv"
        pd.DataFrame(results).to_csv(temp_file, index=False)
        print(f"Intermediate results saved to {temp_file}")

# Quit the driver
driver.quit()

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Save final results
output_file = "/Users/ggsantos/Documents/Data_Python_folder/pandas_projects/Instagram_Data/Profile_Data_With_Followers.csv"
results_df.to_csv(output_file, index=False)
print(f"Scraping complete. Results saved to {output_file}")