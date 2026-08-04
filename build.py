from datetime import datetime
from html import escape
from pathlib import Path

from pybtex.database.input import bibtex


ORCID = "0000-0002-0243-5900"
EMAIL = "amir.amanzadi@gmail.com"
SCHOLAR = "https://scholar.google.com/citations?user=YJbIHQgAAAAJ&hl=en"
GITHUB = "https://github.com/amanzadi"
LINKEDIN = "https://www.linkedin.com/in/amanzadi"
TWITTER = "https://twitter.com/amanzadi"


def get_personal_data():
    bio = f"""
    <p>I'm just a human being. The descriptions below are social statuses I've collected along the way, which you may or may not find interesting.</p>
    <p>My name is Amir, a researcher with an R&amp;D mindset, working across industry and academia, from hands-on wet lab research to large-scale AI deployment. One goal has stayed constant: building methods and tools that help improve human health and longevity. I'm currently a Doctoral Research Fellow in Medicine at the Institute of Clinical Medicine, <a href="https://scholar.google.com/citations?view_op=view_org&amp;hl=en&amp;org=4617098211100467394" target="_blank" rel="noopener">University of Oslo</a>, and <a href="https://www.ous-research.no/" target="_blank" rel="noopener">Oslo University Hospital</a>, working at the <a href="https://www.med.uio.no/klinmed/english/about/organization/divisions/mental-health-addiction/centre-precision-psychiatry/index.html" target="_blank" rel="noopener">Centre for Precision Psychiatry</a> on multi-omics and agentic AI for psychiatric and neurological disease.</p>
    <p>I hold a Master's in Pharmaceutical Sciences from <a href="https://www.uu.se/en" target="_blank" rel="noopener">Uppsala University</a> and double majored in Chemistry and Mechanical Engineering at <a href="https://en.sharif.edu/" target="_blank" rel="noopener">Sharif University of Technology</a>, with roles at <a href="https://ki.se/en" target="_blank" rel="noopener">Karolinska Institutet</a>, <a href="https://www.cmm.ki.se/" target="_blank" rel="noopener">Centre for Molecular Medicine</a>, and <a href="https://celeristx.com" target="_blank" rel="noopener">Celeris Therapeutics</a>. On the AI side, I've worked on AI solution architecture, graph neural networks, and generative AI at <a href="https://www.prepaire.com/" target="_blank" rel="noopener">Prepaire Labs</a>, <a href="https://www.algorithmicdynamics.net/" target="_blank" rel="noopener">Algorithmic Dynamics Lab</a>, and my own ventures, <a href="https://zetazi.com/" target="_blank" rel="noopener">Zetazi</a>, <a href="https://www.linkedin.com/company/shenakhtpajouh" target="_blank" rel="noopener">Cognition Research</a>, <a href="https://www.linkedin.com/company/sharif-cognitive-sciences-community-shenasa/home/" target="_blank" rel="noopener">Shenasa</a>, and <a href="https://linkedin.com/company/yarai/" target="_blank" rel="noopener">Yar AI</a>.</p>
    <p>More in my <a href="cv.html">CV</a>. The interesting parts are harder to list, so feel free to email me.</p>
    """
    education = [
        ("MSc Pharmaceutical Science", "Uppsala University", "2021"),
        ("BSc Chemistry · Mechanical Engineering minor", "Sharif University of Technology", ""),
    ]
    return bio, education


def get_author_dict():
    return {"Andreas Geiger": "https://www.cvlibs.net/"}


def person_name(person):
    return " ".join(person.get_part("first") + person.get_part("last"))


def generate_person_html(persons):
    links = get_author_dict()
    rendered = []
    for person in persons:
        name = person_name(person)
        safe_name = escape(name)
        if name in links:
            safe_name = f'<a href="{escape(links[name], quote=True)}" target="_blank" rel="noopener">{safe_name}</a>'
        if name in {"Amir Amanzadi", "Amir Hossein Amanzadi"}:
            safe_name = f"<strong>{safe_name}</strong>"
        rendered.append(safe_name)
    return ", ".join(rendered)


