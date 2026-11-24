"""Creates the whole GLC Mumbai journals site in one go.

    python manage.py glc_seed             # create / refresh everything
    python manage.py glc_seed --images-only
    python manage.py glc_seed --only criminal   # refresh a single journal

Safe to run many times. It never deletes articles or users. It DOES overwrite
the text of the pages it created, so run it with --only on a journal you have not edited yet.
"""
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.core.management import call_command

from cms import models as cms_models
from journal import models as journal_models
from press import models as press_models
from utils import setting_handler, install, shared

from glc_theme import content, make_images, scholarly
from glc_theme.journals_data import JOURNALS, PRESS_NAME, ADDRESS, PHONE

HIDDEN_SETTINGS = {"display_journal_title": False}


class Command(BaseCommand):
    help = "Creates the nine GLC journals with pages, menus and colours."

    def add_arguments(self, parser):
        parser.add_argument("--images-only", action="store_true")
        parser.add_argument("--only", default=None, help="journal code to (re)build")
        parser.add_argument("--no-admin", action="store_true", help="do not create the test admin user")

    def handle(self, *args, **opts):
        static_dir = os.path.join(settings.BASE_DIR, "static")
        make_images.make_all(static_dir)
        self.stdout.write("Test images written.")
        if opts["images_only"]:
            return

        press = press_models.Press.objects.first()
        press.name = PRESS_NAME
        press.theme = "GLCLaw"
        press.save()

        self.make_admin()
        self.poster = get_user_model().objects.filter(is_superuser=True).first()
        for j in JOURNALS:
            if opts["only"] and j["code"] != opts["only"]:
                continue
            self.build_journal(j)
        shared.clear_cache()
        self.stdout.write(self.style.SUCCESS("All done. Open http://localhost:8000/ to see the site."))

    # ------------------------------------------------------------------
    def build_journal(self, j):
        self.stdout.write(f"Building {j['code']} ...")
        journal = journal_models.Journal.objects.filter(code=j["code"]).first()
        if journal is None:
            install.journal(name=j["name"], code=j["code"], base_url=f"{j['code']}.glc.local", delete=False)
            journal = journal_models.Journal.objects.get(code=j["code"])
            install.update_issue_types(journal, management_command=False)

        sh = setting_handler.save_setting
        sh("general", "journal_name", journal, j["name"])
        sh("general", "journal_description", journal, f"<p>{j['tagline']}</p>")
        sh("general", "press_journal_description", journal, f"<p>{j['tagline']}</p>")
        sh("general", "journal_theme", journal, "GLCLaw")
        sh("general", "journal_base_theme", journal, "OLH")
        sh("general", "main_contact", journal, j["email"])
        sh("general", "support_email", journal, j["email"])
        sh("general", "from_address", journal, j["email"])
        sh("general", "contact_info", journal, f"<p>{ADDRESS}<br>{PHONE}<br>{j['email']}</p>")
        sh("general", "publisher_name", journal, "Government Law College, Mumbai")
        sh("styling", "display_journal_title", journal, "")

        ct = ContentType.objects.get_for_model(journal)

        def save_page(name, display, html, toc=False):
            cms_models.Page.objects.update_or_create(
                content_type=ct, object_id=journal.pk, name=name,
                defaults={"display_name": display, "content": html, "is_markdown": False, "display_toc": toc},
            )

        # Pages that no longer exist for this journal (Moot removed everywhere;
        # the Law Review flagship carries no Events/Programmes or Clinic at all).
        # Clean these up so a reseed retires them instead of leaving orphans.
        retired = ["events-moot", "block-moot"]
        if j["code"] == "lawreview":
            retired += ["events", "events-upcoming", "events-certificate-course",
                        "events-guest-lectures", "clinic",
                        "block-pillars", "block-moments", "block-clinic"]
        cms_models.Page.objects.filter(content_type=ct, object_id=journal.pk, name__in=retired).delete()

        # colour page (very small, very easy)
        save_page(
            "site-colours", "Site Colours (change the two colour codes)",
            f"<p>Main colour: <strong>{j['primary']}</strong></p><p>Accent colour: <strong>{j['accent']}</strong></p>"
            "<p>Type any 6-digit colour code that starts with #. Keep the main colour dark so white words are easy to read.</p>",
        )
        for name, (display, html) in content.home_blocks(j).items():
            save_page(name, display, html)
        for name, (display, html) in content.inner_pages(j).items():
            save_page(name, display, html)

        self.build_nav(journal, j, ct)
        journal.nav_home = journal.nav_news = journal.nav_articles = journal.nav_issues = False
        journal.nav_contact = journal.nav_start = journal.nav_review = journal.nav_sub = False
        journal.save()
        scholarly.build(journal, j, self.poster)

    # ------------------------------------------------------------------
    def build_nav(self, journal, j, ct):
        cms_models.NavigationItem.objects.filter(content_type=ct, object_id=journal.pk).delete()
        code = j["code"]
        page = lambda name: f"/{code}/site/{name}/"
        seq = [0]

        def item(label, link=None, parent=None, sub=False, external=False):
            seq[0] += 1
            return cms_models.NavigationItem.objects.create(
                content_type=ct, object_id=journal.pk, link_name=label, link=link or None,
                has_sub_nav=sub, top_level_nav=parent, sequence=seq[0], is_external=external,
            )

        item("Current Issue", f"/{code}/issue/current/")
        item("Archive", f"/{code}/issues/")
        sub = item("Submissions", sub=True)
        item("Call for Papers", page("journal") + "#cfp", sub)
        item("Author Guidelines", page("journal") + "#guidelines", sub)
        item("Submit a Manuscript", f"/{code}/submit/start/", sub)
        item("Peer Review Policy", page("peer-review"), sub)
        item("Publication Ethics", page("ethics"), sub)
        item("Open Access and Licensing", page("open-access"), sub)
        item("Editorial Board", f"/{code}/editorialteam/")
        if j["code"] != "lawreview":
            ev = item("Programmes", sub=True)
            item("Events Overview", page("events"), ev)
            item("Upcoming & Active Events", page("events-upcoming"), ev)
            item("Certificate Course", page("events-certificate-course"), ev)
            item("Guest Lectures & Webinars", page("events-guest-lectures"), ev)
            item(j["clinic"][0], page("clinic"), ev)
        ab = item("About", sub=True)
        item("About the Journal", page("journal"), ab)
        item("Our Story and Heritage", page("about"), ab)
        item("Faculty and Core Committee", page("team"), ab)
        item("Indexing and Identifiers", page("indexing"), ab)
        item("Join Us", page("join"), ab)
        item("News", f"/{code}/news/", ab)
        item("Contact", page("contact"), ab)

    # ------------------------------------------------------------------
    def make_admin(self):
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                email="admin@glcmumbai.example", password="ChangeMe-12345", username="admin@glcmumbai.example",
                first_name="Site", last_name="Admin",
            )
            self.stdout.write("Created test admin: admin@glcmumbai.example / ChangeMe-12345  (CHANGE THIS PASSWORD)")
