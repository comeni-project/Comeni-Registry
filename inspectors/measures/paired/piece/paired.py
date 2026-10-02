"""Paired: whether the reads come in mates, decided from read names and never from file names.

Two files: a row agrees when both read names match once a trailing `/1` or `/2` is removed.
One file: consecutive reads are compared two at a time, which finds an interleaved file.
"""

import re

from comeni_inspect.outcome import Undetermined, Value

_MATE = re.compile(r"/[12]$")
_R1_FILE = re.compile(r"(_R?1)(_\d+)?\.")


def _stem(name: str) -> str:
    return _MATE.sub("", name)


class Accumulator:
    def __init__(self, decided: dict, files: list[str]) -> None:
        self.min_rows = decided["min_rows"]
        self.agreement = decided["agreement"]
        # File names are kept only to word a reason; they never decide.
        self.files = files
        self.pairs = 0
        self.agreeing = 0
        self.waiting: str | None = None

    def _compare(self, a: str, b: str) -> None:
        self.pairs += 1
        self.agreeing += _stem(a) == _stem(b)

    def add(self, row) -> None:
        if len(row) == 2:
            self._compare(row[0].name, row[1].name)
        elif self.waiting is None:
            self.waiting = row[0].name
        else:
            self._compare(self.waiting, row[0].name)
            self.waiting = None

    def result(self) -> Value | Undetermined:
        evidence = {"pairs": self.pairs, "agreeing": self.agreeing}
        if self.pairs < self.min_rows:
            return Undetermined(reason=f"only {self.pairs} pairs of reads", evidence=evidence)
        share = self.agreeing / self.pairs
        if share >= self.agreement:
            return Value(value=True, evidence=evidence)
        if len(self.files) == 1 and share <= 1 - self.agreement:
            return Value(value=False, evidence=evidence)
        if len(self.files) == 2 and _R1_FILE.search(self.files[0]):
            return Undetermined(reason="names say R1/R2, read names don't match", evidence=evidence)
        return Undetermined(reason="read names don't match", evidence=evidence)
