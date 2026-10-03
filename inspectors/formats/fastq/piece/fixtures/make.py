"""Regenerate every FASTQ fixture case, deterministically (`random.Random(134)`, gzip mtime 0).

Run from anywhere: `uv run python inspectors/formats/fastq/piece/fixtures/make.py`. Each case is
a folder of files; the conformance test adds the golden report beside them as `expected.json`.
Cases that must reach the 1,000-read threshold are gzipped, to keep the registry small.
"""

import gzip
import pathlib
import random
import shutil

HERE = pathlib.Path(__file__).parent
rng = random.Random(134)


def seq(n: int) -> str:
    return "".join(rng.choice("ACGT") for _ in range(n))


def qual(n: int, low: int = 35, high: int = 74) -> str:
    return "".join(chr(rng.randint(low, high)) for _ in range(n))


def record(name: str, length: int, low: int = 35, high: int = 74) -> str:
    return f"@{name}\n{seq(length)}\n+\n{qual(length, low, high)}\n"


def write(case: str, name: str, text: str) -> None:
    folder = HERE / case
    folder.mkdir(parents=True, exist_ok=True)
    data = text.encode()
    if name.endswith(".gz"):
        data = gzip.compress(data, mtime=0)
    (folder / name).write_bytes(data)


def main() -> None:
    for old in HERE.iterdir():
        if old.is_dir():
            shutil.rmtree(old)

    write("single_150", "s_R1.fastq.gz", "".join(record(f"r{n}", 150) for n in range(2000)))

    r1, r2 = [], []
    for n in range(2000):
        r1.append(record(f"r{n}/1", 150))
        r2.append(record(f"r{n}/2", 150))
    write("pair_150", "s_R1.fq.gz", "".join(r1))
    write("pair_150", "s_R2.fq.gz", "".join(r2))

    write("pair_casava", "s_1.fq", "".join(record(f"r{n} 1:N:0:1", 50) for n in range(200)))
    write("pair_casava", "s_2.fq", "".join(record(f"r{n} 2:N:0:1", 50) for n in range(200)))

    write(
        "interleaved",
        "s.fq",
        "".join(record(f"r{n}/1", 50) + record(f"r{n}/2", 50) for n in range(200)),
    )

    write("names_disagree", "a_R1.fq", "".join(record(f"r{n}", 50) for n in range(200)))
    write("names_disagree", "a_R2.fq", "".join(record(f"x{n}", 50) for n in range(200)))

    trimmed = "".join(record(f"r{n}", rng.randint(100, 151)) for n in range(1500))
    write("trimmed", "t.fq.gz", trimmed)
    write("few", "f.fq", "".join(record(f"r{n}", 150) for n in range(12)))
    write("phred64", "old.fq", "".join(record(f"r{n}", 50, 64, 104) for n in range(200)))
    write("ambiguous_quality", "q.fq", "".join(record(f"r{n}", 50, 64, 73) for n in range(200)))
    write("crlf", "w.fq", "".join(record(f"r{n}", 50) for n in range(200)).replace("\n", "\r\n"))

    whole = "".join(record(f"r{n}", 50) for n in range(50))
    write("cut", "c.fq", whole + f"@r50\n{seq(50)}\n")

    write("fasta_named_fastq", "x.fastq", "".join(f">a{n}\nACGT\n" for n in range(20)))

    data = gzip.compress("".join(record(f"r{n}", 150) for n in range(2000)).encode(), mtime=0)
    (HERE / "truncated_gzip").mkdir()
    (HERE / "truncated_gzip" / "t.fq.gz").write_bytes(data[: len(data) // 2])

    write("pair_r2_short", "s_R1.fq", "".join(record(f"r{n}/1", 50) for n in range(400)))
    write("pair_r2_short", "s_R2.fq", "".join(record(f"r{n}/2", 50) for n in range(200)))

    (HERE / "empty").mkdir()
    (HERE / "empty" / "e.fq").write_bytes(b"")

    # Issue 224, added last so the cases above keep their bytes. Record 101 is whole and wrong,
    # with records after it: the facts say where reading stopped.
    before = "".join(record(f"r{n}", 50) for n in range(100))
    after = "".join(record(f"r{n}", 50) for n in range(101, 200))
    write("malformed", "m.fq", before + f"@r100\n{seq(50)}\n+\n{qual(20)}\n" + after)
    # A name ends at a tab as at a space.
    write("pair_tab", "s_1.fq", "".join(record(f"r{n}/1\tBC:1", 50) for n in range(200)))
    write("pair_tab", "s_2.fq", "".join(record(f"r{n}/2\tBC:1", 50) for n in range(200)))


if __name__ == "__main__":
    main()
