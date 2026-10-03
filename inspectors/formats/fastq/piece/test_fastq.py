"""The FASTQ format: four-line records, confirmed by content, a cut head handled."""

import io
import pathlib

import fastq  # the piece; inspectors/conftest.py puts each piece/ on sys.path

FIX = pathlib.Path(__file__).parent / "fixtures"


def _records(path):
    return list(fastq.records(io.BufferedReader(io.BytesIO(path.read_bytes()))))


def test_confirms_fastq_and_refuses_fasta():
    assert fastq.confirms((FIX / "few/f.fq").read_bytes()[:4096])
    assert not fastq.confirms((FIX / "fasta_named_fastq/x.fastq").read_bytes()[:4096])


def test_crlf_is_read_without_the_carriage_return():
    records = _records(FIX / "crlf/w.fq")
    assert len(records) == 200
    assert all(not r.sequence.endswith(b"\r") and len(r.sequence) == 50 for r in records)


def test_a_cut_last_record_is_dropped():
    records = _records(FIX / "cut/c.fq")
    assert len(records) == 50 and all(len(r.sequence) == len(r.quality) for r in records)


def test_the_name_stops_at_the_first_space():
    assert _records(FIX / "pair_casava/s_1.fq")[0].name == "r0"


def test_the_pair_suffix_is_kept_for_the_measure_to_judge():
    assert _records(FIX / "interleaved/s.fq")[0].name == "r0/1"


def test_a_long_read_cut_by_the_window_is_still_confirmed():
    """Review of #134: an ONT or PacBio read of 10 kb does not fit four lines in 4 KiB."""
    record = b"@long\n" + b"A" * 10_000 + b"\n+\n" + b"I" * 10_000 + b"\n"
    assert fastq.confirms(record[:4096])
    assert fastq.confirms(record[:10_020])


def test_a_window_that_is_not_fastq_is_still_refused():
    assert not fastq.confirms(b"@HD\tVN:1.6\n@SQ\tSN:chr1\tLN:100\n")
    assert not fastq.confirms(b"@x\nACGT\nACGT\nIIII\n")
    assert not fastq.confirms(b"@x\nACGT\n+\nIIIIIIII\n")


def _read(data: bytes):
    return fastq.records(io.BufferedReader(io.BytesIO(data)))


def test_a_malformed_record_mid_head_is_said_not_swallowed():
    """Issue 224: a whole record that is wrong, with bytes after it, is not a cut head."""
    from comeni_inspect.records import Malformed

    good = b"@r1\nACGT\n+\nIIII\n@r2\nACGT\n+\nIIII\n"
    bad = b"@r3\nACGT\n+\nII\n"
    got = []
    try:
        for record in _read(good + bad + good):
            got.append(record.name)
    except Malformed as malformed:
        assert str(malformed) == "record 3: its quality is not its sequence's length"
    else:
        raise AssertionError("a malformed record ended the stream quietly")
    assert got == ["r1", "r2"]


def test_a_record_without_its_at_sign_is_malformed():
    from comeni_inspect.records import Malformed

    try:
        list(_read(b"@r1\nACGT\n+\nIIII\nr2\nACGT\n+\nIIII\n"))
    except Malformed as malformed:
        assert str(malformed) == "record 2: it does not start with @"
    else:
        raise AssertionError("a record without @ ended the stream quietly")


def test_the_name_stops_at_a_tab_too():
    assert [r.name for r in _read(b"@r0/1\tBC:1\nACGT\n+\nIIII\n")] == ["r0/1"]
