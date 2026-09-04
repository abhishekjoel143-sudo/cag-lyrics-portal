import os
import secrets

from datetime import datetime
from functools import wraps
from difflib import SequenceMatcher

from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    session,
    jsonify,
)

from werkzeug.utils import secure_filename

from models import (
    db,
    User,
    Song,
    ListedSong,
    Visitor,
)

from converter import convert_pptx_to_lyrics


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# DIRECTORIES
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "uploads"
)

INSTANCE_DIR = os.path.join(
    BASE_DIR,
    "instance"
)

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

os.makedirs(
    INSTANCE_DIR,
    exist_ok=True
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# FLASK CONFIGURATION
# ============================================================

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "dev-secret-change-me"
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(INSTANCE_DIR, 'app.db')}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 2 GB upload limit
app.config["MAX_CONTENT_LENGTH"] = (
    2 * 1024 * 1024 * 1024
)


# ============================================================
# DATABASE
# ============================================================

db.init_app(app)


# ============================================================
# APPLICATION SETTINGS
# ============================================================

CHURCH_NAME = (
    "Calvary Assembly of God Church (CAG)"
)

ADMIN_ID = os.environ.get(
    "ADMIN_ID",
    "Calvary CAG"
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "CalvaryMusic"
)


# ============================================================
# ALLOWED FILE TYPES
# ============================================================

ALLOWED_EXTENSIONS = {
    "pptx"
}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================================
# VISITOR TRACKING
# ============================================================

@app.before_request
def track_visitor():

    # Only track GET requests
    if request.method != "GET":
        return

    # Don't track admin pages
    if request.path.startswith("/admin"):
        return

    # Don't track static files
    if request.path.startswith("/static"):
        return

    # Don't track favicon
    if request.path == "/favicon.ico":
        return

    try:

        visitor = Visitor(
            ip_address=request.remote_addr,
            user_agent=request.headers.get(
                "User-Agent"
            ),
            page=request.path,
            visited_at=datetime.utcnow()
        )

        db.session.add(
            visitor
        )

        db.session.commit()

    except Exception as exc:

        db.session.rollback()

        print(
            "[VISITOR TRACKING ERROR]",
            exc
        )


# ============================================================
# ADMIN REQUIRED
# ============================================================

def admin_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if not session.get("is_admin"):

            flash(
                "Please log in as admin to continue.",
                "error"
            )

            return redirect(
                url_for("admin_login")
            )

        return view(
            *args,
            **kwargs
        )

    return wrapped


# ============================================================
# LOGIN REQUIRED
# ============================================================

def login_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if not session.get("user_id"):

            flash(
                "Please log in to continue.",
                "error"
            )

            return redirect(
                url_for("user_login")
            )

        return view(
            *args,
            **kwargs
        )

    return wrapped


# ============================================================
# GLOBAL USER INFORMATION
# ============================================================

@app.context_processor
def inject_user():

    user = None

    if session.get("user_id"):

        try:

            user = db.session.get(
                User,
                session["user_id"]
            )

        except Exception:

            user = None

    return {
        "current_user": user,
        "is_admin": bool(
            session.get("is_admin")
        )
    }


# ============================================================
# WELCOME PAGE
# ============================================================

@app.route("/")
def welcome():

    return render_template(
        "welcome.html"
    )


# ============================================================
# ROBOTS.TXT
# ============================================================

@app.route("/robots.txt")
def robots_txt():

    return (
        "User-agent: *\n"
        "Allow: /\n\n"
        "Sitemap: "
        "https://cag-lyrics-portal.onrender.com/"
        "sitemap.xml\n"
    ), 200, {
        "Content-Type":
        "text/plain; charset=utf-8"
    }


# ============================================================
# SITEMAP.XML
# ============================================================

@app.route("/sitemap.xml")
def sitemap():

    return send_from_directory(
        app.static_folder,
        "sitemap.xml",
        mimetype="application/xml"
    )


