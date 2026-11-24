"""Sample scholarly content stored in Janeway's own tables.

Issues, articles, news and the editorial board are real Janeway records, so
editors manage them from the Manager like any journal. All of it is SAMPLE
content: replace or delete it before launch.
"""
import datetime
import re

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from comms import models as comms_models
from core import models as core_models
from journal import models as journal_models
from submission import models as sm
from utils import setting_handler

from .journals_data import TITLE_FORMS

# Janeway's workflow roles (core.models.Role). "reader" isn't assigned here: it's
# the implicit role every account already has, not something to grant.
WORKFLOW_ROLES = [
    ("journal-manager", "Test", "Journal Manager"),
    ("editor", "Test", "Editor"),
    ("section-editor", "Test", "Section Editor"),
    ("author", "Test", "Author"),
    ("reviewer", "Test", "Reviewer"),
    ("copyeditor", "Test", "Copyeditor"),
    ("production", "Test", "Production Manager"),
    ("typesetter", "Test", "Typesetter"),
    ("proofing-manager", "Test", "Proofing Manager"),
    ("proofreader", "Test", "Proofreader"),
]

SECTIONS = [("Article", "Articles"), ("Essay", "Essays"), ("Note", "Notes"), ("Case Comment", "Case Comments")]
NAMES = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve"]

ABSTRACT = (
    "<p>This {kind} examines {topic_l} in India. It traces how the courts and the legislature have shaped the "
    "field, identifies gaps between doctrine and practice, and compares the Indian position with other "
    "jurisdictions. It closes with proposals for reform.</p> "
    "<p><em>Sample abstract. Replace it with the real abstract in the Manager.</em></p>"
)


def _aware(y, m, d):
    return timezone.make_aware(datetime.datetime(y, m, d, 9, 0))


def _section(journal, name, plural, seq):
    s = sm.Section.objects.filter(journal=journal, name=name).first()
    if not s:
        s = sm.Section.objects.create(journal=journal, name=name, plural=plural, sequence=seq,
                                      number_of_reviewers=2, public_submissions=True)
    return s


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _user(email, first, last):
    User = get_user_model()
    u = User.objects.filter(email=email).first()
    if not u:
        u = User.objects.create_user(email=email, password=None, username=email)
        u.first_name, u.last_name, u.is_active = first, last, True
        u.save()
    return u


def assign_workflow_role_accounts(journal):
    """One shared test account per Janeway workflow role (Editor, Reviewer,
    Copyeditor, etc.), granted that role on this journal. The same account is
    reused across all nine journals, so there is exactly one "Test Reviewer"
    account site-wide, holding the Reviewer role on every journal.
    """
    for slug, first, last in WORKFLOW_ROLES:
        email = f"{_slug(first)}.{_slug(last)}@example.org"
        u = _user(email, first, last)
        u.add_account_role(slug, journal)


