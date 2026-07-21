/**
 * Hyperledger Caliper Workload Module: Add Evidence
 * Simulates evidence submission transactions
 */

'use strict';

const { WorkloadModuleBase } = require('@hyperledger/caliper-core');

class AddEvidenceWorkload extends WorkloadModuleBase {
    constructor() {
        super();
        this.txIndex = 0;
        this.evidenceTypes = ['text', 'audio', 'location'];
        this.payloadSizes = {
            'text': 600,      // bytes
            'audio': 500,     // bytes (metadata only)
            'location': 400   // bytes
        };
    }

    async initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext) {
        await super.initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext);
        
        console.log(`[Worker ${workerIndex}] Initialized Add Evidence workload`);
        
        // Generate initial evidence IDs for retrieval tests
        this.evidenceIds = [];
        for (let i = 0; i < 100; i++) {
            this.evidenceIds.push(`evidence_${i}_${Date.now()}`);
        }
    }

    async submitTransaction() {
        this.txIndex++;
        
        const evidenceType = this.evidenceTypes[this.txIndex % this.evidenceTypes.length];
        const deviceId = `device_${Math.floor(Math.random() * 100)}`;
        const caseId = `case_${Math.floor(Math.random() * 50)}`;
        const consentId = `consent_${Math.floor(Math.random() * 20)}`;
        
        // Generate evidence data with appropriate size
        const payloadSize = this.payloadSizes[evidenceType] || 500;
        const evidenceData = this.generateEvidenceData(evidenceType, payloadSize);
        
        // Generate encrypted symmetric key (RSA-encrypted)
        const encryptedSymKey = this.generateEncryptedKey();
        
        // Create transaction arguments
        const args = {
            contractId: 'evidencechaincode',
            contractFunction: 'SubmitEvidence',
            contractArguments: [
                evidenceData,
                deviceId,
                encryptedSymKey,
                evidenceType,
                caseId,
                consentId
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
            console.error(`Failed to submit evidence: ${error.message}`);
            return {
                status: 'failed',
                latency: 0,
                error: error.message
            };
        }
    }

    generateEvidenceData(type, size) {
        // Generate realistic evidence data based on type
        if (type === 'text') {
            const messages = [
                'You are worthless and nobody will ever love you.',
                'I hope you disappear from this world forever.',
                'Everyone hates you and you have no friends.',
                'Your posts are so pathetic, just stop trying.',
                'You\'re so ugly, no wonder nobody wants to talk to you.'
            ];
            const baseMessage = messages[Math.floor(Math.random() * messages.length)];
            // Pad to approximate desired size
            while (baseMessage.length < size) {
                baseMessage += ' ' + messages[Math.floor(Math.random() * messages.length)];
            }
            return baseMessage.substring(0, size);
        } else if (type === 'audio') {
            return `audio_data_${Math.random().toString(36).substring(2, 15)}_${this.txIndex}`;
        } else if (type === 'location') {
            return JSON.stringify({
                latitude: (Math.random() * 180) - 90,
                longitude: (Math.random() * 360) - 180,
                accuracy: Math.floor(Math.random() * 50) + 5,
                speed: Math.random() * 100
            });
        }
        return 'x'.repeat(size);
    }

    generateEncryptedKey() {
        // Simulate RSA-encrypted symmetric key
        return 'rsa_encrypted_key_' + Math.random().toString(36).substring(2, 15);
    }
}

function createWorkloadModule() {
    return new AddEvidenceWorkload();
}

module.exports.createWorkloadModule = createWorkloadModule;