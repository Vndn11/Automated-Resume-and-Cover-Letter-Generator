# ai_interaction.py
import google.generativeai as genai
import time

def configure_gemini(api_key):
    """Configures the Google Gemini API client."""
    try:
        genai.configure(api_key=api_key)
        print("Gemini API configured successfully.")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        raise

def get_gemini_response(prompt, retries=3, delay=5):
    """Gets response from Gemini model with basic retry logic."""
    print("\n--- Sending Prompt to Gemini ---")
    # print(f"Prompt: {prompt[:200]}...") # Print start of prompt for debugging
    
    
    

    for attempt in range(retries):
        try:
            model = genai.GenerativeModel(model_name="gemini-pro", # Use gemini-pro (free tier eligible)
                                          generation_config = {
                                            "temperature": 0.7, # Controls randomness - lower is more predictable
                                            "top_p": 1,
                                            "top_k": 1,
                                            "max_output_tokens": 1024, # Adjust as needed
                                            },
                                          safety_settings = [ # Adjust safety settings if needed
                                            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                        ])
            response = model.generate_content(prompt)
            
            # Check if response has text before returning
            if response.parts:
                 print("--- Gemini Response Received ---")
                 return response.text
            else:
                 # Handle cases where the response might be blocked or empty
                 print(f"Warning: Gemini response was empty or blocked. Reason: {response.prompt_feedback}")
                 # If blocked for safety, it won't succeed on retry with same prompt.
                 # If potentially transient issue, retry might help.
                 if response.prompt_feedback and response.prompt_feedback.block_reason:
                    return f"Error: Content blocked by safety settings ({response.prompt_feedback.block_reason}). Please adjust prompt or safety settings."
                 # If empty for other reasons, retry.

        except Exception as e:
            print(f"Error calling Gemini API (Attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Failed to get response from Gemini.")
                return f"Error: Failed to get response after {retries} attempts. Last error: {e}"
                
    return "Error: Failed to get response after multiple retries (potential non-exception issue)."


def generate_resume_content(job_description, base_resume_info):
    """Generates tailored resume content using Gemini."""
    prompt = f"""
    Analyze the following job description and my base resume information.
    Generate 3 concise, impactful project which includes 2-3 bullet points for each project for a resume's project section,
    tailored specifically to highlight how my skills and experience match this job.
    Update the skills section according to the keywords in the job description to make it ATS friendly.
    Focus on achievements and quantify results where possible based on the base info.
    Do NOT invent experience I don't have. Use the base info as the source of truth for my skills.
    Output *only* the bullet points, each starting with '* '.

    --- Job Description ---
    {job_description}

    --- My Base Resume Info ---
    {base_resume_info}

    --- Tailored Resume Bullet Points ---
    """
    return get_gemini_response(prompt)

def generate_cover_letter(job_description, base_resume_info, company_name, role_title):
    """Generates a tailored cover letter using Gemini."""
    prompt = f"""
    Write a professional and enthusiastic cover letter for the position of {role_title} at {company_name}.
    Use the provided job description and my base resume information to tailor the letter.
    Highlight 2-3 key qualifications or experiences from my base info that directly align with the requirements in the job description.
    Maintain a professional tone. Address it generically (e.g., "Dear Hiring Manager,") unless a name is provided (which it isn't here).
    Keep it concise, ideally 3-4 paragraphs.
    Ensure the output is only the cover letter text, ready to be pasted.

    --- Job Description ---
    {job_description}

    --- My Base Resume Info ---
    {base_resume_info}

    --- Cover Letter ---
    """
    return get_gemini_response(prompt)