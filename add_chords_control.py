from pathlib import Path

p = Path("templates/song_view.html")
s = p.read_text(encoding="utf-8-sig")

marker = """<!-- =================================================
     ADD TO LISTED SONGS
================================================== -->"""

block = """<!-- =================================================
     CHORDS CONTROL
================================================== -->

<div class="chords-controls">

  <button
    type="button"
    id="toggleChordsButton"
    class="btn btn-secondary"
    onclick="toggleChords()"
  >
    🎸 Show Chords
  </button>

  <div
    id="chordsControls"
    class="transpose-controls"
    style="display: none;"
  >

    <button
      type="button"
      class="btn btn-secondary"
      onclick="transposeDown()"
    >
      −
    </button>

    <span id="transposeDisplay">
      Key: {{ song.chord_key or 'Original' }}
    </span>

    <button
      type="button"
      class="btn btn-secondary"
      onclick="transposeUp()"
    >
      +
    </button>

    <button
      type="button"
      class="btn btn-secondary"
      onclick="resetTranspose()"
    >
      Reset
    </button>

  </div>

</div>

<div id="chordsData" style="display: none;">{{ song.chords or '' }}</div>

"""

if marker not in s:
    raise SystemExit("ERROR: marker not found")

if "toggleChordsButton" in s:
    raise SystemExit("ERROR: Chords control already exists")

s = s.replace(marker, block + marker, 1)

p.write_text(s, encoding="utf-8-sig")

print("Show Chords control added successfully.")
