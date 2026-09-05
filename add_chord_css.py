from pathlib import Path

p = Path("templates/song_view.html")
s = p.read_text(encoding="utf-8-sig")

marker = """</style>

{% endblock %}"""

css = """
  /* =====================================================
     CHORD DISPLAY
  ====================================================== */

  .chords-controls {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;
    width: 100%;
    margin: 10px 0 20px 0;
    flex-wrap: wrap;
  }

  .transpose-controls {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  #transposeDisplay {
    font-weight: 600;
    white-space: nowrap;
  }

  .lyrics-with-chords {
    width: 100%;
  }

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

  @media (max-width: 768px) {

    .chords-controls {
      justify-content: center;
    }

    .transpose-controls {
      justify-content: center;
    }

  }

"""

if marker not in s:
    raise SystemExit("ERROR: style marker not found")

if ".lyrics-with-chords" in s:
    raise SystemExit("ERROR: chord CSS already exists")

s = s.replace(
    marker,
    css + "\n" + marker,
    1
)

p.write_text(
    s,
    encoding="utf-8-sig"
)

print("Chord CSS added successfully.")
