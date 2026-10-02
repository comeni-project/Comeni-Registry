"""Build an inspection request from a fixture case, for the pieces' own tests."""

import pathlib

import yaml
from comeni_inspect import wire

INSPECTORS = pathlib.Path(__file__).parent
FIXTURES = INSPECTORS / "formats" / "fastq" / "piece" / "fixtures"


def _ref(folder: pathlib.Path, declaration: str) -> wire.PieceRef:
    data = yaml.safe_load((folder / declaration).read_text())
    return wire.PieceRef(
        id=data["id"],
        version=data["version"],
        path=str(folder / data["entry"]),
        decided=data.get("decided", {}),
    )


def request_for(case: str, measures: list[str]) -> tuple[wire.Request, list[bytes]]:
    paths = sorted(p for p in (FIXTURES / case).iterdir() if p.name != "expected.json")
    payloads = [p.read_bytes() for p in paths]
    gz = any(p.name.endswith(".gz") for p in paths)
    request = wire.Request(
        format=_ref(INSPECTORS / "formats" / "fastq", "format.yml"),
        codec=_ref(INSPECTORS / "codecs" / "gzip", "codec.yml") if gz else None,
        measures=[_ref(INSPECTORS / "measures" / m, "measure.yml") for m in measures],
        files=[
            wire.FileHead(name=p.name, length=len(b))
            for p, b in zip(paths, payloads, strict=True)
        ],
        cap_bytes=16 * 2**20,
    )
    return request, payloads