def safe_url(value):
    return escape(value.strip(), quote=True)


def citation(entry_key, entry):
    authors = " and ".join(person_name(person) for person in entry.persons["author"])
    fields = [
        ("author", authors),
        ("title", entry.fields["title"]),
        ("booktitle", entry.fields["booktitle"]),
        ("year", entry.fields["year"]),
    ]
    lines = [f"@InProceedings{{{entry_key},"]
    lines.extend(f"  {name:<10} = {{{value}}}," for name, value in fields)
    lines.append("}")
    return "\n".join(lines)


def artifact_links(entry):
    labels = {
        "html": "project",
        "pdf": "paper",
        "supp": "supplement",
        "video": "video",
        "poster": "poster",
        "code": "code",
        "blog": "blog",
    }
    links = []
    for field, label in labels.items():
        value = entry.fields.get(field, "").strip()
        if value and value != "-":
            links.append(f'<a href="{safe_url(value)}" target="_blank" rel="noopener">{label}</a>')
    return " ".join(links)


def get_publications():
    data = bibtex.Parser().parse_file("publication_list.bib")
    cards = []
    for key, entry in data.entries.items():
        year = entry.fields.get("year", "")
        title = escape(entry.fields.get("title", ""))
        venue = escape(entry.fields.get("booktitle", ""))
        image = safe_url(entry.fields.get("img", "assets/img/publications/default.svg"))
        tags = f"publication {year}"
        if any(entry.fields.get(field) not in (None, "", "-") for field in ("html", "blog")):
            tags += " project"
        if entry.fields.get("code") not in (None, "", "-"):
            tags += " repository"
        award = entry.fields.get("award", "")
        award_html = f'<span class="badge accent">{escape(award)}</span>' if award else ""
        cards.append(f"""
        <article class="research-item" data-tags="{escape(tags)}">
          <img class="research-image" src="{image}" alt="Publication image for {title}" loading="lazy">
          <div class="research-content">
          <h3>{title} <span class="publication-year">{escape(year)}</span></h3>
          <p class="authors">{generate_person_html(entry.persons['author'])}</p>
          <p class="venue">{venue} {award_html}</p>
          <div class="resource-links">{artifact_links(entry)}<details class="citation"><summary>Expand bibtex</summary><pre>{escape(citation(key, entry))}</pre></details></div>
          </div>
        </article>
        """)
    return "".join(cards)


def get_work_talks():
    data = bibtex.Parser().parse_file("talk_list.bib")
    cards = []
    for entry in data.entries.values():
        title = escape(entry.fields.get("title", ""))
        year = escape(entry.fields.get("year", ""))
        image = safe_url(entry.fields.get("img", "assets/img/publications/default.svg"))
        links = []
        for field, label in (("slides", "slides"), ("video", "recording")):
            value = entry.fields.get(field, "").strip()
            if value:
                links.append(f'<a href="{safe_url(value)}" target="_blank" rel="noopener">{label}</a>')
        cards.append(f"""
        <article class="research-item" data-tags="talks">
          <img class="research-image" src="{image}" alt="Talk image for {title}" loading="lazy">
          <div class="research-content">
          <h3>{title} <span class="publication-year">{year}</span></h3>
          <p class="venue">{escape(entry.fields.get('booktitle', ''))}</p>
          <div class="resource-links">{' '.join(links)}</div>
          </div>
        </article>
        """)
    return "".join(cards)


def get_talks():
    data = bibtex.Parser().parse_file("talk_list.bib")
    items = []
    for entry in data.entries.values():
        links = []
        for field, label in (("slides", "slides"), ("video", "recording")):
            value = entry.fields.get(field, "").strip()
            if value:
                links.append(f'<a href="{safe_url(value)}" target="_blank" rel="noopener">{label}</a>')
        items.append(f"""
        <article class="timeline-item">
          <span class="timeline-year">{escape(entry.fields.get('year', ''))}</span>
          <div><h3>{escape(entry.fields.get('title', ''))}</h3>
          <p>{escape(entry.fields.get('booktitle', ''))}</p>
          <div class="resource-links">{' '.join(links)}</div></div>
        </article>
        """)
    return "".join(items)


