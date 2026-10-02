"""Quality encoding: Phred+33 or Phred+64, from the lowest and highest quality character.

Phred+64 is written in `@`–`h` (64–104); Phred+33 from `!` (33) up, past `J` for long reads
(PacBio HiFi, ONT, AVITI). So a character below `;` or above `h` can only be Phred+33, and
Phred+64 is decided only when everything sits in `@`–`h` and something is above `J`. Anything
else fits both, and the person is asked (issue 222).
"""

from comeni_inspect.outcome import Undetermined, Value

_ONLY_PHRED33_BELOW = ord(";")
_ONLY_PHRED33_ABOVE = ord("h")
_PHRED64_FLOOR = ord("@")
_PHRED33_SHORT_READ_CEILING = ord("J")


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
        if self.lowest < _ONLY_PHRED33_BELOW or self.highest > _ONLY_PHRED33_ABOVE:
            return Value(value="phred33", evidence=evidence)
        if self.lowest >= _PHRED64_FLOOR and self.highest > _PHRED33_SHORT_READ_CEILING:
            return Value(value="phred64", evidence=evidence)
        return Undetermined(
            reason="characters fit both Phred+33 and Phred+64", evidence=evidence
        )
