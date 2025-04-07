# sheets_logger.py
import gspread
from google.oauth2.service_account import Credentials
import datetime

def setup_sheets_client(service_account_file):
    """Authenticates and returns a gspread client."""
    try:
        scopes = ['https://www.googleapis.com/auth/spreadsheets',
                  'https://www.googleapis.com/auth/drive.file'] # Drive scope sometimes needed
        credentials = Credentials.from_service_account_file(
            service_account_file, scopes=scopes)
        client = gspread.authorize(credentials)
        print("Google Sheets client authenticated successfully.")
        return client
    except FileNotFoundError:
        print(f"Error: Service account file not found at {service_account_file}")
        raise
    except Exception as e:
        print(f"Error setting up Google Sheets client: {e}")
        raise

def get_existing_jobs(client,sheet_id):
    """
    Returns a set of (company_name, role_title) tuples for fast lookup.
    """
    sheet = client.open_by_key(sheet_id).sheet1
    existing_rows = sheet.get_all_values()[1:]  # Skip header row
    return set((row[0].strip(), row[1].strip()) for row in existing_rows if len(row) >= 2)

def log_job_info(client, existing_jobs_set, sheet_id, company_name, role_title, role_desc, job_url):

    job_key = (company_name.strip(), role_title.strip())

    if job_key in existing_jobs_set:
        print(f"Skipping duplicate: {role_title} at {company_name}")
        return False
    
    try:
        sheet = client.open_by_key(sheet_id).sheet1 # Assumes logging to the first sheet
        row_to_insert = [company_name, role_title, role_desc, job_url]

        sheet.append_row(row_to_insert)
        existing_jobs_set.add(job_key)
        print(f"Successfully logged Job Information for {role_title} at {company_name} to Google Sheet.")
        return True
    except gspread.exceptions.APIError as e:
        print(f"Google Sheets API Error: {e}")
        print("Check if the Sheet ID is correct and the service account has edit permissions.")
        return False
    except Exception as e:
        print(f"Error logging to Google Sheet: {e}")
        return False



def log_application(client, sheet_id, company_name, role_title):
    """Appends application details to the specified Google Sheet."""
    try:
        sheet = client.open_by_key(sheet_id).sheet1 # Assumes logging to the first sheet
        
        date_applied = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_to_insert = [company_name, role_title, date_applied]
        
        sheet.append_row(row_to_insert)
        print(f"Successfully logged application for {role_title} at {company_name} to Google Sheet.")
        return True
    except gspread.exceptions.APIError as e:
        print(f"Google Sheets API Error: {e}")
        print("Check if the Sheet ID is correct and the service account has edit permissions.")
        return False
    except Exception as e:
        print(f"Error logging to Google Sheet: {e}")
        return False