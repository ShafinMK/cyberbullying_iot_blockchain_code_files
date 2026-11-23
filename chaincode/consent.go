// SPDX-License-Identifier: MIT
package main

import (
    "fmt"

    "github.com/hyperledger/fabric-contract-api-go/contractapi"
)

func (s *SmartContract) RecordConsent(ctx contractapi.TransactionContextInterface,
    deviceID, signatureHex, scope string) error {
    if len(signatureHex) == 0 { return fmt.Errorf("consent requires signature") }
    return ctx.GetStub().PutState("consent:"+deviceID, []byte("true"))
}

func (s *SmartContract) WithdrawConsent(ctx contractapi.TransactionContextInterface,
    deviceID, signatureHex string) error {
    if len(signatureHex) == 0 { return fmt.Errorf("withdrawal requires signature") }
    return ctx.GetStub().PutState("consent:"+deviceID, []byte("false"))
}