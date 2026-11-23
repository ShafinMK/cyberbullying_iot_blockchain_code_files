from src.rbac.model import Role
from src.rbac.engine import RBACEngine

def test_assign_and_check():
    e = RBACEngine(); e.assign_role("alice", Role.LE, by="admin")
    assert e.check_permission("alice", Role.LE, "SUBMIT_EVIDENCE")
    assert not e.check_permission("alice", Role.LE, "ADD_ANALYSIS")

def test_revoke():
    e = RBACEngine(); e.assign_role("bob", Role.FE, by="admin")
    e.revoke_role("bob", Role.FE, by="admin")
    assert not e.check_permission("bob", Role.FE, "RETRIEVE_EVIDENCE")

def test_expiry():
    import time; e = RBACEngine()
    e.assign_role("carol", Role.LE, by="admin", expiry_ts=time.time() - 1)
    assert not e.check_permission("carol", Role.LE, "SUBMIT_EVIDENCE")