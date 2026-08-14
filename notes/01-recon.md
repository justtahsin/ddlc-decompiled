# Doki Doki Literature Club — Recon & Decompile

## Target
- Path: `steamapps/common/Doki Doki Literature Club/` (300 MB, AppID 698780)
- Engine: **Ren'Py 6.99.12.4** ("We get the job done.", vc_version 2187)
- Runtime: **Python 2.7** — game ships its own interpreter at `lib/linux-x86_64/python`
- Native Linux build. No Proton needed.
- Archives: **RPA-3.0**, no encryption, no obfuscation.

## Toolchain
- `tools/rpa_extract.py` — own RPA-3.0 extractor, ~30 lines, no dependencies.
- `unrpyc` v2.0.3 (master, targets Ren'Py 8). Warns about Ren'Py <= 7 input but
  decompiled all 35 files cleanly; spot checks read as normal source.
  Legacy branch (v1.x, Python 2) is the fallback if a construct comes out wrong.

## Output
- `extracted/scripts/` — 42 files out of `scripts.rpa` (2.6 MB)
- `decompiled/` — 35 `.rpy`, **24,189 lines**

## Snapshots
- `game-played/` — the install as it stood after previous playthroughs
- `game-fresh/` — reinstall, still carrying residue (see below)
- Live install cleaned to true factory state on 2026-08-15.
- All four `.rpa` are md5-identical across played and fresh installs; play never
  touches them.

## Steam uninstall does NOT reset the game
Uninstall + reinstall left these behind (game-created, not in the manifest):

    monika.chr natsuki.chr sayori.chr yuri.chr   (root, 3 of them 0 bytes)
    log.txt
    game/cache/

Root `monika.chr` is byte-identical to `characters/monika.chr` (md5 c146fd53…),
so the game copied it there. Removed manually to get a real baseline.

## Where the memory actually lives
`options.rpy:141` → `config.save_directory = "DDLC-1454445547"`

Linux: `~/.renpy/DDLC-1454445547/`. Outside the game directory, so a Steam
uninstall never touches it. This is the persistence mechanism.

Reinstall detection (`splash.rpy:220-249`): `game/firstrun` ships as 0 bytes and
the game writes `"1"` into it on first launch. Steam restores the 0-byte version
on reinstall while persistent survives → mismatch → *"A previous save file has
been found. Would you like to delete your save data and start over?"*

## The `.chr` system
The four `.chr` files are **inside `scripts.rpa`** as well as in `characters/`,
so the game can delete and restore them at will:

    definitions.rpy:25   os.remove(config.basedir + "/characters/" + name + ".chr")
    definitions.rpy:29   open(basedir + "/characters/monika.chr", "wb")
                             .write(renpy.file("monika.chr").read())

Restoration is keyed on `persistent.playthrough` (the act counter),
`splash.rpy:278-294`:

| playthrough | restored |
|---|---|
| <= 2 | monika |
| <= 1 or == 4 | natsuki, yuri |
| == 4 | sayori |

**`s_kill_early`** (`splash.rpy:279-283, 329-336`): at playthrough 0 the game
checks whether `characters/sayori.chr` is missing. If the player deleted it
before the game did, an alternate opening plays — its own music
(`bgm/s_kill_early.ogg`) and its own CG (`images/cg/s_kill_early.png`).

## OS-level tricks — **Windows only**
`splash.rpy:203-217`, entirely gated behind `if renpy.windows:`

```python
process_list = subprocess.check_output("wmic process get Description", shell=True)...
for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
    user = os.environ.get(name)
```

On Linux/macOS `process_list` stays `[]` and `currentuser` stays `""`, so both
payoffs below are dead. There is no OBS-specific API call — it is one full
process enumeration, filtered later.

### Payoff 1 — the name, suppressed while streaming (`script-ch30.rpy:200-204`)
```python
stream_list = ["obs32.exe", "obs64.exe", "obs.exe", "xsplit.core.exe",
               "livehime.exe", "pandatool.exe", "yymixer.exe",
               "douyutool.exe", "huomaotool.exe"]
if not list(set(process_list).intersection(stream_list)):   # NOT streaming
    if currentuser != "" and currentuser.lower() != player.lower():
        m "...Do you actually go by [currentuser] or something?"
```
Monika says the player's OS username only when nobody is recording — a
deliberate anti-doxx guard. The list covers Chinese platforms too (Bilibili,
Douyu, YY, Panda, Huomao).

### Payoff 2 — a scene only streamers get (`script-ch30.rpy:386-388, 398`)
```python
stream_list = ["obs32.exe", "obs64.exe", "obs.exe", "xsplit.core.exe"]
if list(set(process_list).intersection(stream_list)):
    call ch30_stream
```
`ch30_stream`: Monika addresses the audience, objects to being recorded without
warning, does a fake "trick" (zooms the master layer for 8s), then a jumpscare
(`monika_scare` + `sfx/mscare.ogg`). Shorter list here — OBS and XSplit only.

## The corruption effect is four lines
`glitchtext.rpy` — the whole "data corruption" look:

```python
nonunicode = "¡¢£¤¥...žŽ"          # Latin-1 Supplement + Latin Extended-A
def glitchtext(length):
    return "".join(random.choice(nonunicode) for _ in range(length))
```

## ARG files written to and removed from the game root
| file | written | removed |
|---|---|---|
| `hxppy thxughts.png` | `script.rpy:65` | `script-ch23.rpy:501` |
| `CAN YOU HEAR ME.txt` | `script.rpy:90` | `script-ch23.rpy:503` |
| `iiiii…iiii.txt` | `script.rpy:102` | `script-ch23.rpy:505` |
| `have a nice weekend!` | `script-ch23.rpy:500` (base64 literal) | `script-ch23.rpy:659` |

## Script layout
```
splash            warning screen, first-run, .chr restoration, s_kill_early
script            entry point + ARG file drops
script-ch0..ch5   Act 1
script-ch20..ch23 Act 2
script-ch30       Act 3 — Monika's room (88 KB decompiled, the largest scene)
script-ch40       Act 4
script-exclusives*  per-character scenes
script-poemresponses  115 KB — largest file in the game
poems / poems_special / script-poemgame   the poem minigame
definitions       104 KB — characters, images, helper functions
effects / glitchtext / transforms         the corruption toolkit
```

## Next
- `script-ch30.rpy` in full — the Monika room is where every fourth-wall beat lives.
- `definitions.rpy` helper functions: `delete_all_saves`, `restore_*_characters`.
- `screens.rpy:800` — the fake "File error: characters/sayori.chr" dialog.
- Decode the `have a nice weekend!` base64 blob.
- Diff `game-played/` vs `game-fresh/` for a full map of what play writes to disk.
