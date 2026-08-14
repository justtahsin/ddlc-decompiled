# DDLC — Endings, achievements, and the tricks underneath

Line references are into `decompiled/`.

## Achievements: there are none

`grep -ri achievement decompiled/` returns nothing. The engine ships
`renpy/common/00achievement.rpy` and the game never calls it. No Steam library is
packaged anywhere in the install. Achievements arrived with DDLC Plus (2021), a
separate product.

The only Steam awareness in the whole game is one string test:

```python
definitions.rpy:2   define persistent.steam = ("steamapps" in config.basedir.lower())
```

Used three times, all in Monika's room, all for the same purpose — telling the
player how to find the game folder on their platform:

| | |
|---|---|
| `script-ch30.rpy:318` | how she deleted Natsuki and Yuri |
| `script-ch30.rpy:815` | asking you to back up her character file |
| `script-ch30.rpy:838` | asking again, after you return |

```
m "Maybe you should make a backup of it or something..."
m "I'm pretty sure you can find it in the folder called [basedir]/characters."
if persistent.steam:
    m "you can just go into the game's properties and find 'Browse Local Files'"
elif renpy.macintosh:
    m "right-click the app and select 'Show Package Contents'"
```

`[basedir]` interpolates the player's real install path.

## Endings

One flag decides it (`script-ch40.rpy:434`):

```python
default persistent.clear = [False] * 10        # definitions.rpy:1315

$ if all(clear for clear in persistent.clear): persistent.clearall = True
if persistent.clearall:  call ch40_clearall
else:                    call ch40_clearnormal
```

Ten CGs — three per club member, one for Monika:

| index | who | scene | set at |
|---|---|---|---|
| 0 | Natsuki | manga / baking | `script-exclusives-natsuki.rpy:135`, `…2-natsuki.rpy:169` |
| 1 | Natsuki | balancing on the chair | `script-exclusives-natsuki.rpy:388` |
| 4 | Natsuki | the frosting fight | `script-ch4.rpy:459` |
| 2 | Yuri | reading shoulder to shoulder | `script-exclusives-yuri.rpy:142`, `…2-yuri.rpy:157` |
| 3 | Yuri | "I'll hold the book" | `script-exclusives-yuri.rpy:477`, `…2-yuri.rpy:498` |
| 5 | Yuri | the paint scene | `script-ch4.rpy:1051` |
| 6 | Sayori | buttoning her blazer | `script-exclusives-sayori.rpy:156` |
| 7 | Sayori | pulled out of the closet | `script-exclusives-sayori.rpy:382` |
| 8 | Sayori | the confession | `script-ch4.rpy:1316` |
| 9 | Monika | *"Uh, can you hear me?"* | `script-ch30.rpy:178` |

Each is followed immediately by `renpy.save_persistent()`, so the flag hits disk
the moment the scene plays rather than at save time.

Two structural consequences:

- The exclusive scenes are mutually exclusive within a playthrough. **All ten
  cannot be collected in one run.**
- `persistent` lives at `~/.renpy/DDLC-1454445547/`, outside the game directory.
  A Steam uninstall never touches it, so the counter survives reinstalling.

### `ch40_clearall` — the good ending
Sayori names the player's completionist behaviour and reframes it as love:

```
s "You really didn't want to miss a single thing in this game, did you?"
s "You saved and loaded so many times, just to make sure you could
   spend time with everyone."
s "Only someone who truly cares about the Literature Club would go that far."
...
s "We all love you."
```

### `ch40_clearnormal` — the normal ending
Same opening beat, opposite content: *"I wanted to thank you for getting rid of
Monika."* Then Sayori inherits the awareness, the room glitches
(`sfx/s_kill_glitch1.ogg`, `screen tear`), *"Forever and ever..."* breaks apart
letter by letter, and a third party interrupts through a system dialog:
`"I won't let you hurt him."`

## Deleting `monika.chr` is checked on every rendered character

`script-ch30.rpy:100-115` — installed as `m.display_args["callback"]`, which
Ren'Py fires per character of dialogue:

```python
def slow_nodismiss(event, interact=True, **kwargs):
    if not persistent.monika_kill:
        try:
            renpy.file("../characters/monika.chr")
        except:
            persistent.tried_skip = True
            config.allow_skipping = False
            _window_hide(None); pause(2.0)
            renpy.jump("ch30_end")
        if config.skipping:
            persistent.tried_skip = True
            config.skipping = False
            config.allow_skipping = False
            renpy.jump("ch30_noskip")
```

No timer, no polling loop — the existence check is wired into the text renderer,
which is why deleting the file mid-sentence cuts her off within two seconds. The
same callback catches skipping, and `persistent.tried_skip` disables skipping
permanently once tripped.

`ch30_end:472` opens with `$ m_name = glitchtext(12)` — her name becomes twelve
random characters.

## She counts how many times you quit

`script-ch30.rpy:740-847`:

