#!/usr/bin/env python3
"""Extract a Ren'Py RPA-3.0 archive.

Format is small enough not to warrant a dependency:
  header  ->  b"RPA-3.0 %016x %08x\n"   (index offset, obfuscation key)
  index   ->  zlib-compressed Python 2 pickle at that offset
              {name: [(offset, length, prefix), ...]}
              with offset and length XORed against the key

  rpa_extract.py game/scripts.rpa extracted/scripts
"""
import pickle
import sys
import zlib
from pathlib import Path


def read_index(fh):
    header = fh.readline()
    if not header.startswith(b"RPA-3.0"):
        sys.exit(f"not an RPA-3.0 archive (header: {header[:20]!r})")
    _, offset, key = header.split()[:3]

    fh.seek(int(offset, 16))
    index = pickle.loads(zlib.decompress(fh.read()), encoding="latin1")
    key = int(key, 16)

    return {
        name: [(off ^ key, length ^ key, prefix) for off, length, prefix in entries]
        for name, entries in index.items()
    }


def main():
    archive = Path(sys.argv[1])
    dest = Path(sys.argv[2])

    with archive.open("rb") as fh:
        index = read_index(fh)

        total = 0
        for name, entries in sorted(index.items()):
            out = dest / name
            out.parent.mkdir(parents=True, exist_ok=True)
            with out.open("wb") as w:
                for off, length, prefix in entries:
                    # A prefix is stored inline in the index; the rest follows at off.
                    if isinstance(prefix, str):
                        prefix = prefix.encode("latin1")
                    w.write(prefix)
                    fh.seek(off)
                    w.write(fh.read(length - len(prefix)))
            total += out.stat().st_size

    print(f"{archive.name}: {len(index)} files, {total / 1024 / 1024:.1f} MB -> {dest}")


if __name__ == "__main__":
    main()
