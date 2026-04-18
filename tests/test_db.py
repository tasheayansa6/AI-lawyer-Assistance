"""Unit tests for db.py"""
import pytest, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ["DB_PATH"] = ":memory:"

import db; db.init_db()

def test_create_and_get_user():
    db.create_user("dbuser1", "hash", "salt", email="db@test.com")
    user = db.get_user("dbuser1")
    assert user is not None
    assert user["email"] == "db@test.com"

def test_case_insensitive_lookup():
    db.create_user("CaseUser", "hash", "salt")
    user = db.get_user_by_username_ci("caseuser")
    assert user is not None

def test_update_user():
    db.create_user("updateuser", "hash", "salt")
    db.update_user("updateuser", role="licensed_lawyer")
    user = db.get_user("updateuser")
    assert user["role"] == "licensed_lawyer"

def test_delete_user():
    db.create_user("deluser", "hash", "salt")
    db.delete_user("deluser")
    assert db.get_user("deluser") is None

def test_create_and_get_case():
    db.create_user("caseowner", "hash", "salt")
    cid = db.create_case("caseowner", "Test Case", "Client A", "Civil", "US")
    assert cid > 0
    cases = db.get_cases("caseowner")
    assert len(cases) == 1
    assert cases[0]["name"] == "Test Case"

def test_log_and_get_time():
    db.create_user("timeuser", "hash", "salt")
    db.log_time("timeuser", None, "Research", 2.5, 200.0, "Test entry")
    entries = db.get_time_entries("timeuser")
    assert len(entries) == 1
    assert entries[0]["hours"] == 2.5

def test_save_and_get_document():
    db.create_user("docuser", "hash", "salt")
    did = db.save_document("docuser", "test.pdf", b"content", "text content", "Contracts")
    assert did > 0
    docs = db.get_documents("docuser")
    assert len(docs) == 1
    assert docs[0]["filename"] == "test.pdf"

def test_search_documents():
    db.create_user("searchuser", "hash", "salt")
    db.save_document("searchuser", "contract.pdf", b"data", "This is a contract agreement", "Contracts")
    results = db.search_documents("searchuser", "contract")
    assert len(results) >= 1

def test_gdpr_export():
    db.create_user("gdpruser", "hash", "salt")
    db.create_case("gdpruser", "GDPR Case", "Client", "Civil", "US")
    data = db.export_user_data("gdpruser")
    assert "user" in data
    assert "cases" in data
    assert "password_hash" not in data["user"]

def test_gdpr_delete():
    db.create_user("gdprdelete", "hash", "salt")
    db.create_case("gdprdelete", "Case", "Client", "Civil", "US")
    db.delete_all_user_data("gdprdelete")
    assert db.get_user("gdprdelete") is None
    assert db.get_cases("gdprdelete") == []

def test_audit_log():
    db.audit("audituser", "TEST_ACTION", "detail here")
    logs = db.get_audit_log(10)
    actions = [l["action"] for l in logs]
    assert "TEST_ACTION" in actions

def test_list_users_pagination():
    for i in range(5):
        db.create_user(f"pageuser{i}", "hash", "salt")
    page1 = db.list_users(limit=3, offset=0)
    page2 = db.list_users(limit=3, offset=3)
    assert len(page1) <= 3
    assert len(page2) <= 3

def test_retention_policy():
    from datetime import datetime, timedelta
    old_ts = (datetime.utcnow() - timedelta(days=100)).isoformat()
    with db.get_conn() as conn:
        conn.execute("INSERT INTO query_log(ts,username,jurisdiction,query,response) VALUES(?,?,?,?,?)",
                     (old_ts, "retuser", "US", "old query", "old response"))
    db.apply_retention_policy()
    with db.get_conn() as conn:
        count = conn.execute("SELECT COUNT(*) FROM query_log WHERE query='old query'").fetchone()[0]
    assert count == 0
