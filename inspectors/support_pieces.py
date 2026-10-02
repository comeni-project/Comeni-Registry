"""Build an inspection request from a FASTQ fixture case, for the pieces' own tests."""

import pathlib

from comeni_inspect import harness

REGISTRY = pathlib.Path(__file__).parent.parent
FASTQ = REGISTRY / "inspectors" / "formats" / "fastq"


def request_for(case: str, measures: list[str]):
    folder = FASTQ / "piece" / "fixtures" / case
    return harness.request_for(REGISTRY, FASTQ, harness.files_of(folder), measures)
