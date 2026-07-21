/**
 * Hyperledger Caliper Workload Module: Update Evidence
 * Simulates evidence update transactions
 */

'use strict';

const { WorkloadModuleBase } = require('@hyperledger/caliper-core');

class UpdateEvidenceWorkload extends WorkloadModuleBase {
    constructor() {
        super();
        this.txIndex = 0;
        this.evidenceIds = [];
    }

    async initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext) {
        await super.initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext);
        
        console.log(`[Worker ${workerIndex}] Initialized Update Evidence workload`);
        
        // Pre-populate evidence IDs
        for (let i = 0; i < 100; i++) {
            this.evidenceIds.push(`evidence_${i}_${Date.now()}`);
        }
    }

    async submitTransaction() {
        this.txIndex++;
        
        const evidenceId = this.evidenceIds[this.txIndex % this.evidenceIds.length];
        const updatedData = `updated_evidence_data_${this.txIndex}_${Date.now()}`;
        
        // Create transaction arguments
        const args = {
            contractId: 'evidencechaincode',
            contractFunction: 'UpdateEvidence',
            contractArguments: [
                evidenceId,
                updatedData
            ],
            timeout: 30,
            readOnly: false
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
            console.error(`Failed to update evidence: ${error.message}`);
            return {
                status: 'failed',
                latency: 0,
                error: error.message
            };
        }
    }
}

function createWorkloadModule() {
    return new UpdateEvidenceWorkload();
}

module.exports.createWorkloadModule = createWorkloadModule;