def get_index_html():
    bio, _ = get_personal_data()
    work_items = get_publications() + get_work_talks()
    now = datetime.now()
    day = now.day
    suffix = "th" if 10 < day % 100 < 14 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    updated = f"{now.strftime('%B')} {day}{suffix} {now.year}"
    return f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Amir Hossein Amanzadi — biomedical AI researcher working on graph neural networks, systems medicine, and drug discovery.">
  <meta property="og:title" content="Amir Hossein Amanzadi">
  <meta property="og:description" content="Biomedical AI, graph neural networks, systems medicine, and drug discovery.">
  <meta property="og:image" content="https://amanzadi.github.io/assets/img/profile.png">
  <title>Amir Hossein Amanzadi</title>
  <link rel="icon" href="assets/tabicon.ico">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #f9f9fa; --surface: #ffffff; --text: #1a1a1a; --muted: #5e5e5e;
      --line: #e2e5eb; --accent: #283a80; --accent-hover: #1e2f63; --accent-soft: #eef0fb; --on-accent: #ffffff; --max: 840px;
    }}
    [data-theme="dark"] {{
      --bg: #0d1b2a; --surface: #16223a; --text: #c8d1e7; --muted: #788bb0;
      --line: #2a3d5e; --accent: #6b79b8; --accent-hover: #5a699c; --accent-soft: #26334d; --on-accent: #0d1b2a;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; scroll-padding-top: 80px; }}
    body {{ margin: 0; background: var(--bg); color: var(--text); font-family: et-book, Palatino, "Palatino Linotype", "Palatino LT STD", "Book Antiqua", Georgia, serif; line-height: 1.65; }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; text-underline-offset: 3px; }}
    button, input {{ font: inherit; }}
    .wrap {{ width: min(calc(100% - 40px), 1080px); margin-inline: auto; }}
    .nav {{ position: sticky; top: 0; z-index: 10; background: color-mix(in srgb, var(--bg) 92%, transparent); backdrop-filter: blur(12px); }}
    .nav::before, .footer::before {{ position: absolute; left: 0; right: 0; content: ""; border-top: 1px solid var(--line); z-index: -1; }}
    .nav::before {{ top: 50%; }} .footer::before {{ top: 41px; }}
    .nav-inner {{ position: relative; display: flex; align-items: center; justify-content: center; min-width: 350px; width: max-content; min-height: 64px; gap: 22px; padding: 0 30px; border-right: 1px solid var(--line); border-left: 1px solid var(--line); background: var(--bg); }}
    .nav-links {{ display: flex; gap: 22px; align-items: center; }}
    .nav-links a {{ position: relative; color: var(--muted); font-size: .92rem; transition: color .2s ease; }}
    .nav-links a::after {{ position: absolute; right: 0; bottom: -8px; left: 0; height: 2px; content: ""; background: var(--accent); transform: scaleX(0); transition: transform .2s ease; }}
    .nav-links a:hover, .nav-links a.active {{ color: var(--accent); }}
    .nav-links a.active::after {{ transform: scaleX(1); }}
    .nav-links a:hover {{ color: var(--accent); }}
    .theme-toggle {{ width: 16px; height: 16px; padding: 0; border: 1px solid var(--text); border-radius: 50%; background: var(--text); cursor: pointer; }}
    [data-theme="light"] .theme-toggle {{ background: transparent; }}
    .hero {{ padding: 56px 40px; background: transparent; animation: rise .55s ease both; }}
    .hero-layout {{ display: flex; flex-direction: column; align-items: center; gap: 28px; }}
    .hero-main {{ width: 100%; }}
    .hero-main h1, .hero-main .role {{ text-align: center; }}
    .portrait {{ order: -1; width: 280px; height: 280px; border: 6px solid var(--accent); border-radius: 50%; background: url("assets/img/profile.png") 58% 30% / 112% auto no-repeat; }}
    h1, h2, h3 {{ font-family: et-book, Palatino, "Palatino Linotype", "Palatino LT STD", "Book Antiqua", Georgia, serif; font-weight: 600; line-height: 1.15; }}
    h1 {{ margin: 0; font-family: "Cinzel", serif; font-size: clamp(2.4rem, 5vw, 3.7rem); letter-spacing: .01em; font-weight: 400; }}
    .hero-main h1 {{ margin-bottom: 0; }}
    h1 .first-name {{ font-weight: 700; }}
    .role {{ margin: 10px 0 24px; color: var(--muted); font-size: 1.05rem; text-align: center; }}
    .hero-copy {{ max-width: none; margin: 0; color: var(--muted); text-align: justify; text-justify: inter-word; font-size: 1rem; line-height: 1.65; }}
    .hero-copy p {{ margin: 0 0 18px; }}
    .hero-copy p:last-child {{ margin-bottom: 0; }}
    .socials {{ display: flex; justify-content: center; gap: 12px; margin-top: 30px; }}
    .socials a {{ display: grid; place-items: center; width: 38px; height: 38px; border: 1px solid var(--line); border-radius: 50%; color: var(--accent); }}
    .section {{ padding: 34px 0; }}
    .section > .wrap {{ padding: 40px; border: 1px solid var(--line); border-radius: 14px; background: var(--surface); box-shadow: 0 18px 50px rgba(0, 0, 0, .12); animation: rise .55s ease both; }}
    .perspective > .wrap {{ max-width: 1080px; }}
    .perspective .section-heading {{ justify-content: center; margin-bottom: 28px; max-width: none; padding-left: 0; border-left: 0; text-align: center; }}
    .perspective .section-heading h2 {{ color: var(--text); font-size: clamp(2rem, 5vw, 3rem); }}
    .perspective-copy {{ max-width: none; margin: 0; color: var(--muted); font-family: inherit; font-size: 1rem; line-height: 1.65; text-align: justify; text-justify: inter-word; }}
    .perspective-copy ol {{ margin: 0; padding-left: 2rem; }}
    .perspective-copy li {{ margin-bottom: 22px; padding-left: .35rem; }}
    .perspective-copy li:last-child {{ margin-bottom: 0; }}
    .perspective-copy li::marker {{ color: var(--accent); font-weight: 700; }}
    .perspective-copy a {{ color: var(--accent); }}
    .section-heading {{ display: flex; align-items: baseline; justify-content: center; gap: 20px; margin-bottom: 28px; text-align: center; }}
    h2 {{ margin: 0; font-size: clamp(2rem, 5vw, 3rem); }}
    .section-kicker {{ color: var(--muted); font-size: .9rem; }}
    .resource-links, .filter-row {{ display: flex; flex-wrap: wrap; gap: 8px 14px; align-items: center; }}
    .tag {{ padding: 4px 9px; border-radius: 999px; background: var(--accent-soft); color: var(--accent); font-size: .8rem; }}
    .filter-row {{ justify-content: center; margin-bottom: 22px; }}
    .filter {{ padding: 6px 12px; border: 1px solid var(--line); border-radius: 999px; background: transparent; color: var(--muted); cursor: pointer; }}
    .filter.active, .filter:hover {{ border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }}
    .search {{ width: 190px; padding: 8px 12px; border: 1px solid var(--line); border-radius: 5px; background: var(--surface); color: var(--text); }}
    .research-list {{ display: grid; gap: 14px; }}
    .research-item {{ display: grid; grid-template-columns: 255px minmax(0, 1fr); gap: 24px; padding: 22px; border: 1px solid var(--line); border-radius: 9px; background: var(--bg); transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease; }}
    .research-item:hover {{ transform: translateY(-3px); border-color: var(--accent); box-shadow: 0 12px 28px rgba(0, 0, 0, .12); }}
    .research-item[hidden] {{ display: none; }}
    .research-image {{ display: block; width: 255px; height: auto; max-height: 180px; margin-top: 9px; border: 1px solid var(--line); border-radius: 4px; object-fit: contain; background: var(--surface); }}
    .research-content {{ min-width: 0; }}
    .item-topline {{ display: flex; justify-content: space-between; gap: 12px; color: var(--muted); font-size: .82rem; text-transform: uppercase; letter-spacing: .04em; }}
    .research-item h3 {{ margin: 9px 0 8px; font-size: 1.2rem; }}
    .publication-year {{ display: inline-block; margin-left: .35rem; padding: .15rem .45rem; border: 1px solid var(--line); border-radius: 999px; color: var(--accent); font-family: Georgia, Cambria, "Times New Roman", serif; font-size: .62em; font-weight: 600; letter-spacing: .02em; vertical-align: .15em; }}
    .authors, .venue {{ margin: 0 0 5px; color: var(--muted); font-size: .94rem; }}
    .venue {{ font-style: italic; }}
    .resource-links a {{ font-size: .86rem; }}
    .resource-links a::after {{ content: " ↗"; }}
    details {{ margin-top: 14px; color: var(--muted); font-size: .86rem; }}
    summary {{ cursor: pointer; color: var(--accent); }}
    pre {{ overflow-x: auto; margin: 10px 0 0; padding: 14px; background: var(--surface); border: 1px solid var(--line); font-size: .78rem; }}
    .badge {{ margin-left: 7px; font-style: normal; }}
    .accent {{ color: var(--accent); }}
    .citation {{ flex: 0 0 auto; min-width: 0; margin: 0; }}
    .citation[open] {{ flex-basis: 100%; }}
    .citation summary {{ display: inline; }}
    .citation pre {{ width: 100%; min-width: 0; max-width: 100%; white-space: pre-wrap; overflow-wrap: anywhere; }}
    .footer {{ position: relative; padding: 30px 0 44px; color: var(--muted); font-size: .82rem; text-align: center; }}
    .footer .wrap {{ position: relative; width: max-content; max-width: calc(100% - 28px); padding: 0 24px; border-right: 1px solid var(--line); border-left: 1px solid var(--line); background: var(--bg); }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @media (max-width: 680px) {{
      .wrap {{ width: min(calc(100% - 28px), 1080px); }}
      .hero, .section > .wrap {{ padding: 32px 20px; }}
      .nav-inner {{ min-width: 0; width: calc(100% - 28px); min-height: 58px; padding: 0 18px; }} .nav-links {{ width: 100%; justify-content: center; gap: 18px; }}
      .hero {{ padding: 32px 20px; }} .portrait {{ width: 220px; height: 220px; }}
      .research-item {{ grid-template-columns: 1fr; gap: 14px; }} .research-image {{ width: 100%; height: auto; max-height: none; }}
      .section-heading {{ display: block; }} .section-kicker {{ display: block; margin-top: 7px; }} .search {{ width: 100%; margin-top: 14px; }}
    }}
    @media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} *, *::before, *::after {{ animation: none !important; transition: none !important; }} }}
  </style>
