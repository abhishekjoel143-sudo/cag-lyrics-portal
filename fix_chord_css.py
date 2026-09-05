from pathlib import Path

p = Path("templates/song_view.html")
s = p.read_text(encoding="utf-8-sig")

marker = """  .lyrics-with-chords {
    width: 100%;
  }"""

css = """

  .lyrics-chord-row {
    width: 100%;
    margin-bottom: 12px;
  }

  .lyrics-chord-line {
    min-height: 22px;
    font-weight: 700;
    white-space: pre-wrap;
    font-family: inherit;
    line-height: 1.2;
  }

  .lyrics-line {
    white-space: pre-wrap;
    line-height: 1.7;
  }
"""

if ".lyrics-chord-row {" in s:
    print("Chord row CSS already exists. No changes made.")
else:
    if marker not in s:
        raise SystemExit("ERROR: existing chord CSS marker not found")

    s = s.replace(marker, marker + css, 1)
    p.write_text(s, encoding="utf-8-sig")
    print("SUCCESS: Missing chord CSS added.")
