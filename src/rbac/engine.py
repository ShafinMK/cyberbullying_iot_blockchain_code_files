from __future__ import annotations
import time
from .model import Role, RoleAssignment, PERMS

class RBACEngine:
    def __init__(self):
        self.assignments: dict[tuple[str, Role], RoleAssignment] = {}
        self.audit: list[dict] = []
        self.case_assignments: dict[str, set[str]] = {}

    def assign_role(self, user_id: str, role: Role, by: str,
                    expiry_ts: float | None = None) -> None:
        self.assignments[(user_id, role)] = RoleAssignment(
            user_id, role, by, time.time(), expiry_ts, False, None)
        self.audit.append({"t": time.time(), "action": "ASSIGN_ROLE",
                           "user": user_id, "role": role.value, "by": by})

    def revoke_role(self, user_id: str, role: Role, by: str) -> None:
        a = self.assignments.get((user_id, role))
        if not a: raise KeyError(f"no assignment for {user_id}/{role}")
        a.revoked = True; a.revoked_at = time.time()
        self.audit.append({"t": time.time(), "action": "REVOKE_ROLE",
                           "user": user_id, "role": role.value, "by": by})

    def check_permission(self, user_id: str, role: Role, perm: str,
                         case_id: str | None = None) -> bool:
        a = self.assignments.get((user_id, role))
        ok = (a is not None and not a.revoked
              and (a.expiry_ts is None or time.time() < a.expiry_ts)
              and perm in PERMS.get(role, set()))
        if ok and case_id and role in (Role.LE, Role.FE):
            ok = case_id in self.case_assignments.get(user_id, set())
        self.audit.append({"t": time.time(), "action": "ACCESS_CHECK",
                           "user": user_id, "role": role.value,
                           "perm": perm, "case": case_id, "granted": ok})
        return ok