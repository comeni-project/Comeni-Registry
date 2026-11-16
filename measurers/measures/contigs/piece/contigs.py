"""Contigs: how many records the assembly holds."""

from comeni_inspect.outcome import Undetermined, Value


class Accumulator:
    def __init__(self, decided: dict, files: list[str]) -> None:
        self.min_records = decided["min_records"]
        self.records = 0

    def add(self, row) -> None:
        self.records += len(row)

    def result(self) -> Value | Undetermined:
        if self.records < self.min_records:
            return Undetermined(reason="no contigs", evidence={"records": self.records})
        return Value(value=self.records, evidence={"records": self.records})