# ============================================================
# USER REGISTRATION
# ============================================================
#
# Username
# Password
# Confirm Password
#
# Mobile number and OTP are NOT required.
#
# The old mobile database column is kept internally so the
# existing database structure is not damaged.
#
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = " ".join(
            request.form.get(
                "username",
                ""
            ).strip().split()
        )

        password = request.form.get(
            "password",
            ""
        )

        confirm = request.form.get(
            "confirm_password",
            ""
        )

        # ----------------------------------------------------
        # REQUIRED FIELDS
        # ----------------------------------------------------

        if (
            not username
            or not password
            or not confirm
        ):

            flash(
                "Username and password are required.",
                "error"
            )

            return render_template(
                "register.html"
            )

        # ----------------------------------------------------
        # USERNAME VALIDATION
        # ----------------------------------------------------

        if not username.replace(
            " ",
            ""
        ).isalpha():

            flash(
                "Name can contain letters and spaces only.",
                "error"
            )

            return render_template(
                "register.html"
            )

        if len(username) < 3:

            flash(
                "Name must be at least 3 characters.",
                "error"
            )

            return render_template(
                "register.html"
            )

        # ----------------------------------------------------
        # PASSWORD VALIDATION
        # ----------------------------------------------------

        if password != confirm:

            flash(
                "Passwords do not match.",
                "error"
            )

            return render_template(
                "register.html"
            )

        if len(password) < 6:

            flash(
                "Password must be at least 6 characters.",
                "error"
            )

            return render_template(
                "register.html"
            )

        # ----------------------------------------------------
        # CHECK USERNAME
        # ----------------------------------------------------

        existing_username = User.query.filter_by(
            username=username
        ).first()

        if existing_username:

            flash(
                "An account with this username already exists. "
                "Please log in.",
                "error"
            )

            return redirect(
                url_for("user_login")
            )

        # ----------------------------------------------------
        # INTERNAL LEGACY MOBILE VALUE
        # ----------------------------------------------------

        internal_mobile = (
            "u"
            + secrets.token_hex(9)
        )

        # ----------------------------------------------------
        # CREATE USER
        # ----------------------------------------------------

        user = User(
            username=username,
            mobile=internal_mobile,
            is_verified=True
        )

        user.set_password(
            password
        )

        # ----------------------------------------------------
        # SAVE USER
        # ----------------------------------------------------

        try:

            db.session.add(
                user
            )

            db.session.commit()

        except Exception as exc:

            db.session.rollback()

            print(
                "[REGISTRATION ERROR]",
                exc
            )

            flash(
                "Could not create the account. Please try again.",
                "error"
            )

            return render_template(
                "register.html"
            )

        flash(
            "Account created successfully. You can now log in.",
            "success"
        )

        return redirect(
            url_for("user_login")
        )

    return render_template(
        "register.html"
    )


# ============================================================
# USER LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def user_login():

    if request.method == "POST":

        username = " ".join(
            request.form.get(
                "username",
                ""
            ).strip().split()
        )

        password = request.form.get(
            "password",
            ""
        )

        if not username or not password:

            flash(
                "Username and password are required.",
                "error"
            )

            return render_template(
                "login.html"
            )

        user = User.query.filter_by(
            username=username
        ).first()

        if (
            not user
            or not user.check_password(
                password
            )
        ):

            flash(
                "Incorrect username or password.",
                "error"
            )

            return render_template(
                "login.html"
            )

        session["user_id"] = user.id

        flash(
            "Logged in successfully.",
            "success"
        )

        return redirect(
            url_for("song_list")
        )

    return render_template(
        "login.html"
    )


# ============================================================
# USER LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.pop(
        "user_id",
        None
    )

    flash(
        "Logged out.",
        "success"
    )

    return redirect(
        url_for("welcome")
    )


# ============================================================
# SIMILARITY SEARCH
# ============================================================

def similarity_score(
    query,
    title
):

    q = query.lower().strip()
    t = title.lower().strip()

    if not q:
        return 0

    if q in t:
        return 1.0

    return SequenceMatcher(
        None,
        q,
        t
    ).ratio()


# ============================================================
# USER SONG LIST
# ============================================================

@app.route("/songs")
@login_required
def song_list():

    q = request.args.get(
        "q",
        ""
    ).strip()

    all_songs = (
        Song.query
        .order_by(
            Song.title.asc()
        )
        .all()
    )

    if q:

        ranked = sorted(
            (
                (
                    similarity_score(
                        q,
                        song.title
                    ),
                    song
                )
                for song in all_songs
            ),
            key=lambda x: x[0],
            reverse=True
        )

        songs = [
            song
            for score, song in ranked
            if score >= 0.20
        ][:30]

    else:

        songs = all_songs

    return render_template(
        "song_list.html",
        songs=songs,
        query=q
    )


# ============================================================
# SONG VIEW
# ============================================================

