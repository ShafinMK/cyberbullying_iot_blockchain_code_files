from src.config import load_config
from src.consensus.stake import random_validators
from src.consensus.committee import committee_size, select_committee
from src.consensus.pbft import run_pbft, max_faulty

def test_stakes_sum_to_one():
    cfg = load_config(); v = random_validators(cfg, 10)
    assert abs(sum(x.stake for x in v) - 1.0) < 1e-9

def test_committee_size():
    assert committee_size(10) == 4
    assert committee_size(4) == 4

def test_pbft_fault_tolerance():
    assert max_faulty(4) == 1
    assert run_pbft(4, faulty=1, base_latency_ms=150, prep_ms=120, commit_ms=60, ledger_ms=35).committed
    assert not run_pbft(4, faulty=2, base_latency_ms=150, prep_ms=120, commit_ms=60, ledger_ms=35).committed

def test_committee_no_replacement():
    cfg = load_config(); v = random_validators(cfg, 10)
    com = select_committee(cfg, v, 0)
    assert len({x.node_id for x in com}) == len(com) == 4