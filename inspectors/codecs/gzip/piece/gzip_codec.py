"""gzip: open the bytes as a gzip stream. The runner caps what comes out and treats a stream cut
mid-way (every head is) as its end."""

import gzip
import io


def open(raw: bytes) -> io.BufferedIOBase:
    return gzip.GzipFile(fileobj=io.BytesIO(raw))