</head>
<body>
  <nav class="nav" aria-label="Primary navigation">
    <div class="wrap nav-inner">
      <div class="nav-links">
        <a href="#about" data-section="about">About</a><a href="#perspective" data-section="perspective">Perspective</a><a href="#research" data-section="research">Work</a><a href="cv.html">CV</a>
        <button class="theme-toggle" id="themeToggle" type="button" aria-label="Switch theme"></button>
      </div>
    </div>
  </nav>

  <main>
    <header class="hero wrap" id="about">
      <div class="hero-layout">
        <div class="hero-main">
          <h1><span class="first-name">Amir</span> Hossein Amanzadi</h1>
          <p class="role">Doctoral Research Fellow @ University of Oslo</p>
          <div class="hero-copy">{bio}</div>
          <div class="socials" aria-label="Social and academic profiles">
            <a href="mailto:{EMAIL}" aria-label="Email"><i class="fa-regular fa-envelope" aria-hidden="true"></i></a>
            <a href="cv.html" aria-label="Interactive CV"><i class="fa-regular fa-file-lines" aria-hidden="true"></i></a>
            <a href="https://orcid.org/{ORCID}" target="_blank" rel="noopener" aria-label="ORCID"><i class="fa-brands fa-orcid" aria-hidden="true"></i></a>
            <a href="{SCHOLAR}" target="_blank" rel="noopener" aria-label="Google Scholar"><i class="fa-solid fa-graduation-cap" aria-hidden="true"></i></a>
            <a href="{GITHUB}" target="_blank" rel="noopener" aria-label="GitHub"><i class="fa-brands fa-github" aria-hidden="true"></i></a>
            <a href="{LINKEDIN}" target="_blank" rel="noopener" aria-label="LinkedIn"><i class="fa-brands fa-linkedin-in" aria-hidden="true"></i></a>
          </div>
        </div>
        <div class="portrait" role="img" aria-label="Portrait of Amir Hossein Amanzadi"></div>
      </div>
    </header>

    <section class="section perspective" id="perspective">
      <div class="wrap">
        <div class="section-heading"><h2>Research Perspective</h2></div>
        <div class="perspective-copy">
          <ol>
            <li>Human biology is dynamic. Disease does not emerge from a single molecule or a single moment. It emerges from interactions across scales, from atoms to populations, unfolding over time.</li>
            <li>Most of our medical data are cross-sectional. Genetics, imaging, and multi-omics each give a precise but static slice of a moving system. To understand disease, we need to connect these snapshots into something that evolves the way the body does.</li>
            <li>I suspect this is a representation problem before it is a data problem. Biology is relational, so it needs an architecture that captures relationships and lets them change. Graph-based knowledge and agentic AI with long-term memory seem like reasonable places to start.</li>
            <li>The obstacle is scale. Biology runs at the molecular, cellular, organ, and population level at once, and no single tool spans all of them. I work at that integration layer, combining multi-omics, genetics, and imaging with graph neural networks and agentic AI, trying to build models that hold up in both space and time.</li>
            <li>The distant dream is a digital twin, a real-time biological runtime of human physiology across all scales. We are nowhere near it, and that absence is part of why medicine moves slowly. It may not arrive in my lifetime, but it seems worth working toward. This is why I work with large population cohorts and national medical registries at Oslo University Hospital, where the data depth makes the direction possible.</li>
          </ol>
        </div>
      </div>
    </section>

    <section class="section" id="research">
      <div class="wrap">
        <div class="section-heading"><h2>Work</h2></div>
        <div class="filter-row" style="margin-top: 34px;">
          <button class="filter active" data-filter="all" type="button">All</button><button class="filter" data-filter="publication" type="button">Publications</button><button class="filter" data-filter="talks" type="button">Talks</button><button class="filter" data-filter="project" type="button">Projects</button><button class="filter" data-filter="repository" type="button">Repositories</button>
          <input class="search" id="researchSearch" type="search" placeholder="Search work" aria-label="Search work">
        </div>
        <div class="research-list" id="researchList">{work_items}</div>
      </div>
    </section>

  </main>

  <footer class="footer"><div class="wrap">Last updated on {updated} · © Vibe coded by <a href="{GITHUB}" target="_blank" rel="noopener">Amir</a></div></footer>

  <script>
    const root = document.documentElement;
    const themeToggle = document.getElementById("themeToggle");
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) root.dataset.theme = savedTheme;
    themeToggle.addEventListener("click", () => {{
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      localStorage.setItem("theme", next);
    }});
    const sectionLinks = [...document.querySelectorAll("[data-section]")];
    const sections = sectionLinks.map((link) => document.getElementById(link.dataset.section));
    function updateActiveSection() {{
      const current = sections.reduce((selected, section) =>
        section.getBoundingClientRect().top <= 120 ? section : selected, sections[0]);
      sectionLinks.forEach((link) => {{
        const active = link.dataset.section === current.id;
        link.classList.toggle("active", active);
        if (active) link.setAttribute("aria-current", "page");
        else link.removeAttribute("aria-current");
      }});
    }}
    window.addEventListener("scroll", updateActiveSection, {{ passive: true }});
    updateActiveSection();
    const cards = [...document.querySelectorAll(".research-item")];
    const search = document.getElementById("researchSearch");
    let activeFilter = "all";
    function updateResearch() {{
      const query = search.value.trim().toLowerCase();
      cards.forEach((card) => {{
        const matchesFilter = activeFilter === "all" || card.dataset.tags.includes(activeFilter);
        const matchesSearch = !query || card.textContent.toLowerCase().includes(query);
        card.hidden = !(matchesFilter && matchesSearch);
      }});
    }}
    document.querySelectorAll("[data-filter]").forEach((button) => button.addEventListener("click", () => {{
      activeFilter = button.dataset.filter;
      document.querySelectorAll("[data-filter]").forEach((item) => item.classList.toggle("active", item === button));
      updateResearch();
    }}));
    search.addEventListener("input", updateResearch);
  </script>