@app.route(
    "/songs/<int:song_id>"
)
@login_required
def song_view(song_id):

    song = Song.query.get_or_404(
        song_id
    )

    lang = request.args.get(
        "lang",
        "kannada"
    )

    from_listed = (
        request.args.get(
            "from_listed",
            "0"
        ) == "1"
    )

    return render_template(
        "song_view.html",
        song=song,
        lang=lang,
        from_listed=from_listed
    )


# ============================================================
# SONG SEARCH API
# ============================================================

@app.route(
    "/api/songs/search"
)
@login_required
def api_song_search():

    q = request.args.get(
        "q",
        ""
    ).strip()

    songs = (
        Song.query
        .order_by(
            Song.title.asc()
        )
        .all()
    )

    if not q:

        ranked = [
            (
                1,
                s
            )
            for s in songs[:20]
        ]

    else:

        ranked = sorted(
            (
                (
                    similarity_score(
                        q,
                        s.title
                    ),
                    s
                )
                for s in songs
            ),
            key=lambda x: x[0],
            reverse=True
        )

        ranked = [
            (
                score,
                s
            )
            for score, s in ranked
            if score >= 0.20
        ][:10]

    return jsonify(
        [
            {
                "id": s.id,
                "title": s.title,
                "score": round(
                    score,
                    3
                )
            }
            for score, s in ranked
        ]
    )


# ============================================================
# USER EDIT SONG
# ============================================================

@app.route(
    "/songs/<int:song_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def user_edit_song(song_id):

    song = Song.query.get_or_404(
        song_id
    )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        kannada_text = request.form.get(
            "kannada_text",
            ""
        )

        english_text = request.form.get(
            "english_text",
            ""
        )

        if not title:

            flash(
                "Song title cannot be empty.",
                "error"
            )

            return render_template(
                "user_edit_chords.html",
                song=song
            )

        song.title = title

        song.kannada_text = (
            kannada_text
        )

        song.english_text = (
            english_text
        )

        try:

            db.session.commit()

        except Exception as exc:

            db.session.rollback()

            print(
                "[USER SONG EDIT ERROR]",
                exc
            )

            flash(
                "Could not save the song. Please try again.",
                "error"
            )

            return render_template(
                "user_edit_chords.html",
                song=song
            )

        flash(
            "Song lyrics and chords updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "song_view",
                song_id=song.id
            )
        )

    return render_template(
        "user_edit_chords.html",
        song=song
    )


# ============================================================
# ADD SONG TO LIST
# ============================================================

@app.route(
    "/songs/<int:song_id>/add-to-list",
    methods=["POST"]
)
@login_required
def add_to_list(song_id):

    song = Song.query.get_or_404(
        song_id
    )

    user_id = session["user_id"]

    existing = (
        ListedSong.query
        .filter_by(
            user_id=user_id,
            song_id=song.id
        )
        .first()
    )

    if existing:

        flash(
            "Song is already in your listed songs.",
            "success"
        )

    else:

        listed_song = ListedSong(
            user_id=user_id,
            song_id=song.id
        )

        db.session.add(
            listed_song
        )

        db.session.commit()

        flash(
            "Song added to your listed songs.",
            "success"
        )

    return redirect(
        url_for(
            "song_view",
            song_id=song.id
        )
    )


# ============================================================
# LISTED SONGS
# ============================================================

@app.route("/listed-songs")
@login_required
def listed_songs():

    user_id = session["user_id"]

    listed = (
        ListedSong.query
        .filter_by(
            user_id=user_id
        )
        .order_by(
            ListedSong.created_at.desc()
        )
        .all()
    )

    return render_template(
        "listed_songs.html",
        listed_songs=listed
    )


# ============================================================
# DELETE LISTED SONG
# ============================================================

