# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
pip install -r requirements.txt   # openai-whisper, tkinterdnd2
python whisper_gui.py             # run the app
```

FFmpeg must be on PATH (`winget install ffmpeg`) — Whisper shells out to it for audio decoding.

There is no test suite, linter, or build step. The only way to verify a change is to launch the GUI and transcribe a real audio file.

## Architecture

The entire application is [whisper_gui.py](whisper_gui.py) — a single Tkinter window class, `WhisperApp`. Some structural decisions are load-bearing and not obvious from a skim:

**The base class is chosen at import time.** `BASE = TkinterDnD.Tk if DND_AVAILABLE else tk.Tk` ([whisper_gui.py:28](whisper_gui.py#L28)). `tkinterdnd2` is an optional dependency: when it is missing, the app degrades to browse-only and every `drop_target_register` call is skipped. Any change to drag-and-drop must keep the no-DND path working.

**Whisper is imported lazily inside the worker thread**, not at module scope ([whisper_gui.py:251](whisper_gui.py#L251)), and only when the selected mode actually needs transcription (`do_transcribe`). This is what keeps the window painting immediately instead of blocking several seconds on the torch import, and what makes "Extraire seulement" mode not pay any Whisper/torch cost at all. Moving that import to the top of the file would visibly regress startup.

**All GUI mutation from the worker goes through `self.after(0, ...)`.** `_process_batch` runs on a daemon thread and never touches widgets directly — it marshals every status, log, and progress update back onto the Tk main loop. Tkinter is not thread-safe; calling a widget method from the worker will crash or corrupt the display intermittently. Preserve this discipline in any new background work.

**`_process_batch` drives three modes off one `mode_var` combobox**: "Transcrire seulement", "Extraire seulement", "Extraire puis transcrire" (`do_extract`/`do_transcribe` booleans derived from it). `whisper.load_model` happens once before the per-file loop only if `do_transcribe`; a failure there aborts the whole batch via `_err`, whereas a per-file failure (extraction or transcription) is caught, logged, counted in `err_count`, and the loop continues. Video files get their audio extracted to a sibling `.mp3` via `_extract_audio` (shells out to `ffmpeg -vn -acodec libmp3lame`) before transcription; audio files skip extraction even when the mode requests it. Transcription output is written as a sibling `.txt` next to the *original* source file (not the extracted `.mp3`) and silently overwrites an existing one.

**`parse_drop_paths` exists because tkinterdnd2 hands over a single string**, not a list. Paths containing spaces arrive wrapped in `{...}` braces while simple paths are bare and space-separated, so the two forms have to be parsed in one pass ([whisper_gui.py:30](whisper_gui.py#L30)).

## Conventions

UI strings are deliberately **unaccented ASCII** ("Aucun fichier charge", "Batch termine") even though the app is French and the README uses full accents. Match the surrounding style rather than "correcting" the labels.

Style is dense on purpose: semicolon-joined statements, colors and fonts as module-level constants at the top, short method names prefixed with `_`. New UI code should read the same way.

## Landmines

Lines 3–6 prepend a **hardcoded `Python314` user site-packages path** to `sys.path` as a `tkinterdnd2` import workaround. It is a no-op on any other interpreter version (the Python on PATH here is 3.12), so it is not the reason imports currently succeed — don't treat it as active machinery, and don't assume editing it fixes an import problem.

`_process_batch` sets `ssl._create_default_https_context = ssl._create_unverified_context` process-wide before downloading a model ([whisper_gui.py:253](whisper_gui.py#L253)). This disables certificate verification for every subsequent HTTPS call in the process, not just the model fetch.

`_on_drop` classifies a path as invalid purely by extension, so a dropped **directory** counts as invalid and is reported in the "format non supporte" warning rather than being expanded. Accepted extensions are `MEDIA_EXT` (`AUDIO_EXT | VIDEO_EXT`); a video passed straight to `model.transcribe()` (mode "Transcrire seulement") still works because Whisper shells out to ffmpeg internally regardless of container — the explicit `_extract_audio` step exists only to produce a reusable standalone audio file, not because Whisper needs it.
