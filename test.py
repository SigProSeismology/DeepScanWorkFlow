from selenium import webdriver

import time

driver = webdriver.Chrome(executable_path='/path/to/chromedriver')


# Function to search Google Scholar
def google_scholar_search(query):
    search_box = driver.find_element_by_name('q')
    search_box.clear()
    search_box.send_keys(query)
    search_box.submit()
    time.sleep(2)

# Initialize WebDriver
driver_path = "/usr/bin/chromedriver"  # Update this with your Chromedriver path
driver = webdriver.Chrome(executable_path=driver_path)
driver.get("https://scholar.google.com/")

# Open file and perform searches
with open('/home/shazam/Desktop/lines.txt', 'r') as f:
    for line in f:
        line = line.strip()  # Remove any trailing whitespace
        if line:  # Only search if the line is not empty
            print(f"Searching for: {line}")
            google_scholar_search(line)
            input("Press Enter to continue to the next search...")

# Close the browser
driver.quit()
