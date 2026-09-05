from pathlib import Path

p = Path("templates/song_view.html")
s = p.read_text(encoding="utf-8-sig")

marker = "<style>\n"

css = """<style>

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

"""

if ".lyrics-chord-row {" in s:
    print("Chord CSS already exists. No changes made.")
    raise SystemExit

if marker not in s:
    raise SystemExit("ERROR: <style> marker not found")

s = s.replace(marker, css, 1)

p.write_text(s, encoding="utf-8-sig")

print("SUCCESS: Chord CSS added safely.")
