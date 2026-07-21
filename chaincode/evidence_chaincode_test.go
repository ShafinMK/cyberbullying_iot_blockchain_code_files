package main

import (
	"testing"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
	"github.com/hyperledger/fabric-contract-api-go/contractapi/mocks"
	"github.com/stretchr/testify/assert"
)

func TestSubmitEvidence(t *testing.T) {
	// Setup mock context
	ctx := new(mocks.TransactionContextInterface)
	stub := new(mocks.ChaincodeStubInterface)
	ctx.On("GetStub").Return(stub)
	ctx.On("GetClientIdentity").Return(&mocks.ClientIdentity{})

	// Create chaincode instance
	cc := new(EvidenceChaincode)

	// Test evidence submission
	evidenceData := "test evidence data"
	deviceID := "device123"
	evidenceType := "text"
	caseID := "case456"
	consentID := "consent789"

	result, err := cc.SubmitEvidence(ctx, evidenceData, deviceID, "", evidenceType, caseID, consentID)

	assert.NoError(t, err)
	assert.Contains(t, result, "Evidence submitted successfully")
}