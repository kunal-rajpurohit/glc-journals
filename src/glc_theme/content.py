"""Builds the HTML for every page of every journal.

The reference site's structure is followed page by page:
home blocks, About, Events (+3 sub pages), Journal, Clinic, Join, Contact, Team.
The Law Review (code "lawreview") is the flagship journal: it carries no
Events/Programmes or Clinic section at all, only journal content.
All names, numbers and partners are TEST CONTENT to be replaced in the Manager.
"""
from .journals_data import ADDRESS, PHONE, HOURS, TITLE_FORMS

IMG = "/static/GLCLaw/img"

import re as _re


class Txt(str):
    """A string whose .lower() keeps acronyms such as AI, GST and ADR in capitals."""

    def lower(self):
        return Txt(_re.sub(r"\b(ai|adr|gst|msme)\b", lambda m: m.group(1).upper(), str.lower(self)))



# ---------- tiny HTML helpers ----------
def band(inner, cls=""):
    return f'<div class="glc-band {cls}"><div class="glc-wrap">{inner}</div></div>'


def btn(label, href, kind="primary"):
    return f'<a class="glc-btn glc-btn-{kind}" href="{href}">{label}</a>'


def btns(*items):
    return '<p class="glc-btns">' + "".join(btn(*i) for i in items) + "</p>"


def hero(j, eyebrow, h1, intro, buttons=(), image=None):
    """Page header in the style of leading journals: no picture, strong type, a coloured rule."""
    return (
        f'<div class="glc-hero glc-hero-page"><div class="glc-wrap">'
        f'<p class="glc-eyebrow">{eyebrow}</p><h1>{h1}</h1><p class="glc-lead">{intro}</p>'
        f"{btns(*buttons) if buttons else ''}</div></div>"
    )


def card(title, body, num=None, link=None, tag=None):
    n = f'<span class="glc-num">{num}</span>' if num else ""
    t = f'<p class="glc-tag">{tag}</p>' if tag else ""
    l = f'<p><a class="glc-link" href="{link[1]}">{link[0]} &rarr;</a></p>' if link else ""
    return f'<div class="glc-card">{n}{t}<h3>{title}</h3><p>{body}</p>{l}</div>'


def grid(cards, cols=3):
    return f'<div class="glc-grid glc-grid-{cols}">' + "".join(cards) + "</div>"


def photo(j, n, caption, tag=""):
    t = f'<span class="glc-tag">{tag}</span>' if tag else ""
    return (
        f'<div class="glc-photo"><img src="{IMG}/{j["code"]}/photo-{n}.svg" alt="{caption}">'
        f"{t}<p>{caption}</p></div>"
    )


def u(j, path):
    """Link inside a journal (path mode): /code/site/page/"""
    return f"/{j['code']}/{path}"


def page_url(j, name):
    return f"/{j['code']}/site/{name}/"


def person(j, n, name, role, extra=""):
    return (
        f'<div class="glc-person"><img src="{IMG}/{j["code"]}/avatar-{n}.svg" alt="{name}">'
        f"<h3>{name}</h3><p class='glc-role'>{role}</p><p class='glc-muted'>{extra}</p>"
        f'<p><a class="glc-link" href="#">LinkedIn Profile</a></p></div>'
    )


