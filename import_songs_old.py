import os
from models import db, Song
from app import app

# ============================================================
# FOLDER CONTAINING YOUR CONVERTED LYRICS
# ============================================================

LYRICS_FOLDER = r"C:\Users\Joel Abhishek S\OneDrive\Desktop\slides 1\converted_lyrics"


def clean_title(filename):
    """
    Convert filename into a clean song title.
    """

    name = os.path.splitext(filename)[0]

    # Remove known suffixes
    suffixes = [
        "_lyrics",
        "_Kannada_English",
        "_English"
    ]

    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]

    return name.strip()


def read_file(filepath):
    """
    Read lyric file using UTF-8.
    """

    encodings = [
        "utf-8-sig",
        "utf-8",
        "utf-16",
        "cp1252"
    ]

    for encoding in encodings:
        try:
            with open(
                filepath,
                "r",
                encoding=encoding
            ) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        f"Could not decode file: {filepath}"
    )


def import_lyrics():
    if not os.path.exists(LYRICS_FOLDER):
        print("ERROR: Lyrics folder not found:")
        print(LYRICS_FOLDER)
        return

    files = [
        f for f in os.listdir(LYRICS_FOLDER)
        if f.lower().endswith(".txt")
    ]

    print("=" * 70)
    print("             CAG LYRICS IMPORT")
    print("=" * 70)

    print(f"Lyrics folder:")
    print(LYRICS_FOLDER)
    print()

    print(f"Total TXT files found: {len(files)}")
    print()

    imported = 0
    skipped = 0
    failed = 0

    with app.app_context():

        for index, filename in enumerate(
            sorted(files),
            start=1
        ):

            filepath = os.path.join(
                LYRICS_FOLDER,
                filename
            )

            try:

                title = clean_title(filename)

                text = read_file(filepath).strip()

                if not text:
                    print(
                        f"[{index}/{len(files)}] "
                        f"SKIPPED - Empty: {filename}"
                    )

                    skipped += 1
                    continue

                # ------------------------------------------------
                # Check whether this song already exists
                # ------------------------------------------------

                existing = Song.query.filter_by(
                    title=title
                ).first()

                if existing:

                    skipped += 1

                    print(
                        f"[{index}/{len(files)}] "
                        f"SKIPPED - Already exists: {title}"
                    )

                    continue

                # ------------------------------------------------
                # Determine language/content
                # ------------------------------------------------

                if "_Kannada_English" in filename:

                    kannada_text = text
                    english_text = ""

                elif "_English" in filename:

                    kannada_text = ""
                    english_text = text

                else:

                    kannada_text = text
                    english_text = ""

                # ------------------------------------------------
                # Create database record
                # ------------------------------------------------

                song = Song(
                    title=title,
                    kannada_text=kannada_text,
                    english_text=english_text,
                    original_filename=filename
                )

                db.session.add(song)

                imported += 1

                print(
                    f"[{index}/{len(files)}] "
                    f"IMPORTED: {title}"
                )

                # Commit every 50 songs
                if imported % 50 == 0:
                    db.session.commit()
                    print(
                        f"   -> Saved {imported} songs..."
                    )

            except Exception as exc:

                failed += 1

                print(
                    f"[{index}/{len(files)}] "
                    f"FAILED: {filename}"
                )

                print(
                    f"   ERROR: {exc}"
                )

        # Final commit
        db.session.commit()

    print()
    print("=" * 70)
    print("                 IMPORT COMPLETE")
    print("=" * 70)

    print(f"Total TXT files : {len(files)}")
    print(f"Imported        : {imported}")
    print(f"Skipped         : {skipped}")
    print(f"Failed          : {failed}")

    print("=" * 70)


if __name__ == "__main__":
    import_lyrics()