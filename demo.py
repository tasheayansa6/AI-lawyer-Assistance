"""
LegalAI Demo Mode
Showcases all features with pre-filled sample data.
No API key required — all responses are realistic mock data.
Run: streamlit run demo.py
"""

import streamlit as st
import os, io, csv, json
from datetime import datetime

os.environ["DB_PATH"] = "demo_legal_ai.db"

import db
db.init_db()

st.set_page_config(
    page_title="LegalAI — Demo",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Demo data ──────────────────────────────────────────────────────────────────
DEMO_QA = [
    {
        "q": "What is a power of attorney?",
        "jurisdiction": "US",
        "a": """## Power of Attorney (POA)

A **Power of Attorney** is a legal document that grants one person (the *agent* or *attorney-in-fact*) the authority to act on behalf of another person (the *principal*) in legal, financial, or medical matters.

### Types of Power of Attorney

| Type | Description |
|------|-------------|
| **General POA** | Broad authority over financial and legal matters |
| **Limited/Special POA** | Authority for a specific transaction or time period |
| **Durable POA** | Remains effective if the principal becomes incapacitated |
| **Medical/Healthcare POA** | Authority to make healthcare decisions |
| **Springing POA** | Only takes effect upon a specific event (e.g., incapacitation) |

### Key Requirements (US)
- Must be signed by the principal while mentally competent
- Typically requires notarization
- Some states require witnesses
- Should be recorded if involving real estate

### When Does It End?
- Principal revokes it in writing
- Principal dies
- Court invalidates it
- Specified expiration date passes

---
**Disclaimer**: This is general information only and does not constitute legal advice. Consult a qualified attorney for your specific situation."""
    },
    {
        "q": "What are my rights if I am arrested?",
        "jurisdiction": "US",
        "a": """## Your Rights Upon Arrest in the United States

Under the **U.S. Constitution** and established case law, you have the following rights:

### Miranda Rights (5th & 6th Amendment)
- **Right to remain silent** — You cannot be compelled to incriminate yourself
- **Right to an attorney** — You may have counsel present during questioning
- **Right to appointed counsel** — If you cannot afford an attorney, one will be appointed

### 4th Amendment Rights
- Protection against **unreasonable searches and seizures**
- Police generally need a **warrant** to search your property
- Exceptions: plain view, consent, exigent circumstances

### What To Do If Arrested
1. Stay calm and do not resist
2. Clearly state: *"I am invoking my right to remain silent"*
3. Ask for an attorney immediately
4. Do not consent to searches
5. Do not discuss your case with anyone except your attorney

### Key Cases
- *Miranda v. Arizona* (1966) — Established Miranda warnings
- *Gideon v. Wainwright* (1963) — Right to appointed counsel

---
**Disclaimer**: This is general information only and does not constitute legal advice. Consult a qualified attorney for your specific situation."""
    },
    {
        "q": "How do I file for divorce?",
        "jurisdiction": "US",
        "a": """## Filing for Divorce in the United States

### Step-by-Step Process

**Step 1: Meet Residency Requirements**
Most states require you or your spouse to have lived in the state for 6–12 months before filing.

**Step 2: Grounds for Divorce**
- **No-fault divorce**: Available in all 50 states (irreconcilable differences)
- **Fault-based divorce**: Adultery, abandonment, cruelty (available in some states)

**Step 3: File the Petition**
- Complete a *Petition for Dissolution of Marriage*
- File with your county courthouse
- Pay filing fee ($100–$400 depending on state)

**Step 4: Serve Your Spouse**
- Spouse must be formally served with divorce papers
- Can use a process server, sheriff, or certified mail

**Step 5: Waiting Period**
- Most states have a mandatory waiting period (30–180 days)

**Step 6: Negotiate Settlement**
- Division of marital property
- Child custody and support
- Spousal support/alimony

**Step 7: Final Decree**
- Judge signs the *Decree of Dissolution*
- Marriage is legally ended

### Timeline
Uncontested divorce: **3–6 months** | Contested divorce: **1–3 years**

---
**Disclaimer**: This is general information only and does not constitute legal advice. Consult a qualified attorney for your specific situation."""
    },
    {
        "q": "What is the statute of limitations for personal injury?",
        "jurisdiction": "US",
        "a": """## Statute of Limitations — Personal Injury (US)

The **statute of limitations** is the deadline by which you must file a lawsuit. Missing this deadline typically bars your claim forever.

### By State (Common Examples)

| State | Time Limit |
|-------|-----------|
| California | 2 years |
| New York | 3 years |
| Texas | 2 years |
| Florida | 4 years |
| Illinois | 2 years |

### Discovery Rule
The clock typically starts when you **knew or should have known** about the injury — not necessarily the date of the incident.

### Exceptions That May Toll (Pause) the Clock
- **Minor victims**: Clock starts at age 18
- **Mental incapacity**: Clock paused during incapacity
- **Defendant concealment**: Fraudulent concealment may extend deadline
- **Government defendants**: Much shorter deadlines (often 6 months)

### Types of Claims & Typical Limits
- Car accidents: 2–3 years
- Medical malpractice: 2–3 years (with discovery rule)
- Product liability: 2–4 years
- Wrongful death: 2–3 years

---
**Disclaimer**: This is general information only and does not constitute legal advice. Consult a qualified attorney for your specific situation."""
    },
]

DEMO_CASES = [
    {
        "name": "Brown v. Board of Education",
        "summary": """## Case Summary: Brown v. Board of Education (1954)

**Citation**: 347 U.S. 483 (1954)

---

**Facts**
Linda Brown, a Black student in Topeka, Kansas, was denied admission to an all-white elementary school near her home and required to attend a segregated Black school. The NAACP, led by Thurgood Marshall, brought suit on behalf of Brown and other plaintiffs challenging racial segregation in public schools.

**Issue**
Does racial segregation in public schools violate the Equal Protection Clause of the 14th Amendment?

**Holding**
Yes. The Supreme Court unanimously held (9-0) that "separate educational facilities are inherently unequal" and therefore unconstitutional.

**Reasoning**
Chief Justice Earl Warren wrote that segregation generates a feeling of inferiority in Black children that may affect their hearts and minds in a way unlikely ever to be undone. The Court rejected the "separate but equal" doctrine established in *Plessy v. Ferguson* (1896).

**Precedent**
- Overturned *Plessy v. Ferguson* (1896)
- Established that racial segregation in public education is unconstitutional
- Paved the way for the Civil Rights Movement
- Led to *Brown II* (1955) ordering desegregation "with all deliberate speed"

---
**Disclaimer**: This is general information only and does not constitute legal advice."""
    },
    {
        "name": "Miranda v. Arizona",
        "summary": """## Case Summary: Miranda v. Arizona (1966)

**Citation**: 384 U.S. 436 (1966)

---

**Facts**
Ernesto Miranda was arrested in Phoenix, Arizona, and interrogated by police for two hours without being informed of his right to counsel or right against self-incrimination. He signed a confession that was used to convict him of kidnapping and rape.

**Issue**
Must police inform suspects of their constitutional rights before custodial interrogation?

**Holding**
Yes. The Supreme Court (5-4) held that statements made during custodial interrogation are inadmissible unless the suspect was informed of their rights and voluntarily waived them.

**Reasoning**
Chief Justice Warren held that the inherently coercive nature of custodial interrogation requires procedural safeguards to protect the 5th Amendment privilege against self-incrimination and the 6th Amendment right to counsel.

**Precedent**
- Established the *Miranda warning* requirement
- Police must inform suspects: right to remain silent, anything said can be used against them, right to an attorney, right to appointed counsel
- Created the *Miranda rights* now standard in all US law enforcement

---
**Disclaimer**: This is general information only and does not constitute legal advice."""
    },
]

DEMO_TOOLS = {
    "Spellbook": {"best_for": "Contract Drafting", "pricing": "Enterprise", "rating": "⭐⭐⭐⭐⭐"},
    "Thomson Reuters CoCounsel": {"best_for": "Legal Research", "pricing": "Subscription", "rating": "⭐⭐⭐⭐⭐"},
    "Lexis+ AI": {"best_for": "Case Analysis", "pricing": "Premium", "rating": "⭐⭐⭐⭐"},
    "Harvey AI": {"best_for": "Large Firm Research", "pricing": "Enterprise", "rating": "⭐⭐⭐⭐⭐"},
    "Clio Manage AI": {"best_for": "Practice Management", "pricing": "$39-$89/user/mo", "rating": "⭐⭐⭐⭐"},
}

DEMO_USERS = [
    {"username": "admin_demo", "role": "administrator", "email": "admin@legalai.demo", "created_at": "2024-01-01"},
    {"username": "lawyer_jane", "role": "licensed_lawyer", "email": "jane@lawfirm.demo", "created_at": "2024-01-15"},
    {"username": "paralegal_bob", "role": "paralegal", "email": "bob@lawfirm.demo", "created_at": "2024-02-01"},
    {"username": "public_user", "role": "general_public", "email": "user@demo.com", "created_at": "2024-03-01"},
]

DEMO_CASES_DB = [
    {"id": 1, "name": "Smith v. Johnson", "client_name": "John Smith", "case_type": "Civil Litigation", "jurisdiction": "US", "status": "Active", "created_at": "2024-03-01"},
    {"id": 2, "name": "ABC Corp Merger", "client_name": "ABC Corporation", "case_type": "Corporate", "jurisdiction": "UK", "status": "Review", "created_at": "2024-03-10"},
    {"id": 3, "name": "Estate of Williams", "client_name": "Mary Williams", "case_type": "Estate Planning", "jurisdiction": "US", "status": "Completed", "created_at": "2024-02-15"},
    {"id": 4, "name": "Tech IP Dispute", "client_name": "TechStart Inc.", "case_type": "IP", "jurisdiction": "US", "status": "Active", "created_at": "2024-04-01"},
]

DEMO_TIME_ENTRIES = [
    {"activity": "Research", "hours": 3.5, "rate": 250, "description": "Case law research on IP infringement", "logged_at": "2024-04-10"},
    {"activity": "Drafting", "hours": 5.0, "rate": 250, "description": "Draft motion to dismiss", "logged_at": "2024-04-11"},
    {"activity": "Client Meeting", "hours": 1.5, "rate": 250, "description": "Strategy session with client", "logged_at": "2024-04-12"},
    {"activity": "Court Appearance", "hours": 4.0, "rate": 300, "description": "Preliminary hearing", "logged_at": "2024-04-13"},
    {"activity": "Review", "hours": 2.0, "rate": 250, "description": "Review opposing counsel documents", "logged_at": "2024-04-14"},
]

# ── CSS (same professional style) ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: "Inter", sans-serif; }
.demo-banner {
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%);
    color: white; padding: 12px 20px; border-radius: 10px;
    text-align: center; font-weight: 600; font-size: 0.9rem;
    margin-bottom: 1.5rem; letter-spacing: 0.3px;
}
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #1e40af 100%);
    color: white; padding: 4rem 2rem; border-radius: 20px;
    text-align: center; margin-bottom: 2rem;
}
.hero h1 { font-size: 3rem; font-weight: 800; margin: 0 0 1rem 0; letter-spacing: -1px; }
.hero p  { font-size: 1.2rem; opacity: 0.85; margin: 0 0 2rem 0; }
.feature-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 14px;
    padding: 1.5rem; text-align: center; height: 100%;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); transition: transform 0.2s;
}
.feature-card:hover { transform: translateY(-3px); }
.feature-card .icon { font-size: 2.5rem; margin-bottom: 0.75rem; }
.feature-card h3 { font-size: 1rem; font-weight: 700; color: #0f172a; margin: 0 0 0.5rem 0; }
.feature-card p  { font-size: 0.85rem; color: #64748b; margin: 0; }
.stat-card {
    background: white; border-radius: 12px; padding: 1.2rem;
    text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border: 1px solid rgba(0,0,0,0.05);
}
.stat-number { font-size: 2rem; font-weight: 700; color: #1e40af; }
.stat-label  { font-size: 0.8rem; font-weight: 600; color: #64748b; text-transform: uppercase; }
.role-badge  {
    display: inline-block; padding: 3px 12px; border-radius: 20px;
    color: white; font-size: 12px; font-weight: 600;
}
.qa-card {
    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 1.2rem; margin-bottom: 1rem; cursor: pointer;
}
.qa-card:hover { border-color: #3b82f6; background: #eff6ff; }
.stTabs [data-baseweb="tab-list"] {
    gap: 0; background: #f1f5f9; border-radius: 10px; padding: 4px; margin-bottom: 1.5rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; padding: 8px 20px; font-weight: 500;
    font-size: 0.875rem; color: #64748b; border: none; background: transparent;
}
.stTabs [aria-selected="true"] {
    background: white !important; color: #0f172a !important;
    font-weight: 600; box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Demo banner ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="demo-banner">
    🎯 DEMO MODE — All responses are pre-filled sample data. No API key required.
    &nbsp;|&nbsp; <a href="https://github.com/tasheayansa6/AI-lawyer-Assistance"
    style="color:white;text-decoration:underline;">View on GitHub</a>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
ROLE_COLORS = {
    "administrator": "#e53e3e", "licensed_lawyer": "#dd6b20",
    "paralegal": "#38a169", "general_public": "#2c5282", "compliance_officer": "#805ad5"
}
ROLE_DISPLAY = {
    "administrator": "Administrator", "licensed_lawyer": "Licensed Lawyer",
    "paralegal": "Paralegal", "general_public": "General Public",
    "compliance_officer": "Compliance Officer"
}

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem 0;">
        <div style="font-size:2rem;">⚖️</div>
        <div style="font-weight:800;font-size:1.1rem;color:#0f172a;">LegalAI</div>
        <div style="font-size:0.75rem;color:#94a3b8;">Professional Legal Platform</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    demo_role = st.selectbox("👤 Demo as role:", list(ROLE_DISPLAY.values()))
    role_key = {v: k for k, v in ROLE_DISPLAY.items()}[demo_role]
    color = ROLE_COLORS[role_key]
    st.markdown(f"""
    <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:10px 14px;margin-bottom:1rem;">
        <div style="font-weight:600;color:#0f172a;font-size:0.9rem;">demo_user</div>
        <span style="background:{color};color:white;padding:2px 10px;border-radius:20px;font-size:0.72rem;font-weight:600;">{demo_role}</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    pages = ["🏠 Home", "⚖️ Q&A", "📄 Documents", "⚖️ Cases", "🤖 AI Tools",
             "🔧 Admin", "👨‍⚖️ Lawyer", "📋 Paralegal", "🔍 Compliance", "⚙️ Settings"]
    selected = st.radio("Navigation", pages, label_visibility="collapsed")
    page = selected.split(" ", 1)[1]

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;font-size:0.72rem;color:#94a3b8;">
        LegalAI Demo v2.0<br>Not a substitute for legal advice
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════
if page == "Home":
    st.markdown("""
    <div class="hero">
        <div style="font-size:4rem;margin-bottom:1rem;">⚖️</div>
        <h1>LegalAI Assistant</h1>
        <p>Professional AI-powered legal information platform for lawyers,<br>
           paralegals, and the general public across 6 jurisdictions.</p>
        <div style="display:flex;justify-content:center;gap:1rem;flex-wrap:wrap;margin-top:1.5rem;">
            <span style="background:rgba(255,255,255,0.15);padding:8px 18px;border-radius:20px;font-size:0.85rem;">🔒 600k PBKDF2 Security</span>
            <span style="background:rgba(255,255,255,0.15);padding:8px 18px;border-radius:20px;font-size:0.85rem;">🌍 6 Jurisdictions</span>
            <span style="background:rgba(255,255,255,0.15);padding:8px 18px;border-radius:20px;font-size:0.85rem;">🤖 Groq AI Powered</span>
            <span style="background:rgba(255,255,255,0.15);padding:8px 18px;border-radius:20px;font-size:0.85rem;">📋 Full Audit Logging</span>
            <span style="background:rgba(255,255,255,0.15);padding:8px 18px;border-radius:20px;font-size:0.85rem;">🛡️ GDPR Compliant</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, (num, label) in zip([c1,c2,c3,c4,c5], [
        ("6", "Jurisdictions"), ("5", "User Roles"), ("15+", "Query Templates"),
        ("7", "AI Tools Listed"), ("100%", "Audit Logged")
    ]):
        with col:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{num}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards
    st.markdown("### ✨ Platform Features")
    cols = st.columns(3)
    features = [
        ("⚖️", "Legal Q&A", "Ask legal questions across US, UK, India, Canada, Australia & Ethiopia with AI-powered answers."),
        ("📄", "Document Analysis", "Upload PDF/DOCX legal documents for AI-powered analysis, clause extraction and Q&A."),
        ("📋", "Case Management", "Create, track and manage legal cases with full status history and client records."),
        ("🔍", "Case Summariser", "Paste or fetch case text from URLs for structured AI summaries with metadata extraction."),
        ("🤖", "AI Tools Directory", "Browse, compare and get recommendations for leading legal AI tools."),
        ("🔒", "Enterprise Security", "600k PBKDF2 hashing, brute-force protection, session timeout, OAuth2 SSO."),
        ("📊", "Audit & Compliance", "Full audit trail, compliance reports, GDPR data export and deletion."),
        ("⏱️", "Time & Billing", "Log billable hours, generate invoices and track billing by case."),
        ("🌍", "Multi-Jurisdiction", "Compare laws across jurisdictions with AI-powered side-by-side analysis."),
    ]
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="icon">{icon}</div>
                <h3>{title}</h3>
                <p>{desc}</p>
            </div><br>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎭 Role-Based Access Control")
    role_cols = st.columns(5)
    roles_info = [
        ("🔴", "Administrator", "Full system access, user management, audit logs, system settings"),
        ("🟠", "Licensed Lawyer", "Case management, research, time tracking, billing, document repository"),
        ("🟢", "Paralegal", "Document processing, research support, law library access"),
        ("🔵", "General Public", "Basic Q&A (10 queries/day), legal information"),
        ("🟣", "Compliance Officer", "Audit logs, compliance reports, analytics, query monitoring"),
    ]
    for col, (dot, role, desc) in zip(role_cols, roles_info):
        with col:
            st.markdown(f"""
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:1rem;text-align:center;height:100%;">
                <div style="font-size:1.5rem;">{dot}</div>
                <div style="font-weight:700;font-size:0.85rem;color:#0f172a;margin:0.5rem 0;">{role}</div>
                <div style="font-size:0.75rem;color:#64748b;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Use the sidebar to explore each feature. Switch roles to see different access levels.")

# ══════════════════════════════════════════════════════════════════════════════
# Q&A PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Q&A":
    st.title("⚖️ Legal Q&A")
    st.caption("Demo mode — select a sample question or type your own to see a pre-filled response.")

    col1, col2 = st.columns([3, 1])
    with col1:
        jurisdiction = st.selectbox("Jurisdiction", ["US", "UK", "India", "Canada", "Australia", "Ethiopia"])
    with col2:
        template = st.selectbox("Template", ["general", "term", "process", "rights", "deadline"])

    # Sample questions
    st.markdown("**Quick sample questions:**")
    qcols = st.columns(2)
    for i, item in enumerate(DEMO_QA):
        with qcols[i % 2]:
            if st.button(f"📋 {item['q'][:50]}...", key=f"q{i}", use_container_width=True):
                st.session_state["demo_q"] = item["q"]
                st.session_state["demo_a"] = item["a"]

    query = st.text_area("Your legal question", value=st.session_state.get("demo_q", ""),
                         height=100, placeholder="e.g. What is a power of attorney?")
    max_tokens = st.slider("Response length", 100, 1000, 500)

    if st.button("Ask", type="primary", use_container_width=True):
        if query.strip():
            with st.spinner("Generating response..."):
                import time; time.sleep(0.8)
            # Find matching demo answer or use generic
            answer = next((d["a"] for d in DEMO_QA if d["q"].lower() in query.lower() or query.lower() in d["q"].lower()),
                          f"""## Response to: {query}

This is a **demo response** showing how LegalAI answers legal questions.

In the live version with a Groq API key, you would receive a detailed, jurisdiction-specific answer covering:

- **Relevant laws and statutes** in {jurisdiction}
- **Step-by-step guidance** for your situation
- **Key deadlines and requirements**
- **Recommended next steps**
- **When to consult an attorney**

### Key Points
- LegalAI provides general legal information, not legal advice
- Responses are tailored to the selected jurisdiction ({jurisdiction})
- All queries are logged for audit purposes
- PII is automatically filtered from queries

---
**Disclaimer**: This is general information only and does not constitute legal advice. Consult a qualified attorney for your specific situation.""")
            st.session_state["demo_a"] = answer

    if st.session_state.get("demo_a"):
        st.markdown("### Response")
        st.markdown(st.session_state["demo_a"])
        st.download_button("📥 Download response (.txt)",
                           st.session_state["demo_a"],
                           file_name="legal_response.txt", mime="text/plain")

    st.markdown("---")
    with st.expander("📜 Query History (Demo)"):
        for item in DEMO_QA[:3]:
            st.markdown(f"**{item['jurisdiction']}** — {item['q']}")
            st.caption("2024-04-15 10:30 UTC")
            st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENTS PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Documents":
    st.title("📄 Document Analysis")
    st.caption("Demo mode — upload a real PDF/DOCX or use the sample document below.")

    tab1, tab2 = st.tabs(["Upload & Analyse", "Document Library"])

    with tab1:
        uploaded = st.file_uploader("Upload PDF or DOCX (max 10MB)", type=["pdf", "docx"])
        if uploaded:
            st.success(f"✅ Parsed: **{uploaded.name}** — demo analysis below")
            col1, col2, col3 = st.columns(3)
            col1.metric("File size", f"{len(uploaded.getvalue())//1024} KB")
            col2.metric("Type", "PDF" if uploaded.name.endswith(".pdf") else "DOCX")
            col3.metric("Legal doc", "Yes ✅")

            st.markdown("### Document Preview")
            st.info("In live mode, full text would be extracted and displayed here.")

            st.markdown("### Ask about this document")
            doc_q = st.text_area("Question", placeholder="e.g. What are the termination clauses?")
            if st.button("Analyse", type="primary"):
                with st.spinner("Analysing..."):
                    import time; time.sleep(0.8)
                st.markdown("""### Analysis Result
**Termination Clauses Found:**
- Section 8.1: Either party may terminate with 30 days written notice
- Section 8.2: Immediate termination for material breach
- Section 8.3: Automatic termination upon insolvency

**Key Obligations:**
- Confidentiality obligations survive termination (Section 12)
- IP rights revert to original owner upon termination

---
**Disclaimer**: Demo response. In live mode, actual document content would be analysed.""")
        else:
            st.markdown("**Or try a sample document analysis:**")
            if st.button("📄 Analyse Sample NDA", type="primary"):
                with st.spinner("Processing sample NDA..."):
                    import time; time.sleep(1)
                st.success("✅ Sample NDA analysed")
                st.markdown("""### Sample NDA Analysis

**Document Type**: Non-Disclosure Agreement (NDA)
**Confidence**: 94% legal document

**Key Clauses Identified:**
| Clause | Section | Summary |
|--------|---------|---------|
| Definition of Confidential Info | 1.1 | Broad definition including technical, business, financial data |
| Obligations | 2.1 | Recipient must protect with same care as own confidential info |
| Exclusions | 3.1 | Public domain, independently developed, legally obtained |
| Term | 5.1 | 3 years from disclosure date |
| Governing Law | 8.1 | State of Delaware |

**Risk Assessment**: 🟡 Medium — Standard NDA with broad confidentiality scope""")

    with tab2:
        st.markdown("### Saved Documents (Demo)")
        demo_docs = [
            {"name": "Smith_v_Johnson_Contract.pdf", "category": "Contracts", "uploaded": "2024-04-10", "size": "245 KB"},
            {"name": "NDA_TechStart_2024.pdf", "category": "Agreements", "uploaded": "2024-04-08", "size": "128 KB"},
            {"name": "Employment_Agreement.docx", "category": "Contracts", "uploaded": "2024-04-05", "size": "89 KB"},
            {"name": "Court_Filing_Motion.pdf", "category": "Court Filings", "uploaded": "2024-04-01", "size": "312 KB"},
        ]
        search = st.text_input("🔍 Search documents")
        filtered = [d for d in demo_docs if not search or search.lower() in d["name"].lower()]
        for doc in filtered:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            col1.markdown(f"📄 **{doc['name']}**")
            col2.caption(doc["category"])
            col3.caption(doc["uploaded"])
            col4.caption(doc["size"])
        st.info("In live mode, documents are stored in the database and searchable by content.")

# ══════════════════════════════════════════════════════════════════════════════
# CASES PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Cases":
    st.title("⚖️ Case Management")
    tab1, tab2, tab3 = st.tabs(["My Cases", "Summarise Case", "Compare Cases"])

    with tab1:
        st.subheader("Active Cases (Demo)")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Cases", "4")
        col2.metric("Active", "2")
        col3.metric("In Review", "1")
        col4.metric("Completed", "1")
        st.markdown("---")

        with st.expander("➕ Create New Case (Demo)"):
            with st.form("demo_case"):
                c1, c2 = st.columns(2)
                with c1:
                    cn = st.text_input("Case Name")
                    cli = st.text_input("Client Name")
                with c2:
                    ct = st.selectbox("Type", ["Civil Litigation","Corporate","Family","Criminal","Real Estate","IP"])
                    jur = st.selectbox("Jurisdiction", ["US","UK","India","Canada","Australia","Ethiopia"])
                sub = st.form_submit_button("Create Case", type="primary")
            if sub and cn:
                st.success(f"✅ Case '{cn}' created for '{cli}' — saved to database in live mode.")

        status_colors = {"Active": "#22c55e", "Review": "#f59e0b", "Completed": "#3b82f6", "Closed": "#94a3b8"}
        for case in DEMO_CASES_DB:
            sc = status_colors.get(case["status"], "#94a3b8")
            with st.expander(f"📋 {case['name']} — {case['case_type']}"):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**Client:** {case['client_name']}")
                c2.markdown(f"**Jurisdiction:** {case['jurisdiction']}")
                c3.markdown(f"**Created:** {case['created_at']}")
                st.markdown(f"**Status:** <span style='color:{sc};font-weight:700'>{case['status']}</span>", unsafe_allow_html=True)
                new_status = st.selectbox("Update status", ["Active","Review","Completed","Closed"], key=f"s{case['id']}")
                if st.button("Update", key=f"u{case['id']}"):
                    st.success(f"Status updated to {new_status}")

    with tab2:
        st.subheader("Summarise a Legal Case")
        input_method = st.radio("Input method", ["Paste text", "Use sample case"], horizontal=True)

        if input_method == "Use sample case":
            selected_case = st.selectbox("Select sample case", [c["name"] for c in DEMO_CASES])
            case_text = next(c["summary"] for c in DEMO_CASES if c["name"] == selected_case)
            if st.button("Show Summary", type="primary"):
                st.markdown("### Case Summary")
                st.markdown(case_text)
                st.download_button("📥 Download summary", case_text, file_name="case_summary.txt", mime="text/plain")
        else:
            case_text = st.text_area("Paste case text here", height=200,
                                     placeholder="Paste the full text of a legal case...")
            if st.button("Summarise", type="primary", disabled=not bool(case_text)):
                with st.spinner("Summarising..."):
                    import time; time.sleep(1)
                summary = f"""## AI Case Summary

**Facts**: Based on the provided text, the case involves a legal dispute between parties regarding the matters described.

**Issue**: The central legal question is whether the actions described constitute a violation of applicable law.

**Holding**: The court ruled in favour of the plaintiff, finding sufficient evidence to support the claims.

**Reasoning**: The court applied established precedent and statutory interpretation to reach its conclusion, weighing the evidence presented by both parties.

**Precedent**: This case reinforces existing doctrine and may be cited in future cases involving similar fact patterns.

---
**Disclaimer**: Demo summary. In live mode, Groq AI analyses your actual case text."""
                st.markdown("### Summary")
                st.markdown(summary)
                st.download_button("📥 Download", summary, file_name="summary.txt", mime="text/plain")

    with tab3:
        st.subheader("Compare Two Cases")
        c1, c2 = st.columns(2)
        with c1:
            case_a = st.text_area("Case A", height=150, placeholder="Paste Case A text...")
        with c2:
            case_b = st.text_area("Case B", height=150, placeholder="Paste Case B text...")

        if st.button("Compare Cases", type="primary"):
            if case_a and case_b:
                with st.spinner("Comparing..."):
                    import time; time.sleep(1)
                st.markdown("""### Comparison Result

**Similarities**
- Both cases involve contractual disputes between commercial parties
- Both rely on common law principles of contract formation
- Similar remedies sought (damages + injunctive relief)

**Differences**
- Case A involves a written contract; Case B involves an implied contract
- Different jurisdictions apply different standards of proof
- Case A has a stronger precedent basis

**Outcomes**
- Case A: Plaintiff prevailed on all counts
- Case B: Mixed verdict — damages awarded, injunction denied

**Legal Principles**
- Offer, acceptance, and consideration required for valid contract
- Breach must be material to justify rescission

**Precedential Value**
- Case A is more likely to be cited due to clearer factual record

---
**Disclaimer**: Demo comparison. In live mode, Groq AI analyses your actual case texts.""")
            else:
                st.warning("Please provide text for both cases.")

# ══════════════════════════════════════════════════════════════════════════════
# AI TOOLS PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "AI Tools":
    st.title("🤖 Legal AI Tools Directory")
    tab1, tab2, tab3 = st.tabs(["Browse Tools", "Get Recommendation", "Compare Side-by-Side"])

    with tab1:
        st.subheader("Leading Legal AI Tools")
        from legal_ai_tools import get_all_tools
        tools = get_all_tools()
        for name, info in tools.items():
            with st.expander(f"**{name}** — {info['description'][:80]}..."):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Best for:** {', '.join(info['best_for'])}")
                    st.markdown(f"**Pricing:** {info['pricing']}")
                    st.markdown(f"**Ideal users:** {', '.join(info['ideal_users'])}")
                with c2:
                    st.markdown(f"**Strengths:** {', '.join(info['strengths'])}")
                    st.markdown(f"**Limitations:** {', '.join(info['limitations'])}")

    with tab2:
        st.subheader("Get a Personalised Recommendation")
        c1, c2, c3 = st.columns(3)
        with c1: budget = st.selectbox("Budget", ["low","medium","high"])
        with c2: size = st.selectbox("Firm size", ["small","medium","large"])
        with c3:
            from legal_ai_tools import get_all_use_cases
            area = st.selectbox("Practice area", get_all_use_cases())
        if st.button("Recommend", type="primary"):
            from legal_ai_tools import recommend_tools, get_tool_info
            recs = recommend_tools(budget, size, area)
            if recs:
                st.success(f"Top picks for {area} ({size} firm, {budget} budget):")
                for r in recs:
                    info = get_tool_info(r)
                    st.markdown(f"**{r}** — {info.get('description','')}")
                    st.caption(f"Pricing: {info.get('pricing','')} | Best for: {', '.join(info.get('best_for',[]))}")
            else:
                st.info("No exact match — try adjusting filters.")

    with tab3:
        st.subheader("Compare Tools Side-by-Side")
        from legal_ai_tools import get_all_tools, compare_tools
        all_names = list(get_all_tools().keys())
        selected = st.multiselect("Select tools to compare (max 4)", all_names, default=all_names[:3], max_selections=4)
        if selected:
            import pandas as pd
            comparison = compare_tools(selected)
            rows = []
            for tool, data in comparison.items():
                rows.append({
                    "Tool": tool,
                    "Best For": ", ".join(data["best_for"]),
                    "Pricing": data["pricing"],
                    "Ideal Users": ", ".join(data["ideal_users"]),
                    "Strengths": ", ".join(data["strengths"]),
                })
            st.dataframe(pd.DataFrame(rows).set_index("Tool"), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Admin":
    st.title("🔧 Administrator Dashboard")
    if role_key != "administrator":
        st.warning("⚠️ In live mode, this page requires Administrator role. Showing demo preview.")

    c1, c2, c3, c4 = st.columns(4)
    for col, (label, val, color) in zip([c1,c2,c3,c4], [
        ("Total Users","4","#1e40af"), ("Admins","1","#e53e3e"),
        ("Lawyers","1","#dd6b20"), ("Public","1","#2c5282")
    ]):
        with col:
            st.markdown(f'<div class="stat-card"><div class="stat-number" style="color:{color}">{val}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["User Management", "Role Assignment", "Audit Log", "System"])

    with tab1:
        st.subheader("All Users")
        search = st.text_input("🔍 Search users")
        filtered = [u for u in DEMO_USERS if not search or search.lower() in u["username"].lower()]
        for u in filtered:
            color = ROLE_COLORS.get(u["role"], "#2c5282")
            with st.expander(f"👤 {u['username']}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Email:** {u['email']}")
                    st.markdown(f"**Created:** {u['created_at']}")
                    st.markdown(f"**Role:** <span class='role-badge' style='background:{color}'>{ROLE_DISPLAY.get(u['role'],u['role'])}</span>", unsafe_allow_html=True)
                with c2:
                    new_role = st.selectbox("New role", list(ROLE_DISPLAY.values()), key=f"nr_{u['username']}")
                    if st.button("Update role", key=f"ur_{u['username']}"):
                        st.success(f"Role updated to {new_role} — saved in live mode.")
                    if st.button("Delete user", key=f"du_{u['username']}", type="secondary"):
                        st.error("Demo mode — deletion disabled.")

        st.markdown("---")
        st.subheader("Create New User")
        with st.form("admin_create"):
            c1, c2, c3 = st.columns(3)
            with c1: nu = st.text_input("Username")
            with c2: ne = st.text_input("Email")
            with c3: nr = st.selectbox("Role", list(ROLE_DISPLAY.values()))
            np = st.text_input("Password", type="password")
            sub = st.form_submit_button("Create User", type="primary")
        if sub and nu:
            st.success(f"✅ User '{nu}' created with role '{nr}' — saved to database in live mode.")

        if st.button("📥 Export Users CSV"):
            import pandas as pd, io
            df = pd.DataFrame(DEMO_USERS)
            buf = io.StringIO(); df.to_csv(buf, index=False)
            st.download_button("Download users.csv", buf.getvalue(), file_name="users.csv", mime="text/csv")

    with tab2:
        st.subheader("Bulk Role Assignment")
        with st.form("bulk_role"):
            target = st.text_input("Username")
            role_sel = st.selectbox("Role", list(ROLE_DISPLAY.values()))
            sub = st.form_submit_button("Assign Role", type="primary")
        if sub:
            st.success(f"Role '{role_sel}' assigned to '{target}' — saved in live mode.")

        st.markdown("**Role Distribution:**")
        import pandas as pd
        role_counts = {}
        for u in DEMO_USERS:
            r = ROLE_DISPLAY.get(u["role"], u["role"])
            role_counts[r] = role_counts.get(r, 0) + 1
        df = pd.DataFrame(list(role_counts.items()), columns=["Role","Count"])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.bar_chart(df.set_index("Role"))

    with tab3:
        st.subheader("Audit Log")
        demo_logs = [
            {"ts": "2024-04-15 10:30:00", "username": "lawyer_jane", "action": "LOGIN", "detail": ""},
            {"ts": "2024-04-15 10:31:00", "username": "lawyer_jane", "action": "QUERY", "detail": "jurisdiction=US"},
            {"ts": "2024-04-15 10:45:00", "username": "admin_demo", "action": "ASSIGN_ROLE", "detail": "target=paralegal_bob role=paralegal"},
            {"ts": "2024-04-15 11:00:00", "username": "paralegal_bob", "action": "DOC_PROCESS", "detail": "contract.pdf"},
            {"ts": "2024-04-15 11:30:00", "username": "public_user", "action": "LOGIN_FAILED", "detail": ""},
            {"ts": "2024-04-15 11:31:00", "username": "public_user", "action": "LOGIN", "detail": ""},
            {"ts": "2024-04-15 12:00:00", "username": "lawyer_jane", "action": "CASE_CREATE", "detail": "id=5 name=New Case"},
            {"ts": "2024-04-15 12:30:00", "username": "admin_demo", "action": "DB_BACKUP", "detail": "path=backup_20240415.db"},
        ]
        import pandas as pd
        df = pd.DataFrame(demo_logs)
        st.dataframe(df, use_container_width=True, hide_index=True)
        buf = io.StringIO(); df.to_csv(buf, index=False)
        st.download_button("📥 Export Audit Log (.csv)", buf.getvalue(), file_name="audit_log.csv", mime="text/csv")

    with tab4:
        st.subheader("System Information")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Security Settings:**")
            st.markdown("- PBKDF2 iterations: **600,000**")
            st.markdown("- Session timeout: **60 minutes**")
            st.markdown("- Max file size: **10 MB**")
            st.markdown("- Brute-force lockout: **5 attempts / 15 min**")
            st.markdown("- Password pepper: **Configured** ✅")
        with c2:
            st.markdown("**Database:**")
            st.markdown("- Engine: **SQLite (WAL mode)**")
            st.markdown("- Indexes: **9 performance indexes**")
            st.markdown("- Foreign keys: **Enabled (CASCADE)**")
            st.markdown("- Query retention: **90 days**")
            st.markdown("- Backup: **Atomic (includes WAL)**")
        st.markdown("---")
        if st.button("💾 Backup Database (Demo)"):
            st.success("✅ Backup created: legal_ai_backup_20240415_120000.db")
        if st.button("🧹 Apply Retention Policy (Demo)"):
            st.success("✅ Deleted 0 old query log entries (nothing older than 90 days)")

# ══════════════════════════════════════════════════════════════════════════════
# LAWYER DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Lawyer":
    st.title("👨‍⚖️ Licensed Lawyer Dashboard")
    if role_key != "licensed_lawyer":
        st.warning("⚠️ In live mode, this page requires Licensed Lawyer role. Showing demo preview.")

    tab1, tab2, tab3, tab4 = st.tabs(["Cases", "Research", "Time Tracking", "Billing"])

    with tab1:
        st.subheader("Case Management")
        import pandas as pd
        df = pd.DataFrame(DEMO_CASES_DB)
        df["created_at"] = df["created_at"].str[:10]
        st.dataframe(df[["id","name","client_name","case_type","jurisdiction","status","created_at"]],
                     use_container_width=True, hide_index=True)

        with st.expander("➕ Create New Case"):
            with st.form("lw_case"):
                c1, c2 = st.columns(2)
                with c1:
                    cn = st.text_input("Case Name")
                    cli = st.text_input("Client Name")
                with c2:
                    ct = st.selectbox("Type", ["Civil Litigation","Corporate","Family","Criminal","Real Estate","IP"])
                    jur = st.selectbox("Jurisdiction", ["US","UK","India","Canada","Australia","Ethiopia"])
                sub = st.form_submit_button("Create", type="primary")
            if sub and cn:
                st.success(f"✅ Case '{cn}' created — persisted to database in live mode.")

    with tab2:
        st.subheader("Legal Research")
        query = st.text_area("Research query", height=100,
                             placeholder="e.g. What are the elements of negligence in tort law?")
        c1, c2 = st.columns(2)
        with c1: jur = st.selectbox("Jurisdiction", ["US","UK","India","Canada","Australia","Ethiopia"])
        with c2: depth = st.selectbox("Depth", ["Standard (500 tokens)","Detailed (800 tokens)","Comprehensive (1000 tokens)"])
        if st.button("Research", type="primary"):
            if query.strip():
                with st.spinner("Researching..."):
                    import time; time.sleep(1)
                st.markdown(f"""### Research Results: {query[:60]}...

**Jurisdiction:** {jur}

**Key Legal Principles:**
1. The law in {jur} establishes clear standards for this area
2. Relevant statutes and case law provide guidance on the matter
3. Courts have consistently applied a multi-factor test

**Relevant Cases:**
- *Smith v. Jones* (2019) — Established the modern standard
- *ABC Corp v. XYZ Ltd* (2021) — Clarified the burden of proof
- *State v. Williams* (2022) — Extended the doctrine to new contexts

**Practical Implications:**
- Parties should document all relevant communications
- Expert testimony may be required
- Statute of limitations: typically 2-3 years

---
**Disclaimer**: Demo response. In live mode, Groq AI provides jurisdiction-specific research.""")
            else:
                st.warning("Enter a research query.")

        st.markdown("---")
        st.subheader("Jurisdiction Comparison")
        c1, c2 = st.columns(2)
        with c1: j1 = st.selectbox("Jurisdiction A", ["US","UK","India","Canada","Australia","Ethiopia"], key="j1")
        with c2: j2 = st.selectbox("Jurisdiction B", ["UK","US","India","Canada","Australia","Ethiopia"], key="j2")
        topic = st.text_input("Legal topic", placeholder="e.g. contract formation requirements")
        if st.button("Compare Jurisdictions", type="primary"):
            if topic:
                with st.spinner("Comparing..."):
                    import time; time.sleep(1)
                st.markdown(f"""### {j1} vs {j2}: {topic}

| Aspect | {j1} | {j2} |
|--------|------|------|
| Legal System | Common Law | Common Law |
| Key Statute | Varies by state | Varies by jurisdiction |
| Standard | Objective reasonable person | Similar objective standard |
| Burden of Proof | Balance of probabilities | Balance of probabilities |
| Limitation Period | 2-6 years | 3-6 years |

**Key Differences:**
- {j1} tends to favour more prescriptive statutory frameworks
- {j2} relies more heavily on case law precedent

**Practical Advice:**
- Always verify current law as statutes change frequently
- Local counsel recommended for jurisdiction-specific matters

---
**Disclaimer**: Demo comparison. In live mode, Groq AI provides detailed analysis.""")

    with tab3:
        st.subheader("Time Tracking")
        with st.expander("⏱️ Log Time Entry"):
            with st.form("time_form"):
                c1, c2 = st.columns(2)
                with c1:
                    case_sel = st.selectbox("Case", [c["name"] for c in DEMO_CASES_DB])
                    activity = st.selectbox("Activity", ["Research","Drafting","Court Appearance","Client Meeting","Review","Admin"])
                with c2:
                    hours = st.number_input("Hours", min_value=0.25, max_value=24.0, value=1.0, step=0.25)
                    rate = st.number_input("Rate/hour ($)", min_value=0.0, value=250.0, step=10.0)
                desc = st.text_area("Description", height=60)
                sub = st.form_submit_button("Log Time", type="primary")
            if sub:
                st.success(f"✅ Logged {hours}h @ ${rate}/h = ${hours*rate:.2f} — saved in live mode.")

        st.markdown("### Time Log")
        import pandas as pd
        df = pd.DataFrame(DEMO_TIME_ENTRIES)
        df["amount"] = df["hours"] * df["rate"]
        st.dataframe(df[["logged_at","activity","hours","rate","amount","description"]],
                     use_container_width=True, hide_index=True)
        st.metric("Total logged", f"{df['hours'].sum():.1f} hours")

    with tab4:
        st.subheader("Billing Summary")
        import pandas as pd
        df = pd.DataFrame(DEMO_TIME_ENTRIES)
        df["amount"] = df["hours"] * df["rate"]
        total = df["amount"].sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Billed", f"${total:,.2f}")
        c2.metric("Total Hours", f"{df['hours'].sum():.1f}h")
        c3.metric("Avg Rate", f"${df['rate'].mean():.0f}/h")
        st.bar_chart(df.set_index("activity")["amount"])

        lines = [f"INVOICE — {datetime.utcnow().strftime('%Y-%m-%d')}\nAttorney: lawyer_jane\n\n"]
        for _, row in df.iterrows():
            lines.append(f"{row['logged_at']}  {row['activity']}  {row['hours']}h @ ${row['rate']}/h = ${row['amount']:.2f}\n")
        lines.append(f"\nTOTAL: ${total:,.2f}\n")
        st.download_button("📥 Download Invoice (.txt)", "".join(lines), file_name="invoice.txt", mime="text/plain")

# ══════════════════════════════════════════════════════════════════════════════
# PARALEGAL DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Paralegal":
    st.title("📋 Paralegal Dashboard")
    if role_key != "paralegal":
        st.warning("⚠️ In live mode, this page requires Paralegal role. Showing demo preview.")

    tab1, tab2 = st.tabs(["Document Processing", "Research Support"])

    with tab1:
        st.subheader("Document Processing")
        uploaded = st.file_uploader("Upload document", type=["pdf","docx"])
        if uploaded:
            with st.spinner("Processing..."):
                import time; time.sleep(0.8)
            st.success(f"✅ Processed: {uploaded.name}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Size", f"{len(uploaded.getvalue())//1024} KB")
            c2.metric("Legal doc", "Yes ✅")
            c3.metric("Confidence", "87%")
            st.download_button("📥 Download cleaned text", "Cleaned document text would appear here in live mode.",
                               file_name="cleaned.txt", mime="text/plain")
        else:
            st.info("Upload a PDF or DOCX to process it. In live mode, text is extracted, cleaned, and stored in the document library.")

    with tab2:
        st.subheader("Research Support")
        query = st.text_area("Research query", height=100)
        jur = st.selectbox("Jurisdiction", ["US","UK","India","Canada","Australia","Ethiopia"])
        if st.button("Research", type="primary"):
            if query.strip():
                with st.spinner("Researching..."):
                    import time; time.sleep(0.8)
                st.markdown(f"""### Research Results

**Query:** {query}
**Jurisdiction:** {jur}

This is a demo response. In live mode, the Groq AI model provides detailed legal research results tailored to the selected jurisdiction, including relevant statutes, case law, and practical guidance.

**Key Points:**
- Relevant legislation applies in {jur}
- Standard legal principles govern this area
- Consult supervising attorney for case-specific advice

---
**Disclaimer**: Demo response. Not legal advice.""")
            else:
                st.warning("Enter a query.")

# ══════════════════════════════════════════════════════════════════════════════
# COMPLIANCE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Compliance":
    st.title("🔍 Compliance Officer Dashboard")
    if role_key != "compliance_officer":
        st.warning("⚠️ In live mode, this page requires Compliance Officer role. Showing demo preview.")

    tab1, tab2, tab3 = st.tabs(["Audit Log", "Query Analytics", "Compliance Report"])

    with tab1:
        st.subheader("Full Audit Log")
        import pandas as pd
        demo_logs = [
            {"ts": "2024-04-15 10:30", "username": "lawyer_jane",   "action": "LOGIN",          "detail": ""},
            {"ts": "2024-04-15 10:31", "username": "lawyer_jane",   "action": "QUERY",          "detail": "jurisdiction=US"},
            {"ts": "2024-04-15 10:45", "username": "admin_demo",    "action": "ASSIGN_ROLE",    "detail": "target=bob role=paralegal"},
            {"ts": "2024-04-15 11:00", "username": "paralegal_bob", "action": "DOC_PROCESS",    "detail": "contract.pdf"},
            {"ts": "2024-04-15 11:30", "username": "public_user",   "action": "LOGIN_FAILED",   "detail": "attempt=1"},
            {"ts": "2024-04-15 11:31", "username": "public_user",   "action": "LOGIN_FAILED",   "detail": "attempt=2"},
            {"ts": "2024-04-15 11:32", "username": "public_user",   "action": "LOGIN",          "detail": ""},
            {"ts": "2024-04-15 12:00", "username": "lawyer_jane",   "action": "CASE_CREATE",    "detail": "id=5"},
            {"ts": "2024-04-15 12:30", "username": "admin_demo",    "action": "DB_BACKUP",      "detail": "backup_20240415.db"},
            {"ts": "2024-04-15 13:00", "username": "lawyer_jane",   "action": "TIME_LOG",       "detail": "hours=3.5 rate=250"},
            {"ts": "2024-04-15 13:30", "username": "paralegal_bob", "action": "LOGOUT",         "detail": ""},
            {"ts": "2024-04-15 14:00", "username": "admin_demo",    "action": "DELETE_USER",    "detail": "target=old_user"},
        ]
        df = pd.DataFrame(demo_logs)
        action_filter = st.multiselect("Filter by action", df["action"].unique().tolist(), default=[])
        if action_filter:
            df = df[df["action"].isin(action_filter)]
        st.dataframe(df, use_container_width=True, hide_index=True)
        buf = io.StringIO(); df.to_csv(buf, index=False)
        st.download_button("📥 Export Audit Log (.csv)", buf.getvalue(), file_name="audit_log.csv", mime="text/csv")

    with tab2:
        st.subheader("Query Analytics")
        import pandas as pd
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Queries", "247")
        c2.metric("Unique Users", "4")
        c3.metric("Avg/Day", "18")

        jur_data = pd.DataFrame({
            "Jurisdiction": ["US","UK","India","Canada","Australia","Ethiopia"],
            "Queries": [142, 38, 27, 21, 14, 5]
        })
        st.markdown("**Queries by Jurisdiction:**")
        st.bar_chart(jur_data.set_index("Jurisdiction"))

        action_data = pd.DataFrame({
            "Action": ["QUERY","LOGIN","DOC_PROCESS","CASE_CREATE","TIME_LOG"],
            "Count": [247, 89, 34, 12, 28]
        })
        st.markdown("**Activity Breakdown:**")
        st.bar_chart(action_data.set_index("Action"))

    with tab3:
        st.subheader("Compliance Report Generator")
        if st.button("Generate Report", type="primary"):
            with st.spinner("Generating..."):
                import time; time.sleep(1)
            report = f"""COMPLIANCE REPORT — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
Generated by: compliance_officer (demo)
================================================================

SUMMARY
-------
Total users:          4
Total queries:        247
Audit log entries:    12
Failed login attempts: 2
Account lockouts:     0

USER BREAKDOWN
--------------
Administrator:        1
Licensed Lawyer:      1
Paralegal:            1
General Public:       1
Compliance Officer:   0

QUERY ACTIVITY (Last 30 Days)
------------------------------
US jurisdiction:      142 queries
UK jurisdiction:       38 queries
India jurisdiction:    27 queries
Canada jurisdiction:   21 queries
Australia jurisdiction: 14 queries
Ethiopia jurisdiction:   5 queries

SECURITY EVENTS
---------------
Failed logins:        2
Account lockouts:     0
Role changes:         1
User deletions:       1
DB backups:           1

DATA RETENTION
--------------
Query log retention:  90 days
Oldest entry:         2024-01-15
Auto-cleanup:         Enabled

GDPR COMPLIANCE
---------------
Data export requests: 0
Data deletion requests: 0
Consent management:   Active

================================================================
This report was auto-generated by LegalAI Compliance Module.
Not a substitute for professional compliance review.
"""
            st.text_area("Report Preview", report, height=400)
            st.download_button("📥 Download Full Report (.txt)", report,
                               file_name="compliance_report.txt", mime="text/plain")
            db.audit("compliance_officer_demo", "COMPLIANCE_REPORT_GENERATED", "demo=True")

# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Settings":
    st.title("⚙️ Settings")
    tab1, tab2, tab3 = st.tabs(["My Account", "Lawyer Referrals", "System Info"])

    with tab1:
        st.subheader("Account Information")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Username:** demo_user")
            st.markdown(f"**Role:** {demo_role}")
            st.markdown("**Email:** demo@legalai.com")
            st.markdown("**Member since:** 2024-01-01")
        with c2:
            st.markdown("**Last login:** 2024-04-15 10:30 UTC")
            st.markdown("**Queries today:** 5 / unlimited")
            st.markdown("**OAuth2:** Not linked")
            st.markdown("**2FA:** Not enabled")

        st.markdown("---")
        st.subheader("Change Password (Demo)")
        with st.form("pw_form"):
            old = st.text_input("Current password", type="password")
            new1 = st.text_input("New password", type="password")
            new2 = st.text_input("Confirm new password", type="password")
            sub = st.form_submit_button("Update Password", type="primary")
        if sub:
            if new1 == new2 and len(new1) >= 8:
                st.success("✅ Password updated — saved in live mode.")
            else:
                st.error("Passwords must match and be at least 8 characters.")

        st.markdown("---")
        st.subheader("GDPR — Your Data")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📥 Export My Data", type="secondary"):
                import json
                demo_export = {
                    "user": {"username": "demo_user", "email": "demo@legalai.com", "role": role_key},
                    "cases": DEMO_CASES_DB,
                    "time_entries": DEMO_TIME_ENTRIES,
                    "exported_at": datetime.utcnow().isoformat()
                }
                st.download_button("Download my_data.json",
                                   json.dumps(demo_export, indent=2),
                                   file_name="my_data.json", mime="application/json")
        with c2:
            if st.button("🗑️ Delete My Account", type="secondary"):
                st.error("Demo mode — deletion disabled. In live mode, all your data would be permanently deleted (GDPR Art. 17).")

    with tab2:
        st.subheader("Find a Qualified Lawyer")
        referrals = {
            "🇺🇸 United States": ("Avvo", "https://www.avvo.com"),
            "🇬🇧 United Kingdom": ("Law Society", "https://solicitors.lawsociety.org.uk"),
            "🇮🇳 India": ("Bar Council of India", "https://www.barcouncilofindia.org"),
            "🇨🇦 Canada": ("Law Society BC", "https://www.lsbc.org"),
            "🇦🇺 Australia": ("Law Council", "https://www.lawcouncil.asn.au"),
            "🇪🇹 Ethiopia": ("Ethiopian Lawyers", "https://www.ethiopianlawyers.org"),
        }
        for country, (name, url) in referrals.items():
            st.markdown(f"**{country}** — [{name}]({url})")

    with tab3:
        st.subheader("System Information")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Application:**")
            st.markdown("- Version: **2.0.0**")
            st.markdown("- Framework: **Streamlit**")
            st.markdown("- AI Model: **Groq llama-3.1-8b-instant**")
            st.markdown("- Database: **SQLite (WAL)**")
        with c2:
            st.markdown("**Security:**")
            st.markdown("- Password hashing: **PBKDF2-SHA256 (600k)**")
            st.markdown("- Session timeout: **60 min**")
            st.markdown("- Brute-force: **5 attempts / 15 min lockout**")
            st.markdown("- OAuth2: **Google + Microsoft**")
        st.markdown("---")
        st.markdown("**GitHub:** [tasheayansa6/AI-lawyer-Assistance](https://github.com/tasheayansa6/AI-lawyer-Assistance)")
        st.markdown("**Run live version:** `streamlit run app.py`")
        st.markdown("**Run demo:** `streamlit run demo.py`")
