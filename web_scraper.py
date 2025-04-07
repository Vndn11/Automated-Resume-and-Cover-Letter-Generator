import time
import os # Add os import if not already there
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException # Import exceptions
from bs4 import BeautifulSoup


def setup_driver():
    """Sets up the Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Run in background without opening window
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36") # Mimic real browser
    
    # Use webdriver-manager to automatically handle driver download/update
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(10) # Implicit wait for elements
        return driver
    except Exception as e:
        print(f"Error setting up WebDriver: {e}")
        print("Please ensure Google Chrome is installed and accessible.")
        return None

def login_to_jobright(driver, username, password, login_url="https://jobright.ai/?login=true"): # Adjust URL if needed!
    """Logs into Jobright.ai."""
    print(f"Attempting to log into Jobright.ai at: {login_url}")
    try:
        driver.get(login_url)

        # --- !!! IMPORTANT: Inspect Jobright.ai login page for correct selectors !!! ---
        # These selectors are GUESSES and WILL likely need adjustment.
        email_selector = 'input[type="text"]' # Example: Find input with type=email
        password_selector = 'input[type="password"]' # Example: Find input with type=password
        
        login_button_selector = 'button[class="ant-btn css-1o9vv16 ant-btn-primary ant-btn-block index_sign-in-button__jjge4"]' # Example: Find button with type=submit
        # It's better to use more specific IDs or names if available, e.g., "#email-input", "button[name='login']"

        # Wait for the email field to be present
        email_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, email_selector))
        )
        password_field = driver.find_element(By.CSS_SELECTOR, password_selector)
        time.sleep(1)
        login_button = driver.find_element(By.CSS_SELECTOR, login_button_selector)
         # Let the scroll settle

        print("Entering credentials...")
        email_field.send_keys(username)
        time.sleep(0.5) # Small delay
        password_field.send_keys(password)
        time.sleep(1)
        print("Clicking login button...")
        login_button.click()

        # --- Verification: Wait for an element that appears *after* login ---
        # Example: Wait for a dashboard element or user profile link. Adjust selector!
        post_login_indicator_selector = "div[class*='index_jobs-page']" # GUESS - Find a reliable element on the post-login page
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, post_login_indicator_selector))
        )
        print("Login appears successful.")
        return True

    except TimeoutException:
        print("Error: Timed out waiting for login elements or post-login indicator.")
        print("Check login URL, selectors, and if the site loaded correctly.")
        return False
    except NoSuchElementException as e:
        print(f"Error: Could not find a login element: {e}")
        print("Check the CSS selectors for email, password, or login button.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during login: {e}")
        return False
    

def scroll_to_bottom(driver, container_selector, pause_time=2, max_scrolls=20):
    """Scrolls inside a specific scrollable container until no more new content loads"""
    container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, container_selector))
    )
    
    last_height = driver.execute_script(
        "return arguments[0].scrollHeight", container
    )

    for i in range(max_scrolls):
        driver.execute_script(
            "arguments[0].scrollTo(0, arguments[0].scrollHeight);", container
        )
        time.sleep(pause_time)
        
        new_height = driver.execute_script(
            "return arguments[0].scrollHeight", container
        )
        if new_height == last_height:
            print("Reached end of scrollable container.")
            break
        last_height = new_height


def scrape_jobright_listings(driver, username, password, search_url):
    """Logs in and then scrapes job listings from Jobright.ai search results."""

    # --- Step 1: Login ---
    logged_in = login_to_jobright(driver, username, password)
    if not logged_in:
        print("Login failed. Cannot proceed to scrape job listings.")
        return [] # Return empty list as scraping cannot happen


    # --- Step 2: Proceed to Scrape (if login was successful) ---
    print(f"\nLogin successful. Navigating to Jobright.ai search: {search_url}")
    try:
        driver.get(search_url)
        # Rest of the scraping logic remains the same...
        # IMPORTANT: Inspect Jobright.ai's actual search results page
        # These selectors are GUESSES and WILL likely need adjustment
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='index_jobs-list-container']")) # Adjust selector #div.index_jobs-list-container__DVqkj
        )
        time.sleep(3) # Allow dynamic content to load

        scrolling_container_selector = "#scrollableDiv"
        scroll_to_bottom(driver, scrolling_container_selector)
    

        time.sleep(3) 

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Adjust these selectors based on actual Jobright structure
        job_cards = soup.select("div[class*='index_job-card']") # Adjust selector #"div.index_job-card__AsPKC"
        print(f"Found {len(job_cards)} potential job listings.")

        jobs = []
        seen_ids = set()
        for card in job_cards:
            try:
                job_id = card.get("id")
                if not job_id or job_id in seen_ids:
                    continue
                seen_ids.add(job_id)
                print('job_id:', job_id)
                title_element = card.select_one("h2[class*='index_job-title']") # Adjust selector #"h2.index_job-title__UjuEY"
                company_element = card.select_one("div[class*='index_company-name']") # Adjust selector #"div.index_company-name__gKiOY"
                location_element = card.select_one("div[class*='index_job-metadata-item'] span") # Adjust selector #"div.index_job-metadata-item__ThMv4 span"
                #link_element = card.select_one("id") # Often the title is the link
                
                print('title_element:', title_element)
                print('company_element:',company_element)
                print('location_element:', location_element)
                
                if title_element and company_element and job_id:
                    title = title_element.get_text(strip=True)
                    company = company_element.get_text(strip=True)
                    location = location_element.get_text(strip=True) if location_element else "N/A"
                    # Construct absolute URL if relative
                    #job_url = link_element.get('id')
                    # if job_url and not job_url.startswith('http'):
                       # Need Jobright.ai's base URL if links are relative
                       #base_url = "https://jobright.ai/jobs/info/" # Adjust if needed
                    job_url = f"https://jobright.ai/jobs/info/{job_id}"

                    print(f"  - Found: {title} at {company}")
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "url": job_url, # This might be the link to apply OR a details page on Jobright
                        "description": None # Will fetch description later
                    })
                else:
                    print("  - Skipping card, missing required elements (title, company, or link).")
            except Exception as e:
                print(f"  - Error parsing a job card: {e}")
        return jobs

    except TimeoutException:
         print(f"Error: Timed out waiting for job listings elements on {search_url}")
         return []
    except Exception as e:
        print(f"Error scraping job listings from {search_url} after login: {e}")
        return []

def get_job_description(driver, job_url):
    """Navigates to the job detail page and extracts responsibilities and skills sections."""
    if not job_url:
        print("Error: No URL provided for job description.")
        return "Description not found."

    print(f"Fetching job description from: {job_url}")
    try:
        driver.get(job_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section[class*='index_sectionContent']")) #"section.index_sectionContent__zTR73"
        )
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # --- Responsibilities ---
        # Select all matching sections and take the one WITHOUT an id (responsibilities)
        responsibility_section = None
        for section in soup.select("section[class*='index_sectionContent']"): #"section.index_sectionContent__zTR73"
            if not section.has_attr("id"):  # The responsibilities section has no ID
                responsibility_section = section
                break

        responsibilities = responsibility_section.get_text(separator='\n', strip=True) if responsibility_section else ""

        # --- Skills (Required + Preferred) ---
        skills_section = soup.select_one("section#skills-section")
        skills = skills_section.get_text(separator='\n', strip=True) if skills_section else ""

        # --- Combine All ---
        full_description = "\n\n".join(filter(None, [
            "Responsibilities:\n" + responsibilities if responsibilities else None,
            "Skills & Qualifications:\n" + skills if skills else None
        ]))
        print('full_description:', full_description)
        return full_description if full_description else "No description found."

    except Exception as e:
        print(f"Error fetching job description from {job_url}: {e}")
        return f"Error fetching description: {e}"