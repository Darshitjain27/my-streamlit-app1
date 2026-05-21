import streamlit as st
import pandas as pd
import datetime

# ------------------ UI CONFIG ------------------
st.set_page_config(page_title="Audit QA Tool", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: Calibri;
}
.main {
    background-color: #FFFFFF;
}
h1, h2, h3 {
    color: #000000;
}
</style>
""", unsafe_allow_html=True)

# ------------------ SESSION INIT ------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "logs" not in st.session_state:
    st.session_state.logs = []

if "engagements" not in st.session_state:
    st.session_state.engagements = []

if "checklist" not in st.session_state:
    st.session_state.checklist = []

if "qa_results" not in st.session_state:
    st.session_state.qa_results = {}


# ------------------ AUTH ------------------
def login():
    st.title("🔐 Sign In")

    users = {"admin": "admin123", "auditor": "audit123"}

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if users.get(username) == password:
            st.session_state.user = username
            st.success("Login Successful")
        else:
            st.error("Invalid Credentials")


# ------------------ LOGGING ------------------
def add_log(action):
    st.session_state.logs.append({
        "user": st.session_state.user,
        "action": action,
        "time": datetime.datetime.now()
    })


# ------------------ HOME ------------------
def home():
    st.title("🏠 Home")
    st.write(f"Welcome, {st.session_state.user}")

    st.info("Navigate using sidebar")


# ------------------ DASHBOARD ------------------
def dashboard():
    st.title("📊 Dashboard")

    total = len(st.session_state.checklist)
    completed = sum(1 for v in st.session_state.qa_results.values() if v == "Pass")
    failed = sum(1 for v in st.session_state.qa_results.values() if v == "Fail")
    progress = int((completed / total) * 100) if total > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total QA", total)
    col2.metric("Completed", completed)
    col3.metric("Failed", failed)
    col4.metric("Progress %", progress)


# ------------------ CREATE CLIENT ------------------
def create_client():
    st.title("👤 Create Client")

    name = st.text_input("Client Name")

    if st.button("Create"):
        st.success(f"Client {name} created")
        add_log("Client created")


# ------------------ CREATE ENGAGEMENT ------------------
def create_engagement():
    st.title("📁 Create Engagement")

    with st.form("eng"):
        fy = st.text_input("Financial Year")
        process = st.selectbox("Audit Process", ["Claims", "Underwriting"])
        auditor = st.text_input("Auditor Name")
        auditee = st.text_input("Auditee Name")
        dept = st.text_input("Department")
        title = st.text_input("Title")

        submit = st.form_submit_button("Create")

    if submit:
        st.session_state.engagements.append({
            "FY": fy,
            "Process": process,
            "Auditor": auditor
        })
        generate_checklist(process)
        st.success("Engagement Created")
        add_log("Engagement created")


# ------------------ CHECKLIST GENERATION ------------------
def generate_checklist(process):
    master = [
        "Check policy compliance",
        "Verify claims approval",
        "Validate documents",
        "Check fraud indicators"
    ]
    st.session_state.checklist = master


# ------------------ DOCUMENT UPLOAD ------------------
def upload_docs():
    st.title("📄 Upload Documents")

    required = [
        "Audit Scoping Memo",
        "Audit Report",
        "RCM",
        "Audit Program",
        "Workpapers",
        "Evidence"
    ]

    uploads = {}
    for r in required:
        uploads[r] = st.file_uploader(r)

    if st.button("Save Docs"):
        st.success("Documents Uploaded")
        add_log("Documents uploaded")


# ------------------ QA ENGINE ------------------
def run_qa(step):
    # SIMPLE MOCK LOGIC
    if "fraud" in step.lower():
        return "Fail"
    return "Pass"


# ------------------ CHECKLIST EXECUTION ------------------
def checklist_page():
    st.title("✅ QA Checklist")

    for i, step in enumerate(st.session_state.checklist):

        st.subheader(f"{i+1}. {step}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"Run QA {i}"):
                result = run_qa(step)
                st.session_state.qa_results[step] = result
                add_log(f"QA Run {step}")

        with col2:
            na = st.checkbox(f"Not Applicable {i}")
            remarks = st.text_input(f"Remarks {i}")

        if step in st.session_state.qa_results:
            st.write("Result:", st.session_state.qa_results[step])

        # CHAT
        query = st.text_input(f"Chat refine {i}")
        if query:
            st.write("AI Suggestion: Improve documentation")

        st.divider()


# ------------------ REVIEW ------------------
def review_page():
    st.title("👨‍💼 Review & Signoff")

    for step, result in st.session_state.qa_results.items():
        st.write(step, "→", result)

    approve = st.radio("Approve Report?", ["Yes", "No"])

    if approve == "Yes":
        st.success("Signed Off")
        add_log("Report signed off")


# ------------------ REPORT ------------------
def generate_report():
    st.title("📑 Final Report")

    df = pd.DataFrame([
        {"Step": k, "Result": v}
        for k, v in st.session_state.qa_results.items()
    ])

    st.dataframe(df)

    prompt = st.text_area("Refine Report")

    if prompt:
        st.write("Refined report generated...")

    st.download_button("Download CSV", df.to_csv(index=False), "report.csv")

    if st.button("Archive"):
        st.success("Archived")
        add_log("Archived")


# ------------------ LOGS ------------------
def show_logs():
    st.title("📜 Audit Logs")

    df = pd.DataFrame(st.session_state.logs)
    st.dataframe(df)


# ------------------ MAIN ------------------
if not st.session_state.user:
    login()
else:
    menu = st.sidebar.selectbox("Menu", [
        "Home",
        "Dashboard",
        "Create Client",
        "Create Engagement",
        "Upload Documents",
        "Checklist",
        "Review",
        "Report",
        "Logs"
    ])

    if menu == "Home":
        home()
    elif menu == "Dashboard":
        dashboard()
    elif menu == "Create Client":
        create_client()
    elif menu == "Create Engagement":
        create_engagement()
    elif menu == "Upload Documents":
        upload_docs()
    elif menu == "Checklist":
        checklist_page()
    elif menu == "Review":
        review_page()
    elif menu == "Report":
        generate_report()
    elif menu == "Logs":
        show_logs()
