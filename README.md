# Facebook Page Search Automation

## Project Description

This project is a Python-based automation script that leverages Selenium to log into Facebook, perform search queries, filter results to only include pages, and then process those results by saving URLs and taking screenshots of the pages. The script is multi-threaded, allowing multiple search queries to be executed concurrently.

## Features

- **Automated Login**: Logs into Facebook using cookies or user credentials.
- **Search Execution**: Performs a search based on a query list.
- **Page Filtering**: Filters search results to only include Facebook pages.
- **Screenshot Capture**: Takes screenshots of the pages found in search results.
- **Multi-threading**: Supports concurrent execution of multiple search queries.

## Requirements

- Python 3.x
- Google Chrome Browser
- ChromeDriver (compatible with your Chrome version)
- Selenium

## Installation

1. **Clone the repository**:

```bash
git clone https://github.com/luckystars0612/Facebook-page-search-automation.git
cd Facebook-page-search-automation
```
2. **Set up a virtual environment (optional but recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
3. **Install the required packages:**
```bash
pip install -r requirements.txt
```
4. **Install ChromeDriver:**
- Download ChromeDriver from [here](https://developer.chrome.com/docs/chromedriver/downloads).
- Ensure the downloaded ChromeDriver version matches your installed Google Chrome version.
- Place the chromedriver executable in a directory included in your system's PATH (optional)

## Usage
1. **Prepare the search queries:**
- Create a text file named search_queries.txt in the project directory.
- Add one search query per line in the file.
2. **Run the script:**
```bash
python facesearchauto.py <your_facebook_email> <your_facebook_password>
```
***Example***
```bash
python facesearchauto.py user@example.com mysecurepassword
```
The script will:

- Log into Facebook.
- Perform each search query from search_queries.txt.
- Filter the results to only include pages.
- Save the URLs and take screenshots of the pages found.
- Store the results in the results/YYYY-MM-DD/ directory, where YYYY-MM-DD is the current date.
3.**Results**
- Screenshots and URLs of the identified pages will be stored in the results folder.
- The script will append newly identified URLs to *newphishingpages.txt* (if it does not exist) and exclude those listed in *tookdownpages.txt* **.
## Notes
- **Cookies**: The script attempts to use stored cookies (facebook_cookies.pkl) to bypass the login process. If cookies are invalid or missing, it will proceed with a standard login using the provided email and password.
- **Multi-threading**: The script processes multiple search queries concurrently. Adjust the thread count in the script if needed, based on your system's capabilities.
## Troubleshooting
- **Browser Issues**: Ensure that your Chrome version is up to date and matches the version of ChromeDriver.
- **Slow Performance**: Facebook might throttle your browsing speed if the script is running too quickly. Consider increasing the sleep times in the script if you encounter issues.
- **Login Issues**: If the script fails to log in, try deleting facebook_cookies.pkl and running the script again to force a manual login.

> [!CAUTION]
> There is no clean code, no penetration test provided, this repo is for educational purposes only. Do not use for illegal purposes. I'm never responsible for illegal use. Educational purpose only!
## Support me (optional)
If you find it useful, you can support me with a cup of coffee.
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Y8Y2123O0D)