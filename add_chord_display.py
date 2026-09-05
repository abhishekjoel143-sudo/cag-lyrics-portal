from pathlib import Path

p = Path("templates/song_view.html")
s = p.read_text(encoding="utf-8-sig")

marker = """<div class="lyrics-box"
    id="lyricsBox"
  >"""

block = """<div
  id="chordLyricsDisplay"
  class="chord-lyrics-display"
  style="display: none;"
></div>

"""

if marker not in s:
    raise SystemExit("ERROR: lyrics box marker not found")

if "id=\"chordLyricsDisplay\"" in s:
    raise SystemExit("ERROR: Chord lyrics display already exists")

s = s.replace(marker, block + marker, 1)

p.write_text(s, encoding="utf-8-sig")

print("Chord lyrics display added successfully.")
