"""Unit tests for auth.py"""
import pytest, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ["DB_PATH"] = ":memory:"

import db; db.init_db()
import auth
from auth import UserRole

def test_register_and_login():
    ok, msg = auth.register("testuser", "Password1!", "Password1!", email="t@t.com")
    assert ok, msg
    ok2, result = auth.login("testuser", "Password1!")
    assert ok2
    assert result == "testuser"

def test_register_duplicate():
    auth.register("dupuser", "Password1!", "Password1!")
    ok, msg = auth.register("dupuser", "Password1!", "Password1!")
    assert not ok
    assert "already exists" in msg

def test_register_weak_password():
    ok, msg = auth.register("weakuser", "short", "short")
    assert not ok

def test_login_wrong_password():
    auth.register("logintest", "Password1!", "Password1!")
    ok, msg = auth.login("logintest", "wrongpass")
    assert not ok

def test_brute_force_lockout():
    auth.register("bruteuser", "Password1!", "Password1!")
    for _ in range(5):
        auth.login("bruteuser", "wrongpass")
    locked, until = db.is_account_locked("bruteuser")
    assert locked

def test_assign_role():
    auth.register("roleuser", "Password1!", "Password1!")
    ok, msg = auth.assign_role("roleuser", UserRole.LICENSED_LAWYER, "admin")
    assert ok
    user = db.get_user("roleuser")
    assert user["role"] == UserRole.LICENSED_LAWYER

def test_password_reset():
    auth.register("resetuser", "Password1!", "Password1!")
    token = auth.generate_reset_token("resetuser")
    assert token
    ok, msg = auth.reset_password(token, "NewPass2!", "NewPass2!")
    assert ok
    ok2, _ = auth.login("resetuser", "NewPass2!")
    assert ok2

def test_validate_url_whitelist():
    import os
    os.environ["ALLOWED_URL_DOMAINS"] = "example.com"
    from importlib import reload
    import auth as a
    ok, _ = a.validate_url("https://example.com/page")
    assert ok
    ok2, _ = a.validate_url("https://evil.example.com.attacker.com/page")
    assert not ok2
    os.environ["ALLOWED_URL_DOMAINS"] = ""

def test_validate_file_size(tmp_path):
    import io
    class FakeFile:
        name = "test.pdf"
        def getvalue(self): return b"%PDF" + b"x" * (11 * 1024 * 1024)
    ok, msg = auth.validate_file(FakeFile())
    assert not ok
    assert "MB" in msg

def test_validate_file_magic_bytes():
    class FakeFile:
        name = "test.pdf"
        def getvalue(self): return b"NOTPDF" + b"x" * 100
    ok, msg = auth.validate_file(FakeFile())
    assert not ok