</body>
</html>
"""


def get_cv_html():
    _, education = get_personal_data()
    education_html = "".join(f"""
      <article class="cv-entry" data-kind="education">
        <span class="year">{escape(year) or '—'}</span>
        <div><h2>{escape(degree)}</h2><p>{escape(school)}</p></div>
      </article>
    """ for degree, school, year in education)
    talks = get_talks().replace('class="timeline-item"', 'class="cv-entry" data-kind="talks"')
    return f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Curriculum vitae of Amir Hossein Amanzadi.">
  <title>CV · Amir Hossein Amanzadi</title>
  <link rel="icon" href="assets/tabicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{ --bg:#f9f9fa; --surface:#ffffff; --text:#1a1a1a; --muted:#5e5e5e; --line:#e2e5eb; --accent:#283a80; --accent-hover:#1e2f63; --on-accent:#ffffff; --max:840px; }}
    [data-theme="dark"] {{ --bg:#0d1b2a; --surface:#16223a; --text:#c8d1e7; --muted:#788bb0; --line:#2a3d5e; --accent:#6b79b8; --accent-hover:#5a699c; --on-accent:#0d1b2a; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; background:var(--bg); color:var(--text); font-family:et-book,Palatino,"Palatino Linotype","Palatino LT STD","Book Antiqua",Georgia,serif; line-height:1.65; }}
    a {{ color:var(--accent); text-decoration:none; }} a:hover {{ text-decoration:underline; }} button {{ font:inherit; }}
    .wrap {{ width:min(calc(100% - 40px),var(--max)); margin-inline:auto; }}
    nav {{ position:relative; }} nav::before, footer::before {{ position:absolute; left:0; right:0; content:""; border-top:1px solid var(--line); z-index:-1; }} nav::before {{ top:50%; }} footer::before {{ top:.825em; }} .nav-inner {{ position:relative; display:flex; justify-content:center; gap:24px; align-items:center; min-width:350px; width:max-content; min-height:64px; margin:auto; padding:0 30px; border-right:1px solid var(--line); border-left:1px solid var(--line); background:var(--bg); }} nav a {{ color:var(--muted); font-size:.92rem; }}
    .theme {{ width:16px; height:16px; padding:0; border:1px solid var(--text); border-radius:50%; background:var(--text); cursor:pointer; }} [data-theme="light"] .theme {{ background:transparent; }}
    main {{ padding:74px 0; }} h1,h2,h3 {{ font-family:et-book,Palatino,"Palatino Linotype","Palatino LT STD","Book Antiqua",Georgia,serif; line-height:1.15; }} h1 {{ margin:0; font-family:"Cinzel",serif; font-size:clamp(2.6rem,7vw,4.5rem); }} h2 {{ margin:0 0 4px; font-size:1.35rem; }}
    .intro, .cv-card {{ padding:40px; border:1px solid var(--line); border-radius:14px; background:var(--surface); box-shadow:0 18px 50px rgba(0,0,0,.12); }} .intro p {{ color:var(--muted); }}
    .actions {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:24px; }} .button {{ padding:10px 15px; border:1px solid var(--accent); border-radius:5px; background:var(--accent); color:var(--on-accent); }}
    .cv-card {{ margin-top:28px; }} .filters {{ display:flex; gap:8px; margin-bottom:24px; }} .filter {{ padding:7px 13px; border:1px solid var(--line); border-radius:999px; background:transparent; color:var(--muted); cursor:pointer; }} .filter.active,.filter:hover {{ border-color:var(--accent); color:var(--accent); background:var(--accent); color:var(--on-accent); }}
    .cv-entry {{ display:grid; grid-template-columns:72px 1fr; gap:18px; padding:20px 0; border-top:1px solid var(--line); }} .cv-entry[hidden] {{ display:none; }} .year {{ color:var(--accent); font-size:.88rem; }} .cv-entry p {{ margin:0; color:var(--muted); }} .cv-entry h3 {{ margin:0; font-family:et-book,Palatino,"Palatino Linotype",Georgia,serif; }}
    footer {{ position:relative; padding:0 0 44px; color:var(--muted); font-size:.82rem; text-align:center; }} footer span {{ position:relative; display:inline-block; max-width:calc(100% - 28px); padding:0 24px; border-right:1px solid var(--line); border-left:1px solid var(--line); background:var(--bg); }}
    @media(max-width:680px) {{ .wrap {{ width:min(calc(100% - 28px),var(--max)); }} .nav-inner {{ min-width:0; width:calc(100% - 28px); padding:0 18px; gap:16px; }} .intro,.cv-card {{ padding:26px 20px; }} main {{ padding:46px 0; }} }}
  </style>
</head>
<body>
  <nav><div class="wrap nav-inner"><a href="index.html#about">About</a><a href="index.html#research">Work</a><a href="cv.html">CV</a><button class="theme" id="theme" type="button" aria-label="Switch theme"></button></div></nav>
  <main class="wrap">
    <section class="intro"><h1>Curriculum Vitae</h1><p>Education, talks, and selected academic activities.</p><div class="actions"><a class="button" href="assets/pdf/CV_Amir_Amanzadi.pdf" target="_blank" rel="noopener">Download PDF ↗</a></div></section>
    <section class="cv-card"><div class="filters"><button class="filter active" data-kind="all" type="button">All</button><button class="filter" data-kind="education" type="button">Education</button><button class="filter" data-kind="talks" type="button">Talks</button></div><div id="cvEntries">{education_html}{talks}</div></section>
  </main>
  <footer><span>Last updated on {datetime.now().strftime('%B %-d, %Y')} · © Vibe coded by <a href="{GITHUB}" target="_blank" rel="noopener">Amir</a></span></footer>
  <script>
    const root=document.documentElement, theme=document.getElementById("theme"), saved=localStorage.getItem("theme");
    if(saved) root.dataset.theme=saved;
    theme.addEventListener("click",()=>{{const next=root.dataset.theme==="dark"?"light":"dark";root.dataset.theme=next;localStorage.setItem("theme",next);}});
    document.querySelectorAll("[data-kind]").forEach(button=>button.addEventListener("click",()=>{{const kind=button.dataset.kind;document.querySelectorAll(".filter").forEach(item=>item.classList.toggle("active",item===button));document.querySelectorAll(".cv-entry").forEach(entry=>entry.hidden=kind!=="all"&&entry.dataset.kind!==kind);}}));
  </script>
</body>
</html>
"""


def write_index_html(filename="index.html"):
    Path(filename).write_text(get_index_html(), encoding="utf-8")
    print(f"Written index content to {filename}.")


def write_cv_html(filename="cv.html"):
    Path(filename).write_text(get_cv_html(), encoding="utf-8")
    print(f"Written CV content to {filename}.")


if __name__ == "__main__":
    write_index_html()
    write_cv_html()
