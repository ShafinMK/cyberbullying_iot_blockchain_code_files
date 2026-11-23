// SPDX-License-Identifier: MIT
package main

import (
    "encoding/json"
    "fmt"
    "time"

    "github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type RoleAssignment struct {
    UserID     string `json:"userID"`
    Role       string `json:"role"`
    AssignedBy string `json:"assignedBy"`
    AssignedAt int64  `json:"assignedAt"`
    ExpiryTs   int64  `json:"expiryTs,omitempty"`
    Revoked    bool   `json:"revoked"`
}

func (s *SmartContract) AssignRole(ctx contractapi.TransactionContextInterface,
    caller, userID, role string, expiryTs int64) error {
    if !s.rbacAllowed(ctx, caller, "SuperAdmin", "ASSIGN_ROLE") {
        return fmt.Errorf("caller not authorized to assign roles")
    }
    ra := RoleAssignment{userID, role, caller, time.Now().UnixMilli(), expiryTs, false}
    b, _ := json.Marshal(ra)
    return ctx.GetStub().PutState("role:"+userID+":"+role, b)
}

func (s *SmartContract) RevokeRole(ctx contractapi.TransactionContextInterface,
    caller, userID, role string) error {
    if !s.rbacAllowed(ctx, caller, "SuperAdmin", "REVOKE_ROLE") &&
       !s.rbacAllowed(ctx, caller, "EvidenceManager", "REVOKE_ROLE") {
        return fmt.Errorf("caller not authorized to revoke roles")
    }
    key := "role:" + userID + ":" + role
    b, err := ctx.GetStub().GetState(key)
    if err != nil || b == nil { return fmt.Errorf("assignment not found") }
    var ra RoleAssignment
    _ = json.Unmarshal(b, &ra)
    ra.Revoked = true
    nb, _ := json.Marshal(ra)
    return ctx.GetStub().PutState(key, nb)
}

func (s *SmartContract) rbacAllowed(ctx contractapi.TransactionContextInterface,
    userID, role, perm string) bool {
    b, err := ctx.GetStub().GetState("role:" + userID + ":" + role)
    if err != nil || b == nil { return false }
    var ra RoleAssignment
    if json.Unmarshal(b, &ra) != nil { return false }
    if ra.Revoked { return false }
    if ra.ExpiryTs > 0 && time.Now().UnixMilli() > ra.ExpiryTs { return false }
    return permissionInRole(role, perm)
}

func permissionInRole(role, perm string) bool {
    m := map[string]map[string]bool{
        "LawEnforcement":  {"SUBMIT_EVIDENCE": true, "RETRIEVE_EVIDENCE": true, "VIEW_CUSTODY": true},
        "ForensicExpert":  {"RETRIEVE_EVIDENCE": true, "ADD_ANALYSIS": true, "VIEW_METADATA": true},
        "Judge":           {"RETRIEVE_EVIDENCE": true, "VIEW_CUSTODY": true, "REQUEST_DELETION": true},
        "EvidenceManager": {"ASSIGN_ROLE": true, "VIEW_LOGS": true},
        "SuperAdmin":      {"ASSIGN_ROLE": true, "REVOKE_ROLE": true, "CONFIG": true, "VIEW_LOGS": true,
                            "SUBMIT_EVIDENCE": true, "RETRIEVE_EVIDENCE": true, "VIEW_CUSTODY": true,
                            "ADD_ANALYSIS": true, "VIEW_METADATA": true, "REQUEST_DELETION": true},
    }
    return m[role] != nil && m[role][perm]
}

func (s *SmartContract) deviceAuthorized(ctx contractapi.TransactionContextInterface, id string) bool {
    b, err := ctx.GetStub().GetState("dev:" + id)
    return err == nil && b != nil
}

func (s *SmartContract) consentActive(ctx contractapi.TransactionContextInterface, id string) bool {
    b, err := ctx.GetStub().GetState("consent:" + id)
    if err != nil || b == nil { return false }
    return string(b) == "true"
}