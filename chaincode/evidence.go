// SPDX-License-Identifier: MIT
package main

import (
    "crypto/sha256"
    "encoding/hex"
    "encoding/json"
    "fmt"
    "time"

    "github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type EvidenceRecord struct {
    UID        string `json:"uid"`
    DeviceID   string `json:"deviceID"`
    Kind       string `json:"kind"`
    SHA256     string `json:"sha256"`
    CID        string `json:"cid,omitempty"`
    WrappedKey string `json:"wrappedKey"`
    Timestamp  int64  `json:"timestamp"`
}

// SubmitEvidence implements Algorithm 1.
func (s *SmartContract) SubmitEvidence(ctx contractapi.TransactionContextInterface,
    deviceID, kind, sha256Hex, wrappedKey, cid string) (string, error) {

    if !s.deviceAuthorized(ctx, deviceID) {
        return "", fmt.Errorf("device %s not authorized", deviceID)
    }
    if !s.consentActive(ctx, deviceID) {
        return "", fmt.Errorf("consent withdrawn for %s", deviceID)
    }
    if len(sha256Hex) != 64 {
        return "", fmt.Errorf("invalid sha256 length")
    }
    if _, err := hex.DecodeString(sha256Hex); err != nil {
        return "", fmt.Errorf("sha256 not hex: %w", err)
    }

    now := time.Now().UnixMilli()
    uidHash := sha256.Sum256([]byte(fmt.Sprintf("%s|%s|%d", sha256Hex, deviceID, now)))
    uid := hex.EncodeToString(uidHash[:])

    rec := EvidenceRecord{UID: uid, DeviceID: deviceID, Kind: kind,
        SHA256: sha256Hex, CID: cid, WrappedKey: wrappedKey, Timestamp: now}

    b, err := json.Marshal(rec)
    if err != nil { return "", err }
    if err := ctx.GetStub().PutState(uid, b); err != nil { return "", err }
    _ = ctx.GetStub().SetEvent("EvidenceSubmitted", b)
    return uid, nil
}

// RetrieveEvidence implements Algorithm 2 (RBAC-gated retrieval).
func (s *SmartContract) RetrieveEvidence(ctx contractapi.TransactionContextInterface,
    uid, requesterID, role string) (string, error) {

    if !s.rbacAllowed(ctx, requesterID, role, "RETRIEVE_EVIDENCE") {
        return "", fmt.Errorf("access denied for %s/%s", requesterID, role)
    }
    b, err := ctx.GetStub().GetState(uid)
    if err != nil || b == nil { return "", fmt.Errorf("evidence %s not found", uid) }

    logKey, _ := ctx.GetStub().CreateCompositeKey("audit", []string{uid, requesterID})
    _ = ctx.GetStub().PutState(logKey, []byte(fmt.Sprintf(
        `{"t":%d,"user":"%s"}`, time.Now().UnixMilli(), requesterID)))
    return string(b), nil
}

// GetEvidenceHistory returns the chain of custody.
func (s *SmartContract) GetEvidenceHistory(ctx contractapi.TransactionContextInterface,
    uid string) (string, error) {
    it, err := ctx.GetStub().GetHistoryForKey(uid)
    if err != nil { return "", err }
    defer it.Close()
    var out []string
    for it.HasNext() {
        m, err := it.Next()
        if err != nil { return "", err }
        out = append(out, string(m.Value))
    }
    j, _ := json.Marshal(out)
    return string(j), nil
}