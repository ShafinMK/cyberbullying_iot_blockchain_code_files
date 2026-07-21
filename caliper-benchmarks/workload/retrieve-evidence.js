/**
 * Hyperledger Caliper Workload Module: Retrieve Evidence
 * Simulates evidence retrieval transactions with RBAC enforcement
 */

'use strict';

const { WorkloadModuleBase } = require('@hyperledger/caliper-core');

class RetrieveEvidenceWorkload extends WorkloadModuleBase {
    constructor() {
        super();
        this.txIndex = 0;
        this.evidenceIds = [];
        this.roles = ['LAW_ENFORCEMENT', 'FORENSIC_EXPERT', 'JUDGE'];
    }

    async initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext) {
        await super.initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext);
        
        console.log(`[Worker ${workerIndex}] Initialized Retrieve Evidence workload`);
        
        // Pre-populate evidence IDs (in production, these would be fetched from the ledger)
        for (let i = 0; i < 100; i++) {
            this.evidenceIds.push(`evidence_${i}_${Date.now()}`);
        }
    }

    async submitTransaction() {
        this.txIndex++;
        
        const evidenceId = this.evidenceIds[this.txIndex % this.evidenceIds.length];
        const role = this.roles[this.txIndex % this.roles.length];
        
        // Create transaction arguments
        const args = {
            contractId: 'evidencechaincode',
            contractFunction: 'RetrieveEvidence',
            contractArguments: [
                evidenceId
            ],
            timeout: 30,
            readOnly: true
        };
        
        // Submit the transaction
        try {
            const startTime = Date.now();
            const result = await this.sutAdapter.sendRequests(args);
            const endTime = Date.now();
            
            const latency = endTime - startTime;
            
            return {
                status: 'success',
                latency: latency,
                result: result
            };
        } catch (error) {
            console.error(`Failed to retrieve evidence: ${error.message}`);
            return {
                status: 'failed',
                latency: 0,
                error: error.message
            };
        }
    }
}

function createWorkloadModule() {
    return new RetrieveEvidenceWorkload();
}

module.exports.createWorkloadModule = createWorkloadModule;