@app.route(
    "/listed-songs/<int:listed_id>/delete",
    methods=["POST"]
)
@login_required
def delete_listed_song(listed_id):

    listed = ListedSong.query.get_or_404(
        listed_id
    )

    if listed.user_id != session["user_id"]:

        flash(
            "You cannot remove another user's song.",
            "error"
        )

        return redirect(
            url_for("listed_songs")
        )

    db.session.delete(
        listed
    )

    db.session.commit()

    flash(
        "Song removed from your listed songs.",
        "success"
    )

    return redirect(
        url_for("listed_songs")
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        admin_id = request.form.get(
            "admin_id",
            ""
        ).strip()

        admin_password = request.form.get(
            "admin_password",
            ""
        )

        if (
            admin_id == ADMIN_ID
            and ADMIN_PASSWORD
            and admin_password == ADMIN_PASSWORD
        ):

            session["is_admin"] = True

            flash(
                "Admin login successful.",
                "success"
            )

            return redirect(
                url_for("admin_dashboard")
            )

        flash(
            "Incorrect admin ID or password.",
            "error"
        )

    return render_template(
        "admin_login.html"
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop(
        "is_admin",
        None
    )

    flash(
        "Admin logged out.",
        "success"
    )

    return redirect(
        url_for("welcome")
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    query = request.args.get(
        "q",
        ""
    ).strip()

    all_songs = (
        Song.query
        .order_by(
            Song.uploaded_at.desc()
        )
        .all()
    )

    if query:

        ranked = sorted(
            (
                (
                    similarity_score(
                        query,
                        song.title
                    ),
                    song
                )
                for song in all_songs
            ),
            key=lambda x: x[0],
            reverse=True
        )

        songs = [
            song
            for score, song in ranked
            if score >= 0.20
        ]

    else:

        songs = all_songs

    return render_template(
        "admin_dashboard.html",
        songs=songs,
        query=query,
        total_songs=len(all_songs)
    )


# ============================================================
# ADMIN VISITOR RECORDS
# ============================================================

@app.route("/admin/visitors")
@admin_required
def admin_visitors():

    visitors = (
        Visitor.query
        .order_by(
            Visitor.visited_at.desc()
        )
        .all()
    )

    total_visitors = Visitor.query.count()

    return render_template(
        "admin_visitors.html",
        visitors=visitors,
        total_visitors=total_visitors
    )


# ============================================================
# DELETE ONE VISITOR RECORD
# ============================================================

@app.route(
    "/admin/visitors/<int:visitor_id>/delete",
    methods=["POST"]
)
@admin_required
def delete_visitor(visitor_id):

    visitor = Visitor.query.get_or_404(
        visitor_id
    )

    try:

        db.session.delete(
            visitor
        )

        db.session.commit()

        flash(
            "Visitor record deleted successfully.",
            "success"
        )

    except Exception as exc:

        db.session.rollback()

        print(
            "[DELETE VISITOR ERROR]",
            exc
        )

        flash(
            "Could not delete visitor record.",
            "error"
        )

    return redirect(
        url_for("admin_visitors")
    )


# ============================================================
# DELETE ALL VISITOR RECORDS
# ============================================================

@app.route(
    "/admin/visitors/delete-all",
    methods=["POST"]
)
@admin_required
def delete_all_visitors():

    try:

        deleted_count = (
            Visitor.query.delete(
                synchronize_session=False
            )
        )

        db.session.commit()

        flash(
            f"{deleted_count} visitor records deleted successfully.",
            "success"
        )

    except Exception as exc:

        db.session.rollback()

        print(
            "[DELETE ALL VISITORS ERROR]",
            exc
        )

        flash(
            "Could not delete visitor records.",
            "error"
        )

    return redirect(
        url_for("admin_visitors")
    )


# ============================================================
# ADMIN SINGLE PPTX UPLOAD
# ============================================================

@app.route(
    "/admin/upload",
    methods=["GET", "POST"]
)
@admin_required
def admin_upload():

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        file = request.files.get(
            "pptx_file"
        )

        if not title:

            flash(
                "Please provide a song title.",
                "error"
            )

            return render_template(
                "admin_upload.html"
            )

        if not file or not file.filename:

            flash(
                "Please choose a .pptx file.",
                "error"
            )

            return render_template(
                "admin_upload.html"
            )

        if not allowed_file(
            file.filename
        ):

            flash(
                "Only .pptx files are supported.",
                "error"
            )

            return render_template(
                "admin_upload.html"
            )

        filename = secure_filename(
            file.filename
        )

        if not filename:

            flash(
                "Invalid filename.",
                "error"
            )

            return render_template(
                "admin_upload.html"
            )

        save_path = os.path.join(
            UPLOAD_DIR,
            filename
        )

        if os.path.exists(save_path):

            base, ext = os.path.splitext(
                filename
            )

            counter = 1

            while os.path.exists(
                save_path
            ):

                filename = (
                    f"{base}_{counter}{ext}"
                )

                save_path = os.path.join(
                    UPLOAD_DIR,
                    filename
                )

                counter += 1

        try:

            file.save(
                save_path
            )

            kannada_text, english_text = (
                convert_pptx_to_lyrics(
                    save_path
                )
            )

        except Exception as exc:

            print(
                f"[SINGLE UPLOAD ERROR] "
                f"{filename}: {exc}"
            )

            flash(
                f"PowerPoint conversion failed: {exc}",
                "error"
            )

            return render_template(
                "admin_upload.html"
            )

        if not kannada_text.strip():

            flash(
                "The PPT was read, but no text "
                "was found in its slides.",
                "error"
            )

            return render_template(
                "admin_upload.html"
            )

        song = Song(
            title=title,
            kannada_text=kannada_text,
            english_text=english_text,
            original_filename=filename
        )

        db.session.add(
            song
        )

        db.session.commit()

        flash(
            f"'{title}' was converted and added "
            f"to the song database.",
            "success"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    return render_template(
        "admin_upload.html"
    )


# ============================================================
# ADMIN BULK PPTX UPLOAD
# ============================================================

@app.route(
    "/admin/bulk-upload",
    methods=["GET", "POST"]
)
@admin_required
def admin_bulk_upload():

    if request.method == "POST":

        files = request.files.getlist(
            "pptx_files"
        )

        if not files:

            flash(
                "Please select one or more PPTX files.",
                "error"
            )

            return render_template(
                "admin_bulk_upload.html"
            )

        processed = 0
        skipped = 0
        failed = 0

        for file in files:

            if not file or not file.filename:
                continue

            original_filename = file.filename

            if not allowed_file(
                original_filename
            ):

                print(
                    f"[BULK SKIPPED] "
                    f"Not a PPTX: "
                    f"{original_filename}"
                )

                failed += 1
                continue

            filename = secure_filename(
                original_filename
            )

            if not filename:

                failed += 1
                continue

            save_path = os.path.join(
                UPLOAD_DIR,
                filename
            )

            if os.path.exists(
                save_path
            ):

                base, ext = os.path.splitext(
                    filename
                )

                counter = 1

                while os.path.exists(
                    save_path
                ):

                    filename = (
                        f"{base}_{counter}{ext}"
                    )

                    save_path = os.path.join(
                        UPLOAD_DIR,
                        filename
                    )

                    counter += 1

            try:

                file.save(
                    save_path
                )

                kannada_text, english_text = (
                    convert_pptx_to_lyrics(
                        save_path
                    )
                )

                if not kannada_text.strip():

                    print(
                        f"[BULK FAILED] "
                        f"No text found: "
                        f"{filename}"
                    )

                    failed += 1
                    continue

                title = os.path.splitext(
                    filename
                )[0].strip()

                if not title:

                    failed += 1
                    continue

                existing = (
                    Song.query
                    .filter_by(
                        title=title
                    )
                    .first()
                )

                if existing:

                    print(
                        f"[BULK SKIPPED] "
                        f"Already exists: "
                        f"{title}"
                    )

                    skipped += 1
                    continue

                song = Song(
                    title=title,
                    kannada_text=kannada_text,
                    english_text=english_text,
                    original_filename=filename
                )

                db.session.add(
                    song
                )

                processed += 1

                print(
                    f"[BULK SUCCESS] "
                    f"{title}"
                )

            except Exception as exc:

                print(
                    f"[BULK UPLOAD ERROR] "
                    f"{filename}: {exc}"
                )

                failed += 1

        try:

            db.session.commit()

        except Exception as exc:

            db.session.rollback()

            print(
                f"[DATABASE ERROR] "
                f"{exc}"
            )

            flash(
                f"Database error during bulk upload: "
                f"{exc}",
                "error"
            )

            return redirect(
                url_for("admin_dashboard")
            )

        flash(
            f"Bulk upload complete: "
            f"{processed} imported, "
            f"{skipped} skipped, "
            f"{failed} failed.",
            "success"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    return render_template(
        "admin_bulk_upload.html"
    )


# ============================================================
# ADMIN EDIT SONG
# ============================================================
#
# IMPORTANT CHORD SYSTEM
#
# Original Kannada and English lyrics are stored separately
# and remain unchanged.
#
# Chords are stored separately in song.chords.
#
# There is ONE shared chord arrangement for the complete song.
#
# The same chord arrangement is used for:
#
#     Kannada lyrics
#     English pronunciation
#
# Song Key is stored separately in:
#
#     song.chord_key
#
# Example:
#
#     Dm
#     Am
#     F#
#     C#
#
# The exact key selected by the Admin is saved and sent to
# song_view.html.
#
# The old chords_enabled database field is maintained only
# for backward compatibility.
#
# ============================================================

@app.route(
    "/admin/songs/<int:song_id>/edit",
    methods=["GET", "POST"]
)
@admin_required
def admin_edit_song(song_id):

    song = Song.query.get_or_404(
        song_id
    )

    # ========================================================
    # POST REQUEST
    # ========================================================

    if request.method == "POST":

        # ----------------------------------------------------
        # SONG TITLE
        # ----------------------------------------------------

        title = request.form.get(
            "title",
            ""
        ).strip()

        # ----------------------------------------------------
        # ORIGINAL KANNADA LYRICS
        # ----------------------------------------------------

        kannada_text = request.form.get(
            "kannada_text",
            ""
        )

        # ----------------------------------------------------
        # ORIGINAL ENGLISH PRONUNCIATION
        # ----------------------------------------------------

        english_text = request.form.get(
            "english_text",
            ""
        )

        # ----------------------------------------------------
        # SONG KEY
        # ----------------------------------------------------
        #
        # This is the IMPORTANT new part.
        #
        # The Admin selects the original song key.
        #
        # Examples:
        #
        # C
        # C#
        # Dm
        # Am
        # F#
        #
        # The exact value is saved.
        #
        # ----------------------------------------------------

        chord_key = request.form.get(
            "chord_key",
            ""
        ).strip()

        # ----------------------------------------------------
        # CHORD DATA
        # ----------------------------------------------------

        chord_data = request.form.get(
            "chord_data",
            ""
        ).strip()

        # ====================================================
        # VALIDATE TITLE
        # ====================================================

        if not title:

            flash(
                "Song title cannot be empty.",
                "error"
            )

            return render_template(
                "admin_edit_song.html",
                song=song
            )

        # ====================================================
        # SAVE ORIGINAL SONG DATA
        # ====================================================
        #
        # IMPORTANT:
        #
        # Do NOT add chord spacing to these fields.
        #
        # Original lyrics remain unchanged.
        #
        # ====================================================

        song.title = title

        song.kannada_text = (
            kannada_text
        )

        song.english_text = (
            english_text
        )

        # ====================================================
        # SAVE SONG KEY
        # ====================================================
        #
        # The exact key selected by Admin is stored.
        #
        # Example:
        #
        # Admin selects Dm
        #
        # Database:
        #
        # song.chord_key = "Dm"
        #
        # User side:
        #
        # Dm
        #
        # ====================================================

        if chord_key:

            song.chord_key = chord_key

        else:

            song.chord_key = None

        # ====================================================
        # SAVE SHARED CHORD ARRANGEMENT
        # ====================================================
        #
        # ONE chord arrangement for BOTH languages.
        #
        # ====================================================

        if chord_data:

            song.chords = chord_data

            # Keep old database field synchronized.
            #
            # This field is NOT shown as a checkbox.

            song.chords_enabled = True

        else:

            song.chords = None

            song.chords_enabled = False

        # ====================================================
        # DATABASE SAVE
        # ====================================================

        try:

            db.session.commit()

        except Exception as exc:

            db.session.rollback()

            print(
                "[ADMIN SONG EDIT ERROR]",
                exc
            )

            flash(
                "Could not save the song. Please try again.",
                "error"
            )

            return render_template(
                "admin_edit_song.html",
                song=song
            )

        # ====================================================
        # SUCCESS MESSAGE
        # ====================================================

        if chord_data and chord_key:

            flash(
                f"Song saved successfully. "
                f"Song Key: {chord_key}. "
                f"The same chords are saved for both languages.",
                "success"
            )

        elif chord_key:

            flash(
                f"Song saved successfully. "
                f"Song Key: {chord_key}.",
                "success"
            )

        elif chord_data:

            flash(
                "Song saved successfully. "
                "The same chords are saved for both languages.",
                "success"
            )

        else:

            flash(
                "Song saved successfully.",
                "success"
            )

        return redirect(
            url_for(
                "admin_dashboard"
            )
        )

    # ========================================================
    # GET REQUEST
    # ========================================================

    return render_template(
        "admin_edit_song.html",
        song=song
    )


# ============================================================
# ADMIN DELETE SONG
# ============================================================

@app.route(
    "/admin/songs/<int:song_id>/delete",
    methods=["POST"]
)
@admin_required
def admin_delete_song(song_id):

    song = Song.query.get_or_404(
        song_id
    )

    db.session.delete(
        song
    )

    db.session.commit()

    flash(
        "Song deleted.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

with app.app_context():

    db.create_all()


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        )
    )