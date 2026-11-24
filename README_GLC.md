# GLC Mumbai Journals (Janeway)

One press, one law review and eight subject journals, all on Janeway JMS, with a custom theme called **GLCLaw**.

| Journal | Web address | Main / accent colour |
|---|---|---|
| The Law Review, Government Law College, Mumbai | `/lawreview/` | #7A1E2E / #C9A227 |
| Constitution Law | `/constitution/` | #002F65 / #8FB3E0 |
| Taxation Law | `/taxation/` | #1B5E3B / #D4A017 |
| Criminal Law | `/criminal/` | #2B3440 / #C0392B |
| Banking, Finance and Mercantile Law | `/bfm/` | #8A6410 / #1F3A5F |
| Women Law | `/women/` | #6B2A5B / #E0A3CF |
| Human Rights | `/humanrights/` | #A8431A / #F2B880 |
| Cyber, AI and Allied Laws | `/cyberai/` | #0E7490 / #7DD3E8 |
| Business Law | `/business/` | #4C3FA0 / #B9B2F0 |

The home of the press (`/`) lists all nine journals.

## This copy is pre-built

The database already has the press, all 9 journals, sample issues and articles, and your
superuser account. You do **not** need to run `install_janeway` or `glc_seed` yourself.

## Start in two steps

1. Install Python 3.10, 3.11 or 3.12.
2. Run `bash setup.sh` (Linux/Mac) or double-click `setup.bat` (Windows) — this only installs
   Python packages into a virtual environment, since the site itself is already built.
3. Run `bash run.sh` (or double-click `run.bat`) and open <http://localhost:8000/>.

**Login:** use the email address and password given to you separately when this copy was
prepared. Janeway logs people in by **email address**, not a plain username — type the full
address in the email field on the login page. **Change the password the first time you log
in** (click your name, top right, then "My profile").

## Running it in Docker instead

A `Dockerfile` and a `docker-compose.glc.yml` are included, built specifically for this
pre-seeded copy (Janeway's own `docker-compose.yml` and `dockerfiles/` in this repo are for
a different, Postgres-based dev setup — ignore those for this package).

```
docker compose -f docker-compose.glc.yml up --build
```

Then open <http://localhost:8000/>. The database, uploaded files and logs are bind-mounted
from this folder (`db.sqlite3`, `src/files`, `logs`), so edits made in the Manager survive
a rebuild. To run it without Compose:

```
docker build -t glc-journals .
docker run -p 8000:8000 -v "$(pwd)/db.sqlite3:/app/db.sqlite3" glc-journals
```

**One limitation to know:** the site's press domain is stored in the database as
`localhost:8000`. If you map the container to a different host or port, Janeway will
redirect every page back to `http://localhost:8000` instead of serving them. Either keep
the mapping as `8000:8000` on `localhost`, or update the press/journal domain afterwards
in the Manager (Journal Settings) or directly in `db.sqlite3`.

I was able to review the Dockerfile's logic carefully (the SQLite path resolution matches
Janeway's own settings, and the same Python dependencies installed cleanly in a plain
virtual environment on Python 3.12), but I could not actually run `docker build` myself in
this environment — the sandbox's network policy blocks pulling images from Docker Hub. If
the build fails on your machine, it's most likely one of: an architecture mismatch (try
adding `--platform linux/amd64` on Apple Silicon if a dependency has no arm64 wheel), or
port 8000 already being used by something else on your machine.

## Design (editorial edition)

The look follows the conventions of leading journals such as the Yale Law Journal, Stanford Law Review and *Nature*: the current issue comes first; every piece shows a type label, title, byline, short abstract, pages and keywords; colour is an accent rather than a background; photographs are kept to the programme pages. Each journal also has:

* a typeset issue cover, an issue contents page grouped by section, and an archive of all issues;
* article pages with abstract, keywords, "Cite this" with one-click copy, download buttons, "In this issue", licence, and Google Scholar citation tags;
* Peer Review, Publication Ethics (COPE-based), Open Access and Licensing, and Indexing pages (templates to adapt);
* a masthead (editorial board), news, search and a "Submit" button in the header.

Issues, articles, news and the masthead are real Janeway records seeded as **samples**, so the home page updates itself when editors publish. Delete the samples before launch.

## What is on every journal (11 pages, copied from the IPR Cell site layout)

Home, About, Events Overview, Upcoming and Active Events, Certificate Course, Moot Court (the subject's own competition), Guest Lectures and Webinars, Journal (guidelines, call for papers, archive table), Clinic (the subject's own pro bono clinic), Join Us (3-tier membership), Contact, and Faculty and Core Committee.
Menus, dropdowns, footer and journal switcher are all included. All pictures are labelled **TEST IMAGE**. All names, dates and partners are test content.

## How editing works

Every block of text is a normal Janeway **Page** (Manager, then Content, then Pages; or the address `/<journal>/cms/`). Signed-in editors also see yellow **Edit** buttons right on the website. The menu is Janeway's own **Navigation** screen (`/<journal>/cms/nav/`). Colours live on a page called **Site Colours**. See `EASY_EDITING_GUIDE.html`, written for complete beginners.

## Where things are

| What | Where |
|---|---|
| Theme templates | `src/themes/GLCLaw/templates/` |
| Theme look (CSS) and script | `src/static/GLCLaw/css/glc.css`, `src/static/GLCLaw/js/glc.js` |
| Test images (SVG) | `src/static/GLCLaw/img/<journal>/` |
| Subject text for each journal | `src/glc_theme/journals_data.py` |
| Page layouts and wording | `src/glc_theme/content.py` |
| Seed command | `python manage.py glc_seed` (run inside `src/`) |
| Local settings | `src/core/settings.py` |

Changing a journal's subject text in `journals_data.py` and running `python manage.py glc_seed --only criminal` rebuilds that journal's pages. It overwrites any edits you made to those pages, so use it on journals you have not edited yet.

## Before you go live

* In `src/core/settings.py`: set `DEBUG = False`, set a new `SECRET_KEY` (or the `JANEWAY_SECRET_KEY` environment variable), set `DEFAULT_HOST`, `ALLOWED_HOSTS` and real e-mail settings.
* Change the press domain in Manager or in the database to your real domain, then run `python manage.py collectstatic`.
* Use a real web server (gunicorn or uWSGI behind nginx) and PostgreSQL or MySQL, as Janeway's own install guide describes: <https://janeway.readthedocs.io/>.
* Replace the TEST content, the placeholder social links in the footer, and all test names.
* Fonts load from Google Fonts. Remove the two `fonts.googleapis.com` lines in `src/themes/GLCLaw/templates/core/base.html` if you want a fully offline site.

## About the design

The layout follows the IPR Cell site (iprcellglcmumbai.in): top bar, sticky header with dropdown menu, hero with calls to action, About plus numbers, a photo carousel, four pillars, moot feature, clinic feature, journal feature, join call-to-action, and a three-column footer. The look is new, built from scratch for this project: sticky blurred header, journal switcher, per-journal colours, hover cards, scroll effects and a mobile menu.
