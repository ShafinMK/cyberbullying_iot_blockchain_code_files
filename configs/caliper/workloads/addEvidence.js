'use strict';
const { WorkloadModuleBase } = require('@hyperledger/caliper-core');
class AddEvidence extends WorkloadModuleBase {
  async submitTransaction() {
    const id = 'dev' + Math.floor(Math.random() * 1000);
    const hash = 'a'.repeat(64);
    await this.sutAdapter.sendRequests({
      contractId: 'evidence',
      contractFunction: 'SubmitEvidence',
      contractArguments: [id, 'text', hash, 'ff', ''],
      readOnly: false,
    });
  }
}
module.exports.createWorkloadModule = () => new AddEvidence();