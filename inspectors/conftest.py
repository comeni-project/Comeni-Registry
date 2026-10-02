"""Each piece's tests import the piece by its file name: put every `piece/` on `sys.path`."""

import pathlib
import sys

for piece in sorted(pathlib.Path(__file__).parent.glob("*/*/piece")):
    sys.path.insert(0, str(piece))
sys.path.insert(0, str(pathlib.Path(__file__).parent))
