# Blockchain-Driven Forensic Framework for Cyberbullying Evidence Collection in IoT Environments

This repository contains the complete source code, configuration files, and benchmarking tools for the paper titled **"A Blockchain-Driven Forensic Framework for Secure Cyberbullying Evidence Collection in IoT Environments"** published in Scientific Reports.

## Overview

The framework integrates:

* **Hyperledger Fabric v2.5** for permissioned blockchain infrastructure
* **Go-based chaincode** for evidence submission, retrieval, and RBAC enforcement
* **Python-based IoT device simulators** for generating realistic cyberbullying evidence
* **IPFS** for off-chain storage of large multimedia files
* **Hybrid PoS+PBFT consensus mechanism** for enhanced security and scalability

## Repository Structure

```
.
├── chaincode/          # Hyperledger Fabric Go chaincode
├── iot-simulator/       # Python IoT device simulation
├── caliper-benchmarks/  # Hyperledger Caliper benchmarks
├── deployment/          # Docker and network deployment scripts
└── analysis/            # Performance analysis and visualization
```

## Prerequisites

* Docker v24.0.2+
* Docker Compose v2.20.0+
* Go v1.19+
* Python v3.9+
* Node.js v16+
* Hyperledger Fabric v2.5
* Hyperledger Caliper v0.5.0

## Quick Start

### 1\. Deploy the Blockchain Network

```bash
cd deployment
./network.sh up
./network.sh createChannel
./network.sh deployChaincode
```

### 2\. Run IoT Device Simulation

```bash
cd ../iot-simulator
pip install -r requirements.txt
python device\_simulator.py --config config.yaml
```

### 3\. Run Performance Benchmarks

```bash
cd ../caliper-benchmarks
npm install
npx caliper launch manager --config config.yaml --network network/fabric-network.yaml --benchmark benchmarks/forensic-benchmark.yaml
```

### 4\. Analyze Results

```bash
cd ../analysis
python performance\_analysis.py
python visualize\_results.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this code in your research, please cite our paper:

```bibtex
@article{shafin2026blockchain,
  title={A Blockchain-Driven Forensic Framework for Secure Cyberbullying Evidence Collection in IoT Environments},
  author={Shafin, K.M. and Reno, S.},
  journal={Scientific Reports},
  year={2026}
}
```

## Contact

For questions or issues, please contact:

* Saha Reno: reno.saha39@gmail.com
* Khandaker Md Shafin: khandakar.md.shafin.74@gmail.com

\---

## Appendix: Source Files

### `requirements.txt` (Root)

```
# Root requirements for the overall project
```

### `chaincode/evidence\_chaincode.go`

```go
/\*
 \* Evidence Chaincode for Hyperledger Fabric v2.5
 \* Implements evidence submission, retrieval, RBAC, and consent management
 \* Based on Algorithms 1 and 2 in the paper
 \*/

package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// EvidenceChaincode implements the smart contract for forensic evidence management
type EvidenceChaincode struct {
	contractapi.Contract
}

// Evidence represents a forensic evidence record
type Evidence struct {
	ID              string    `json:"id"`
	DeviceID        string    `json:"deviceId"`
	EncryptedData   string    `json:"encryptedData"`
	EncryptedSymKey string    `json:"encryptedSymKey"`
	Hash            string    `json:"hash"`
	Timestamp       int64     `json:"timestamp"`
	Status          string    `json:"status"`
	EvidenceType    string    `json:"evidenceType"` // text, audio, location
	CaseID          string    `json:"caseId"`
	SubmittedBy     string    `json:"submittedBy"`
	ConsentID       string    `json:"consentId"`
}

// AccessLog represents a chain-of-custody access record
type AccessLog struct {
	EvidenceID  string `json:"evidenceId"`
	RequesterID string `json:"requesterId"`
	AccessTime  int64  `json:"accessTime"`
	Action      string `json:"action"`
	TxID        string `json:"txId"`
}

// Consent represents a user consent record
type Consent struct {
	Pseudonym   string `json:"pseudonym"`
	DeviceID    string `json:"deviceId"`
	Consented   bool   `json:"consented"`
	Timestamp   int64  `json:"timestamp"`
	Expiry      int64  `json:"expiry"`
	Withdrawn   bool   `json:"withdrawn"`
	WithdrawnAt int64  `json:"withdrawnAt"`
	Scope       string `json:"scope"`
}

