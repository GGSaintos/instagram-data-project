import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Path to your ChromeDriver
driver_path = "/opt/anaconda3/bin/chromedriver"

# Start Selenium WebDriver using Service
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# Instagram Login Credentials
username = "username"
password = "password"

# Open Instagram login page
driver.get("https://www.instagram.com/accounts/login/")
time.sleep(5)

# Enter username and password
driver.find_element(By.NAME, "username").send_keys(username)
driver.find_element(By.NAME, "password").send_keys(password)
driver.find_element(By.NAME, "password").submit()
time.sleep(5)

# Load profile URLs from the CSV file
file_path = "/Users/ggsantos/Documents/Data_Python_folder/pandas_projects/Instagram_Data/Missing_Data_1.90 - Missing_Data_1.75 - Sheet1.csv.csv"
profile_urls = pd.read_csv(file_path).iloc[:, 0].tolist()  # Convert the first column to a list

# Loop through each profile URL
view_counts = []

for profile_url in profile_urls:
    try:
        print(f"Processing profile: {profile_url}")
        driver.get(profile_url)  # Navigate to the profile URL
        time.sleep(5)

        # Extract the view counts for the first 12 reels
        for i in range(1, 13):  # Loop through the first 12 reels
            try:
                # Locate the nth reel's parent div
                reel = driver.find_element(By.XPATH, f"(//div[contains(@class, '_aajy')])[{i}]")

                # Locate the span containing the view count
                view_count_span = reel.find_element(By.XPATH, ".//span[contains(@class, 'xdj266r')]")
                view_count_text = view_count_span.text

                # Parse the view count
                if "k" in view_count_text.lower():
                    views = int(float(view_count_text.lower().replace("k", "")) * 1000)
                elif "m" in view_count_text.lower():
                    views = int(float(view_count_text.lower().replace("m", "")) * 1000000)
                else:
                    views = int(view_count_text.replace(",", "").strip())

                print(f"Reel {i} Views: {views}")
                view_counts.append({"Profile URL": profile_url, "Reel Number": i, "View Count": views})

            except Exception as e:
                print(f"Error processing reel {i} for profile {profile_url}: {e}")
                view_counts.append({"Profile URL": profile_url, "Reel Number": i, "View Count": None})

    except Exception as e:
        print(f"Error processing profile {profile_url}: {e}")

# Create a DataFrame and save the results
df = pd.DataFrame(view_counts)

# Save to CSV
output_filepath = "/Users/ggsantos/Documents/Data_Python_Folder/Pandas_Projects/Insta_View_Counts_20.csv"
df.to_csv(output_filepath, index=False)
print(f"Data saved to {output_filepath}")

# Quit the driver
driver.quit()
