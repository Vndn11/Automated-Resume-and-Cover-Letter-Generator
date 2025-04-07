import os
from dotenv import load_dotenv
import fitz 

def load_config():
    """Loads configuration from .env file."""
    load_dotenv()
    config = {
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "google_sheet_id": os.getenv("GOOGLE_SHEET_ID"),
        "service_account_file": os.getenv("SERVICE_ACCOUNT_FILE"),
        "base_resume_info_file": os.getenv("BASE_RESUME_INFO_FILE"),
        "downloads_folder": os.getenv("DOWNLOADS_FOLDER"),
        "jobright_username": os.getenv("JOBRIGHT_USERNAME"),
        "jobright_password": os.getenv("JOBRIGHT_PASSWORD"),
    }
    # Basic validation
    
    if not all(config.values()):
        missing = [k for k, v in config.items() if not v]
        raise ValueError(f"Missing configuration in .env file: {', '.join(missing)}")
    
    if not os.path.isdir(config["downloads_folder"]):
         print(f"Warning: Downloads folder specified in .env does not exist: {config['downloads_folder']}")
    return config
    
    
# def load_base_resume_info(filepath):
#     """Loads base resume information from a text file."""
#     try:
#         with open(filepath, 'r', encoding='utf-8') as f:
#             return f.read()
#     except FileNotFoundError:
#         print(f"Error: Base resume file not found at {filepath}")
#         return "Experienced professional seeking new opportunities." # Default fallback
#     except Exception as e:
#         print(f"Error reading base resume file: {e}")
#         return "Experienced professional seeking new opportunities."
    

def load_base_resume_info(filepath):
    """Loads text from a resume PDF file."""
    try:
        doc = fitz.open(filepath)
        resume_text = ""
        for page in doc:
            resume_text += page.get_text()
        doc.close()
        return resume_text.strip()
    except FileNotFoundError:
        print(f"File not found at: {filepath}")
        return "Experienced professional seeking new opportunities."
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return "Experienced professional seeking new opportunities."