// RoleAssignment represents a user role assignment
type RoleAssignment struct {
	UserID        string `json:"userId"`
	RoleName      string `json:"roleName"`
	AssignedBy    string `json:"assignedBy"`
	AssignedAt    int64  `json:"assignedAt"`
	Expiry        int64  `json:"expiry"`
	Revoked       bool   `json:"revoked"`
	RevokedAt     int64  `json:"revokedAt"`
}

// InitLedger initializes the ledger with empty state
func (c \*EvidenceChaincode) InitLedger(ctx contractapi.TransactionContextInterface) error {
	return nil
}

// ============================================================
// EVIDENCE SUBMISSION - Algorithm 1 from the paper
// ============================================================

// SubmitEvidence implements Algorithm 1: SubmitEvidence - Chaincode Function
func (c \*EvidenceChaincode) SubmitEvidence(
	ctx contractapi.TransactionContextInterface,
	evidenceData string,
	deviceID string,
	encryptedSymKey string,
	evidenceType string,
	caseID string,
	consentID string,
) (string, error) {

	// Step 1: Authenticate device using MSP (Membership Service Provider)
	clientIdentity := ctx.GetClientIdentity()
	clientID, err := clientIdentity.GetID()
	if err != nil {
		return "", fmt.Errorf("failed to get client identity: %v", err)
	}

	// Verify device is authorized - check if client has SUBMIT\_EVIDENCE permission
	hasPermission, err := c.HasPermission(ctx, clientID, "SUBMIT\_EVIDENCE")
	if err != nil {
		return "", fmt.Errorf("failed to verify permission: %v", err)
	}
	if !hasPermission {
		return "", fmt.Errorf("device not authorized to submit evidence")
	}

	// Verify device ID matches client identity
	// In production, this would be validated through MSP attributes
	// For simulation, we accept the provided deviceID

	// Step 2: Check consent
	hasConsent, err := c.CheckConsent(ctx, clientID, deviceID)
	if err != nil {
		return "", fmt.Errorf("failed to check consent: %v", err)
	}
	if !hasConsent {
		return "", fmt.Errorf("consent not provided or withdrawn for device: %s", deviceID)
	}

	// Step 3: Encrypt evidence data is already encrypted at device level
	// We receive encryptedData as input

	// Step 4: Generate SHA-256 hash for integrity check
	hash := c.GenerateHash(evidenceData)

	// Step 5: Create timestamp
	timestamp := time.Now().UnixNano() / 1000000 // milliseconds

	// Step 6: Create evidence object
	evidenceID := c.GenerateEvidenceID(deviceID, timestamp)

	evidence := Evidence{
		ID:              evidenceID,
		DeviceID:        deviceID,
		EncryptedData:   evidenceData,
		EncryptedSymKey: encryptedSymKey,
		Hash:            hash,
		Timestamp:       timestamp,
		Status:          "SUBMITTED",
		EvidenceType:    evidenceType,
		CaseID:          caseID,
		SubmittedBy:     clientID,
		ConsentID:       consentID,
	}

	// Step 7: Store evidence in world state (CouchDB)
	evidenceJSON, err := json.Marshal(evidence)
	if err != nil {
		return "", fmt.Errorf("failed to marshal evidence: %v", err)
	}

	err = ctx.GetStub().PutState(evidenceID, evidenceJSON)
	if err != nil {
		return "", fmt.Errorf("failed to store evidence: %v", err)
	}

	// Step 8: Emit event for off-chain IPFS storage
	err = ctx.GetStub().SetEvent("EvidenceSubmitted", \[]byte(evidenceID))
	if err != nil {
		return "", fmt.Errorf("failed to emit event: %v", err)
	}

	// Step 9: Return confirmation
	return fmt.Sprintf("Evidence submitted successfully. ID: %s", evidenceID), nil
}

// ============================================================
// EVIDENCE RETRIEVAL WITH RBAC - Algorithm 2 from the paper
// ============================================================

