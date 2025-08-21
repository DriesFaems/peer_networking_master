import streamlit as st
import os
from PyPDF2 import PdfReader
from pyairtable import Table
import datetime
import re

PERSONAL_ACCESS_TOKEN = st.secrets["PERSONAL_ACCESS_TOKEN"]
BASE_ID = st.secrets["BASE_ID"]
TABLE_NAME = st.secrets["TABLE_NAME"]  # Replace with your table name

# set environment variable for GROQ API key

airtable = Table(PERSONAL_ACCESS_TOKEN, BASE_ID, TABLE_NAME)

# Create title for WHU MBA Streamlit App
st.title("Registration Match With Your WHU Peers")

text = ""

# Helper function to validate email format
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Helper function to validate name (at least 2 words)
def is_valid_name(name):
    return len(name.strip().split()) >= 2

# Display initial input form for user details and PDF upload
with st.form("registration_form"):
    name = st.text_input("Please enter your first name and last name *", placeholder="e.g., John Doe")
    email = st.text_input("Please enter your email address *", placeholder="e.g., john.doe@example.com")
    
    # User needs to select exactly one program from the list
    program_options = [
        "Master in Management",
        "Master in Finance",
        "Master in Business Analytics",
        "Master in Entrepreneurship",
        "Master in International Business"
    ]
    selected_program = st.radio(
        "Please select your program of study *",
        program_options,
        index=None
    )
    
    # user needs to upload a PDF of their LinkedIn profile
    uploaded_file = st.file_uploader("Please upload a PDF of your LinkedIn profile. You can find this PDF by going to your LinkedIn profile page, click on Resources, and click on Save PDF. You can also upload a PDF ofyour CV if you are not able to get a LinkedIn PDF By uploading the file, you agree that we use and store your LinkedIn profile/CV for the purpose of WHU peer matching", 
                                   type="pdf")
    
    # user needs to describe their hobbies and interests
    hobbies = st.text_area("Please describe your hobbies and interests *", placeholder="e.g., I like to play soccer, read books, and travel.")
    
    # user needs to describe their goals for the upcoming academic year
    goals = st.text_area("Please describe your goals for the upcoming academic year *", placeholder="e.g., I want to learn more about AI and how to use it in my business.")
    
    # user needs to describe their career aspirations
    career_aspirations = st.text_area("Please describe your career aspirations *", placeholder="e.g., I want to create my own SaaS startup.")
    
    # Add a required opt-in checkbox for email sharing consent
    email_sharing_opt_in = st.checkbox(
        "I agree that matched people will receive my email address to reach out *",
        value=False,
        help="Required: You must agree to allow your email address to be shared with matched participants."
    )
    
    st.markdown("*Required fields")
    submit_form = st.form_submit_button("Submit")

# If the form is submitted
if submit_form:
    # Collect all validation errors
    errors = []

    # Validate name
    if not name or not name.strip():
        errors.append("Please enter your name.")
    elif not is_valid_name(name):
        errors.append("Please enter both your first name and last name.")

    # Validate email
    if not email or not email.strip():
        errors.append("Please enter your email address.")
    elif not is_valid_email(email):
        errors.append("Please enter a valid email address.")

    # Validate program selection
    if selected_program is None:
        errors.append("Please select your program of study.")

    # Validate PDF upload
    if uploaded_file is None:
        errors.append("Please upload your LinkedIn profile PDF.")

    # Validate hobbies and interests
    if not hobbies or not hobbies.strip():
        errors.append("Please describe your hobbies and interests.")

    # Validate goals for the upcoming academic year
    if not goals or not goals.strip():
        errors.append("Please describe your goals for the upcoming academic year.")

    # Validate career aspirations
    if not career_aspirations or not career_aspirations.strip():
        errors.append("Please describe your career aspirations.")
    
    # Validate email sharing opt-in
    if not email_sharing_opt_in:
        errors.append("You must agree to allow your email address to be shared with matched participants.")
    
    # Display errors if any
    if errors:
        for error in errors:
            st.error(error)
    else:
        # All validations passed, process the form
        try:
            # Read the pdf file
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

            # Additional validation: check if PDF contains text
            if not text.strip():
                st.error("The uploaded PDF appears to be empty or contains no readable text. Please upload a valid LinkedIn profile PDF.")
            else:
                st.session_state.profile = text

                record = {
                    "Name": name.strip(),
                    "Email": email.strip().lower(),
                    "Program": selected_program,
                    "LinkedIn Profile": st.session_state.profile,
                    "Hobbies and Interests": hobbies.strip(),
                    "Goals": goals.strip(),
                    "Career Aspirations": career_aspirations.strip(),
                    "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                airtable.create(record)
                st.success("**Registration successful.**")

        except Exception as e:
            st.error(f"An error occurred while processing your PDF: {str(e)}. Please try uploading the file again.")



