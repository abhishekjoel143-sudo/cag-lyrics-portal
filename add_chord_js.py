from pathlib import Path

p = Path("templates/song_view.html")
s = p.read_text(encoding="utf-8-sig")

marker = """</script>

<!-- =====================================================
     STYLES
====================================================== -->"""

js = r"""
  // =====================================================
  // CHORD DISPLAY + TRANSPOSE
  // =====================================================

  let chordsVisible = false;
  let transposeSteps = 0;

  const originalChords = {{ song.chords|tojson }};
  const originalKey = {{ (song.chord_key or '')|tojson }};

  const chordNames = [
    "C", "C#", "D", "D#", "E", "F",
    "F#", "G", "G#", "A", "A#", "B"
  ];

  function transposeChord(chord, steps) {

    const match = chord.match(/^([A-G](?:#|b)?)(.*)$/);

    if (!match) {
      return chord;
    }

    const aliases = {
      "Db": "C#",
      "Eb": "D#",
      "Gb": "F#",
      "Ab": "G#",
      "Bb": "A#"
    };

    const root = aliases[match[1]] || match[1];

    const index = chordNames.indexOf(root);

    if (index < 0) {
      return chord;
    }

    const newIndex =
      (index + steps % 12 + 12) % 12;

    return chordNames[newIndex] + match[2];
  }


  function transposeText(text, steps) {

    if (!text) {
      return "";
    }

    return text.replace(
      /\b[A-G](?:#|b)?(?:m|maj|min|dim|aug|sus|add)?[0-9]*(?:\/[A-G](?:#|b)?)?\b/g,
      function(chord) {
        return transposeChord(chord, steps);
      }
    );
  }


  function getTransposedChords() {

    return transposeText(
      originalChords,
      transposeSteps
    );
  }


  function updateTransposeDisplay() {

    const display =
      document.getElementById("transposeDisplay");

    if (!display) {
      return;
    }

    if (originalKey) {

      display.textContent =
        "Key: " +
        transposeChord(
          originalKey,
          transposeSteps
        );

    } else {

      display.textContent = "Key: Original";

    }
  }


  function applyChordsToLyrics() {

    const lyricsElements =
      document.querySelectorAll(".lyrics-text");

    const chordLines =
      getTransposedChords().split(/\r?\n/);

    lyricsElements.forEach(function(lyricsElement) {

      const lyricsLines =
        lyricsElement.textContent.split(/\r?\n/);

      const wrapper =
        document.createElement("div");

      wrapper.className =
        "lyrics-with-chords";

      lyricsLines.forEach(function(line, index) {

        const row =
          document.createElement("div");

        row.className =
          "lyrics-chord-row";

        const chord =
          document.createElement("div");

        chord.className =
          "lyrics-chord-line";

        chord.textContent =
          chordLines[index] || "";

        const lyric =
          document.createElement("div");

        lyric.className =
          "lyrics-line";

        lyric.textContent =
          line;

        row.appendChild(chord);
        row.appendChild(lyric);

        wrapper.appendChild(row);

      });

      lyricsElement.style.display = "none";

      lyricsElement.parentNode.insertBefore(
        wrapper,
        lyricsElement
      );

    });

  }


  function removeChordsFromLyrics() {

    document
      .querySelectorAll(".lyrics-with-chords")
      .forEach(function(element) {

        element.remove();

      });

    document
      .querySelectorAll(".lyrics-text")
      .forEach(function(element) {

        element.style.display = "";

      });

  }


  function refreshChordDisplay() {

    if (chordsVisible) {

      removeChordsFromLyrics();

      applyChordsToLyrics();

    }

    updateTransposeDisplay();

  }


  function toggleChords() {

    chordsVisible =
      !chordsVisible;

    const button =
      document.getElementById(
        "toggleChordsButton"
      );

    const controls =
      document.getElementById(
        "chordsControls"
      );

    if (chordsVisible) {

      applyChordsToLyrics();

      if (button) {
        button.textContent =
          "🎸 Hide Chords";
      }

      if (controls) {
        controls.style.display =
          "flex";
      }

    } else {

      removeChordsFromLyrics();

      if (button) {
        button.textContent =
          "🎸 Show Chords";
      }

      if (controls) {
        controls.style.display =
          "none";
      }

    }

  }


  function transposeUp() {

    transposeSteps++;

    refreshChordDisplay();

  }


  function transposeDown() {

    transposeSteps--;

    refreshChordDisplay();

  }


  function resetTranspose() {

    transposeSteps = 0;

    refreshChordDisplay();

  }

"""

if marker not in s:
    raise SystemExit("ERROR: script marker not found")

if "function toggleChords()" in s:
    raise SystemExit("ERROR: chord JavaScript already exists")

s = s.replace(
    marker,
    js + "\n" + marker,
    1
)

p.write_text(
    s,
    encoding="utf-8-sig"
)

print("Chord JavaScript added successfully.")
