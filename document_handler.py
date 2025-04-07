# document_handler.py
import os
import time
import shutil

def save_text_to_file(content, filename):
    """Saves text content to a file."""
    try:
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
             os.makedirs(directory)
             
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully saved content to: {filename}")
        return True
    except Exception as e:
        print(f"Error saving file {filename}: {e}")
        return False

def find_latest_resume_pdf(download_folder, base_name="YourName_Resume"):
    """
    Finds the most recently downloaded PDF in the specified folder,
    assuming a naming convention after manual download from Overleaf.
    THIS IS A GUESS - requires user to download with a predictable name.
    A better approach might involve asking the user to confirm the file path.
    """
    print(f"Searching for latest resume PDF in: {download_folder}")
    time.sleep(5) # Give time for download to complete

    try:
        files = [os.path.join(download_folder, f) for f in os.listdir(download_folder) if f.lower().endswith('.pdf')]
        if not files:
            print("No PDF files found in the download folder.")
            return None

        # Find the most recently modified PDF file
        latest_file = max(files, key=os.path.getmtime)
        print(f"Found potential latest resume: {latest_file}")
        # Optional: Add a check if filename contains base_name or similar?
        # if base_name.lower() in os.path.basename(latest_file).lower():
        return latest_file
        # else:
        #     print(f"Warning: Latest PDF '{os.path.basename(latest_file)}' doesn't match expected base name '{base_name}'.")
        #     return latest_file # Return it anyway, user needs to be careful

    except FileNotFoundError:
        print(f"Error: Download folder not found at {download_folder}")
        return None
    except Exception as e:
        print(f"Error finding latest resume PDF: {e}")
        return None

def rename_resume(original_path, company_name, role_title, output_dir=".", base_name="YourName"):
    """Renames the resume PDF and moves it to the output directory."""
    if not original_path or not os.path.exists(original_path):
        print("Error: Original resume path is invalid.")
        return None

    # Sanitize company and role names for use in filenames
    safe_company = "".join(c for c in company_name if c.isalnum() or c in (' ', '_')).rstrip()
    safe_role = "".join(c for c in role_title if c.isalnum() or c in (' ', '_')).rstrip()
    new_filename = f"{base_name}_Resume_{safe_company}_{safe_role}.pdf"
    new_path = os.path.join(output_dir, new_filename)

    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        shutil.move(original_path, new_path) # Use move to handle potential cross-drive issues better than rename
        print(f"Resume renamed and moved to: {new_path}")
        return new_path
    except Exception as e:
        print(f"Error renaming/moving resume from {original_path} to {new_path}: {e}")
        # Attempt to copy if move failed (e.g., permissions), leave original
        try:
            shutil.copy2(original_path, new_path) # copy2 preserves metadata
            print(f"Resume copied (original retained) to: {new_path}")
            return new_path
        except Exception as copy_e:
            print(f"Error copying resume either: {copy_e}")
            return None # Failed to move or copy