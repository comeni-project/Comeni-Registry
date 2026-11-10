"""Read length: the most common length, over every read of every file."""

from collections import Counter

from comeni_inspect.outcome import Undetermined, Value


class Accumulator:
    def __init__(self, decided: dict, files: list[str]) -> None:
        self.min_records = decided["min_records"]
        self.modal_share = decided["modal_share"]
        self.lengths: Counter[int] = Counter()

    def add(self, row) -> None:
        for record in row:
            self.lengths[len(record.sequence)] += 1

    def result(self) -> Value | Undetermined:
        records = sum(self.lengths.values())
        if records < self.min_records:
            return Undetermined(reason=f"only {records} reads", evidence={"records": records})
        modal, count = max(self.lengths.items(), key=lambda item: (item[1], item[0]))
        low, high = min(self.lengths), max(self.lengths)
        evidence = {
            "records": records,
            "share": round(count / records, 4),
            "min": low,
            "max": high,
        }
        if count / records < self.modal_share:
            return Undetermined(reason=f"lengths vary: {low}–{high}, trimmed?", evidence=evidence)
        return Value(value=modal, evidence=evidence)
