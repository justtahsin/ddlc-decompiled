# ddlc-re

Decompiled scripts from Doki Doki Literature Club.
For research and educational purposes. No assets included.

## Target

| | |
|---|---|
| Engine | Ren'Py 6.99.12.4 (vc_version 2187) |
| Runtime | Python 2.7 |
| Archives | RPA-3.0, no encryption, no obfuscation |
| Platform | native Linux build |

## Contents

- `decompiled/` — 35 `.rpy` files, 24,189 lines
- `notes/` — recon writeup: the persistence mechanism, the `.chr` system,
  the Windows-only OS hooks, the ARG file drops
- `tools/rpa_extract.py` — standalone RPA-3.0 extractor, no dependencies

## Reproducing

```sh
python3 tools/rpa_extract.py "<game>/game/scripts.rpa" extracted/scripts

git clone --depth 1 https://github.com/CensoredUsername/unrpyc
cp -r extracted/scripts decompiled && rm -f decompiled/*.txt decompiled/*.chr
python3 unrpyc/unrpyc.py --clobber decompiled/*.rpyc
```

unrpyc v2 targets Ren'Py 8 and warns on this input, but decompiled all 35 files
cleanly. Its legacy branch (v1.x, Python 2) is the fallback — the game also
ships a usable Python 2.7 at `lib/linux-x86_64/python`.

## See also

[needy-girl-overdose-re](https://github.com/justtahsin/needy-girl-overdose-re)
— same exercise against a Unity/Mono target.
