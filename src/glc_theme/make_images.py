"""Makes clearly-labelled TEST images (SVG) for every journal.

Run:  python manage.py glc_seed --images-only
Replace any of them later by uploading a real picture in the Manager.
"""
import os

from .journals_data import JOURNALS


def _shade(hexcol, f):
    h = hexcol.lstrip("#")
    r, g, b = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    r, g, b = [max(0, min(255, int(c * f))) for c in (r, g, b)]
    return f"#{r:02X}{g:02X}{b:02X}"


def _columns(x0, w, h, col, n=7, op=0.18):
    out = []
    cw = w / (n * 1.6)
    for i in range(n):
        x = x0 + i * (w / n) + cw * 0.3
        out.append(f'<rect x="{x:.0f}" y="{h*0.28:.0f}" width="{cw:.0f}" height="{h*0.55:.0f}" fill="{col}" opacity="{op}"/>')
    out.append(f'<polygon points="{x0+w*0.04:.0f},{h*0.28:.0f} {x0+w*0.5:.0f},{h*0.1:.0f} {x0+w*0.96:.0f},{h*0.28:.0f}" fill="{col}" opacity="{op}"/>')
    out.append(f'<rect x="{x0+w*0.04:.0f}" y="{h*0.85:.0f}" width="{w*0.92:.0f}" height="{h*0.05:.0f}" fill="{col}" opacity="{op}"/>')
    return "".join(out)


def hero_svg(p, a, w=1600, h=700, label=""):
    d = _shade(p, 0.55)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p}"/><stop offset="1" stop-color="{d}"/></linearGradient></defs>'
        f'<rect width="{w}" height="{h}" fill="url(#g)"/>' + _columns(w * 0.45, w * 0.55, h, a, 8, 0.22)
        + f'<circle cx="{w*0.12}" cy="{h*0.2}" r="{h*0.35}" fill="{a}" opacity="0.08"/>'
        f'<text x="{w-24}" y="{h-20}" text-anchor="end" font-family="sans-serif" font-size="22" fill="#fff" opacity="0.55">{label}</text></svg>'
    )


def photo_svg(p, a, n, w=800, h=600):
    d = _shade(p, 0.6 + (n % 4) * 0.12)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">'
        f'<rect width="{w}" height="{h}" fill="{d}"/>'
        f'<circle cx="{w*(0.2+0.12*(n%5))}" cy="{h*0.35}" r="{h*0.28}" fill="{a}" opacity="0.28"/>'
        + _columns(w * 0.1, w * 0.8, h, "#ffffff", 5, 0.1)
        + f'<text x="{w/2}" y="{h/2}" text-anchor="middle" font-family="sans-serif" font-size="46" font-weight="700" fill="#fff" opacity="0.9">TEST IMAGE {n}</text>'
        f'<text x="{w/2}" y="{h/2+44}" text-anchor="middle" font-family="sans-serif" font-size="22" fill="#fff" opacity="0.7">Replace with a real photo</text></svg>'
    )


def engraving_svg(p, a, n, w=900, h=700):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">'
        f'<rect width="{w}" height="{h}" fill="#F6F1E7"/><rect x="18" y="18" width="{w-36}" height="{h-36}" fill="none" stroke="{p}" stroke-width="3" opacity="0.6"/>'
        + _columns(w * 0.1, w * 0.8, h, p, 6, 0.55)
        + f'<circle cx="{w/2}" cy="{h*0.52}" r="{h*0.12}" fill="{a}" opacity="0.8"/>'
        f'<text x="{w/2}" y="{h-40}" text-anchor="middle" font-family="serif" font-size="26" fill="{p}">Test engraving {n}</text></svg>'
    )


def crest_svg(p, a, initials):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400"><circle cx="200" cy="200" r="190" fill="{p}"/>'
        f'<circle cx="200" cy="200" r="168" fill="none" stroke="{a}" stroke-width="6"/>'
        f'<circle cx="200" cy="200" r="150" fill="none" stroke="{a}" stroke-width="2" opacity="0.6"/>'
        + _columns(110, 180, 300, a, 4, 0.55)
        + f'<text x="200" y="330" text-anchor="middle" font-family="serif" font-size="58" font-weight="700" fill="#fff">{initials}</text></svg>'
    )


def avatar_svg(p, a, n):
    bg = _shade(p, 0.7 + (n % 3) * 0.15)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300"><rect width="300" height="300" fill="{bg}"/>'
        f'<circle cx="150" cy="115" r="55" fill="{a}" opacity="0.9"/><ellipse cx="150" cy="270" rx="95" ry="85" fill="{a}" opacity="0.9"/>'
        f'<text x="150" y="292" text-anchor="middle" font-family="sans-serif" font-size="16" fill="#fff" opacity="0.8">TEST PHOTO</text></svg>'
    )


def initials(name):
    stop = {"and", "of", "the", "law", "journal"}
    letters = [w[0] for w in name.replace(",", "").split() if w.lower() not in stop]
    return "".join(letters[:3]).upper() or "GLC"


def make_all(static_dir):
    root = os.path.join(static_dir, "GLCLaw", "img")
    for j in JOURNALS:
        d = os.path.join(root, j["code"])
        os.makedirs(d, exist_ok=True)
        p, a = j["primary"], j["accent"]

        def w(name, svg):
            with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
                fh.write(svg)

        for key in ("hero", "events", "journal", "clinic", "join", "contact", "about"):
            w(f"{key}.svg", hero_svg(p, a))
        for n in range(1, 7):
            w(f"photo-{n}.svg", photo_svg(p, a, n))
        for n in range(1, 4):
            w(f"engraving-{n}.svg", engraving_svg(p, a, n))
        for n in range(1, 9):
            w(f"avatar-{n}.svg", avatar_svg(p, a, n))
        w("crest.svg", crest_svg(p, a, initials(j["short"] if j["code"] != "lawreview" else "Law Review")))
        w("logo.svg", crest_svg(p, a, initials(j["short"] if j["code"] != "lawreview" else "Law Review")))
    # shared college crest and press cover
    shared = os.path.join(root, "shared")
    os.makedirs(shared, exist_ok=True)
    with open(os.path.join(shared, "college-crest.svg"), "w", encoding="utf-8") as fh:
        fh.write(crest_svg("#3A2A1A", "#C9A227", "GLC"))
    with open(os.path.join(shared, "press-hero.svg"), "w", encoding="utf-8") as fh:
        fh.write(hero_svg("#7A1E2E", "#C9A227", 1600, 700))
    return root
