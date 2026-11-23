from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class Role(str, Enum):
    LE = "LawEnforcement"; FE = "ForensicExpert"; JU = "Judge"
    EM = "EvidenceManager"; SA = "SuperAdmin"

PERMS: dict[Role, set[str]] = {
    Role.LE: {"SUBMIT_EVIDENCE", "RETRIEVE_EVIDENCE", "VIEW_CUSTODY"},
    Role.FE: {"RETRIEVE_EVIDENCE", "ADD_ANALYSIS", "VIEW_METADATA"},
    Role.JU: {"RETRIEVE_EVIDENCE", "VIEW_CUSTODY", "REQUEST_DELETION"},
    Role.EM: {"ASSIGN_ROLE", "VIEW_LOGS"},
    Role.SA: {"ASSIGN_ROLE", "REVOKE_ROLE", "CONFIG", "VIEW_LOGS",
              "SUBMIT_EVIDENCE", "RETRIEVE_EVIDENCE", "VIEW_CUSTODY",
              "ADD_ANALYSIS", "VIEW_METADATA", "REQUEST_DELETION"},
}

@dataclass
class RoleAssignment:
    user_id: str
    role: Role
    assigned_by: str
    assigned_at: float
    expiry_ts: float | None
    revoked: bool = False
    revoked_at: float | None = None