// RetrieveEvidence implements Algorithm 2: RetrieveEvidence with RBAC
func (c \*EvidenceChaincode) RetrieveEvidence(
	ctx contractapi.TransactionContextInterface,
	evidenceID string,
) (string, error) {

	// Step 1: Get client identity
	clientIdentity := ctx.GetClientIdentity()
	clientID, err := clientIdentity.GetID()
	if err != nil {
		return "", fmt.Errorf("failed to get client identity: %v", err)
	}

	// Step 2: Fetch evidence from ledger
	evidenceBytes, err := ctx.GetStub().GetState(evidenceID)
	if err != nil {
		return "", fmt.Errorf("failed to retrieve evidence: %v", err)
	}
	if evidenceBytes == nil {
		return "", fmt.Errorf("evidence not found: %s", evidenceID)
	}

	var evidence Evidence
	err = json.Unmarshal(evidenceBytes, \&evidence)
	if err != nil {
		return "", fmt.Errorf("failed to unmarshal evidence: %v", err)
	}

	// Step 3: RBAC check - verify user has RETRIEVE\_EVIDENCE permission
	hasPermission, err := c.HasPermission(ctx, clientID, "RETRIEVE\_EVIDENCE")
	if err != nil {
		return "", fmt.Errorf("failed to verify permission: %v", err)
	}
	if !hasPermission {
		return "", fmt.Errorf("access denied: user lacks RETRIEVE\_EVIDENCE permission")
	}

	// Step 4: Verify integrity - check hash matches
	recomputedHash := c.GenerateHash(evidence.EncryptedData)
	if recomputedHash != evidence.Hash {
		return "", fmt.Errorf("integrity check failed: evidence may have been tampered")
	}

	// Step 5: Log access (chain of custody)
	txID := ctx.GetStub().GetTxID()
	timestamp := time.Now().UnixNano() / 1000000

	accessLog := AccessLog{
		EvidenceID:  evidenceID,
		RequesterID: clientID,
		AccessTime:  timestamp,
		Action:      "RETRIEVE",
		TxID:        txID,
	}

	logJSON, err := json.Marshal(accessLog)
	if err != nil {
		return "", fmt.Errorf("failed to marshal access log: %v", err)
	}

	// Store access log with composite key for efficient querying
	logKey := fmt.Sprintf("log\_%s\_%d", evidenceID, timestamp)
	err = ctx.GetStub().PutState(logKey, logJSON)
	if err != nil {
		return "", fmt.Errorf("failed to log access: %v", err)
	}

	// Step 6: Return encrypted data (NO decryption in chaincode)
	return evidence.EncryptedData, nil
}

// ============================================================
// EVIDENCE UPDATE
// ============================================================

// UpdateEvidence updates an existing evidence record
func (c \*EvidenceChaincode) UpdateEvidence(
	ctx contractapi.TransactionContextInterface,
	evidenceID string,
	encryptedData string,
) (string, error) {

	// Get client identity
	clientIdentity := ctx.GetClientIdentity()
	clientID, err := clientIdentity.GetID()
	if err != nil {
		return "", fmt.Errorf("failed to get client identity: %v", err)
	}

	// Check permission
	hasPermission, err := c.HasPermission(ctx, clientID, "UPDATE\_EVIDENCE")
	if err != nil {
		return "", fmt.Errorf("failed to verify permission: %v", err)
	}
	if !hasPermission {
		return "", fmt.Errorf("access denied: user lacks UPDATE\_EVIDENCE permission")
	}

	// Fetch existing evidence
	evidenceBytes, err := ctx.GetStub().GetState(evidenceID)
	if err != nil {
		return "", fmt.Errorf("failed to retrieve evidence: %v", err)
	}
	if evidenceBytes == nil {
		return "", fmt.Errorf("evidence not found: %s", evidenceID)
	}

	var evidence Evidence
	err = json.Unmarshal(evidenceBytes, \&evidence)
	if err != nil {
		return "", fmt.Errorf("failed to unmarshal evidence: %v", err)
	}

	// Update evidence
	evidence.EncryptedData = encryptedData
	evidence.Hash = c.GenerateHash(encryptedData)
	evidence.Status = "UPDATED"
	evidence.Timestamp = time.Now().UnixNano() / 1000000

	// Store updated evidence
	updatedJSON, err := json.Marshal(evidence)
	if err != nil {
		return "", fmt.Errorf("failed to marshal updated evidence: %v", err)
	}

	err = ctx.GetStub().PutState(evidenceID, updatedJSON)
	if err != nil {
		return "", fmt.Errorf("failed to update evidence: %v", err)
	}

	// Log the update
	txID := ctx.GetStub().GetTxID()
	logKey := fmt.Sprintf("log\_%s\_%d", evidenceID, evidence.Timestamp)
	logEntry := AccessLog{
		EvidenceID:  evidenceID,
		RequesterID: clientID,
		AccessTime:  evidence.Timestamp,
		Action:      "UPDATE",
		TxID:        txID,
	}
	logJSON, \_ := json.Marshal(logEntry)
	ctx.GetStub().PutState(logKey, logJSON)

	return fmt.Sprintf("Evidence %s updated successfully", evidenceID), nil
}

