import re

from django import template
from django.contrib.contenttypes.models import ContentType

from cms import models as cms_models
from journal import models as journal_models
from glc_theme.journals_data import JOURNALS

register = template.Library()
DEFAULTS = {j["code"]: j for j in JOURNALS}
HEX = re.compile(r"#[0-9A-Fa-f]{6}\b")


def _journal_of(context):
    request = context.get("request")
    return getattr(request, "journal", None) if request else None


def _page(journal, name):
    if journal is None:
        return None
    ct = ContentType.objects.get_for_model(journal)
    return cms_models.Page.objects.filter(content_type=ct, object_id=journal.pk, name=name).first()


@register.simple_tag(takes_context=True)
def glc_page(context, name):
    """Returns the CMS page with this link name for the current journal (or None)."""
    return _page(_journal_of(context), name)


@register.simple_tag(takes_context=True)
def glc_colours(context):
    """Inline CSS variables for the current journal, read from the 'site-colours' page.

    Anyone can change the two colour codes in Manager > Pages > Site Colours.
    """
    journal = _journal_of(context)
    d = DEFAULTS.get(getattr(journal, "code", None), {"primary": "#7A1E2E", "accent": "#C9A227"})
    primary, accent = d["primary"], d["accent"]
    page = _page(journal, "site-colours")
    if page and page.content:
        found = HEX.findall(re.sub(r"<[^>]+>", " ", page.content))
        if len(found) >= 1:
            primary = found[0]
        if len(found) >= 2:
            accent = found[1]
    return f"--glc-primary:{primary};--glc-accent:{accent};"


@register.simple_tag(takes_context=True)
def glc_can_edit(context):
    """True for logged-in people who may edit pages (editors, managers, staff)."""
    request = context.get("request")
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return False
    journal = _journal_of(context)
    if user.is_staff or user.is_superuser:
        return True
    try:
        return bool(journal and (user.is_journal_manager(journal) or user.is_editor(request, journal)))
    except Exception:
        return False


@register.simple_tag(takes_context=True)
def glc_journals(context):
    """All journals on the site, with their colours, for the home page and the switcher."""
    request = context.get("request")
    out = []
    order = {j["code"]: i for i, j in enumerate(JOURNALS)}
    for jr in sorted(journal_models.Journal.objects.all(), key=lambda x: order.get(x.code, 99)):
        d = DEFAULTS.get(jr.code, {})
        page = _page(jr, "site-colours")
        primary, accent = d.get("primary", "#7A1E2E"), d.get("accent", "#C9A227")
        if page and page.content:
            found = HEX.findall(re.sub(r"<[^>]+>", " ", page.content))
            if found:
                primary = found[0]
            if len(found) > 1:
                accent = found[1]
        out.append({
            "code": jr.code,
            "name": jr.name,
            "url": jr.site_url(),
            "primary": primary,
            "accent": accent,
            "tagline": d.get("tagline", ""),
            "subject": d.get("subject", ""),
            "image": "/static/GLCLaw/img/%s/photo-1.svg" % jr.code,
            "logo": "/static/GLCLaw/img/%s/logo.svg" % jr.code,
        })
    return out


# ---------------------------------------------------------------- live journal data
from django.utils import timezone as _tz
from comms import models as _comms
from submission import models as _sm


def _published(qs):
    return qs.filter(stage=_sm.STAGE_PUBLISHED, date_published__lte=_tz.now())


@register.simple_tag(takes_context=True)
def glc_current_issue(context):
    """The journal's current issue (or its newest issue)."""
    journal = _journal_of(context)
    if not journal:
        return None
    issue = journal.current_issue
    if not issue:
        issue = journal_models.Issue.objects.filter(journal=journal, date__lte=_tz.now()).order_by("-date").first()
    return issue


@register.simple_tag
def glc_issue_articles(issue, limit=12):
    if not issue:
        return []
    return list(_published(issue.articles.all()).select_related("section").order_by("first_page", "pk")[:limit])


@register.simple_tag(takes_context=True)
def glc_archive_articles(context, limit=4):
    """Published articles that are not in the current issue."""
    journal = _journal_of(context)
    if not journal:
        return []
    qs = _published(_sm.Article.objects.filter(journal=journal)).select_related("section")
    if journal.current_issue_id:
        qs = qs.exclude(primary_issue=journal.current_issue_id)
    return list(qs.order_by("-date_published", "first_page")[:limit])


@register.simple_tag(takes_context=True)
def glc_news(context, limit=4):
    journal = _journal_of(context)
    if not journal:
        return []
    ct = ContentType.objects.get_for_model(journal)
    return list(_comms.NewsItem.objects.filter(content_type=ct, object_id=journal.pk).order_by("-posted")[:limit])


@register.simple_tag
def glc_latest_across(limit=9):
    """The newest published piece from each journal, newest first, for the press home page."""
    out = []
    for jr in journal_models.Journal.objects.all():
        a = (_published(_sm.Article.objects.filter(journal=jr)).select_related("section", "journal")
             .order_by("-date_published", "first_page").first())
        if a:
            out.append(a)
    order = {j["code"]: i for i, j in enumerate(JOURNALS)}
    out.sort(key=lambda a: (-a.date_published.timestamp(), order.get(a.journal.code, 99)))
    return out[:limit]


@register.filter
def glc_byline(article):
    names = [a.full_name() for a in article.frozenauthor_set.all().order_by("order")]
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " & " + names[-1]


@register.filter
def glc_keywords(article):
    return [k.word for k in article.keywords.all()]


@register.filter
def glc_colour_of(journal):
    d = DEFAULTS.get(getattr(journal, "code", None), {})
    return d.get("primary", "#7A1E2E")