# ---------- HOME BLOCKS ----------
def home_blocks(j):
    s, short, code = Txt(j["subject"]), j["short"], j["code"]
    p = lambda name: page_url(j, name)
    is_flagship = j["code"] == "lawreview"
    course_name, course_topics = j["course"]
    clinic_name, clinic_blurb, clinic_services = j["clinic"]
    topics = [Txt(t) for t in j["topics"]]
    blocks = {}

    blocks["block-hero"] = (
        "Home: mission statement (under the journal name)",
        f'<p class="glc-statement">{j["tagline"]} A double-blind peer-reviewed, open-access journal of '
        f"Government Law College, Mumbai, publishing articles, essays, notes and case comments on {s.lower()}.</p>"
        + btns(("Submit a Manuscript", u(j, "submit/start/")), ("Read the Current Issue", u(j, "issue/current/"), "ghost"),
               ("Author Guidelines", p("journal") + "#guidelines", "ghost")),
    )

    about_activity = ("rigorous research, meticulous editing and double-blind peer review"
                       if is_flagship else
                       "education, research, competitions, expert interaction and pro bono work")
    blocks["block-about"] = (
        f"Home: About the {short}",
        f"<h2>{j['motion']}</h2>"
        f"<p>The {short} aims to build awareness, research and practical learning in {s.lower()} "
        f"through {about_activity}. "
        f"We cover {', '.join(t.lower() for t in topics[:-1])} and {topics[-1].lower()}.</p>"
        f'<p><a class="glc-link" href="{p("about")}">Read our story &rarr;</a></p>',
    )

    stats_mid = "Issues and articles published" if is_flagship else "Events, courses and competitions"
    blocks["block-stats"] = (
        "Home: the three big numbers",
        "<ul><li><strong>1000+</strong><span>Students engaged</span></li>"
        f"<li><strong>20+</strong><span>{stats_mid}</span></li>"
        "<li><strong>2023</strong><span>Active since</span></li></ul>",
    )

    if not is_flagship:
        moments = [
            (f"Colloquium on {topics[0]}", "Eminent Guest Colloquium", "Guest Colloquium"),
            (f"In Conversation: {topics[1]}", "Practitioner Dialogue", "Dialogue"),
            (f"Panel on {topics[2]}", "Industry and academia in one room", "Panel"),
            (f"{course_name} Cohort", "Certificate Course Session", "Certificate Course"),
            (f"{clinic_name} Outreach", "Workshop for the Public", "Workshop"),
            ("Induction Ceremony", "Welcoming the new batch", "Induction"),
        ]
        mo = "".join(photo(j, i + 1, f"{t}: {c}", tag=g) for i, (t, c, g) in enumerate(moments))
        blocks["block-moments"] = (
            "Home: Moments from our flagship initiatives (6 photos)",
            '<h2>Moments from Our Flagship Initiatives</h2>'
            f'<p class="glc-btns">{btn("Explore All Events", p("events"), "ghost")}</p>'
            f'<div class="glc-carousel">{mo}</div>',
        )

        blocks["block-pillars"] = (
            "Home: Four ways we advance the subject",
            f"<h2>Four ways we advance {s.lower()}</h2>"
            + grid([
                card("Educate", f"Structured, practitioner-led learning in {s.lower()}.", "01",
                     ("Certificate courses and guest lectures", p("events-certificate-course"))),
                card("Convene", "Public talks and panels that bring practitioners and academics together.", "02",
                     ("Guest lectures and webinars", p("events-guest-lectures"))),
                card("Research", "Peer-reviewed scholarship from students, scholars and practitioners.", "03",
                     ("The journal and submission guidelines", p("journal"))),
                card("Serve", f"Applying {s.lower()} knowledge to help people who need it.", "04",
                     (clinic_name, p("clinic"))),
            ], 4),
        )

        blocks["block-clinic"] = (
            "Home: the free clinic feature",
            f"<h2>Applying legal expertise where it matters most.</h2>"
            f"<p>The {clinic_name} offers {clinic_blurb}. Student researchers work under faculty supervision.</p>"
            + btns(("Learn About the Clinic", p("clinic")))
            + f'<blockquote><p>{j["maxim"]}</p><cite>Our guiding maxim</cite></blockquote>',
        )

    blocks["block-journal"] = (
        "Home: Call for Papers box",
        f'<p class="glc-eyebrow">Call for Papers</p><h2>Volume 3 is open for submissions</h2>'
        f"<p>We invite original research on {', '.join(t.lower() for t in topics[:4])} and related questions of {s.lower()}. "
        "Deadline: 31 January 2027 (sample date).</p>"
        "<ul class='glc-facts'><li><strong>Review</strong><span>Double-blind, two reviewers</span></li>"
        "<li><strong>Decision</strong><span>Within 8 weeks (target)</span></li>"
        "<li><strong>Fees</strong><span>None to submit or publish</span></li>"
        "<li><strong>Access</strong><span>Open access, CC BY 4.0</span></li></ul>"
        + btns(("Submit a Manuscript", u(j, "submit/start/")), ("Read the Guidelines", p("journal") + "#guidelines", "ghost")),
    )

    blocks["block-join"] = (
        "Home: Why join us",
        f"<h2>Why join the {short} team?</h2>"
        f"<p>We welcome students interested in {', '.join(t.lower() for t in topics[:3])} and emerging areas of {s.lower()}. "
        f"No prior expertise is required.</p>"
        + btns(("Apply for Induction", p("join")), ("Contact Office Bearers", p("contact"), "ghost")),
    )

    blocks["block-footer"] = (
        "Footer: short description",
        f"<p>{j['name']} is a student-edited, faculty-guided publication of Government Law College, Mumbai, "
        f"working on {s.lower()} through research, competitions and public service.</p>"
        f"<p>{ADDRESS}<br>Phone: {PHONE}<br>Email: <a href='mailto:{j['email']}'>{j['email']}</a></p>",
    )
    return blocks


