import google.generativeai as genai
import streamlit as st

# Gemini API setup
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
    Email: [email address], Contact Name: [name/department]
    """
    return model.generate_content(prompt).text.strip()

# Streamlit UI
st.set_page_config(page_title="CivicBot", layout="centered")
st.title("🌍 CivicBot: File a Local Civic Issue")

with st.form("civic_form"):
    sender = st.text_input("Your Name (leave blank for anonymous)")
    location = st.text_input("📍 Area / Locality")
    issue_type = st.selectbox("💧 Select Issue Type", [
        "Sanitation", "Drainage", "Water Supply", "Electricity", "Road Damage",
        "Garbage Collection", "Street Lighting", "Noise Pollution", "Air Pollution",
        "Illegal Parking", "Animal Nuisance", "Sewage Overflow", "Construction Debris",
        "Tree Cutting", "Public Toilet Maintenance", "Potholes", "Blocked Footpaths",
        "Open Manholes", "Other"
    ])
    if issue_type == "Other":
        issue_type = st.text_input("Please specify the issue")

    issue_description = st.text_area("🗣️ Describe the Issue")
    submitted = st.form_submit_button("Submit")

if submitted:
    with st.spinner("Getting follow-up questions..."):
        questions = follow_up(location, issue_type, issue_description)
    st.markdown("---")
    st.subheader("🖊️ Follow-Up Questions")
    followup = st.text_area("Please answer:", value=questions, height=150)

    if st.button("Generate Complaint Letter"):
        with st.spinner("Looking up contact and drafting letter..."):
            contact = find_contact_email(location, issue_type)
            complaint = generate_complaint(location, issue_type, issue_description, sender, followup, contact)

        st.markdown("---")
        st.subheader("📩 Contact Details")
        st.code(contact)

        st.subheader("✍️ Complaint Letter")
        st.text_area("Letter", value=complaint, height=300)
