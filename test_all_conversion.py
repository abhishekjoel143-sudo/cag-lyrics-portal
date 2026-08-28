from pathlib import Path
import zipfile
from converter import convert_pptx_to_lyrics

ROOT = Path(r"songs_to_import\slides 1")

files = [
    p for p in ROOT.rglob("*.pptx")
    if not p.name.startswith("~$")
]

print("=" * 70)
print("FULL PPTX CONVERSION TEST")
print("=" * 70)
print(f"Total PPTX found: {len(files)}")
print()

success = 0
invalid = 0
failed = 0

invalid_files = []
failed_files = []

for i, pptx in enumerate(files, 1):

    print(f"[{i}/{len(files)}] {pptx.name}")

    # Check whether PPTX is actually a valid ZIP/PPTX
    if not zipfile.is_zipfile(pptx):
        print("    INVALID PPTX - skipped")
        invalid += 1
        invalid_files.append(pptx)
        continue

    try:
        kannada_text, english_text = convert_pptx_to_lyrics(pptx)

        if not kannada_text.strip():
            print("    WARNING: No text extracted")
        else:
            success += 1
            print("    OK")

    except Exception as e:
        failed += 1
        failed_files.append((pptx, str(e)))
        print(f"    FAILED: {e}")

print()
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)

print(f"Total PPTX : {len(files)}")
print(f"Successful : {success}")
print(f"Invalid    : {invalid}")
print(f"Failed     : {failed}")

if invalid_files:
    print()
    print("INVALID FILES:")
    for f in invalid_files:
        print(" -", f)

if failed_files:
    print()
    print("FAILED FILES:")
    for f, error in failed_files:
        print(" -", f)
        print("   ", error)

print()
print("=" * 70)
print("Conversion test complete.")
print("=" * 70)