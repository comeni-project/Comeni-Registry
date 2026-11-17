"""Assembly length: the bases over every contig."""

from comeni_inspect.outcome import Undetermined, Value


class Accumulator:
    def __init__(self, decided: dict, files: list[str]) -> None:
        self.min_records = decided["min_records"]
        self.records = 0
        self.bases = 0

    def add(self, row) -> None:
        for record in row:
            self.records += 1
            self.bases += len(record.sequence)

    def result(self) -> Value | Undetermined:
        evidence = {"records": self.records}
        if self.records < self.min_records or self.bases == 0:
            return Undetermined(reason="no contigs", evidence=evidence)
        return Value(value=self.bases, evidence=evidence)
