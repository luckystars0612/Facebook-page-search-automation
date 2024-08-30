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
    """Save a URL to a file."""
    try:
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
    
    date_folder = datetime.now().strftime('%Y-%m-%d')
    os.makedirs(f"results/{date_folder}", exist_ok=True)

    results_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Search results']"))
    )
    
    articles = results_container.find_elements(By.XPATH, ".//div[@role='article']")
    
    for i, article in enumerate(articles):
        try:
            link = article.find_element(By.XPATH, ".//a[@href]")
            page_url = link.get_attribute("href")
            
            if any(url in page_url for url in tookdown_pagelist) or any(url_ in page_url for url_ in newphishing_pagelist):
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
    chrome_driver_path = "C:/chromedriver-win64/chromedriver.exe"  # Replace with your actual path
    cookies_file_path = "facebook_cookies.pkl"

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://www.facebook.com")
        time.sleep(3)

        load_cookies(driver, cookies_file_path)
        driver.refresh()
        time.sleep(5)

        try:
            login_button_present = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[@name='login']"))
            )
        except:
            login_button_present = False
        
        if login_button_present:
            print("Cookies did not work, proceeding with username and password login.")
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

def main() -> None:
    """Main function to execute the search queries in separate threads."""
    if len(sys.argv) != 3:
        print("Usage: python script.py <email> <password>")
        sys.exit(1)

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

if __name__ == "__main__":
    main()