// ============================================================
// RBAC FUNCTIONS
// ============================================================

// HasPermission checks if a user has a specific permission
func (c \*EvidenceChaincode) HasPermission(
	ctx contractapi.TransactionContextInterface,
	userID string,
	permission string,
) (bool, error) {

	// Get all roles for the user
	roles, err := c.GetUserRoles(ctx, userID)
	if err != nil {
		return false, err
	}

	// Define role permissions (flat model)
	rolePermissions := map\[string]\[]string{
		"LAW\_ENFORCEMENT": {
			"SUBMIT\_EVIDENCE",
			"RETRIEVE\_EVIDENCE",
			"VIEW\_CUSTODY",
			"MAP\_PSEUDONYM",
		},
		"FORENSIC\_EXPERT": {
			"RETRIEVE\_EVIDENCE",
			"ADD\_ANALYSIS",
			"VIEW\_METADATA",
			"VIEW\_CUSTODY",
		},
		"JUDGE": {
			"RETRIEVE\_EVIDENCE",
			"VIEW\_CUSTODY",
			"REQUEST\_DELETION",
		},
		"EVIDENCE\_MANAGER": {
			"ASSIGN\_ROLE",
			"REVOKE\_ROLE",
			"VIEW\_LOGS",
			"VIEW\_METADATA",
		},
		"SUPER\_ADMIN": {
			"SUBMIT\_EVIDENCE",
			"RETRIEVE\_EVIDENCE",
			"UPDATE\_EVIDENCE",
			"VIEW\_CUSTODY",
			"ASSIGN\_ROLE",
			"REVOKE\_ROLE",
			"VIEW\_LOGS",
			"MAP\_PSEUDONYM",
			"REQUEST\_DELETION",
		},
	}

	// Check if any of the user's roles have the requested permission
	for \_, role := range roles {
		perms, exists := rolePermissions\[role]
		if !exists {
			continue
		}
		for \_, p := range perms {
			if p == permission {
				return true, nil
			}
		}
	}

	return false, nil
}

// GetUserRoles retrieves all active roles for a user
func (c \*EvidenceChaincode) GetUserRoles(
	ctx contractapi.TransactionContextInterface,
	userID string,
) (\[]string, error) {

	// Query for role assignments for this user that are not revoked and not expired
	queryString := fmt.Sprintf(`{"selector": {"userId": "%s", "revoked": false, "expiry": {"$gt": %d}}}`,
		userID, time.Now().UnixNano()/1000000)

	resultsIterator, err := ctx.GetStub().GetQueryResult(queryString)
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var roles \[]string
	for resultsIterator.HasNext() {
		queryResult, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}
		var assignment RoleAssignment
		err = json.Unmarshal(queryResult.Value, \&assignment)
		if err != nil {
			continue
		}
		roles = append(roles, assignment.RoleName)
	}

	return roles, nil
}

// AssignRole assigns a role to a user (super-admin only)
func (c \*EvidenceChaincode) AssignRole(
	ctx contractapi.TransactionContextInterface,
	userID string,
	roleName string,
	expirySeconds int64,
) (string, error) {

	// Verify caller is super-admin or evidence-manager
	callerID, err := ctx.GetClientIdentity().GetID()
	if err != nil {
		return "", fmt.Errorf("failed to get caller identity: %v", err)
	}

	hasPermission, err := c.HasPermission(ctx, callerID, "ASSIGN\_ROLE")
	if err != nil {
		return "", fmt.Errorf("failed to verify permission: %v", err)
	}
	if !hasPermission {
		return "", fmt.Errorf("access denied: only super-admin or evidence-manager can assign roles")
	}

	// Validate role name
	validRoles := map\[string]bool{
		"LAW\_ENFORCEMENT": true,
		"FORENSIC\_EXPERT": true,
		"JUDGE":           true,
		"EVIDENCE\_MANAGER": true,
	}
	if !validRoles\[roleName] {
		return "", fmt.Errorf("invalid role: %s", roleName)
	}

	// Create role assignment
	assignment := RoleAssignment{
		UserID:     userID,
		RoleName:   roleName,
		AssignedBy: callerID,
		AssignedAt: time.Now().UnixNano() / 1000000,
		Expiry:     time.Now().UnixNano()/1000000 + expirySeconds\*1000,
		Revoked:    false,
		RevokedAt:  0,
	}

	assignmentKey := fmt.Sprintf("role\_%s\_%s", userID, roleName)
	assignmentJSON, err := json.Marshal(assignment)
	if err != nil {
		return "", fmt.Errorf("failed to marshal assignment: %v", err)
	}

	err = ctx.GetStub().PutState(assignmentKey, assignmentJSON)
	if err != nil {
		return "", fmt.Errorf("failed to store assignment: %v", err)
	}

	// Emit event
	ctx.GetStub().SetEvent("RoleAssigned", \[]byte(fmt.Sprintf("%s:%s", userID, roleName)))

	return fmt.Sprintf("Role %s assigned to %s", roleName, userID), nil
}

