"""N50: the length of the contig that, with every longer one, holds half the assembly."""

from comeni_inspect.outcome import Undetermined, Value


class Accumulator:
    def __init__(self, decided: dict, files: list[str]) -> None:
        self.min_records = decided["min_records"]
        self.lengths: list[int] = []

    def add(self, row) -> None:
        self.lengths += [len(record.sequence) for record in row]

    def result(self) -> Value | Undetermined:
        total = sum(self.lengths)
        evidence = {"records": len(self.lengths)}
        if len(self.lengths) < self.min_records or total == 0:
            return Undetermined(reason="no contigs", evidence=evidence)
        held = 0
        for length in sorted(self.lengths, reverse=True):
            held += length
            if 2 * held >= total:
                return Value(value=length, evidence={**evidence, "longest": max(self.lengths)})
        raise AssertionError("unreachable: the lengths sum to the total")
