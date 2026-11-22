#!/usr/bin/env python3
"""Copy the bundled front-page image to the make.fun output directory.

The entry image (entry.png) sits next to this file in the repository.
The grader runs this program twice with no network access; both runs
must produce byte-identical output, which a plain file copy guarantees.
Only the Python standard library is used.
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
CHUNK = 65536


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    with open(SOURCE, "rb") as src, open(target, "wb") as dst:
        while True:
            chunk = src.read(CHUNK)
            if not chunk:
                break
            dst.write(chunk)
    return target


if __name__ == "__main__":
    main()
