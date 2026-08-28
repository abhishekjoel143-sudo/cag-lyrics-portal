from pathlib import Path
from models import db, Song
from app import app
from converter import convert_pptx_to_lyrics


# ============================================================
# FOLDER CONTAINING PPTX FILES
# ============================================================

PPT_FOLDER = Path(r"E:\CAG_Lyrics_Portal_Combined\cag-lyrics-site\songs_to_import\slides 1")


# ============================================================
# CLEAN SONG TITLE
# ============================================================

def clean_title(filename):
    """
    Convert PPT filename into a clean song title.
    """

    name = Path(filename).stem

    # Remove temporary PowerPoint files
    if name.startswith("~$"):
        return ""

    return name.strip()


# ============================================================
# IMPORT SONGS
# ============================================================

def import_songs():

    if not PPT_FOLDER.exists():

        print("ERROR: PPT folder not found:")
        print(PPT_FOLDER)

        return

    # --------------------------------------------------------
    # Find all PPTX files recursively
    # --------------------------------------------------------

    files = sorted(
        [
            p for p in PPT_FOLDER.rglob("*.pptx")
            if not p.name.startswith("~$")
        ],
        key=lambda p: str(p).lower()
    )

    print("=" * 70)
    print("              CAG LYRICS SONG IMPORT")
    print("=" * 70)

    print()
    print("PPT folder:")
    print(PPT_FOLDER)

    print()
    print(f"Total PPTX files found: {len(files)}")
    print()

    imported = 0
    skipped = 0
    failed = 0

    with app.app_context():

        for index, pptx_path in enumerate(files, start=1):

            try:

                title = clean_title(pptx_path.name)

                if not title:

                    print(
                        f"[{index}/{len(files)}] "
                        f"SKIPPED: {pptx_path.name}"
                    )

                    skipped += 1
                    continue

                # ------------------------------------------------
                # Check duplicate by original filename
                # ------------------------------------------------

                existing = Song.query.filter_by(
                    original_filename=pptx_path.name
                ).first()

                if existing:

                    print(
                        f"[{index}/{len(files)}] "
                        f"SKIPPED - Already exists: {title}"
                    )

                    skipped += 1
                    continue

                # ------------------------------------------------
                # Convert PPTX
                # ------------------------------------------------

                kannada_text, english_text = convert_pptx_to_lyrics(
                    pptx_path
                )

                # ------------------------------------------------
                # Validate conversion
                # ------------------------------------------------

                if not kannada_text.strip() and not english_text.strip():

                    print(
                        f"[{index}/{len(files)}] "
                        f"SKIPPED - No text: {pptx_path.name}"
                    )

                    skipped += 1
                    continue

                # ------------------------------------------------
                # Create Song
                # ------------------------------------------------

                song = Song(
                    title=title,
                    kannada_text=kannada_text,
                    english_text=english_text,
                    original_filename=pptx_path.name
                )

                db.session.add(song)

                imported += 1

                print(
                    f"[{index}/{len(files)}] "
                    f"IMPORTED: {title}"
                )

                # ------------------------------------------------
                # Commit every 50 songs
                # ------------------------------------------------

                if imported % 50 == 0:

                    db.session.commit()

                    print(
                        f"    -> Saved {imported} songs..."
                    )

            except Exception as exc:

                failed += 1

                print()
                print(
                    f"[{index}/{len(files)}] "
                    f"FAILED: {pptx_path.name}"
                )

                print(
                    f"    ERROR: {exc}"
                )

                # Roll back this failed transaction
                db.session.rollback()

        # --------------------------------------------------------
        # Final commit
        # --------------------------------------------------------

        try:

            db.session.commit()

        except Exception as exc:

            db.session.rollback()

            print()
            print("FINAL DATABASE COMMIT FAILED:")
            print(exc)

            return

    # ============================================================
    # SUMMARY
    # ============================================================

    print()
    print("=" * 70)
    print("                 IMPORT COMPLETE")
    print("=" * 70)

    print(f"Total PPTX files : {len(files)}")
    print(f"Imported         : {imported}")
    print(f"Skipped          : {skipped}")
    print(f"Failed           : {failed}")

    print("=" * 70)


if __name__ == "__main__":
    import_songs()