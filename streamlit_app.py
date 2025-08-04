# civicbot_streamlit.py
import os
import google.generativeai as genai
import threading
import time
import streamlit as st

# Loader spinner in console (used in CLI, not Streamlit UI)
def loader(message="⏳ Working"):
    chars = ["", ".", "..", "..."]
    i = 0
    while not stop_loader:
        print(f"\r{message}{chars[i % 4]}", end="")
        i += 1
        time.sleep(0.4)
    print("\r", end="")

# Wrapper for Gemini API call with console loader
def generate_with_loader(fn, *args, message="⏳ Working", **kwargs):
    global stop_loader
    stop_loader = False
    t = threading.Thread(target=loader, args=(message,))
    t.start()
    result = fn(*args, **kwargs)
    stop_loader = True
    t.join()
    return result

# Configure Gemini API Key
genai.configure(api_key="AIzaSyDsEjUH14QGHeKmxmhX2ABAa7NppS44PK4")

def follow_up(location, issue_type, issue_description):
    model = genai.GenerativeModel("gemini-2.5-pro")
    prompt = f"""
    You're a civic bot designed to educate and draft formal complaints.
    Based on user input ({location}, {issue_type}, {issue_description}), ask 3 short follow-up questions to clarify details.
    Only return the questions.
    """
    response = generate_with_loader(lambda: model.generate_content(prompt))
    return response.text.strip()

def further_steps(location, issue_type, issue_description):
    model = genai.GenerativeModel("gemini-2.5-pro")
    prompt = f"""
    Suggest actionable steps a citizen can take for this civic issue:
    Location: {location}
    Issue: {issue_type}
    Description: {issue_description}
    """
    response = generate_with_loader(lambda: model.generate_content(prompt))
    return response.text.strip()

def generate_complaint(location, issue_type, issue_description, sender, followup, contact=""):
    model = genai.GenerativeModel("gemini-2.5-pro")
    prompt = f"""
    Write a formal complaint letter for a civic issue:
    Location: {location.title()}
    Issue: {issue_type}
    Description: {issue_description}
    Sender: {sender if sender else f"a concerned resident of {location}"}
    Follow-up Info: {followup}
    Contact: {contact}
    Use polite, professional, and assertive language.
    """
    response = generate_with_loader(lambda: model.generate_content(prompt))
    return response.text.strip()

def find_contact_email(location, issue_type):
    model = genai.GenerativeModel("gemini-2.5-pro")
    prompt = f"""
    Find the most likely official contact email for {issue_type} in {location}, India.
    Prefer .gov.in domains. Format output as:
    Email: [email address], Contact Name: [name/department]
    """
    response = generate_with_loader(lambda: model.generate_content(prompt))
    return response.text.strip()

# Streamlit App Starts Here
st.set_page_config(page_title="CivicBot", layout="centered")
st.title("🌍 CivicBot: Raise Your Voice for Local Issues")

options_list = [
    "Choose", "Sanitation", "Drainage", "Water Supply", "Electricity", "Road Damage",
    "Garbage Collection", "Street Lighting", "Noise Pollution", "Air Pollution",
    "Illegal Parking", "Animal Nuisance", "Sewage Overflow", "Construction Debris",
    "Tree Cutting", "Public Toilet Maintenance", "Potholes", "Blocked Footpaths",
    "Open Manholes", "Other"
]

# Session state tracker
for key in ["sender_done", "location_done", "issue_type_done", "issue_description_done", "followup_done"]:
    if key not in st.session_state:
        st.session_state[key] = False

# Step 1: Name
if not st.session_state.sender_done:
    sender = st.text_input("Enter your name (or leave blank for anonymous):", key="sender_input").strip()
    if sender or sender == "":
        st.session_state.sender = sender
        st.session_state.sender_done = True
        st.rerun()

# Step 2: Location
if st.session_state.sender_done and not st.session_state.location_done:
    location = st.text_input("📍 Enter your area/locality:", key="location_input").strip()
    if location:
        st.session_state.location = location
        st.session_state.location_done = True
        st.rerun()

# Step 3: Issue Type
if st.session_state.location_done and not st.session_state.issue_type_done:
    issue_type = st.selectbox("💧 Select the issue type:", options_list, index=0, key="issue_type_input")
    if issue_type != "Choose":
        if issue_type == "Other":
            custom_issue = st.text_input("Please describe the issue:", key="custom_issue_input")
            if custom_issue:
                issue_type = custom_issue
        st.session_state.issue_type = issue_type
        st.session_state.issue_type_done = True
        st.rerun()

# Step 4: Description
if st.session_state.issue_type_done and not st.session_state.issue_description_done:
    issue_description = st.text_input("📣 Briefly describe the issue:", key="issue_desc_input").strip()
    if issue_description:
        st.session_state.issue_description = issue_description
        st.session_state.issue_description_done = True
        st.rerun()

# Step 5: Follow-Up Questions
if st.session_state.issue_description_done and not st.session_state.followup_done:
    questions = follow_up(
        st.session_state.location,
        st.session_state.issue_type,
        st.session_state.issue_description
    )
    followup = st.text_area("Please answer the following:", value=questions, key="followup_input")
    if followup:
        st.session_state.followup = followup
        st.session_state.followup_done = True
        st.rerun()

# After all inputs
if st.session_state.followup_done:
    contact = find_contact_email(st.session_state.location, st.session_state.issue_type)
    st.subheader("📩 Contact Details")
with st.status("Searching for Contact"):
    st.write("Searching on google")
    time.sleep(2)
    st.write("Found URL.")
    time.sleep(1)
    st.write("Retrieving Address")
    time.sleep(1)     

st.button("Rerun")
st.code(contact)

st.subheader("✍️ Generated Complaint Letter")
    complaint = generate_complaint(
        st.session_state.location,
        st.session_state.issue_type,
        st.session_state.issue_description,
        st.session_state.sender,
        st.session_state.followup,
        contact
    )
st.code(complaint)

    if st.button("Show Suggested Further Steps"):
        steps = further_steps(
            st.session_state.location,
            st.session_state.issue_type,
            st.session_state.issue_description
        )
        st.markdown("### 🧑‍📋 Further Steps You Can Take")
        st.markdown(steps)