// RevokeRole revokes a role from a user
func (c \*EvidenceChaincode) RevokeRole(
	ctx contractapi.TransactionContextInterface,
	userID string,
	roleName string,
) (string, error) {

	// Verify caller has REVOKE\_ROLE permission
	callerID, err := ctx.GetClientIdentity().GetID()
	if err != nil {
		return "", fmt.Errorf("failed to get caller identity: %v", err)
	}

	hasPermission, err := c.HasPermission(ctx, callerID, "REVOKE\_ROLE")
	if err != nil {
		return "", fmt.Errorf("failed to verify permission: %v", err)
	}
	if !hasPermission {
		return "", fmt.Errorf("access denied: insufficient permissions to revoke role")
	}

	// Fetch existing assignment
	assignmentKey := fmt.Sprintf("role\_%s\_%s", userID, roleName)
	assignmentBytes, err := ctx.GetStub().GetState(assignmentKey)
	if err != nil {
		return "", fmt.Errorf("failed to retrieve assignment: %v", err)
	}
	if assignmentBytes == nil {
		return "", fmt.Errorf("role assignment not found: %s for %s", roleName, userID)
	}

	var assignment RoleAssignment
	err = json.Unmarshal(assignmentBytes, \&assignment)
	if err != nil {
		return "", fmt.Errorf("failed to unmarshal assignment: %v", err)
	}

	// Update assignment
	assignment.Revoked = true
	assignment.RevokedAt = time.Now().UnixNano() / 1000000

	updatedJSON, err := json.Marshal(assignment)
	if err != nil {
		return "", fmt.Errorf("failed to marshal updated assignment: %v", err)
	}

	err = ctx.GetStub().PutState(assignmentKey, updatedJSON)
	if err != nil {
		return "", fmt.Errorf("failed to update assignment: %v", err)
	}

	ctx.GetStub().SetEvent("RoleRevoked", \[]byte(fmt.Sprintf("%s:%s", userID, roleName)))

	return fmt.Sprintf("Role %s revoked for %s", roleName, userID), nil
}

// ============================================================
// CONSENT MANAGEMENT FUNCTIONS
// ============================================================

// RecordConsent records user consent on the blockchain
func (c \*EvidenceChaincode) RecordConsent(
	ctx contractapi.TransactionContextInterface,
	pseudonym string,
	deviceID string,
	scope string,
	expirySeconds int64,
) (string, error) {

	// Verify caller is the user (or has appropriate permissions)
	clientID, err := ctx.GetClientIdentity().GetID()
	if err != nil {
		return "", fmt.Errorf("failed to get client identity: %v", err)
	}

	// In production, verify that clientID matches pseudonym mapping
	// For simulation, we accept the provided pseudonym

	consent := Consent{
		Pseudonym:   pseudonym,
		DeviceID:    deviceID,
		Consented:   true,
		Timestamp:   time.Now().UnixNano() / 1000000,
		Expiry:      time.Now().UnixNano()/1000000 + expirySeconds\*1000,
		Withdrawn:   false,
		WithdrawnAt: 0,
		Scope:       scope,
	}

	consentKey := fmt.Sprintf("consent\_%s\_%s", pseudonym, deviceID)
	consentJSON, err := json.Marshal(consent)
	if err != nil {
		return "", fmt.Errorf("failed to marshal consent: %v", err)
	}

	err = ctx.GetStub().PutState(consentKey, consentJSON)
	if err != nil {
		return "", fmt.Errorf("failed to store consent: %v", err)
	}

	ctx.GetStub().SetEvent("ConsentRecorded", \[]byte(pseudonym))

	return "Consent recorded successfully", nil
}

