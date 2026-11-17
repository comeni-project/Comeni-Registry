"""The FASTA format: `>` records over many lines, confirmed by content, a FASTQ refused."""

import io
import pathlib

import fasta  # the piece; measurers/conftest.py puts each piece/ on sys.path
import pytest
from comeni_inspect.records import Malformed

FIX = pathlib.Path(__file__).parent / "fixtures"


def _records(raw: bytes):
    return list(fasta.records(io.BufferedReader(io.BytesIO(raw))))


def test_confirms_fasta_and_refuses_fastq():
    assert fasta.confirms((FIX / "multiline/a.fna").read_bytes()[:4096])
    assert not fasta.confirms((FIX / "fastq_named_fasta/x.fasta").read_bytes()[:4096])
    assert not fasta.confirms(b"")


def test_a_window_cut_inside_the_first_sequence_line_is_confirmed():
    assert fasta.confirms(b">contig_1 len=2800000\nACGTACGTAC")


def test_sequence_lines_are_joined_and_the_name_stops_at_a_space():
    records = _records((FIX / "multiline/a.fna").read_bytes())
    assert [(r.name, len(r.sequence)) for r in records] == [("c1", 16), ("c2", 30), ("c3", 5)]
    assert all(r.quality is None for r in records)


def test_crlf_is_read_without_the_carriage_return():
    records = _records((FIX / "crlf/w.fa").read_bytes())
    assert [r.sequence for r in records] == [b"ACGTACGTACGT", b"ACG"]


def test_a_sequence_with_other_than_letters_is_malformed():
    with pytest.raises(Malformed, match="record 2"):
        _records(b">a\nACGT\n>b\nAC GT\n")
    with pytest.raises(Malformed, match="before any >"):
        _records(b"ACGT\n>a\nACGT\n")


def test_an_empty_file_is_unreadable_not_an_assembly():
    from comeni_inspect.run import inspect
    from support_pieces import request_for

    assert inspect(*request_for("empty", None, format="fasta")).unreadable == "e.fna is empty"
