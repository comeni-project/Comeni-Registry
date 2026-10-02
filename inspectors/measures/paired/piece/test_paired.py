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
