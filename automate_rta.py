from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
from pymongo import MongoClient
from datetime import datetime

def parse_fine_data(raw_text):
    """Parse the raw text data into structured format"""
    lines = raw_text.strip().split('\n')
    
    # Extract vehicle info (first line)
    vehicle_info = lines[0] if len(lines) > 0 else ""
    
    # Find date, amount, source
    date_time = ""
    amount = ""
    source = ""
    black_points = ""
    
    for i, line in enumerate(lines):
        if "Date and Time" in line and i + 1 < len(lines):
            date_time = lines[i + 1]
        elif "Amount" in line and i + 1 < len(lines):
            amount = lines[i + 1]
        elif "Source" in line and i + 1 < len(lines):
            source = lines[i + 1]
        elif "Black points" in line and i + 1 < len(lines):
            black_points = lines[i + 1]
    
    return {
        "vehicle_info": vehicle_info,
        "date_time": date_time,
        "amount": amount,
        "source": source,
        "black_points": black_points,
        "created_at": datetime.now()
    }

def save_to_mongodb(fines_data, total_amount):
    """
    Save fines records and total amount to MongoDB
    """
    # MongoDB Configuration
    MONGODB_URI = "mongodb+srv://devxulfiqar:nSISUpLopruL7S8j@mypaperlessoffice.z5g84.mongodb.net/?retryWrites=true&w=majority&appName=mypaperlessoffice"
    DB_NAME = "fleet-management"
    
    try:
        # Connect to MongoDB
        print("\nConnecting to MongoDB...")
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        
        # Collections
        fines_collection = db['rta_fines']
        total_collection = db['rta_total']
        
        # Save individual fines (avoid duplicates)
        saved_count = 0
        duplicate_count = 0
        
        for fine in fines_data:
            # Check if record already exists (based on vehicle info, date_time, and amount)
            existing = fines_collection.find_one({
                "vehicle_info": fine["vehicle_info"],
                "date_time": fine["date_time"],
                "amount": fine["amount"]
            })
            
            if not existing:
                fines_collection.insert_one(fine)
                saved_count += 1
                print(f"Saved fine: {fine['vehicle_info']} - {fine['amount']}")
            else:
                duplicate_count += 1
                print(f"Duplicate found, skipped: {fine['vehicle_info']} - {fine['amount']}")
        
        print(f"\nTotal saved: {saved_count}, Duplicates skipped: {duplicate_count}")
        
        # Update total amount (upsert - update if exists, insert if not)
        total_collection.update_one(
            {"type": "total_fines"},
            {
                "$set": {
                    "total_amount": total_amount,
                    "last_updated": datetime.utcnow()
                }
            },
            upsert=True
        )
        print(f"Total amount updated: {total_amount}")
        
        print("MongoDB operations completed successfully!")
        
    except Exception as e:
        print(f"MongoDB error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

def automate_rta_violations(headless=True):
    """
    Automates the RTA violations website interaction
    Opens the page and clicks on the specified element
    
    Args:
        headless (bool): If True, runs Chrome in headless mode (invisible background mode)
    """
    # Initialize the Chrome driver with options
    chrome_options = webdriver.ChromeOptions()
    
    if headless:
        chrome_options.add_argument('--headless=new')  # Run in background
        chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration
        chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
        chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        chrome_options.add_argument('--window-size=1920,1080')  # Set window size
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Hide automation
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        print("Running in HEADLESS mode (background - no visible browser)")
    else:
        print("Running in NORMAL mode (visible browser)")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Remove webdriver property to avoid detection
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    try:
        # Open the URL
        url = "https://ums.rta.ae/violations/public-fines/fines-search"
        print(f"Opening URL: {url}")
        driver.get(url)
        
        # Wait for the page to load
        print("Waiting for page to load...")
        time.sleep(10)  # Increased wait for headless mode
        
        # CSS Selector for the target element
        css_selector = "#root > div > div > div.container.umsPortal > div > div > div > div > div.slick-slider.slick-initialized > div > div > div:nth-child(4) > div > div > span"
        
        # Wait for the element to be clickable
        print("Waiting for element to be clickable...")
        wait = WebDriverWait(driver, 30)
        element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        
        # Click the element
        print("Clicking the element...")
        element.click()
        print("Element clicked successfully!")
        
        # Wait for the input field to appear
        print("Waiting for traffic file number input field...")
        time.sleep(3)
        
        # Find the input field and enter the traffic file number
        input_field = wait.until(EC.presence_of_element_located((By.ID, "Id_trafficFileNumber")))
        print("Entering traffic file number...")
        input_field.clear()
        input_field.send_keys("51563245")
        print("Traffic file number entered successfully!")
        
        # Click the search button
        print("Clicking search button...")
        search_button = wait.until(EC.element_to_be_clickable((By.ID, "Id_searchBTN")))
        # Scroll to button and use JavaScript click to avoid interception
        driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", search_button)
        print("Search button clicked successfully!")
        
        # Wait for the results page to load
        print("Waiting for results page to load...")
        time.sleep(5)
        
        # Find and fetch text from Id_PayAll element
        print("Finding Id_PayAll element...")
        pay_all_element = wait.until(EC.presence_of_element_located((By.ID, "Id_PayAll")))
        pay_all_text = pay_all_element.text
        print(f"Text from Id_PayAll: {pay_all_text}")
        
        # Find and fetch data from the table row
        print("Finding table data element...")
        table_selector = "#Id_FinesResultTable > div.p-datatable-wrapper > table > tbody > tr:nth-child(1) > td:nth-child(2) > div"
        table_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, table_selector)))
        table_data = table_element.text
        print(f"Row 1 data: {table_data}")
        
        # Find and fetch data from the second table row
        print("\nFinding second table row data...")
        table_selector_2 = "#Id_FinesResultTable > div.p-datatable-wrapper > table > tbody > tr:nth-child(2) > td:nth-child(2) > div"
        table_element_2 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, table_selector_2)))
        table_data_2 = table_element_2.text
        print(f"Row 2 data: {table_data_2}")
        
        # Find and fetch data from the third table row
        print("\nFinding third table row data...")
        table_selector_3 = "#Id_FinesResultTable > div.p-datatable-wrapper > table > tbody > tr:nth-child(3) > td:nth-child(2) > div"
        table_element_3 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, table_selector_3)))
        table_data_3 = table_element_3.text
        print(f"Row 3 data: {table_data_3}")
        
        # Parse and save data to MongoDB
        fines_data = [
            parse_fine_data(table_data),
            parse_fine_data(table_data_2),
            parse_fine_data(table_data_3)
        ]
        
        save_to_mongodb(fines_data, pay_all_text)
        
        # Keep browser open for a few seconds to see the result
        time.sleep(5)
        
    except TimeoutException:
        print("Error: Element not found within the timeout period")
        print("The page structure might have changed or the element takes longer to load")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        # Close the browser
        print("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    automate_rta_violations()
