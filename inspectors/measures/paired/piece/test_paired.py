"""Paired: decided from read names, never from file names (spec §5)."""

from comeni_inspect.run import inspect
from support_pieces import request_for


def _paired(case):
    return inspect(*request_for(case, ["paired"])).facts["paired"]


def test_two_files_with_matching_names_are_paired():
    assert _paired("pair_150").value is True
    assert _paired("pair_casava").value is True


def test_one_interleaved_file_is_paired():
    assert _paired("interleaved").value is True


def test_one_plain_file_is_single_end():
    assert _paired("single_150").value is False


def test_file_names_alone_never_decide():
    assert _paired("names_disagree").undetermined == "names say R1/R2, read names don't match"


def test_a_short_r2_stops_at_the_shorter_file_and_still_decides():
    fact = _paired("pair_r2_short")
    assert fact.value is True and fact.evidence["rows"] == 200


def test_too_few_rows_are_undetermined():
    assert _paired("few").undetermined == "only 6 pairs of reads"


def test_file_names_say_r1_r2_only_when_both_do():
    """Issue 224: the wording checked only the first file's name."""
    import paired
    from comeni_inspect.records import SequenceRecord

    def row(a, b):
        return (SequenceRecord(a, b"A", b"I"), SequenceRecord(b, b"A", b"I"))

    for second, said in (("a_R2.fq", "names say R1/R2, "), ("other.fq", "")):
        measure = paired.Accumulator({"min_rows": 2, "agreement": 0.9}, ["a_R1.fq", second])
        for n in range(4):
            measure.add(row(f"x{n}", f"y{n}"))
        assert measure.result().reason == f"{said}read names don't match"
