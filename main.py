# main.py
import time
import os
from datetime import datetime

from config_loader import load_config, load_base_resume_info
from web_scraper import setup_driver, scrape_jobright_listings, get_job_description
from ai_interaction import configure_gemini, generate_resume_content, generate_cover_letter
# from document_handler import save_text_to_file, find_latest_resume_pdf, rename_resume
# from browser_automation import fill_application_form
from sheets_logger import setup_sheets_client, log_application, log_job_info, get_existing_jobs

# --- Configuration ---
try:
    config = load_config() # Loads all config including jobright credentials
    base_resume_info = load_base_resume_info(config["base_resume_info_file"])
    print(base_resume_info)
    configure_gemini(config["gemini_api_key"])
    sheets_client = setup_sheets_client(config["service_account_file"])
    existing_jobs = get_existing_jobs(sheets_client,config["google_sheet_id"])
except (ValueError, FileNotFoundError, Exception) as e:
    print(f"Critical setup error: {e}")
    print("Exiting.")
    exit()

# --- User Data (for filling forms) ---
USER_DATA = {
    "first_name": "YourFirstName",
    "last_name": "YourLastName",
    "email": "your.email@example.com",
    "phone": "123-456-7890",
    "linkedin": "https://linkedin.com/in/yourprofile",
}
YOUR_NAME_FOR_FILENAME = "YourName"


def main():
    driver = None
    try:
        driver = setup_driver()
        if not driver:
            return

        # 1. Login to Jobright and Check for openings
        print("Logging into Jobright and searching for jobs...")
        job_listings = scrape_jobright_listings(
            driver,
            username=config["jobright_username"], # Pass username
            password=config["jobright_password"], # Pass password
            search_url="https://jobright.ai/jobs/recommend?login=true" # Example Search
        )

        if not job_listings:
            print("No job listings found or login failed.")
            # Driver is closed in finally block
            return

        print(f"\nFound {len(job_listings)} jobs after login. Processing...")

        processed_jobs_count = 0
        output_dir = "generated_documents"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)


        for job in job_listings:
            print(f"\n--- Processing Job: {job['title']} at {job['company']} ---")

            # 2. Get Job Description
            # We use the same driver instance, session should persist
            
            job_description = get_job_description(driver, job['url'])
            if not job_description or "Error fetching description" in job_description or "Description not found" in job_description :
                 print("Could not get job description. Skipping job.")
                 continue
            
            print("\nLogging Job Information attempt to Google Sheets...")
            log_job_info(sheets_client, existing_jobs, config["google_sheet_id"], job['company'], job['title'], job_description, job['url'])

            # # --- AI Generation ---
            # # 3. Prompt AI for Tailored Resume Content
            # print("\nGenerating tailored resume content...")
            # resume_bullet_points = generate_resume_content(job_description, base_resume_info)
            # print("\n--- Suggested Resume Bullet Points (Copy to Overleaf) ---")
            # print(resume_bullet_points)
            # print("---------------------------------------------------------")

            # # 6. Prompt AI for Cover Letter
            # print("\nGenerating cover letter...")
            # cover_letter_text = generate_cover_letter(job_description, base_resume_info, job['company'], job['title'])
            # print("\n--- Generated Cover Letter Text (Preview) ---")
            # print(cover_letter_text[:500] + "..." if len(cover_letter_text) > 500 else cover_letter_text)
            # print("---------------------------------------------")

            # # --- Document Handling ---
            # # 7. Save Cover Letter to file
            # safe_company = "".join(c for c in job['company'] if c.isalnum() or c in (' ', '_')).rstrip()
            # safe_role = "".join(c for c in job['title'] if c.isalnum() or c in (' ', '_')).rstrip()
            # cl_filename = os.path.join(output_dir, f"CoverLetter_{safe_company}_{safe_role}.txt")
            # save_text_to_file(cover_letter_text, cl_filename)

            # # 4. MANUAL STEP: Update Resume on Overleaf & Download
            # print("\n--- ACTION REQUIRED ---")
            # print("1. Copy the generated resume bullet points above.")
            # print("2. Paste them into your resume project on Overleaf.")
            # print("3. Recompile your resume on Overleaf.")
            # print(f"4. Download the updated PDF resume to your '{config['downloads_folder']}' folder.")
            # input("Press Enter when you have downloaded the updated resume PDF...")

            # # 5. Find and Rename Downloaded Resume
            # latest_resume_path = find_latest_resume_pdf(config["downloads_folder"])
            # if not latest_resume_path:
            #      print("Could not find the downloaded resume PDF. Skipping application step.")
            #      continue

            # renamed_resume_path = rename_resume(latest_resume_path, job['company'], job['title'], output_dir, YOUR_NAME_FOR_FILENAME)
            # if not renamed_resume_path:
            #      print("Failed to rename the resume PDF. Using original path for application attempt.")
            #      renamed_resume_path = latest_resume_path

            # # --- Application Step ---
            # # 8. Apply Online (Attempt)
            # application_link = job['url'] # Still assuming job['url'] is the apply link
            # print(f"\nApplication Link: {application_link}")

            # apply_attempt = input("Attempt to automatically fill the application form? (yes/no): ").lower()
            # submission_attempted = False
            # if apply_attempt == 'yes':
            #      if application_link:
            #           # Pass the existing driver instance to the application function
            #           submission_attempted = fill_application_form(driver, application_link, renamed_resume_path, cl_filename, USER_DATA)
            #      else:
            #           print("Cannot attempt application, no valid link found.")
            # else:
            #     print("Skipping automated form filling.")

            # 9. Log to Google Sheets
            # print("\nLogging application attempt to Google Sheets...")
            # log_application(sheets_client, config["google_sheet_id"], job['company'], job['title'])

            processed_jobs_count += 1
            print(f"--- Finished processing {job['title']} ---")
            time.sleep(5) # Slightly shorter delay between jobs maybe
            # break # For Debugging

    except Exception as e:
        print(f"\nAn error occurred during the main process: {e}")
        import traceback # Optional: Print full traceback for debugging
        traceback.print_exc()
    finally:
        if driver:
            print("Closing browser...")
            driver.quit()
        print("\nAutomation finished.")

if __name__ == "__main__":
    main()