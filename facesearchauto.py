from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import re
import os
import sys
import threading
from datetime import datetime
from threading import Lock
from PIL import Image
import keyboard
import matplotlib.pyplot as plt

# Initialize a global lock object
file_write_lock = Lock()
#Initiate current datetime for searching
date_folder = datetime.now().strftime('%Y-%m-%d')

def save_cookies(driver: webdriver.Chrome, file_path: str) -> None:
    """Save cookies to a file."""
    cookies = driver.get_cookies()
    with open(file_path, 'wb') as file:
        pickle.dump(cookies, file)

def load_cookies(driver: webdriver.Chrome, file_path: str) -> None:
    """Load cookies from a file."""
    try:
        with open(file_path, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
    except FileNotFoundError:
        print(f"No cookies found at {file_path}")

def scroll_to_load_all_results(driver: webdriver.Chrome) -> None:
    """Scroll down the page to load all results."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def click_see_more_buttons(driver: webdriver.Chrome) -> None:
    """Click on 'See More' buttons to reveal additional content."""
    while True:
        try:
            see_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'See More') or contains(text(), 'More')]"))
            )
            see_more_button.click()
            time.sleep(2)
        except Exception as e:
            print("No more 'See More' buttons found or error occurred:", e)
            break

def filter_pages(driver: webdriver.Chrome) -> bool:
    """Apply the 'Pages' filter to the search results."""
    try:
        pages_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Pages')]"))
        )
        pages_filter.click()
        time.sleep(5)

        scroll_to_load_all_results(driver)
        click_see_more_buttons(driver)
        
        return True
    except Exception as e:
        print("Error filtering pages or applying filter:", e)
        return False

def save_url_to_file(path: str, url: str, mode: str) -> None:
    """ 
        Save a URL to a file in a thread-safe way.
    """
    try:
        with file_write_lock: # Acquire the lock before writing to the file
            with open(path, mode, encoding='utf-8') as f:
                f.write(url + '\n')
    except Exception as e:
        print(e)

def read_url_from_file(file_path: str) -> list[str]:
    """Read URLs from a file and return them as a list."""
    urlist = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            urlist = [line.strip() for line in file]
    except Exception as e:
        print(e)
    return urlist

def process_search_results(driver: webdriver.Chrome) -> None:
    """Process the search results and take screenshots of pages."""
    tookdown_pagelist = read_url_from_file('tookdownpages.txt')
    newphishing_pagelist = read_url_from_file('newphishingpages.txt')
    os.makedirs(f"results/{date_folder}", exist_ok=True)

    results_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Search results']"))
    )
    
    articles = results_container.find_elements(By.XPATH, ".//div[@role='article']")
    print(f"Articles number : {len(articles)}")

    for i, article in enumerate(articles):
        try:
            link = article.find_element(By.XPATH, ".//a[@href]")
            page_url = link.get_attribute("href")
            
            if any(url in page_url for url in tookdown_pagelist) or any(url_ in page_url for url_ in newphishing_pagelist):
                print("Duplicate page found: "+ page_url)
                continue

            save_url_to_file('newphishingpages.txt', page_url, 'a')
            file_name = re.sub(r'[\\/*?:"<>|]', "_", page_url.split("&", 1)[0])
            print(f"Page URL: {page_url}")

            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(page_url)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='main']"))
            )

            save_url_to_file(f"results/{date_folder}/newphishingpage.txt", page_url, 'a')
            driver.save_screenshot(f"results/{date_folder}/{file_name}.png")

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except Exception as e:
            print(f"Error processing article: {e}")

def perform_search(email: str, password: str, search_query: str) -> None:
    """Perform a search on Facebook and process the results."""
    chrome_driver_path = "D:/chromedriver-win64/chromedriver.exe"  # Replace with your actual chrome driver path
    cookies_file_path = "facebook_cookies.pkl"

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://www.facebook.com")
        time.sleep(1)

        load_cookies(driver, cookies_file_path)
        driver.refresh()
        time.sleep(1)

        try:
            login_button_present = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[@name='login']"))
            )
        except:
            login_button_present = False
        
        if login_button_present:
            print("Cookies did not work, proceeding with username and password login.")
            if not email or password:
                print("Both cookies and credentials are not provided")
                sys.exit(1)
            email_input = driver.find_element(By.ID, "email")
            password_input = driver.find_element(By.ID, "pass")

            email_input.send_keys(email)
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)

            save_cookies(driver, cookies_file_path)

    except Exception as e:
        print(f"Error during login: {e}")
        driver.quit()
        return

    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='search']"))
    )
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)

    if filter_pages(driver):
        process_search_results(driver)

    driver.quit()

def search() -> None:
    """Main function to execute the search queries in separate threads."""
    if len(sys.argv) != 3:
        if not os.path.exists('facebook_cookies.pkl'):
            print("Usage: python script.py <email> <password>")
            sys.exit(1)
        else:
            email = None
            password = None
    else:
        email = sys.argv[1]
        password = sys.argv[2]

    search_queries = []
    try:
        with open('search_queries.txt', 'r', encoding='utf-8') as f:
            search_queries = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("search_queries.txt not found")
        sys.exit(1)

    threads = []
    for query in search_queries:
        thread = threading.Thread(target=perform_search, args=(email, password, query))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

# Initial URL load
def load_urls(url_file_path):
    with open(url_file_path, 'r') as f:
        return f.readlines()
    
# Create a dictionary to map images to their URLs using your filename processing regex
def build_url_map(urls):
    url_map = {}
    for url in urls:
        image_name = re.sub(r'[\\/*?:"<>|]', "_", url.strip()) + '.png'
        url_map[image_name] = url.strip()
    return url_map

def manually_check() -> None:
    # Paths
    image_folder = f'results/{date_folder}'
    url_file_path = f'results/{date_folder}/newphishingpage.txt'

    # Read the URLs
    urls = read_url_from_file(url_file_path)

    # Create a dictionary to map images to their URLs (replacing special characters)
    url_map = build_url_map(urls)

    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)

        # Proceed if the file is in the URL map or skip if it's not an image
        if not image_name.endswith('.png'):
            continue

        try:
            # Open the image
            img = Image.open(image_path)
            plt.imshow(img)
            plt.axis('off')
            plt.draw()
            plt.pause(0.1)
            # Wait for 'r' or 'p' keystroke
            print(f"Viewing '{image_name}'. Press 'r' to remove or 'p' to proceed to the next image.")
            while True:
                if keyboard.is_pressed('r'):
                    os.remove(image_path)
                    print(f"Removed image: {image_path}")

                    # Remove URL if associated with the image
                    if image_name in url_map:
                        with open(url_file_path, 'w') as f:
                            urls = [url for url in urls if url.strip() != url_map[image_name]]
                            f.writelines(urls)
                        print(f"Removed URL: {url_map[image_name]}")

                    # Update URL map after deletion
                    urls = load_urls()
                    url_map = build_url_map(urls)
                    break  # Move to next image

                elif keyboard.is_pressed('p'):
                    print(f"Skipped image: {image_name}")
                    break  # Move to the next image
            plt.close()
        except Exception as e:
            print(f"Error opening image '{image_name}': {e}")

    print("All images processed.")

if __name__ == "__main__":
    #search()
    manually_check()
