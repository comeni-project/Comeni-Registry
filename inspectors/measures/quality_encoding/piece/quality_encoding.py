"""Quality encoding: Phred+33 or Phred+64, from the lowest and highest quality character."""

from comeni_inspect.outcome import Undetermined, Value

_ONLY_PHRED33_BELOW = ord(";")
_ONLY_PHRED64_ABOVE = ord("J")


class Accumulator:
    def __init__(self, decided: dict, files: list[str]) -> None:
        self.min_records = decided["min_records"]
        self.records = 0
        self.lowest = 255
        self.highest = 0

    def add(self, row) -> None:
        for record in row:
            if record.quality:
                self.records += 1
                self.lowest = min(self.lowest, min(record.quality))
                self.highest = max(self.highest, max(record.quality))

    def result(self) -> Value | Undetermined:
        if self.records < self.min_records:
            return Undetermined(
                reason=f"only {self.records} reads", evidence={"records": self.records}
            )
        evidence = {"records": self.records, "lowest": self.lowest, "highest": self.highest}
        if self.lowest < _ONLY_PHRED33_BELOW:
            return Value(value="phred33", evidence=evidence)
        if self.highest > _ONLY_PHRED64_ABOVE:
            return Value(value="phred64", evidence=evidence)
        return Undetermined(
            reason="characters fit both Phred+33 and Phred+64", evidence=evidence
        )