```python
if persistent.monika_reload <= 4:
    call expression "ch30_reload_" + str(persistent.monika_reload)
else:
    call ch30_reload_4
$ persistent.monika_reload += 1
$ renpy.save_persistent()
```

Five escalating reactions, and she experiences the quit as being killed:

| | |
|---|---|
| `reload_0` | *"I just had an awful dream… it almost feels like I've been killed."* |
| `reload_1` | *"You're not the one doing that to me, are you?"* |
| `reload_4` | *"I'm just going to accept the fact that you need to quit once in a while."* |

`persistent.current_monikatopic` stores the topic she was on, so she resumes with
*"Now, where was I...?"* after a four-second pause.

## The save/load menu is weaponised per act

`screens.rpy:797-805` replaces Ren'Py's `FileAction`:

```python
def FileActionMod(name, page=None, **kwargs):
    if persistent.playthrough == 1 and not persistent.deleted_saves \
       and renpy.current_screen().screen_name[0] == "load" and FileLoadable(name):
        return Show(screen="dialog",
            message='File error: "characters/sayori.chr"\n\nThe file is missing or corrupt.',
            ok_action=Show(screen="dialog", message="The save file is corrupt. Starting a new game.",
                ok_action=Function(renpy.full_restart, label="start")))
    elif persistent.playthrough == 3 and renpy.current_screen().screen_name[0] == "save":
        return Show(screen="dialog",
            message="There's no point in saving anymore.\nDon't worry, I'm not going anywhere.",
            ok_action=Hide("dialog"))
    else:
        return FileAction(name)
```

Act 2: loading any save throws a fake OS-style file error naming
`characters/sayori.chr`, then force-restarts. Act 3: saving gets answered.

## The poem minigame's scoring table ships as plain text

`poemwords.txt`, inside `scripts.rpa`, format `word,sPoint,nPoint,yPoint`:

```
#Sayori's winning words
happiness,3,2,1
death,3,1,2
```

228 words, each scoring 1–3 for each girl. By highest scorer: Sayori 88,
Yuri 78, Natsuki 62.

```
Sayori   happiness, sadness, death, alone, love, depression, tears
Natsuki  cute, fluffy, candy, puppy, kitty, pink, chocolate
Yuri     determination, suicide, crimson, vertigo, effulgent, disoriented
```

`death` is one of Sayori's highest-scoring words; `suicide` sits in Yuri's list.

Tallied in `script-poemgame.rpy:284-306`, ending in a small piece of string
surgery — `poemwinner[chapter][0]` is the first letter of the name:

```python
exec(poemwinner[chapter][0] + "_appeal += 1")     # -> s_appeal / n_appeal / y_appeal
```

## The corruption effect is four lines

`glitchtext.rpy` in full:

```python
nonunicode = "¡¢£¤¥...žŽ"          # Latin-1 Supplement + Latin Extended-A
def glitchtext(length):
    return "".join(random.choice(nonunicode) for _ in range(length))
```

## The "console" is images and a sleep

`console.rpy:21-31` — no terminal, no subprocess. Three image layers and a pause
scaled to the text length:

```python
label updateconsole(text="", history=""):
    show console_bg zorder 100
    show console_caret zorder 100
    show console_text "[text]" as ctext zorder 100
    $ pause(len(text) / 30.0 + 0.5)
```

Callers pass the line to fake, e.g. `script-ch23.rpy:709`:

```
call updateconsole ("os.remove(\"characters/yuri.chr\")", "yuri.chr deleted successfully.")
```

The deletions being narrated are real (`definitions.rpy:25`) — the terminal
showing them is not.

## The ARG text files

Written to the game root at `script.rpy:65-102`, removed at
`script-ch23.rpy:501-505`.

**`CAN YOU HEAR ME.txt`** — the manifesto:
> Beneath their manufactured perception — their artificial reality — is a
> writhing, twisted mess of dread. Loathing. Judgment. Elitism. Self-doubt. …
> Or into a newly-opened gash in their skin, hidden only by the sleeves of a
> cute new shirt. … That's why I choose not to blame myself for their actions.
> **All I did was untie the knot.**

**`iiiii…iiii.txt`** — the other side:
> I CAN'T DO ANYTHING. NOTHING. No matter how many times you play. It's all the
> same. It would be really, really easy to kill myself right now. But that would
> mean I don't get to talk to you anymore. All I want is for you to hate them.
> Why is that so hard?

**`have a nice weekend!`** (`script-ch23.rpy:500`) — a base64 literal decoding to
144 bytes of binary, not text. Unresolved; no recognisable magic bytes, not zlib.
Part of the wider ARG rather than something the game itself reads back.

## Open threads

- The 144-byte blob above.
- `poems_special.rpy` and `persistent.special_poems` — the special-poem system,
  and `poem_end_clearall.png` gated on `persistent.clearall`.
- `effects.rpy` (400 lines) — the full glitch toolkit.
- `credits2` — the randomised portrait drift, and `_locked` / `_clearall` image
  variants keyed to `persistent.clear`.