def build(journal, j, poster):
    code = j["code"]
    topics = j["topics"]
    issue_type = journal_models.IssueType.objects.filter(journal=journal, code="issue").first()
    sections = [_section(journal, n, p, i) for i, (n, p) in enumerate(SECTIONS)]

    # remove earlier sample records so the command can run again
    sm.Article.objects.filter(journal=journal, article_agreement="GLC-SAMPLE").delete()
    journal_models.Issue.objects.filter(journal=journal, short_description__startswith="Sample issue").delete()

    plan = [
        # volume, number, date, title, how many articles
        (1, "1", _aware(2025, 11, 15), f"Contemporary Horizons in {j['subject']}", 4),
        (2, "1", _aware(2026, 11, 1), f"{topics[0]} and {topics[1]}: New Directions", 6),
    ]
    kinds = [0, 0, 1, 2, 3, 1]
    n = 0
    issues = []
    for vol, num, date, title, count in plan:
        issue = journal_models.Issue.objects.create(
            journal=journal, volume=vol, issue=num, issue_title=title, date=date, issue_type=issue_type,
            short_description="Sample issue: all titles, authors and abstracts are placeholder content.",
        )
        page = 1
        for i in range(count):
            topic = topics[(n + vol) % len(topics)]
            sec = sections[kinds[i]]
            title_text = TITLE_FORMS[n % len(TITLE_FORMS)].format(t=topic)
            length = [32, 30, 18, 12][kinds[i]]
            art = sm.Article.objects.create(
                journal=journal, title=title_text, section=sec, article_agreement="GLC-SAMPLE",
                abstract=ABSTRACT.format(kind=sec.name.lower(), topic_l=topic.lower()),
                stage=sm.STAGE_PUBLISHED, date_published=date, date_submitted=date - datetime.timedelta(days=120),
                date_accepted=date - datetime.timedelta(days=30), first_page=page, last_page=page + length - 1,
                primary_issue=issue, language="eng",
            )
            page += length
            for k in range(1 if kinds[i] in (2, 3) else 2):
                sm.FrozenAuthor.objects.create(
                    article=art, first_name="Author", last_name=NAMES[(n * 2 + k) % len(NAMES)], order=k + 1,
                    frozen_email=f"author{n}{k}.{code}@example.org",
                )
            for o, word in enumerate([topic, j["subject"]]):
                kw, _ = sm.Keyword.objects.get_or_create(word=word)
                sm.KeywordArticle.objects.get_or_create(article=art, keyword=kw, defaults={"order": o + 1})
            issue.articles.add(art)
            n += 1
        issues.append(issue)
    journal.current_issue = issues[-1]
    journal.save()

    # ---- news
    ct = ContentType.objects.get_for_model(journal)
    comms_models.NewsItem.objects.filter(content_type=ct, object_id=journal.pk, body__contains="glc-sample").delete()
    is_flagship = j["code"] == "lawreview"
    if is_flagship:
        news = [
            ("Call for Papers: Volume 3 now open", f"Submissions on all areas of {j['subject'].lower()} are welcome until 31 January 2027 (sample date)."),
            ("New Board of Editors inducted", "The journal welcomes its editorial board for the 2026-27 term (sample)."),
            ("Volume 3 submissions under review", "The editorial board has begun double-blind review of received manuscripts (sample)."),
            ("Call for peer reviewers", "Practitioners and academics interested in reviewing manuscripts may write to the editorial board (sample)."),
        ]
    else:
        news = [
            ("Call for Papers: Volume 3 now open", f"Submissions on all areas of {j['subject'].lower()} are welcome until 31 January 2027 (sample date)."),
            (f"Guest lecture: {j['lectures'][0]}", "A public lecture followed by questions. Open to all students (sample)."),
            ("New Board of Editors inducted", "The journal welcomes its editorial board for the 2026-27 term (sample)."),
            (f"{j['clinic'][0]} walk-in session", "Free guidance session for students and the public (sample)."),
        ]
    for i, (t, b) in enumerate(news):
        comms_models.NewsItem.objects.create(
            content_type=ct, object_id=journal.pk, title=t, body=f'<p>{b}</p><span class="glc-sample"></span>',
            posted_by=poster, posted=_aware(2026, 11, 20 - i * 6), start_display=datetime.date(2026, 11, 20 - i * 6),
        )

    # ---- editorial board
    core_models.EditorialGroup.objects.filter(journal=journal, description__contains="glc-sample").delete()
    groups = [
        ("Faculty Advisors", [("Prof. (Dr.) Shilpi", "Jha"), ("Test Faculty", "Advisor")]),
        ("Board of Editors", [("Dr. Asmita Advait", "Vaidya"), ("Test Managing", "Editor"), ("Test Senior", "Editor One"), ("Test Senior", "Editor Two")]),
        ("Associate Editors", [("Test Associate", "Editor One"), ("Test Associate", "Editor Two"), ("Test Associate", "Editor Three")]),
        ("Advisory Board", [("Test Advisory", "Member One"), ("Test Advisory", "Member Two")]),
    ]
    for gi, (gname, people) in enumerate(groups):
        g = core_models.EditorialGroup.objects.create(
            journal=journal, name=gname, sequence=gi, description='<p>Sample names.</p><span class="glc-sample"></span>')
        for pi, (first, last) in enumerate(people):
            email = f"{_slug(first)}.{_slug(last)}.{code}@example.org"
            u = _user(email, first, last)
            core_models.EditorialGroupMember.objects.create(group=g, user=u, sequence=pi)
    setting_handler.save_setting("general", "enable_editorial_display", journal, "on")
    setting_handler.save_setting("styling", "editorial_group_page_name", journal, "Editorial Board")

    assign_workflow_role_accounts(journal)
    return issues
