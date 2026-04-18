"""
Professional AI Lawyer Assistant - Streamlit Web Application
Fully refactored: secure auth, SQLite DB, real dashboards, audit logging,
session timeout, file validation, retry/backoff, export, password reset.
"""

import streamlit as st
import json
import os
import io
import csv
import logging
import time
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

# Internal modules
import db
import auth
from auth import UserRole, get_permissions, has_permission, current_user, current_role
from chat import LegalAssistant, JURISDICTION_INFO, VALID_JURISDICTIONS
from prompts import get_prompt, get_template_descriptions, list_templates
from legal_ai_tools import (get_tool_info, get_tools_by_use_case, get_all_tools,
                             get_all_use_cases, recommend_tools, compare_tools)
from document_parser import extract_text, get_document_info, is_legal_document, clean_legal_text
from case_summarizer import (summarize_case, fetch_case_from_url, compare_cases,
                              extract_case_metadata, validate_case_text, format_case_summary)

# ── Bootstrap ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
db.init_db()

st.set_page_config(
    page_title="AI Lawyer Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session timeout check ──────────────────────────────────────────────────────
auth.init_session()

# ── OAuth2 callback handling ───────────────────────────────────────────────────
qp = st.query_params
if "code" in qp and "state" in qp:
    username, err = auth.handle_oauth2_callback()
    if username:
        st.session_state["username"] = username
        st.session_state["last_active"] = datetime.utcnow().isoformat()
        st.query_params.clear()
        st.rerun()
    elif err:
        st.error(f"OAuth2 login failed: {err}")
        st.query_params.clear()

# ── CSS ────────────────────────────────────────────────────────────────────────
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── Auth page wrapper ── */
    .auth-wrapper {
        max-width: 480px;
        margin: 0 auto;
        padding: 2rem 0;
    }

    /* ── Logo / hero ── */
    .auth-logo {
        text-align: center;
        margin-bottom: 2rem;
    }
    .auth-logo .icon {
        font-size: 3.5rem;
        display: block;
        margin-bottom: 0.5rem;
    }
    .auth-logo h1 {
        font-size: 2rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .auth-logo p {
        color: #64748b;
        font-size: 0.95rem;
        margin: 0.4rem 0 0 0;
    }

    /* ── Auth card ── */
    .auth-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 2rem 2.2rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.07);
    }
    .auth-card h2 {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0 0 0.25rem 0;
    }
    .auth-card .subtitle {
        color: #64748b;
        font-size: 0.875rem;
        margin: 0 0 1.5rem 0;
    }

    /* ── Tab styling ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #f1f5f9;
        border-radius: 10px;
        padding: 4px;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 500;
        font-size: 0.875rem;
        color: #64748b;
        border: none;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #0f172a !important;
        font-weight: 600;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1.5px solid #e2e8f0 !important;
        padding: 10px 14px !important;
        font-size: 0.9rem !important;
        transition: border-color 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
    }

    /* ── Primary button ── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.2px;
        transition: opacity 0.2s, transform 0.1s;
        width: 100%;
    }
    .stButton > button[kind="primary"]:hover {
        opacity: 0.92;
        transform: translateY(-1px);
    }

    /* ── Secondary button ── */
    .stButton > button[kind="secondary"] {
        border-radius: 8px !important;
        border: 1.5px solid #e2e8f0 !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
    }

    /* ── OAuth buttons ── */
    .oauth-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        width: 100%;
        padding: 10px 16px;
        border-radius: 8px;
        border: 1.5px solid #e2e8f0;
        background: white;
        font-size: 0.875rem;
        font-weight: 500;
        color: #0f172a;
        cursor: pointer;
        text-decoration: none;
        transition: background 0.15s, border-color 0.15s;
    }
    .oauth-btn:hover { background: #f8fafc; border-color: #cbd5e1; }
    .oauth-btn.google { }
    .oauth-btn.microsoft { }

    /* ── Divider ── */
    .auth-divider {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 1.2rem 0;
        color: #94a3b8;
        font-size: 0.8rem;
    }
    .auth-divider::before, .auth-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: #e2e8f0;
    }

    /* ── Feature pills on landing ── */
    .feature-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
        margin: 1.5rem 0;
    }
    .feature-pill {
        display: flex;
        align-items: center;
        gap: 10px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 14px;
        font-size: 0.85rem;
        font-weight: 500;
        color: #334155;
    }
    .feature-pill .fi { font-size: 1.2rem; }

    /* ── Trust badges ── */
    .trust-row {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        margin-top: 1.5rem;
        flex-wrap: wrap;
    }
    .trust-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 500;
    }

    /* ── Role badge ── */
    .role-badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        color: white;
        font-size: 12px;
        font-weight: 600;
        margin-left: 8px;
    }

    /* ── Dashboard stat cards ── */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
    }
    .stat-number { font-size: 2rem; font-weight: 700; color: #1e40af; }
    .stat-label  { font-size: 0.8rem; font-weight: 600; color: #64748b; text-transform: uppercase; }

    .card {
        background: #f8fafc;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.8rem;
    }

    /* ── Password strength bar ── */
    .pw-bar { height: 4px; border-radius: 4px; margin-top: 6px; transition: width 0.3s; }

    /* ── Alert overrides ── */
    .stAlert { border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ── Helpers ────────────────────────────────────────────────────────────────────
def role_badge(role: str) -> str:
    color = UserRole.BADGE_COLOR.get(role, "#2c5282")
    name  = UserRole.DISPLAY.get(role, role)
    return f'<span class="role-badge" style="background:{color}">{name}</span>'

def require_login():
    if not current_user():
        st.warning("Please log in to access this feature.")
        st.stop()

def require_perm(perm: str):
    require_login()
    if not has_permission(current_user(), perm):
        st.error(f"Access denied — {perm} permission required.")
        st.stop()


# ── Auth pages ─────────────────────────────────────────────────────────────────
def _auth_logo():
    st.markdown("""
    <div class="auth-logo">
        <span class="icon">⚖️</span>
        <h1>LegalAI Assistant</h1>
        <p>Professional AI-powered legal information platform</p>
    </div>
    """, unsafe_allow_html=True)


def _feature_grid():
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-pill"><span class="fi">🔍</span> Legal Q&amp;A</div>
        <div class="feature-pill"><span class="fi">📄</span> Document Analysis</div>
        <div class="feature-pill"><span class="fi">⚖️</span> Case Summariser</div>
        <div class="feature-pill"><span class="fi">🌍</span> 6 Jurisdictions</div>
        <div class="feature-pill"><span class="fi">🔒</span> Secure &amp; Private</div>
        <div class="feature-pill"><span class="fi">🤖</span> AI-Powered</div>
    </div>
    <div class="trust-row">
        <span class="trust-item">🔐 600k PBKDF2 encryption</span>
        <span class="trust-item">📋 Full audit logging</span>
        <span class="trust-item">🛡️ PII filtering</span>
    </div>
    """, unsafe_allow_html=True)


def _oauth_buttons():
    google_url = auth.get_oauth2_auth_url("google")
    ms_url     = auth.get_oauth2_auth_url("microsoft")
    if not google_url and not ms_url:
        return
    st.markdown('<div class="auth-divider">or continue with</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if google_url:
            st.markdown(
                f'<a href="{google_url}" target="_self" class="oauth-btn google">'
                f'<img src="https://www.google.com/favicon.ico" width="16"/> Google</a>',
                unsafe_allow_html=True,
            )
        else:
            st.caption("Google OAuth2 not configured")
    with col2:
        if ms_url:
            st.markdown(
                f'<a href="{ms_url}" target="_self" class="oauth-btn microsoft">'
                f'<img src="https://www.microsoft.com/favicon.ico" width="16"/> Microsoft</a>',
                unsafe_allow_html=True,
            )
        else:
            st.caption("Microsoft OAuth2 not configured")


def page_login():
    # Centre the auth card
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        _auth_logo()

        tab_login, tab_register, tab_reset = st.tabs(["Sign In", "Create Account", "Reset Password"])

        # ── LOGIN ──────────────────────────────────────────────────────────────
        with tab_login:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<h2>Welcome back</h2><p class="subtitle">Sign in to your account to continue</p>', unsafe_allow_html=True)

            with st.form("login_form"):
                username  = st.text_input("Username", placeholder="Enter your username")
                password  = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submitted:
                if not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    with st.spinner("Authenticating..."):
                        ok, result = auth.login(username, password)
                    if ok:
                        st.session_state["username"] = result
                        st.session_state["last_active"] = datetime.utcnow().isoformat()
                        st.rerun()
                    else:
                        st.error(result)

            _oauth_buttons()
            st.markdown('</div>', unsafe_allow_html=True)

        # ── REGISTER ───────────────────────────────────────────────────────────
        with tab_register:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<h2>Create your account</h2><p class="subtitle">Join thousands of legal professionals</p>', unsafe_allow_html=True)

            with st.form("register_form"):
                new_user  = st.text_input("Username", placeholder="Choose a username (3–30 chars)")
                new_email = st.text_input("Email address", placeholder="you@example.com (optional)")
                new_pass  = st.text_input("Password", type="password",
                                          placeholder="Min 8 chars, upper + lower + digit")
                conf_pass = st.text_input("Confirm password", type="password",
                                          placeholder="Repeat your password")
                submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

            if submitted:
                ok, msg = auth.register(new_user, new_pass, conf_pass, email=new_email)
                if ok:
                    st.success("Account created — you can now sign in.")
                else:
                    st.error(msg)

            st.markdown("""
            <div style="margin-top:1rem;padding:12px;background:#f0fdf4;border:1px solid #bbf7d0;
                        border-radius:8px;font-size:0.8rem;color:#166534;">
                🔒 Your password is hashed with 600,000-iteration PBKDF2 + pepper.
                We never store it in plain text.
            </div>
            """, unsafe_allow_html=True)
            _oauth_buttons()
            st.markdown('</div>', unsafe_allow_html=True)

        # ── RESET PASSWORD ─────────────────────────────────────────────────────
        with tab_reset:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<h2>Reset password</h2><p class="subtitle">Get a token then set a new password</p>', unsafe_allow_html=True)

            step = st.radio("Step", ["1 — Request token", "2 — Set new password"],
                            horizontal=True, label_visibility="collapsed")

            if step == "1 — Request token":
                with st.form("req_reset"):
                    ru  = st.text_input("Username", placeholder="Your username")
                    sub = st.form_submit_button("Send Reset Token", use_container_width=True, type="primary")
                if sub:
                    token = auth.generate_reset_token(ru)
                    if token:
                        st.info(f"Your reset token (copy it now):\n\n`{token}`")
                        st.caption("Token expires in 1 hour.")
                    else:
                        st.error("Username not found.")
            else:
                with st.form("do_reset"):
                    tok  = st.text_input("Reset Token", placeholder="Paste your token here")
                    np1  = st.text_input("New Password", type="password")
                    np2  = st.text_input("Confirm New Password", type="password")
                    sub2 = st.form_submit_button("Reset Password", use_container_width=True, type="primary")
                if sub2:
                    ok, msg = auth.reset_password(tok, np1, np2)
                    if ok:
                        st.success(msg + " — you can now sign in.")
                    else:
                        st.error(msg)

            st.markdown('</div>', unsafe_allow_html=True)

        # ── Feature grid below tabs ────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        _feature_grid()


# ── Sidebar ────────────────────────────────────────────────────────────────────
def render_sidebar():
    username = current_user()
    role     = current_role()
    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="padding:1rem 0 0.5rem 0;text-align:center;">
            <div style="font-size:2rem;">⚖️</div>
            <div style="font-weight:800;font-size:1.1rem;color:#0f172a;letter-spacing:-0.3px;">
                LegalAI
            </div>
            <div style="font-size:0.75rem;color:#94a3b8;margin-top:2px;">
                Professional Legal Platform
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # User info
        if username:
            role_color = UserRole.BADGE_COLOR.get(role, "#2c5282")
            role_name  = UserRole.DISPLAY.get(role, role)
            st.markdown(f"""
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
                        padding:12px 14px;margin-bottom:1rem;">
                <div style="font-weight:600;color:#0f172a;font-size:0.9rem;">👤 {username}</div>
                <div style="margin-top:4px;">
                    <span style="background:{role_color};color:white;padding:2px 10px;
                                 border-radius:20px;font-size:0.72rem;font-weight:600;">
                        {role_name}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            can, msg = auth.can_query(username)
            icon = "✅" if can else "🚫"
            st.caption(f"{icon} {msg}")

        st.markdown("---")

        # Navigation
        perms = get_permissions(role)
        pages = ["🏠 Q&A"]
        if perms.get("document_upload"):
            pages.append("📄 Documents")
        pages.append("⚖️ Cases")
        pages.append("🤖 AI Tools")
        if role == UserRole.ADMINISTRATOR:
            pages.append("🔧 Admin")
        if role == UserRole.LICENSED_LAWYER:
            pages.append("👨‍⚖️ Lawyer")
        if role == UserRole.PARALEGAL:
            pages.append("📋 Paralegal")
        if role == UserRole.COMPLIANCE_OFFICER:
            pages.append("🔍 Compliance")
        pages.append("⚙️ Settings")

        selected = st.radio("Navigation", pages, label_visibility="collapsed")

        st.markdown("---")
        if username:
            if st.button("🚪 Sign Out", use_container_width=True):
                auth.logout()
                st.rerun()

        st.markdown("""
        <div style="text-align:center;padding:0.5rem 0;font-size:0.72rem;color:#94a3b8;">
            LegalAI v2.0 · Secure Platform<br>
            Not a substitute for legal advice
        </div>
        """, unsafe_allow_html=True)

    # Strip emoji prefix for routing
    return selected.split(" ", 1)[1] if " " in selected else selected


# ── Q&A Page ───────────────────────────────────────────────────────────────────
def page_qa():
    require_login()
    st.title("⚖️ Legal Q&A")
    username = current_user()
    role     = current_role()
    perms    = get_permissions(role)
    max_tok  = perms.get("max_tokens", 300)

    col1, col2 = st.columns([3, 1])
    with col1:
        jurisdiction = st.selectbox("Jurisdiction", list(VALID_JURISDICTIONS))
    with col2:
        template_type = st.selectbox("Template", list_templates())

    query = st.text_area("Your legal question", height=120,
                         placeholder="e.g. What is a power of attorney?")
    max_tokens = st.slider("Response length (tokens)", 100, max_tok, min(500, max_tok))

    if st.button("Ask", type="primary", use_container_width=True):
        if not query.strip():
            st.warning("Please enter a question.")
            return
        can, msg = auth.can_query(username)
        if not can:
            st.error(msg)
            return
        formatted = get_prompt(template_type, query)
        with st.spinner("Thinking..."):
            assistant = LegalAssistant()
            response  = assistant.ask_legal(formatted, jurisdiction, max_tokens)
        auth.increment_query_count()
        db.log_query_db(username, jurisdiction, query, response)
        db.audit(username, "QUERY", f"jurisdiction={jurisdiction}")

        st.markdown("### Response")
        st.markdown(response)

        # Export
        if perms.get("export_pdf_reports"):
            st.download_button("Download response (.txt)", response,
                               file_name="legal_response.txt", mime="text/plain")

    # Chat history from DB
    with st.expander("Query History"):
        with db.get_conn() as conn:
            rows = conn.execute(
                "SELECT ts, jurisdiction, query, response FROM query_log "
                "WHERE username=? ORDER BY id DESC LIMIT 20", (username,)
            ).fetchall()
        if rows:
            for r in rows:
                st.markdown(f"**{r['ts']}** [{r['jurisdiction']}] {r['query'][:80]}...")
        else:
            st.caption("No history yet.")


# ── Documents Page ─────────────────────────────────────────────────────────────
def page_documents():
    require_perm("document_upload")
    st.title("📄 Document Analysis")
    username = current_user()

    uploaded = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])
    if uploaded:
        ok, err = auth.validate_file(uploaded)
        if not ok:
            st.error(err)
            return
        uploaded.seek(0)
        with st.spinner("Extracting text..."):
            try:
                info = get_document_info(uploaded)
                uploaded.seek(0)
                text = extract_text(uploaded)
            except Exception as e:
                st.error(f"Failed to parse document: {e}")
                return

        st.success(f"Parsed: {info.get('name')} — {info.get('word_count',0)} words, {info.get('size_kb',0)} KB")

        legal = is_legal_document(text)
        if legal["is_legal"]:
            st.info(f"Legal document detected (confidence {legal['confidence']:.0%}). Indicators: {', '.join(legal['indicators'][:5])}")

        with st.expander("Document Preview"):
            st.text(text[:1000] + ("..." if len(text) > 1000 else ""))

        st.markdown("### Ask about this document")
        doc_q = st.text_area("Question about the document", height=80)
        jurisdiction = st.selectbox("Jurisdiction", list(VALID_JURISDICTIONS), key="doc_jur")
        if st.button("Analyse", type="primary"):
            if doc_q.strip():
                can, msg = auth.can_query(username)
                if not can:
                    st.error(msg)
                    return
                prompt = f"Based on this document:\n\n{text[:3000]}\n\nQuestion: {doc_q}"
                with st.spinner("Analysing..."):
                    assistant = LegalAssistant()
                    answer = assistant.ask_legal(prompt, jurisdiction, 800)
                auth.increment_query_count()
                db.log_query_db(username, jurisdiction, doc_q, answer)
                db.audit(username, "DOC_QUERY", info.get("name",""))
                st.markdown("### Analysis")
                st.markdown(answer)
                st.download_button("Download analysis (.txt)", answer,
                                   file_name="doc_analysis.txt", mime="text/plain")
            else:
                st.warning("Enter a question first.")


# ── Cases Page ─────────────────────────────────────────────────────────────────
def page_cases():
    require_login()
    st.title("⚖️ Case Management")
    username = current_user()
    role     = current_role()

    tab1, tab2, tab3 = st.tabs(["Summarise Case", "Compare Cases", "My Cases"])

    with tab1:
        st.subheader("Summarise a Case")
        input_method = st.radio("Input method", ["Paste text", "Fetch from URL"], horizontal=True)
        case_text = ""
        if input_method == "Paste text":
            case_text = st.text_area("Paste case text", height=200)
        else:
            url = st.text_input("Case URL")
            if st.button("Fetch"):
                ok, err = auth.validate_url(url)
                if not ok:
                    st.error(err)
                else:
                    with st.spinner("Fetching..."):
                        try:
                            case_text = fetch_case_from_url(url)
                            st.success(f"Fetched {len(case_text)} characters")
                            st.text_area("Fetched text", case_text[:500], height=120)
                        except Exception as e:
                            st.error(str(e))

        if case_text:
            val = validate_case_text(case_text)
            st.caption(f"Words: {val['word_count']} | Likely legal case: {'Yes' if val['likely_case'] else 'No'}")
            meta = extract_case_metadata(case_text)
            if any(meta.values()):
                with st.expander("Extracted Metadata"):
                    for k, v in meta.items():
                        if v:
                            st.markdown(f"**{k.title()}:** {v}")

        if st.button("Summarise", type="primary", disabled=not bool(case_text)):
            can, msg = auth.can_query(username)
            if not can:
                st.error(msg)
            else:
                with st.spinner("Summarising..."):
                    summary = summarize_case(case_text)
                auth.increment_query_count()
                db.audit(username, "CASE_SUMMARISE")
                st.markdown("### Summary")
                st.markdown(format_case_summary(summary))
                st.download_button("Download summary (.txt)", summary,
                                   file_name="case_summary.txt", mime="text/plain")

    with tab2:
        st.subheader("Compare Two Cases")
        c1 = st.text_area("Case A", height=150)
        c2 = st.text_area("Case B", height=150)
        if st.button("Compare", type="primary"):
            if c1.strip() and c2.strip():
                can, msg = auth.can_query(username)
                if not can:
                    st.error(msg)
                else:
                    with st.spinner("Comparing..."):
                        result = compare_cases(c1, c2)
                    auth.increment_query_count()
                    db.audit(username, "CASE_COMPARE")
                    st.markdown("### Comparison")
                    st.markdown(result)
            else:
                st.warning("Provide text for both cases.")

    with tab3:
        st.subheader("My Cases")
        if role in (UserRole.LICENSED_LAWYER, UserRole.PARALEGAL, UserRole.ADMINISTRATOR):
            with st.expander("Create New Case"):
                with st.form("new_case"):
                    cn   = st.text_input("Case Name")
                    cli  = st.text_input("Client Name")
                    ct   = st.selectbox("Type", ["Civil Litigation","Corporate","Family","Criminal","Real Estate","IP"])
                    jur  = st.selectbox("Jurisdiction", list(VALID_JURISDICTIONS))
                    sub  = st.form_submit_button("Create")
                if sub and cn and cli:
                    cid = db.create_case(username, cn, cli, ct, jur)
                    db.audit(username, "CASE_CREATE", f"id={cid} name={cn}")
                    st.success(f"Case '{cn}' created (ID {cid})")

            cases = db.get_cases(username)
            if cases:
                for c in cases:
                    with st.expander(f"📋 {c['name']} — {c['status']}"):
                        st.markdown(f"**Client:** {c['client_name']}  |  **Type:** {c['case_type']}  |  **Jurisdiction:** {c['jurisdiction']}")
                        st.caption(f"Created: {c['created_at']}")
                        new_status = st.selectbox("Update status", ["Active","Review","Completed","Closed"],
                                                  key=f"status_{c['id']}")
                        if st.button("Update", key=f"upd_{c['id']}"):
                            db.update_case_status(c["id"], new_status)
                            db.audit(username, "CASE_STATUS_UPDATE", f"id={c['id']} status={new_status}")
                            st.success("Status updated")
                            st.rerun()
            else:
                st.info("No cases yet.")
        else:
            st.info("Case management is available for lawyers, paralegals, and admins.")


# ── AI Tools Page ──────────────────────────────────────────────────────────────
def page_ai_tools():
    require_login()
    st.title("🤖 Legal AI Tools")
    tab1, tab2, tab3 = st.tabs(["Browse Tools", "Recommend", "Compare"])

    with tab1:
        tools = get_all_tools()
        for name, info in tools.items():
            with st.expander(f"**{name}**"):
                st.markdown(info["description"])
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Best for:** {', '.join(info['best_for'])}")
                    st.markdown(f"**Pricing:** {info['pricing']}")
                with col2:
                    st.markdown(f"**Strengths:** {', '.join(info['strengths'])}")
                    st.markdown(f"**Limitations:** {', '.join(info['limitations'])}")

    with tab2:
        st.subheader("Get a Recommendation")
        col1, col2, col3 = st.columns(3)
        with col1:
            budget = st.selectbox("Budget", ["low","medium","high"])
        with col2:
            size = st.selectbox("Firm size", ["small","medium","large"])
        with col3:
            area = st.selectbox("Practice area", get_all_use_cases())
        if st.button("Recommend", type="primary"):
            recs = recommend_tools(budget, size, area)
            if recs:
                st.success(f"Top picks: {', '.join(recs)}")
                for r in recs:
                    info = get_tool_info(r)
                    st.markdown(f"**{r}** — {info.get('description','')}")
            else:
                st.info("No exact match — try adjusting filters.")

    with tab3:
        st.subheader("Compare Tools Side-by-Side")
        all_names = list(get_all_tools().keys())
        selected  = st.multiselect("Select tools to compare", all_names, max_selections=4)
        if selected:
            comparison = compare_tools(selected)
            import pandas as pd
            rows = []
            for tool, data in comparison.items():
                rows.append({
                    "Tool":        tool,
                    "Best For":    ", ".join(data["best_for"]),
                    "Pricing":     data["pricing"],
                    "Ideal Users": ", ".join(data["ideal_users"]),
                    "Strengths":   ", ".join(data["strengths"]),
                })
            st.dataframe(pd.DataFrame(rows).set_index("Tool"), use_container_width=True)


# ── Admin Dashboard ────────────────────────────────────────────────────────────
def page_admin():
    require_perm("modify_system_settings")
    st.title("🔧 Administrator Dashboard")
    username = current_user()

    users = db.list_users()
    role_counts = {}
    for u in users:
        r = u.get("role", UserRole.GENERAL_PUBLIC)
        role_counts[r] = role_counts.get(r, 0) + 1

    # Stats
    cols = st.columns(4)
    stats = [
        ("Total Users",     len(users)),
        ("Admins",          role_counts.get(UserRole.ADMINISTRATOR, 0)),
        ("Lawyers",         role_counts.get(UserRole.LICENSED_LAWYER, 0)),
        ("Public",          role_counts.get(UserRole.GENERAL_PUBLIC, 0)),
    ]
    for col, (label, val) in zip(cols, stats):
        with col:
            st.markdown(f'<div class="stat-card"><div class="stat-label">{label}</div><div class="stat-number">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["User Management", "Role Assignment", "Audit Log", "System"])

    with tab1:
        st.subheader("Users")
        search = st.text_input("Search by username or role")
        filtered = [u for u in users if
                    (not search or search.lower() in u["username"].lower()
                     or search.lower() in u.get("role","").lower())]
        for u in filtered:
            with st.expander(f"👤 {u['username']}  ({UserRole.DISPLAY.get(u.get('role',''), u.get('role',''))})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Created:** {u.get('created_at','')[:10]}")
                    st.markdown(f"**Last login:** {(u.get('last_login') or 'Never')[:10]}")
                    st.markdown(f"**Email:** {u.get('email') or '—'}")
                with col2:
                    new_role = st.selectbox("New role", UserRole.ALL,
                                            index=UserRole.ALL.index(u.get("role", UserRole.GENERAL_PUBLIC)),
                                            key=f"role_{u['username']}")
                    if st.button("Update role", key=f"upd_{u['username']}"):
                        ok, msg = auth.assign_role(u["username"], new_role, username)
                        st.success(msg) if ok else st.error(msg)
                        st.rerun()
                    if st.button("Delete user", key=f"del_{u['username']}", type="secondary"):
                        if u["username"] != username:
                            ok, msg = auth.delete_account(u["username"], username)
                            st.success(msg) if ok else st.error(msg)
                            st.rerun()
                        else:
                            st.error("Cannot delete your own account.")

        # Create user
        st.markdown("---")
        st.subheader("Create New User")
        with st.form("create_user"):
            nu = st.text_input("Username")
            np = st.text_input("Password", type="password")
            nr = st.selectbox("Role", UserRole.ALL)
            ne = st.text_input("Email (optional)")
            sub = st.form_submit_button("Create")
        if sub:
            ok, msg = auth.register(nu, np, np, email=ne)
            if ok:
                auth.assign_role(nu, nr, username)
                st.success(f"User '{nu}' created with role {nr}")
            else:
                st.error(msg)

        # Export users CSV
        if st.button("Export users as CSV"):
            buf = io.StringIO()
            w = csv.DictWriter(buf, fieldnames=["username","role","email","created_at","last_login"])
            w.writeheader()
            for u in users:
                w.writerow({k: u.get(k,"") for k in ["username","role","email","created_at","last_login"]})
            st.download_button("Download users.csv", buf.getvalue(),
                               file_name="users.csv", mime="text/csv")

    with tab2:
        st.subheader("Bulk Role Assignment")
        with st.form("bulk_role"):
            target = st.text_input("Username")
            role   = st.selectbox("Role", UserRole.ALL)
            sub    = st.form_submit_button("Assign")
        if sub:
            ok, msg = auth.assign_role(target, role, username)
            st.success(msg) if ok else st.error(msg)

        st.markdown("**Role distribution:**")
        import pandas as pd
        if role_counts:
            df = pd.DataFrame(list(role_counts.items()), columns=["Role","Count"])
            df["Role"] = df["Role"].map(lambda r: UserRole.DISPLAY.get(r, r))
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Audit Log")
        logs = db.get_audit_log(200)
        if logs:
            import pandas as pd
            df = pd.DataFrame(logs)[["ts","username","action","detail"]]
            df["ts"] = df["ts"].str[:19]
            st.dataframe(df, use_container_width=True, hide_index=True)
            buf = io.StringIO()
            df.to_csv(buf, index=False)
            st.download_button("Export audit log (.csv)", buf.getvalue(),
                               file_name="audit_log.csv", mime="text/csv")
        else:
            st.info("No audit entries yet.")

    with tab4:
        st.subheader("System Info")
        st.markdown(f"**DB path:** `{db.DB_PATH}`")
        st.markdown(f"**Session timeout:** {auth.SESSION_TIMEOUT_MINUTES} minutes")
        st.markdown(f"**Max file size:** {auth.MAX_FILE_SIZE_MB} MB")
        st.markdown(f"**PBKDF2 iterations:** {auth.PBKDF2_ITERATIONS:,}")
        if st.button("Backup DB"):
            import shutil
            backup = f"legal_ai_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(db.DB_PATH, backup)
            st.success(f"Backup saved as {backup}")


# ── Lawyer Dashboard ───────────────────────────────────────────────────────────
def page_lawyer():
    require_perm("case_law_research")
    st.title("👨‍⚖️ Licensed Lawyer Dashboard")
    username = current_user()

    tab1, tab2, tab3, tab4 = st.tabs(["Cases", "Research", "Time Tracking", "Billing"])

    with tab1:
        st.subheader("Case Management")
        with st.expander("Create New Case"):
            with st.form("lw_new_case"):
                cn  = st.text_input("Case Name")
                cli = st.text_input("Client Name")
                ct  = st.selectbox("Type", ["Civil Litigation","Corporate","Family","Criminal","Real Estate","IP"])
                jur = st.selectbox("Jurisdiction", list(VALID_JURISDICTIONS))
                sub = st.form_submit_button("Create")
            if sub and cn and cli:
                cid = db.create_case(username, cn, cli, ct, jur)
                db.audit(username, "CASE_CREATE", f"id={cid}")
                st.success(f"Case '{cn}' created")

        cases = db.get_cases(username)
        if cases:
            import pandas as pd
            df = pd.DataFrame(cases)[["id","name","client_name","case_type","jurisdiction","status","created_at"]]
            df["created_at"] = df["created_at"].str[:10]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No cases yet.")

    with tab2:
        st.subheader("Legal Research")
        query = st.text_area("Research query", height=100)
        col1, col2 = st.columns(2)
        with col1:
            jur = st.selectbox("Jurisdiction", list(VALID_JURISDICTIONS), key="res_jur")
        with col2:
            depth = st.selectbox("Depth", ["Standard (500 tokens)","Detailed (800 tokens)","Comprehensive (1000 tokens)"])
        tok_map = {"Standard (500 tokens)": 500, "Detailed (800 tokens)": 800, "Comprehensive (1000 tokens)": 1000}
        if st.button("Research", type="primary"):
            if query.strip():
                can, msg = auth.can_query(username)
                if not can:
                    st.error(msg)
                else:
                    with st.spinner("Researching..."):
                        assistant = LegalAssistant()
                        result = assistant.ask_legal(query, jur, tok_map[depth])
                    auth.increment_query_count()
                    db.log_query_db(username, jur, query, result)
                    db.audit(username, "LEGAL_RESEARCH")
                    st.markdown("### Research Results")
                    st.markdown(result)
                    st.download_button("Export (.txt)", result,
                                       file_name="research.txt", mime="text/plain")
            else:
                st.warning("Enter a research query.")

        st.markdown("---")
        st.subheader("Jurisdiction Comparison")
        col1, col2 = st.columns(2)
        with col1:
            j1 = st.selectbox("Jurisdiction A", list(VALID_JURISDICTIONS), key="jc1")
        with col2:
            j2 = st.selectbox("Jurisdiction B", list(VALID_JURISDICTIONS), key="jc2")
        topic = st.text_input("Legal topic to compare")
        if st.button("Compare Jurisdictions", type="primary"):
            if topic.strip():
                can, msg = auth.can_query(username)
                if not can:
                    st.error(msg)
                else:
                    prompt = (f"Compare the law on '{topic}' between {j1} and {j2}. "
                              "Cover: key differences, similarities, practical implications.")
                    with st.spinner("Comparing..."):
                        assistant = LegalAssistant()
                        result = assistant.ask_legal(prompt, j1, 800)
                    auth.increment_query_count()
                    db.audit(username, "JURISDICTION_COMPARE", f"{j1} vs {j2}")
                    st.markdown("### Comparison")
                    st.markdown(result)
            else:
                st.warning("Enter a legal topic.")

    with tab3:
        st.subheader("Time Tracking")
        cases = db.get_cases(username)
        case_options = {f"{c['name']} (#{c['id']})": c["id"] for c in cases} if cases else {}

        with st.expander("Log Time Entry"):
            with st.form("time_entry"):
                case_sel  = st.selectbox("Case", list(case_options.keys()) or ["No cases"])
                activity  = st.selectbox("Activity", ["Research","Drafting","Court Appearance","Client Meeting","Review","Admin"])
                hours     = st.number_input("Hours", min_value=0.25, max_value=24.0, value=1.0, step=0.25)
                rate      = st.number_input("Rate/hour ($)", min_value=0.0, max_value=2000.0, value=250.0, step=10.0)
                desc      = st.text_area("Description", height=80)
                sub       = st.form_submit_button("Log")
            if sub and case_options:
                cid = case_options.get(case_sel)
                db.log_time(username, cid, activity, hours, rate, desc)
                db.audit(username, "TIME_LOG", f"hours={hours} rate={rate}")
                st.success(f"Logged {hours}h @ ${rate}/h = ${hours*rate:.2f}")

        entries = db.get_time_entries(username)
        if entries:
            import pandas as pd
            df = pd.DataFrame(entries)[["logged_at","activity","hours","rate","description"]]
            df["amount"] = df["hours"] * df["rate"]
            df["logged_at"] = df["logged_at"].str[:10]
            st.dataframe(df, use_container_width=True, hide_index=True)
            total = df["amount"].sum()
            st.metric("Total billed", f"${total:,.2f}")

            buf = io.StringIO()
            df.to_csv(buf, index=False)
            st.download_button("Export time log (.csv)", buf.getvalue(),
                               file_name="time_log.csv", mime="text/csv")
        else:
            st.info("No time entries yet.")

    with tab4:
        st.subheader("Billing Summary")
        entries = db.get_time_entries(username)
        if entries:
            import pandas as pd
            df = pd.DataFrame(entries)
            df["amount"] = df["hours"] * df["rate"]
            total   = df["amount"].sum()
            this_mo = df[df["logged_at"].str[:7] == datetime.utcnow().strftime("%Y-%m")]["amount"].sum()
            col1, col2, col3 = st.columns(3)
            col1.metric("Total billed (all time)", f"${total:,.2f}")
            col2.metric("This month", f"${this_mo:,.2f}")
            col3.metric("Entries", len(df))

            # Invoice download
            lines = [f"INVOICE — {datetime.utcnow().strftime('%Y-%m-%d')}\n",
                     f"Attorney: {username}\n\n"]
            for _, row in df.iterrows():
                lines.append(f"{row['logged_at'][:10]}  {row['activity']}  {row['hours']}h @ ${row['rate']}/h = ${row['amount']:.2f}\n")
            lines.append(f"\nTOTAL: ${total:,.2f}\n")
            st.download_button("Download Invoice (.txt)", "".join(lines),
                               file_name="invoice.txt", mime="text/plain")
        else:
            st.info("No billing data yet.")


# ── Paralegal Dashboard ────────────────────────────────────────────────────────
def page_paralegal():
    require_login()
    if current_role() not in (UserRole.PARALEGAL, UserRole.ADMINISTRATOR):
        st.error("Access denied.")
        return
    st.title("📋 Paralegal Dashboard")
    username = current_user()

    tab1, tab2 = st.tabs(["Document Processing", "Legal Research Support"])

    with tab1:
        st.subheader("Document Processing")
        uploaded = st.file_uploader("Upload document for processing", type=["pdf","docx"])
        if uploaded:
            ok, err = auth.validate_file(uploaded)
            if not ok:
                st.error(err)
            else:
                uploaded.seek(0)
                try:
                    info = get_document_info(uploaded)
                    uploaded.seek(0)
                    text = extract_text(uploaded)
                    st.success(f"Processed: {info['name']} — {info['word_count']} words")
                    legal = is_legal_document(text)
                    st.info(f"Legal document: {'Yes' if legal['is_legal'] else 'No'} (confidence {legal['confidence']:.0%})")
                    with st.expander("Preview"):
                        st.text(text[:800])
                    cleaned = clean_legal_text(text)
                    st.download_button("Download cleaned text", cleaned,
                                       file_name="cleaned.txt", mime="text/plain")
                    db.audit(username, "DOC_PROCESS", info["name"])
                except Exception as e:
                    st.error(str(e))

    with tab2:
        st.subheader("Legal Research Support")
        query = st.text_area("Research query", height=100)
        jur   = st.selectbox("Jurisdiction", list(VALID_JURISDICTIONS))
        if st.button("Research", type="primary"):
            if query.strip():
                can, msg = auth.can_query(username)
                if not can:
                    st.error(msg)
                else:
                    with st.spinner("Researching..."):
                        assistant = LegalAssistant()
                        result = assistant.ask_legal(query, jur, 600)
                    auth.increment_query_count()
                    db.log_query_db(username, jur, query, result)
                    db.audit(username, "PARALEGAL_RESEARCH")
                    st.markdown("### Results")
                    st.markdown(result)
            else:
                st.warning("Enter a query.")


# ── Compliance Dashboard ───────────────────────────────────────────────────────
def page_compliance():
    require_perm("access_audit_logs")
    st.title("🔍 Compliance Officer Dashboard")
    username = current_user()

    tab1, tab2, tab3 = st.tabs(["Audit Log", "Query Analytics", "Compliance Report"])

    with tab1:
        st.subheader("Full Audit Log")
        limit = st.slider("Entries to show", 50, 500, 200)
        logs  = db.get_audit_log(limit)
        if logs:
            import pandas as pd
            df = pd.DataFrame(logs)[["ts","username","action","detail","ip"]]
            df["ts"] = df["ts"].str[:19]
            st.dataframe(df, use_container_width=True, hide_index=True)
            buf = io.StringIO()
            df.to_csv(buf, index=False)
            st.download_button("Export audit log (.csv)", buf.getvalue(),
                               file_name="audit_log.csv", mime="text/csv")
        else:
            st.info("No audit entries.")

    with tab2:
        st.subheader("Query Analytics")
        with db.get_conn() as conn:
            rows = conn.execute(
                "SELECT jurisdiction, COUNT(*) as cnt FROM query_log GROUP BY jurisdiction ORDER BY cnt DESC"
            ).fetchall()
            total = conn.execute("SELECT COUNT(*) FROM query_log").fetchone()[0]
        st.metric("Total queries", total)
        if rows:
            import pandas as pd
            df = pd.DataFrame([dict(r) for r in rows])
            st.bar_chart(df.set_index("jurisdiction")["cnt"])

    with tab3:
        st.subheader("Compliance Report")
        if st.button("Generate Report", type="primary"):
            logs  = db.get_audit_log(1000)
            users = db.list_users()
            with db.get_conn() as conn:
                q_count = conn.execute("SELECT COUNT(*) FROM query_log").fetchone()[0]
            lines = [
                f"COMPLIANCE REPORT — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n",
                f"Total users: {len(users)}\n",
                f"Total queries: {q_count}\n",
                f"Audit entries: {len(logs)}\n\n",
                "Recent audit events:\n",
            ]
            for entry in logs[:50]:
                lines.append(f"  {entry['ts'][:19]}  {entry['username']}  {entry['action']}  {entry['detail']}\n")
            report = "".join(lines)
            st.text_area("Report preview", report[:2000], height=300)
            st.download_button("Download full report (.txt)", report,
                               file_name="compliance_report.txt", mime="text/plain")
            db.audit(username, "COMPLIANCE_REPORT_GENERATED")


# ── Settings Page ──────────────────────────────────────────────────────────────
def page_settings():
    require_login()
    st.title("⚙️ Settings")
    username = current_user()
    role     = current_role()

    tab1, tab2, tab3 = st.tabs(["My Account", "Lawyer Referrals", "System Info"])

    with tab1:
        st.subheader("Change Password")
        with st.form("change_pw"):
            old_pw  = st.text_input("Current password", type="password")
            new_pw  = st.text_input("New password", type="password")
            conf_pw = st.text_input("Confirm new password", type="password")
            sub     = st.form_submit_button("Update Password")
        if sub:
            ok, result = auth.login(username, old_pw)
            if not ok:
                st.error("Current password is incorrect.")
            else:
                import secrets as _sec
                token = auth.generate_reset_token(username)
                ok2, msg = auth.reset_password(token, new_pw, conf_pw)
                if ok2:
                    st.success(msg)
                else:
                    st.error(msg)

        st.markdown("---")
        st.subheader("Account Info")
        user = db.get_user(username)
        if user:
            st.markdown(f"**Username:** {user['username']}")
            st.markdown(f"**Role:** {UserRole.DISPLAY.get(role, role)}")
            st.markdown(f"**Email:** {user.get('email') or '—'}")
            st.markdown(f"**Member since:** {(user.get('created_at') or '')[:10]}")
            st.markdown(f"**Last login:** {(user.get('last_login') or 'Never')[:10]}")

        st.markdown("---")
        st.subheader("Delete My Account")
        st.warning("This is permanent and cannot be undone.")
        confirm = st.text_input("Type your username to confirm deletion")
        if st.button("Delete Account", type="secondary"):
            if confirm == username:
                auth.delete_account(username, username)
                auth.logout()
                st.success("Account deleted.")
                st.rerun()
            else:
                st.error("Username does not match.")

    with tab2:
        st.subheader("Find a Lawyer")
        referrals = {
            "US":        "https://www.avvo.com",
            "UK":        "https://solicitors.lawsociety.org.uk",
            "India":     "https://www.barcouncilofindia.org",
            "Canada":    "https://www.lsbc.org",
            "Australia": "https://www.lawcouncil.asn.au",
            "Ethiopia":  "https://www.ethiopianlawyers.org",
        }
        for jur, url in referrals.items():
            st.markdown(f"**{jur}:** [{url}]({url})")

    with tab3:
        st.subheader("System Information")
        st.markdown(f"**Session timeout:** {auth.SESSION_TIMEOUT_MINUTES} min")
        st.markdown(f"**Max upload size:** {auth.MAX_FILE_SIZE_MB} MB")
        st.markdown(f"**Password hashing:** PBKDF2-HMAC-SHA256 ({auth.PBKDF2_ITERATIONS:,} iterations)")
        st.markdown(f"**Database:** SQLite (`{db.DB_PATH}`)")
        st.markdown(f"**Groq model:** {os.getenv('GROQ_MODEL','llama-3.1-8b-instant')}")
        st.markdown(f"**Response cache TTL:** {os.getenv('RESPONSE_CACHE_TTL','300')}s")


# ── Disclaimer ─────────────────────────────────────────────────────────────────
def show_disclaimer():
    if st.session_state.get("disclaimer_accepted"):
        return True
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("""
        <div style="background:#fffbeb;border:1px solid #fcd34d;border-radius:14px;
                    padding:2rem;text-align:center;margin-top:3rem;">
            <div style="font-size:2.5rem;margin-bottom:0.75rem;">⚖️</div>
            <h2 style="color:#92400e;font-size:1.3rem;margin:0 0 0.75rem 0;font-weight:700;">
                Legal Disclaimer
            </h2>
            <p style="color:#78350f;font-size:0.9rem;line-height:1.6;margin:0 0 1.5rem 0;">
                This application provides <strong>general legal information only</strong>.
                It does not constitute legal advice and does not create an attorney-client relationship.
                Always consult a qualified, licensed attorney for advice specific to your situation.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("I understand and accept", type="primary", use_container_width=True):
            st.session_state["disclaimer_accepted"] = True
            st.rerun()
    return False


# ── Main router ────────────────────────────────────────────────────────────────
def main():
    if not current_user():
        page_login()
        return

    if not show_disclaimer():
        return

    page = render_sidebar()

    if page == "Q&A":
        page_qa()
    elif page == "Documents":
        page_documents()
    elif page == "Cases":
        page_cases()
    elif page == "AI Tools":
        page_ai_tools()
    elif page == "Admin":
        page_admin()
    elif page == "Lawyer":
        page_lawyer()
    elif page == "Paralegal":
        page_paralegal()
    elif page == "Compliance":
        page_compliance()
    elif page == "Settings":
        page_settings()


if __name__ == "__main__":
    main()
