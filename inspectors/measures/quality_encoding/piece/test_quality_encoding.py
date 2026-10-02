"""Quality encoding: Phred+33 or Phred+64, decided only by a character only one allows."""

from comeni_inspect.run import inspect
from support_pieces import request_for


def _enc(case):
    return inspect(*request_for(case, ["quality_encoding"])).facts["quality_encoding"]


def test_modern_is_phred33():
    assert _enc("single_150").value == "phred33"


def test_old_illumina_is_phred64():
    assert _enc("phred64").value == "phred64"


def test_overlap_is_undetermined():
    assert _enc("ambiguous_quality").undetermined == "characters fit both Phred+33 and Phred+64"


def test_twelve_reads_are_not_enough():
    assert _enc("few").undetermined == "only 12 reads"


def _decide(low: int, high: int):
    """The rule alone, over 200 reads whose qualities span `low`..`high` (issue 222)."""
    from comeni_inspect.records import SequenceRecord
    from quality_encoding import Accumulator

    acc = Accumulator({"min_records": 100}, ["x.fq"])
    for _ in range(200):
        acc.add((SequenceRecord("r", b"AC", bytes([low, high])),))
    return acc.result()


def test_long_reads_above_h_are_phred33():
    """PacBio HiFi and ONT write Phred+33 above Q41; Phred+64 never goes past `h` (104)."""
    assert _decide(60, 126).value == "phred33"


def test_inside_the_overlap_with_a_solexa_low_end_is_undetermined():
    """`;`–`?` (59–63) is outside Phred+64's `@` floor: phred64 is not decided from it."""
    assert _decide(60, 90).reason == "characters fit both Phred+33 and Phred+64"


def test_everything_in_at_to_h_above_j_is_phred64():
    assert _decide(64, 90).value == "phred64"
