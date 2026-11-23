from __future__ import annotations
import hashlib, pathlib, tempfile

class LocalIPFSStub:
    def __init__(self, root=None):
        self.root = pathlib.Path(root or tempfile.mkdtemp(prefix="ipfs-stub-"))
        self.root.mkdir(parents=True, exist_ok=True)
        self.pins: set[str] = set()

    def put(self, data: bytes) -> str:
        cid = "Qm" + hashlib.sha256(data).hexdigest()[:44]
        (self.root / cid).write_bytes(data)
        self.pins.add(cid)
        return cid

    def get(self, cid: str) -> bytes:
        p = self.root / cid
        if not p.exists(): raise FileNotFoundError(cid)
        return p.read_bytes()

    def unpin(self, cid: str) -> None:
        self.pins.discard(cid)
        p = self.root / cid
        if p.exists(): p.unlink()