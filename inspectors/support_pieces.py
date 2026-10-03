"""Build an inspection request from a format's fixture case, for the pieces' own tests."""

import pathlib

from comeni_inspect import harness

REGISTRY = pathlib.Path(__file__).parent.parent
FORMATS = REGISTRY / "inspectors" / "formats"


def request_for(case: str, measures: list[str], format: str = "fastq"):
    """`case` under `formats/<format>/piece/fixtures/`, read by that format: a measure's tests
    name no format and get FASTQ's; a new format's tests name their own."""
    folder = FORMATS / format / "piece" / "fixtures" / case
    if not folder.is_dir():
        raise FileNotFoundError(f"no fixture case {case!r} for the format {format!r}: {folder}")
    return harness.request_for(REGISTRY, FORMATS / format, harness.files_of(folder), measures)