// WithdrawConsent withdraws user consent
func (c \*EvidenceChaincode) WithdrawConsent(
	ctx contractapi.TransactionContextInterface,
	pseudonym string,
	deviceID string,
) (string, error) {

	// Verify caller is the user
	clientID, err := ctx.GetClientIdentity().GetID()
	if err != nil {
		return "", fmt.Errorf("failed to get client identity: %v", err)
	}

	consentKey := fmt.Sprintf("consent\_%s\_%s", pseudonym, deviceID)
	consentBytes, err := ctx.GetStub().GetState(consentKey)
	if err != nil {
		return "", fmt.Errorf("failed to retrieve consent: %v", err)
	}
	if consentBytes == nil {
		return "", fmt.Errorf("consent not found for %s:%s", pseudonym, deviceID)
	}

	var consent Consent
	err = json.Unmarshal(consentBytes, \&consent)
	if err != nil {
		return "", fmt.Errorf("failed to unmarshal consent: %v", err)
	}

	consent.Withdrawn = true
	consent.WithdrawnAt = time.Now().UnixNano() / 1000000

	updatedJSON, err := json.Marshal(consent)
	if err != nil {
		return "", fmt.Errorf("failed to marshal updated consent: %v", err)
	}

	err = ctx.GetStub().PutState(consentKey, updatedJSON)
	if err != nil {
		return "", fmt.Errorf("failed to update consent: %v", err)
	}

	ctx.GetStub().SetEvent("ConsentWithdrawn", \[]byte(pseudonym))

	return "Consent withdrawn successfully", nil
}

// CheckConsent checks if consent is active for a device
func (c \*EvidenceChaincode) CheckConsent(
	ctx contractapi.TransactionContextInterface,
	pseudonym string,
	deviceID string,
) (bool, error) {

	consentKey := fmt.Sprintf("consent\_%s\_%s", pseudonym, deviceID)
	consentBytes, err := ctx.GetStub().GetState(consentKey)
	if err != nil {
		return false, err
	}
	if consentBytes == nil {
		return false, nil
	}

	var consent Consent
	err = json.Unmarshal(consentBytes, \&consent)
	if err != nil {
		return false, err
	}

	// Check if consent is active
	if consent.Withdrawn {
		return false, nil
	}
	if consent.Expiry < time.Now().UnixNano()/1000000 {
		return false, nil
	}

	return true, nil
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

// GenerateHash generates SHA-256 hash of input data
func (c \*EvidenceChaincode) GenerateHash(data string) string {
	hash := sha256.Sum256(\[]byte(data))
	return hex.EncodeToString(hash\[:])
}

// GenerateEvidenceID generates a unique evidence ID
func (c \*EvidenceChaincode) GenerateEvidenceID(deviceID string, timestamp int64) string {
	raw := fmt.Sprintf("%s\_%d", deviceID, timestamp)
	hash := sha256.Sum256(\[]byte(raw))
	return hex.EncodeToString(hash\[:])\[:16]
}

// GetEvidenceHistory retrieves the full chain of custody for an evidence record
func (c \*EvidenceChaincode) GetEvidenceHistory(
	ctx contractapi.TransactionContextInterface,
	evidenceID string,
) (\[]AccessLog, error) {

	// Verify caller has VIEW\_CUSTODY permission
	clientID, err := ctx.GetClientIdentity().GetID()
	if err != nil {
		return nil, fmt.Errorf("failed to get client identity: %v", err)
	}

	hasPermission, err := c.HasPermission(ctx, clientID, "VIEW\_CUSTODY")
	if err != nil {
		return nil, fmt.Errorf("failed to verify permission: %v", err)
	}
	if !hasPermission {
		return nil, fmt.Errorf("access denied: user lacks VIEW\_CUSTODY permission")
	}

	// Query access logs for this evidence
	queryString := fmt.Sprintf(`{"selector": {"evidenceId": "%s"}}`, evidenceID)
	resultsIterator, err := ctx.GetStub().GetQueryResult(queryString)
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var logs \[]AccessLog
	for resultsIterator.HasNext() {
		queryResult, err := resultsIterator.Next()
		if err != nil {
			continue
		}
		var log AccessLog
		err = json.Unmarshal(queryResult.Value, \&log)
		if err != nil {
			continue
		}
		logs = append(logs, log)
	}

	return logs, nil
}

// ============================================================
// MAIN
// ============================================================

func main() {
	chaincode, err := contractapi.NewChaincode(\&EvidenceChaincode{})
	if err != nil {
		fmt.Printf("Error creating chaincode: %v\\n", err)
		return
	}

	if err := chaincode.Start(); err != nil {
		fmt.Printf("Error starting chaincode: %v\\n", err)
	}
}
```

