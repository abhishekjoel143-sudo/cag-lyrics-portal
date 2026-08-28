# CAG Lyrics Portal — Combined PPT/Nudi Converter + Song Website

This version combines the original CAG lyrics website with the supplied Nudi/Unicode PPT converter.

## Included features

1. **User login**
   - Email + password.
   - Registration sends a 6-digit OTP to the registered email.
   - OTP expires after 10 minutes.
   - After login, the top-right shows the user's numeric **User ID** and email.

2. **Centered song search**
   - Large search box in the center of the song page.
   - Live similar-title suggestions while typing.
   - Search results show matching/similar songs.
   - Click a song to open its lyrics.

3. **PPT upload → converter → database**
   - Admin uploads a `.pptx`.
   - The same Nudi/Unicode conversion logic supplied in the converter ZIP is run automatically.
   - Kannada Unicode lyrics and English pronunciation are saved to SQLite.
   - The new song immediately appears in the user song list.

4. **Admin complete editing**
   - Admin can edit the song title.
   - Admin can edit the entire Kannada lyrics.
   - Admin can edit the entire English pronunciation lyrics.
   - Admin can delete songs.

5. **Logo**
   - A working CAG logo asset is included at `static/logo.svg`.
   - It is displayed on the welcome/login/register/OTP/admin-login screens.
   - Replace this SVG with the church's official logo later if required.

6. **Song import**
   - Put the PPTX song files you provide into `songs_to_import/`.
   - Run `python import_songs.py`.
   - This uses the same converter and inserts the songs into the database.

## Setup on Windows

Open PowerShell inside this folder:

```powershell
python -m venv myenv
.\myenv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set:
- `SECRET_KEY`
- `ADMIN_ID`
- `ADMIN_PASSWORD`
- Gmail SMTP credentials if you want real OTP email delivery.

### Gmail OTP setup

Use a Gmail **App Password** for `MAIL_PASSWORD`. Do not put your normal Gmail password in the project.

Example:

```text
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=yourgmail@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=yourgmail@gmail.com
```

Then run:

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Important: database songs

The two ZIP files supplied with this build did not contain the actual song PPT files/database. The combined project therefore includes an empty `songs_to_import/` folder.

When you provide the song PPT/ZIP:
1. Put the PPTX files into `songs_to_import/`.
2. Run `python import_songs.py`.
3. They will be converted and stored in `instance/app.db`.

Alternatively, the admin can upload individual PPTX files from the Admin Dashboard.

## Database

The default database is:

`instance/app.db`

It is created automatically the first time the application starts.

For a large production deployment, PostgreSQL/MySQL can be configured later using `DATABASE_URL`.

## Project structure

- `app.py` — Flask routes, login, OTP, search, upload, admin edit.
- `models.py` — User, OTP and Song database models.
- `converter.py` — integrated PPT/Nudi/Unicode converter.
- `converter_source_original.py` — original converter supplied in the second ZIP.
- `import_songs.py` — bulk song/PPT importer.
- `templates/` — website pages.
- `static/css/style.css` — website design.
- `static/logo.svg` — included logo.
- `uploads/` — uploaded PPT files.
- `songs_to_import/` — place the song PPT files here for initial database import.
- `instance/app.db` — generated SQLite database.

## Flow

User:
Login/Register → Email OTP → Song Search → Similar Song List → Open Lyrics

Admin:
Admin Login → Dashboard → Upload PPT → Converter → Database → Song List

Admin editing:
Admin Dashboard → Edit Lyrics → Change title/Kannada/English completely → Save
