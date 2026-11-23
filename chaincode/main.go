// SPDX-License-Identifier: MIT
package main

import (
    "github.com/hyperledger/fabric-contract-api-go/contractapi"
)

func main() {
    cc, err := contractapi.NewChaincode(&SmartContract{})
    if err != nil { panic(err.Error()) }
    if err := cc.Start(); err != nil { panic(err.Error()) }
}