# ---------- INNER PAGES ----------
def inner_pages(j):
    s, short, code = Txt(j["subject"]), j["short"], j["code"]
    topics = [Txt(t) for t in j["topics"]]
    p = lambda name: page_url(j, name)
    is_flagship = j["code"] == "lawreview"
    course_name, course_topics = j["course"]
    clinic_name, clinic_blurb, clinic_services = j["clinic"]
    pages = {}

    # ---- About
    pages["about"] = ("About", (
        hero(j, "Established 1855, Churchgate, Mumbai", f"About Government Law College and the {short}",
             "A 170-year legal tradition and a student-led publication with a clear mandate.",
             [("Join the Team", p("join")), ("Meet the Team", p("team"), "ghost")])
        + band(
            f'<div class="glc-split"><div><h2>Asia\'s Oldest Institution for Legal Education</h2>'
            f"<p>Government Law College, Mumbai was founded in 1855 and has trained generations of lawyers, judges and public leaders. "
            f"Its campus sits in Churchgate, next to the Bombay High Court and the University of Mumbai.</p>"
            f"<p>Today the college combines classroom learning with practical training, journals, clinics and public lectures. "
            f"This test paragraph can be replaced with your own college history.</p>"
            f"<p class='glc-muted'>{ADDRESS}</p></div>"
            f'<img src="{IMG}/{code}/engraving-1.svg" alt="Heritage engraving (test image)"></div>')
        + band(
            f'<div class="glc-split glc-flip"><img src="{IMG}/{code}/crest.svg" alt="{short} emblem (test image)">'
            f"<div><h2>The Genesis and Mission of the {short}</h2>"
            f"<p>The {short} began as a small group of students who wanted a serious home for writing on {s.lower()}. "
            f"We publish research on {', '.join(t.lower() for t in topics[:-1])} and {topics[-1].lower()}.</p>"
            f"<p>{'Our work is centred on rigorous research, meticulous editing and faculty-guided peer review.' if is_flagship else f'Our work includes certificate courses, practitioner colloquiums, and pro bono help through the {clinic_name}.'}</p></div></div>", "glc-tint")
        + band(
            f'<div class="glc-quote-block"><img src="{IMG}/{code}/avatar-1.svg" alt="Principal (test image)">'
            f"<div><h2>Message from the Principal</h2>"
            f"<blockquote><p>Test message: the Principal's welcome note goes here. Replace this text with the real message.</p>"
            f"<cite>Principal, Government Law College, Mumbai</cite></blockquote></div></div>")
        + band(
            f'<div class="glc-quote-block"><img src="{IMG}/{code}/avatar-2.svg" alt="Founder (test image)">'
            f"<div><h2>Origin and Vision</h2><h3>Bridging classroom theory with real practice in {s.lower()}.</h3>"
            f"<blockquote><p>Test founder's address: explain why the journal was started and what it hopes to change.</p>"
            f"<cite>Founding Editor-in-Chief (test name)</cite></blockquote></div></div>", "glc-tint")
        + band(
            f'<h2 id="committee">Governance and Team</h2><p class="glc-btns">{btn("View Full Roster", p("team"), "ghost")}</p>'
            + '<div class="glc-people">'
            + person(j, 3, "Prof. Test Faculty One", "Professor In-Charge", "Assistant Professor of Law")
            + person(j, 4, "Prof. Test Faculty Two", "Professor In-Charge", "Assistant Professor of Law")
            + person(j, 5, "Test Editor One", "Editor-in-Chief", "Batch of 2027")
            + person(j, 6, "Test Editor Two", "Managing Editor", "Batch of 2028")
            + "</div>")
        + band(
            f"<h2>Join the {short}</h2><p>Induction is held every year. Apply, interview, and start working on real publications.</p>"
            + btns(("Apply for Induction", p("join"))), "glc-cta")
    ))

    # ---- Events overview (the Law Review, our flagship, runs no programmes)
    if not is_flagship:
        pages["events"] = ("Events Overview", (
            hero(j, "Flagship programmes", "Academic Flagships and Initiatives",
                 f"Practitioner-led certificate courses, guest lectures and national discussion on {s.lower()}.",
                 [("Explore Flagships", "#flagships"), ("Inquire for Partnerships", p("contact"), "ghost")], "events")
            + band(
                f'<h2 id="flagships">Flagship Pillars</h2><p>Programmes that link academic study with practitioner masterclasses.</p>'
                + grid([
                    card("Certificate Courses", f"Weekend programmes on {', '.join(Txt(t).lower() for t in course_topics)}, taught by practising lawyers. "
                         "Recent editions: 2026, 2025, 2024.", "01", ("View Full Course Editions", p("events-certificate-course")), "Practitioner Masterclass"),
                    card(clinic_name, f"{clinic_blurb.capitalize()}, run by student researchers under faculty supervision.",
                         "02", ("Explore the Clinic", p("clinic")), "Pro Bono Initiative"),
                    card("Guest Lectures and Colloquiums", f"Public talks and panels on topics such as {topics[0].lower()} and {topics[1].lower()}.",
                         "03", ("Explore Lecture Series", p("events-guest-lectures")), "Public Discourse and Panels"),
                ]))
            + band('<h2>Flagship Photo Archives</h2><div class="glc-grid glc-grid-4">'
                   + "".join(photo(j, n, c) for n, c in [(1, "Colloquium on " + topics[0]), (2, "Clinic Outreach Session"),
                                                          (3, "Guest Lecture"), (4, "Practitioner Masterclass")]) + "</div>", "glc-tint")
            + band(f"<h2>Partner with us</h2><p>Law firms, senior jurists and corporate counsel are invited to speak at colloquiums or mentor course cohorts.</p>"
                   + btns(("Connect with Coordinators", p("contact"))), "glc-cta")
            + band("<h2>Sponsors and Knowledge Partners</h2><p>With thanks to our sponsors, bar associations, law firms and research partners.</p>"
                   '<div class="glc-logos">' + "".join(f"<span>Partner {i}</span>" for i in range(1, 9)) + "</div>")
        ))

        # ---- Upcoming
        pages["events-upcoming"] = ("Upcoming and Active Events", (
            hero(j, "What is on", "Upcoming and Active Events",
                 "Workshops, symposiums and open registrations. Dates below are test dates.",
                 [("All Events", p("events"), "ghost")], "events")
            + band("<h2>Open Registrations</h2>" + grid([
                card(f"{course_name} 2027 Registrations", "Weekend programme, seats limited.", None, ("Register interest", p("contact")), "Opens 1 January 2027 (test date)"),
                card(f"Workshop: {topics[0]}", "A half-day workshop with a practitioner.", None, ("Ask for a seat", p("contact")), "15 February 2027 (test date)"),
                card(f"Symposium on {topics[1]}", "Papers from our latest issue discussed in person.", None, ("Ask for a seat", p("contact")), "20 March 2027 (test date)"),
            ]))
            + band("<h2>Call for Papers</h2><p>The next issue is open for submissions. See the guidelines on the journal page.</p>"
                   + btns(("Call for Papers", p("journal") + "#cfp")), "glc-cta")
        ))

        # ---- Course
        pages["events-certificate-course"] = ("Certificate Course", (
            hero(j, "Practitioner masterclass", course_name,
                 "A weekend programme taught by practising lawyers and academics.", [("Ask About the Next Edition", p("contact"))], "events")
            + band("<h2>What you will learn</h2>" + grid([card(t, "Hands-on sessions with practitioners and a short assessment.", f"0{i+1}") for i, t in enumerate(course_topics)])
                   + "<h2>Recent editions</h2><table class='glc-table'><thead><tr><th>Year</th><th>Theme</th><th>Mode</th></tr></thead><tbody>"
                   f"<tr><td>2026</td><td>{course_topics[0]}</td><td>Weekend, on campus</td></tr>"
                   f"<tr><td>2025</td><td>{course_topics[1]}</td><td>Weekend, on campus</td></tr>"
                   f"<tr><td>2024</td><td>{course_topics[2]}</td><td>Weekend, online</td></tr></tbody></table>")
        ))

        # ---- Lectures
        pages["events-guest-lectures"] = ("Guest Lectures and Webinars", (
            hero(j, "Public discourse", "Guest Lectures and Webinars",
                 f"Talks and panels on {s.lower()} with judges, practitioners and scholars.", [("Suggest a Speaker", p("contact"))], "events")
            + band("<h2>Lecture series</h2>" + grid([card(t, "A public talk followed by questions. Recording shared with members.", f"0{i+1}") for i, t in enumerate(j["lectures"])])
                   + '<div class="glc-grid glc-grid-3">' + "".join(photo(j, n, c) for n, c in [(1, j["lectures"][0]), (2, j["lectures"][1]), (3, j["lectures"][2])]) + "</div>")
        ))

    # ---- Journal
    arts = []
    cats = ["Article", "Essay", "Case Comment", "Article", "Note", "Article", "Essay", "Case Comment", "Article", "Note"]
    for i in range(10):
        t = topics[i % len(topics)]
        arts.append(f"<tr><td>{i+1}</td><td>Test Author {i+1}</td><td>{TITLE_FORMS[i].format(t=t)}</td><td>{t}</td></tr>")
    pages["journal"] = ("Journal", (
        hero(j, "Annual peer-reviewed journal", f"{j['name']}",
             f"A double-blind peer-reviewed publication on {s.lower()}.", [("Explore Volume I", "#archive"), ("Call for Papers", "#cfp", "ghost")], "journal")
        + band(f'<div class="glc-split"><div><h2>Fostering Rigorous Legal Scholarship</h2>'
               f"<p>The journal is student-edited and faculty-guided. It covers {', '.join(t.lower() for t in topics[:-1])} and {topics[-1].lower()}.</p>"
               f"<p>Every submission goes through double-blind review. Doctrinal, empirical and policy work is welcome.</p></div>"
               f'<img src="{IMG}/{code}/engraving-2.svg" alt="Engraving (test image)"></div>')
        + band("<h2>Academic Affiliations</h2>" + grid([card("Knowledge Partner (test)", "Research database partner."), card("Citation Partner (test)", "Legal analytics partner.")], 2), "glc-tint")
        + band('<h2 id="cfp">Call for Papers</h2><p>We are accepting submissions for the next volume. Submit through the portal using the button below.</p>'
               + btns(("Start a Submission", u(j, "submit/start/")), ("All Submission Info", u(j, "submissions/"), "ghost")), "glc-cta")
        + band('<h2 id="guidelines">Guidelines for Submissions</h2>'
               "<h3>Who can submit</h3><p>Law students (LL.B., B.A. LL.B., LL.M.), research scholars, academics and legal practitioners in India and abroad.</p>"
               "<h3>Article types</h3><ul><li><strong>Research Articles</strong>: 5,000 to 6,000 words.</li><li><strong>Essays</strong>: 3,000 to 5,000 words.</li>"
               "<li><strong>Case Comments</strong>: 2,500 to 3,000 words.</li></ul>"
               "<h3>Format and citation</h3><ul><li>Bluebook (21st Edition), footnotes only.</li><li>Times New Roman, 12 point body, 10 point footnotes.</li>"
               "<li>1.5 line spacing for the body. Up to two co-authors.</li></ul>"
               "<h3>Submission and review</h3><ul><li>Anonymise the manuscript. Send a separate cover letter.</li><li>Upload .docx or .doc through the portal.</li>"
               "<li>There is no registration or publication fee.</li></ul>")
        + band(f'<h2 id="archive">Published Archive: Volume I</h2><h3>Contemporary Horizons in {s}</h3>'
               f"<p>This is a test archive. Real issues are added from the Manager and appear on the Issues page.</p>"
               + btns(("Browse All Issues", u(j, "issues/")), ("Download Journal (PDF)", "#", "ghost"))
               + "<table class='glc-table'><thead><tr><th>#</th><th>Author</th><th>Title</th><th>Subject</th></tr></thead><tbody>"
               + "".join(arts) + "</tbody></table><p class='glc-muted'>Showing 10 of 10 articles</p>", "glc-tint")
    ))

    # ---- Clinic
    if not is_flagship:
        pages["clinic"] = (clinic_name, (
            hero(j, "Pro bono initiative", clinic_name,
                 f"{clinic_blurb.capitalize()}.", [("Book a Session", "#book"), ("Explore Clinic Mandate", "#mandate", "ghost")], "clinic")
            + band(f'<div class="glc-split"><div><h2>Making {s.lower()} easier to understand</h2>'
                   f"<p>The clinic offers {clinic_blurb}. It also runs workshops, research fellowships and one-to-one advice sessions.</p></div>"
                   f'<img src="{IMG}/{code}/engraving-3.svg" alt="Engraving (test image)"></div>')
            + band('<h2 id="mandate">Core Mandate and Practice Streams</h2>'
                   + grid([card(t, "Free guidance under faculty supervision.", f"0{i+1}") for i, t in enumerate(clinic_services)], 4), "glc-tint")
            + band('<h2 id="book">Book a Pro Bono Guidance Session</h2><div class="glc-grid glc-grid-2"><div class="glc-card"><h3>Preliminary Advisory</h3>'
                   "<ul><li>Duration: 30 minutes per session</li><li>Mode: online or in person at GLC Mumbai</li>"
                   "<li>Open to students, startups, artists and members of the public</li>"
                   "<li>Run by student researchers under faculty oversight</li></ul><p><strong>All sessions are free.</strong></p></div>"
                   "<div class='glc-card'><h3>How it works</h3><ol><li>Pick a time slot.</li><li>Describe your question in a few lines.</li>"
                   "<li>Get a calendar invitation and confirmation.</li></ol><h3>Please have ready</h3><ul><li>Any documents or drafts</li>"
                   "<li>Your specific questions</li><li>Any earlier case or reference numbers</li></ul></div></div>"
                   + btns(("Book a Session", p("contact"))))
            + band("<h2>Academic Disclaimer</h2><p>The clinic gives educational information only. It does not replace formal representation by an advocate.</p>", "glc-tint")
        ))

    # ---- Join
    join_cards = [
        card("Real Depth", f"Work on {topics[0].lower()}, {topics[1].lower()} and {topics[2].lower()}.", "01"),
        card("Flagship Experience",
             "Help run editorial meetings, colloquiums and events." if is_flagship
             else "Help organise certificate courses and colloquiums.", "02"),
        card("Professional Network", "Meet senior advocates, partners and counsel.", "03"),
        card("Publication Profile", "Write for and edit the journal.", "04"),
    ]
    if not is_flagship:
        join_cards.append(card("Public Impact", f"Support the {clinic_name}.", "05"))
    departments = ("Research, Creatives, Editing, Logistics, Finance and Public Relations" if is_flagship
                   else "Research, Creatives, Clinic, Logistics, Finance and Public Relations")
    pages["join"] = ("Join Us", (
        hero(j, "Student induction", "Student Induction and Membership Pathway",
             f"Publish scholarship and work with senior practitioners of {s.lower()}.",
             [("View Hierarchy and Tiers", "#hierarchy"), ("Selection Protocol", "#protocol", "ghost")], "join")
        + band(f"<h2>A Platform for Curious Minds in {s}</h2><p>Open to every student interested in {s.lower()}. No prior expertise is needed.</p>"
               + grid(join_cards, 3))
        + band('<h2 id="hierarchy">3-Tier Leadership Hierarchy</h2>' + grid([
            card("Junior Members (JM)", "Open to students of the 5-year and 3-year programmes. Duties: research, logistics, drafting support.", "Tier 01"),
            card("Junior Core Members (JC)", f"Chosen at year end for performance. Duties: lead departments such as {departments}.", "Tier 02"),
            card("Senior Core Members (SC)", "Chosen from top JC members. Duties: set strategy, mentor juniors, run national flagships.", "Tier 03"),
        ]), "glc-tint")
        + band('<h2 id="protocol">Induction Guidelines and Protocol</h2><h3 id="eligibility">Eligibility</h3>'
               f"<ul><li>Enrolled students of the 5-year and 3-year programmes</li><li>Curiosity about {s.lower()}</li>"
               "<li>Commitment to rigour and teamwork</li></ul><h3>3-Step Selection</h3>"
               + grid([card("Application", "A short application on motivation, academics and interest.", "1"),
                       card("Shortlisting and Interview", "A friendly interview on curiosity and commitment.", "2"),
                       card("Induction and Orientation", "Final selection, department orientation and first project.", "3")])
               + btns(("Inquire with the Student Secretariat", p("contact")))
               + "<h3>Upcoming Induction Cycle</h3><p>Notices and deadlines are posted every autumn semester (test text).</p>")
    ))

    # ---- Contact
    pages["contact"] = ("Contact", (
        hero(j, "Registry and liaison", "Institutional Registry and Communications",
             "Write to us, call us or visit the campus.", [("Email Us", f"mailto:{j['email']}"), ("Call the Office", "tel:02222041707", "ghost")], "contact")
        + band(f'<div class="glc-split"><div><h2>Campus Headquarters</h2><p>{ADDRESS}</p>'
               f"<p><strong>Email:</strong> <a href='mailto:{j['email']}'>{j['email']}</a><br><strong>Phone (GLC office):</strong> {PHONE}<br>"
               f"<strong>Hours:</strong> {HOURS}</p></div>"
               f'<img src="{IMG}/{code}/photo-1.svg" alt="Campus (test image)"></div>')
        + band('<h2>Office Bearers and Points of Contact</h2><div class="glc-people">'
               + person(j, 1, "Test President", "President", "Batch of 2029")
               + person(j, 2, "Test Vice President", "Vice President", "Batch of 2029")
               + person(j, 3, "Test Secretary", "Secretary", "Batch of 2029") + "</div>", "glc-tint")
    ))

    # ---- Policies (what leading journals publish)
    pages["peer-review"] = ("Peer Review Policy", (
        hero(j, "Policies", "Peer Review Policy", "How every manuscript is assessed, from first read to final decision.")
        + band("<h2>Process</h2><ol class='glc-steps'>"
               "<li><strong>Desk review.</strong> The Board of Editors checks scope, originality and format within two weeks.</li>"
               "<li><strong>Plagiarism check.</strong> Similarity above 10% (excluding statutes and quotations) leads to rejection.</li>"
               "<li><strong>Double-blind review.</strong> Two independent reviewers, at least one external to the college, assess the anonymised manuscript.</li>"
               "<li><strong>Decision.</strong> Accept, minor revisions, major revisions or reject, with written reasons.</li>"
               "<li><strong>Editing.</strong> Accepted pieces go through substantive and technical (citation) editing before publication.</li></ol>"
               "<h2>Reviewers</h2><p>Reviewers are academics and practitioners in the field. They declare conflicts of interest and keep manuscripts confidential.</p>"
               "<p class='glc-muted'>Template policy. Adapt it to your board's actual practice before launch.</p>")))
    pages["ethics"] = ("Publication Ethics", (
        hero(j, "Policies", "Publication Ethics and Malpractice Statement", "Our commitments to authors, reviewers and readers, guided by COPE principles.")
        + band("<h2>Authors</h2><ul><li>Submit original, unpublished work not under review elsewhere.</li><li>Cite all sources and disclose funding and conflicts.</li>"
               "<li>Disclose any use of AI tools in research or writing.</li></ul>"
               "<h2>Editors</h2><ul><li>Judge manuscripts only on merit.</li><li>Keep submissions confidential.</li><li>Step aside where they have a conflict.</li></ul>"
               "<h2>Reviewers</h2><ul><li>Review objectively and on time.</li><li>Report suspected plagiarism or duplicate publication.</li></ul>"
               "<h2>Corrections and retractions</h2><p>Errors are corrected through published corrigenda. Serious misconduct leads to retraction, following COPE guidance.</p>"
               "<p class='glc-muted'>Template policy. Adapt it before launch.</p>")))
    pages["open-access"] = ("Open Access and Licensing", (
        hero(j, "Policies", "Open Access and Licensing", "Everything we publish is free to read, download and share.")
        + band("<h2>Licence</h2><p>Articles are published under the Creative Commons Attribution 4.0 International licence (CC BY 4.0). Authors keep their copyright.</p>"
               "<h2>Fees</h2><p>There are no submission, processing or publication charges.</p>"
               "<h2>Archiving</h2><p>Published issues are archived on this website and may be deposited with indexing partners.</p>"
               "<p class='glc-muted'>Template policy. Confirm the licence with your board before launch.</p>")))
    pages["indexing"] = ("Indexing and Identifiers", (
        hero(j, "About the journal", "Indexing and Identifiers", "How readers and databases find our work.")
        + band("<table class='glc-table'><tbody>"
               "<tr><th>ISSN (online)</th><td>To be assigned</td></tr>"
               "<tr><th>DOI prefix</th><td>To be assigned (Crossref)</td></tr>"
               "<tr><th>Citation style</th><td>The Bluebook, 21st edition</td></tr>"
               "<tr><th>Frequency</th><td>Annual, with rolling online publication</td></tr>"
               "<tr><th>Indexed in</th><td>List databases here once accepted (for example Google Scholar, HeinOnline, Manupatra, SCC Online)</td></tr>"
               "<tr><th>Publisher</th><td>Government Law College, Mumbai</td></tr></tbody></table>"
               "<p class='glc-muted'>Fill in each row as identifiers and indexing are confirmed.</p>")))

    # ---- Team
    roster = [("Prof. Test Faculty One", "Professor In-Charge"), ("Prof. Test Faculty Two", "Professor In-Charge"),
              ("Test Founder", "Student Founder"), ("Test Co-Founder", "Co-Founder"),
              ("Test President", "President"), ("Test Vice President", "Vice President"),
              ("Test Secretary", "Secretary"), ("Test Research Head", "Head, Research"),
              ("Test Creatives Head", "Head, Creatives"),
              ("Test Editorial Head", "Head, Editorial Standards") if is_flagship else ("Test Clinic Head", "Head, Clinic"),
              ("Test PR Head", "Head, Public Relations"), ("Test Finance Head", "Head, Finance")]
    pages["team"] = ("Faculty and Core Committee", (
        hero(j, "Governance", "Faculty and Core Committee", f"The people who run the {short}.", [("Join the Team", p("join"))], "about")
        + band('<div class="glc-people">' + "".join(person(j, (i % 8) + 1, n, r) for i, (n, r) in enumerate(roster)) + "</div>")
    ))
    return pages
