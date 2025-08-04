# civicbot_gemini.py
import os
import google.generativeai as genai
import threading
import time
import sys
import streamlit as st

def loader(message="⏳ Working"):
    chars = ["", ".", "..", "..."]
    i = 0
    while not stop_loader:
        print(f"\r{message}{chars[i % 4]}", end="")
        i += 1
        time.sleep(0.4)
    print("\r", end="")  # Clear loader after done

# Wrap the Gemini call
def generate_with_loader(fn, *args, message="⏳ Working", **kwargs):
    global stop_loader
    stop_loader = False
    t = threading.Thread(target=loader, args=(message,))
    t.start()

    result = fn(*args, **kwargs)

    stop_loader = True
    t.join()
    return result

# Load API key
# GEMINI_API_KEY = os.getenv("AIzaSyDsEjUH14QGHeKmxmhX2ABAa7NppS44PK4") or st.input_text("🔑 Enter your Gemini API Key: ")
genai.configure(api_key="AIzaSyDsEjUH14QGHeKmxmhX2ABAa7NppS44PK4")

def follow_up(location, issue_type, issue_description):
    model = genai.GenerativeModel("gemini-2.5-pro")
    prompt = f"""
    You're a civic bot designed to educate and draft formal complaints to authorities for immediate solution of problems of users.
    Based on the user's input of {location},{issue_type},{issue_description}, ask 3 short, relevant follow-up questions
    that would help you write the most accurate and personalized civic complaint letter and print them only first.
    """
    response = generate_with_loader(lambda:model.generate_content(prompt))
    return response.text.strip()


def further_steps(location, issue_type, issue_description):
    model = genai.GenerativeModel("gemini-2.5-pro")
    prompt = f"""
    You're a civic bot designed to educate and draft formal complaints to authorities for immediate solution of problems of users.

    Task:
    - Further steps user can take on own based on following-
    - Location: {location.title()}
    - Type: {issue_type}
    - Description: {issue_description}
    
    """
    response = generate_with_loader(lambda:model.generate_content(prompt))
    return response.text.strip()


# Step 1: Generate complaint letter
def generate_complaint(location, issue_type, issue_description,sender,followup,contact=""):
    model = genai.GenerativeModel("gemini-2.5-pro")
    prompt = f"""
    You're a civic bot designed to educate and draft formal complaints to authorities for immediate solution of problems of users.
    

    Task:
    - Write a formal complaint for the following civic issue:
    - Location: {location.title()}
    - Type: {issue_type}
    - Description: {issue_description}
    - Contact: {contact}
    - Sender: {sender}
    - Context: {followup}
    Output:
    - Well-formatted letter
    - Polite and assertive tone
    - Professional language
    If sender name is blank its for anonymouse reasons mention resident of location.
    """
    response = generate_with_loader(lambda:model.generate_content(prompt))
    return response.text.strip()


# Step 2: Ask Gemini to find email contact based on search knowledge
def find_contact_email(location, issue_type):
    model = genai.GenerativeModel("gemini-2.5-pro")
    search_prompt = f"""
Find the official contact email for handling {issue_type} issues in {location}, India.

- Categorize the issue: If {issue_type} is "sanitation" or "drainage", search for the Municipal Corporation or City Corporation. For "water supply", search for the Public Health Engineering Department.
- Prefer `.gov.in` email addresses. If a `.gov.in` address is not found, return the most official-looking alternative (e.g., a formal department email).
- Return only the most likely email address and the name of the department or specific official it belongs to, in the format: `Email: [email address], Contact Name: [name/department]`.
- If a single, accurate email is not found, return a list of the most relevant addresses with their corresponding contact names/departments, each on a new line, in the same format.
- Do not include any other text or explanation.
    """
    response = generate_with_loader(lambda:model.generate_content(search_prompt))
    
    return response.text.strip()

# CLI Interaction


if __name__ == "__main__":
    options_list = [
    "Choose",
    "Sanitation",
    "Drainage",
    "Water Supply",
    "Electricity",
    "Road Damage",
    "Garbage Collection",
    "Street Lighting",
    "Noise Pollution",
    "Air Pollution",
    "Illegal Parking",
    "Animal Nuisance",
    "Sewage Overflow",
    "Construction Debris",
    "Tree Cutting",
    "Public Toilet Maintenance",
    "Potholes",
    "Blocked Footpaths",
    "Open Manholes",
    "Other"
]

    st.title("\n🌍 CivicBot: Raise Your Voice for Local Issues\n")

    if "sender_done" not in st.session_state:
        st.session_state.sender_done = False
    if "location_done" not in st.session_state:
        st.session_state.location_done = False
    if "issue_type_done" not in st.session_state:
        st.session_state.issue_type_done = False
    if "issue_description_done" not in st.session_state:
        st.session_state.issue_description_done = False
    if "followup_done" not in st.session_state:
        st.session_state.followup_done = False

    if not st.session_state.sender_done:
        sender = st.text_input("Enter your name or leave blank for anonymity: ",key="sender_input").strip()
    if sender:
        st.session_state.sender_done = True
        st.rerun()

    if not st.session_state.location_done:
        location = st.text_input("📍 Enter your area/locality: ").strip()
    if location:
        st.session_state.location_done = True
        st.rerun()

    if not st.session_state.issue_type_done:
        issue_type = st.selectbox("🔧 Enter the issue type (e.g., sanitation, drainage): ",options_list,0).strip()
    if issue_type == "Other":
        custom_issue = st.text_input("Please describe the issue:")
    if issue_type:
        st.session_state.issue_type_done = True
        st.rerun()

    if not st.session_state.issue_description_done:
        issue_description = st.text_input("📢 Describe the issue briefly: ").strip()
    if issue_description:
        st.session_state.issue_description_done = True
        st.rerun()

    if not st.session_state_followup_done:
        followup = st.text_input(follow_up(location, issue_type, issue_description))
    if followup:
        st.session_state.followup_done = True
        st.rerun()
    
    print("\n🔎 Trying to find relevant email/contact...")
    contact = find_contact_email(location, issue_type)
    # print(contact)
    print("\n📬 Suggested Contact:\n")
    print(contact)
    st.text("Would you like to know some steps you can take on your own - Yes/No ")
    permission_yes = st.button(" Yes ")
    permission_no = st.button(" No ")
    if permission_yes:
        further_steps(location,issue_type,issue_description)
    st.text("\n✍️ Generating complaint letter...")
    complaint = generate_complaint(location, issue_type, issue_description,sender,followup,contact)
    st.text("\n📝 Complaint Letter:\n")
    st.text(complaint)
    # print("\n📝 Want me to fill your personal details:\n")

    
