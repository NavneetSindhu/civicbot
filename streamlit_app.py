import google.generativeai as genai
import streamlit as st

import requests

def send_to_n8n(data):
    n8n_webhook_url = "https://aicivicbot.app.n8n.cloud/webhook/84d05857-4b9c-4a0a-8267-68f9701ca678"  # Replace with your real URL
    try:
        response = requests.post(n8n_webhook_url, json=data)
        if response.status_code == 200:
            st.success("Data sent to n8n successfully!")
        else:
            st.warning(f"n8n returned status code: {response.status_code}")
    except Exception as e: 
        st.error(f"Error sending data to n8n: {e}")

genai.configure(api_key="AIzaSyDsEjUH14QGHeKmxmhX2ABAa7NppS44PK4")

def follow_up(location, issue_type, issue_description):
    model = genai.GenerativeModel("gemini-2.5-pro")
    prompt = f"""
    You're a civic bot designed to educate and draft formal complaints.
    Based on user input ({location}, {issue_type}, {issue_description}), ask 3 short follow-up questions to clarify details.
    Only return the questions.
    """
    return model.generate_content(prompt).text.strip()

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
    return model.generate_content(prompt).text.strip()

def find_contact_email(location, issue_type):
    model = genai.GenerativeModel("gemini-2.5-pro")
    prompt = f"""
    Find the most likely official contact email for {issue_type} in {location}, India.
    Prefer .gov.in domains. Format output as:
    email id only to be sent to http request further
    """
    return model.generate_content(prompt).text.strip()

# Streamlit UI
st.set_page_config(page_title="CivicBot", layout="centered")
st.title("\U0001F30D CivicBot: File a Local Civic Issue")

if "followup_stage" not in st.session_state:
    st.session_state.followup_stage = False

if "questions" not in st.session_state:
    st.session_state.questions = ""

if "complaint_generated" not in st.session_state:
    st.session_state.complaint_generated = False

if not st.session_state.followup_stage:
    with st.form("civic_form"):
        sender = st.text_input("Your Name (leave blank for anonymous)")
        location = st.text_input("\U0001F4CD Area / Locality")
        issue_type = st.selectbox("\U0001F4A7 Select Issue Type", [
            "Sanitation", "Drainage", "Water Supply", "Electricity", "Road Damage",
            "Garbage Collection", "Street Lighting", "Noise Pollution", "Air Pollution",
            "Illegal Parking", "Animal Nuisance", "Sewage Overflow", "Construction Debris",
            "Tree Cutting", "Public Toilet Maintenance", "Potholes", "Blocked Footpaths",
            "Open Manholes", "Other"
        ])
        if issue_type == "Other":
            issue_type = st.text_input("Please specify the issue")

        issue_description = st.text_area("\U0001F5E3️ Describe the Issue")
        submitted = st.form_submit_button("Submit")

    if submitted:
        with st.spinner("Getting follow-up questions..."):
            questions = follow_up(location, issue_type, issue_description)
            st.session_state.questions = questions
            st.session_state.sender = sender
            st.session_state.location = location
            st.session_state.issue_type = issue_type
            st.session_state.issue_description = issue_description
            st.session_state.followup_stage = True
        st.rerun()

else:
    st.subheader("\U0001F58A️ Follow-Up Questions")
    st.markdown("_Please provide answers to the following questions:_")
    st.code(st.session_state.questions)
    followup = st.text_area("Your Answers")

    if st.button("Generate Complaint Letter"):
        with st.spinner("Looking up contact and drafting letter..."):
            contact = find_contact_email(st.session_state.location, st.session_state.issue_type)
            complaint = generate_complaint(
                st.session_state.location,
                st.session_state.issue_type,
                st.session_state.issue_description,
                st.session_state.sender,
                followup,
                contact
            )
            st.session_state.contact = contact
            st.session_state.complaint = complaint
            st.session_state.complaint_generated = True
        st.rerun()

if st.session_state.complaint_generated:
    st.markdown("---")
    st.subheader("\U0001F4E9 Contact Details")
    st.code(st.session_state.contact)

    st.subheader("\u270D️ Complaint Letter")
    st.code(st.session_state.complaint)

    if st.button("Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if st.button("Submit Complaint and Trigger Automation"):
    final_data = {
        "to": "demo@gmail.com",
        "letter": "stsnjdnj"
    }
    send_to_n8n(final_data)

