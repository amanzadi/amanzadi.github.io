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
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Amir Hossein Amanzadi — a career in biomedical research, zoomed out.">
  <title>Zooming Out · Amir Hossein Amanzadi</title>
  <link rel="icon" href="assets/tabicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600&display=swap" rel="stylesheet">
  <style>
    :root { --bg:#05080d; --ink:#e8edf4; --ink-dim:#7c8a9c; --teal:#4fd1c5; --blue:#6ea8ff; --line:#1c2733; }
    * { box-sizing:border-box; }
    html,body { margin:0; background:var(--bg); color:var(--ink); font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; overflow-x:hidden; }
    #canvas-holder { position:fixed; inset:0; z-index:1; }
    canvas { display:block; }
    .site-nav { position:fixed; top:0; left:0; right:0; z-index:20; display:flex; justify-content:space-between; padding:22px clamp(20px,5vw,72px); font:11px/1 "Courier New",monospace; letter-spacing:.12em; text-transform:uppercase; pointer-events:none; }
    .site-nav a { pointer-events:auto; color:var(--ink-dim); text-decoration:none; transition:color .2s; }
    .site-nav a:hover { color:var(--teal); }
    #scalebar { position:fixed; right:clamp(18px,3vw,34px); top:50%; z-index:10; display:flex; flex-direction:column; align-items:center; transform:translateY(-50%); font:10px/1 "Courier New",monospace; color:var(--ink-dim); }
    #scalebar .track { position:relative; width:2px; height:320px; background:var(--line); }
    #scalebar .fill { position:absolute; bottom:0; width:100%; background:var(--teal); box-shadow:0 0 8px var(--teal); }
    #scalebar .marks { position:absolute; top:0; right:18px; display:flex; height:100%; flex-direction:column; justify-content:space-between; text-align:right; }
    #scalebar .marks span { opacity:.35; transition:opacity .2s,color .2s; }
    #scalebar .marks span.active { color:var(--teal); opacity:1; }
    main { position:relative; z-index:5; }
    .scene { display:flex; min-height:100vh; flex-direction:column; justify-content:center; padding:120px 12vw 100px; pointer-events:none; }
    .scene > div { max-width:46ch; }
    .eyebrow { margin-bottom:14px; color:var(--teal); font:12px/1.2 "Courier New",monospace; letter-spacing:.18em; text-transform:uppercase; }
    h1,h2 { margin:0 0 20px; font-family:"Cinzel",Georgia,serif; font-weight:500; letter-spacing:.01em; line-height:1.12; }
    h1 { max-width:9ch; font-size:clamp(2.8rem,7vw,5.2rem); }
    h2 { max-width:12ch; font-size:clamp(2.15rem,5vw,4rem); }
    p { max-width:46ch; margin:0 0 22px; color:var(--ink-dim); font-size:clamp(.98rem,1.6vw,1.08rem); line-height:1.72; }
    .stat { max-width:40ch; border-left:2px solid var(--teal); padding-left:12px; color:var(--ink); font:13px/1.6 "Courier New",monospace; }
    .stat b { color:var(--teal); font-size:15px; }
    .scroll-hint { position:absolute; bottom:38px; color:var(--ink-dim); font:11px/1 "Courier New",monospace; letter-spacing:.1em; animation:pulse 2s ease-in-out infinite; }
    .spacer { height:14vh; }
    #outro { align-items:center; text-align:center; }
    #outro > div { max-width:52ch; }
    #outro h2 { max-width:none; }
    #outro .cta { pointer-events:auto; display:inline-block; margin-top:8px; padding:13px 26px; border:1px solid var(--teal); color:var(--teal); font:12px/1 "Courier New",monospace; letter-spacing:.1em; text-decoration:none; text-transform:uppercase; transition:background .2s,color .2s; }
    #outro .cta:hover { background:var(--teal); color:var(--bg); }
    @keyframes pulse { 50% { opacity:.45; } }
    @media (max-width:680px) { .scene { min-height:92vh; padding:96px 58px 80px 26px; } #scalebar .track { height:230px; } .site-nav { padding:18px 22px; } .spacer { height:7vh; } }
    @media (prefers-reduced-motion:reduce) { #canvas-holder,#scalebar { display:none; } .scene { min-height:auto; padding:100px 8vw; } .spacer { display:none; } .scroll-hint { display:none; } }
  </style>
</head>
<body>
  <nav class="site-nav" aria-label="CV navigation"><a href="index.html">← About</a><a href="assets/pdf/CV_Amir_Amanzadi.pdf" target="_blank" rel="noopener">Download CV ↗</a></nav>
  <div id="canvas-holder" aria-hidden="true"></div>
  <aside id="scalebar" aria-label="Career scale"><div class="marks" id="marks"><span>Å</span><span>nm</span><span>μm</span><span>mm</span><span>cm</span><span>km</span><span>∞</span></div><div class="track"><div class="fill" id="fill"></div></div></aside>
  <main>
    <section class="scene" id="hero"><div><div class="eyebrow">A career, zoomed out</div><h1>Zooming Out</h1><p>Scroll from a single molecule to half a million people. Each scale below is a real chapter, in order.</p><span class="scroll-hint">↓ scroll to begin</span></div></section><div class="spacer"></div>
    <section class="scene"><div><div class="eyebrow">Å · molecules</div><h2>Where it started</h2><p>Chemistry and mechanical engineering at Sharif. A peptide designed for metal chelation and Aβ inhibition. A bio-compatible hydrogel for wound healing.</p><div class="stat"><b>2</b> published papers before graduating</div></div></section><div class="spacer"></div>
    <section class="scene"><div><div class="eyebrow">nm · proteins</div><h2>Targets, not guesses</h2><p>At Celeris Therapeutics, geometric deep learning to predict which protein interactions could be targeted for degradation. In-silico screening against alpha-synuclein for Parkinson's disease.</p><div class="stat">A <b>patented</b> candidate, now in lead optimization</div></div></section><div class="spacer"></div>
    <section class="scene"><div><div class="eyebrow">μm · cells &amp; genes</div><h2>Where AI entered</h2><p>Graph representation learning for drug combinations at Karolinska Institutet. Few-shot models for early detection of Ataxia-Telangiectasia from genetic profiles.</p><div class="stat">Graph neural networks became the <b>through-line</b> of everything after</div></div></section><div class="spacer"></div>
    <section class="scene"><div><div class="eyebrow">mm · tissue &amp; organ</div><h2>From model to patient</h2><p>The DECISION EU project at Karolinska University Hospital. Multi-omic modeling across three cohorts of decompensated cirrhosis patients.</p><div class="stat"><b>2,500+</b> patients, 3 treatments now in phase II trials</div></div></section><div class="spacer"></div>
    <section class="scene"><div><div class="eyebrow">cm · brain</div><h2>The current chapter</h2><p>Doctoral Research Fellow at the Centre for Precision Psychiatry, University of Oslo. Multi-omics and agentic AI for psychiatric and neurological disease.</p><div class="stat">Where every earlier scale <b>converges</b></div></div></section><div class="spacer"></div>
    <section class="scene"><div><div class="eyebrow">km · population</div><h2>Half a million people</h2><p>A metabolome-wide association study of psychotic experiences across UK Biobank. Molecular signals, connected to outcomes, at population scale.</p><div class="stat"><b>490,000</b> participants, one dataset</div></div></section><div class="spacer"></div>
    <section class="scene" id="outro"><div><div class="eyebrow">∞ · the distant dream</div><h2>A digital twin</h2><p>A real-time biological runtime of human physiology, across every scale, in both space and time. We are nowhere near it. It still seems worth working toward.</p><a class="cta" href="assets/pdf/CV_Amir_Amanzadi.pdf" target="_blank" rel="noopener">See the full CV ↗</a></div></section>
  </main>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script>
    (() => {
      if (matchMedia("(prefers-reduced-motion: reduce)").matches || !window.WebGLRenderingContext) return;
      const scene = new THREE.Scene();
      scene.fog = new THREE.FogExp2(0x05080d, .026);
      const camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, .1, 300);
      const renderer = new THREE.WebGLRenderer({ antialias:true, alpha:true });
      renderer.setPixelRatio(Math.min(devicePixelRatio, innerWidth < 680 ? 1.25 : 2));
      renderer.setSize(innerWidth, innerHeight);
      document.getElementById("canvas-holder").appendChild(renderer.domElement);
      scene.add(new THREE.AmbientLight(0x2a3644, 1.35));
      const key = new THREE.PointLight(0x4fd1c5, 2.5, 80); key.position.set(6, 6, 10); scene.add(key);
      const rim = new THREE.PointLight(0x6ea8ff, 1, 80); rim.position.set(-8, -4, -6); scene.add(rim);
      const groups = [], materials = [];
      const material = (color = 0x4fd1c5, emissive = 0x0d3330) => { const value = new THREE.MeshStandardMaterial({ color, emissive, metalness:.25, roughness:.38, transparent:true }); materials.push(value); return value; };
      const wire = () => { const value = new THREE.MeshBasicMaterial({ color:0x6ea8ff, wireframe:true, transparent:true, opacity:.16 }); materials.push(value); return value; };
      const dim = () => { const value = new THREE.MeshStandardMaterial({ color:0x2a3644, roughness:.65, transparent:true }); materials.push(value); return value; };
      const register = (group) => { groups.push(group); scene.add(group); return group; };
      const setOpacity = (group, opacity) => group.traverse((node) => { if (!node.material) return; const list = Array.isArray(node.material) ? node.material : [node.material]; list.forEach((value) => { value.opacity = opacity * (value.userData.baseOpacity || 1); value.visible = opacity > .01; }); });

      const molecule = register(new THREE.Group());
      const atomGeo = new THREE.SphereGeometry(.34, 20, 20), bondGeo = new THREE.CylinderGeometry(.045, .045, 1, 8);
      const points = [[0,0,0],[1.35,.6,.3],[-1.2,.8,-.4],[.55,-1.25,.5],[-.9,-1,.6],[2.05,-.4,-.6],[-2,-.2,.8],[.2,1.55,-.7]];
      points.forEach((point, index) => { const atom = new THREE.Mesh(atomGeo, material(index % 3 === 0 ? 0x6ea8ff : 0x4fd1c5)); atom.position.set(...point); atom.scale.setScalar(index ? .82 : 1.3); molecule.add(atom); });
      [[0,1],[0,2],[0,3],[0,4],[1,5],[2,6],[0,7]].forEach(([from,to]) => { const a = new THREE.Vector3(...points[from]), b = new THREE.Vector3(...points[to]), direction = b.clone().sub(a), bond = new THREE.Mesh(bondGeo, dim()); bond.scale.y = direction.length(); bond.position.copy(a).addScaledVector(direction, .5); bond.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), direction.normalize()); molecule.add(bond); });

      const protein = register(new THREE.Group());
      const foldPoints = Array.from({ length:34 }, (_, index) => { const t = index / 33 * Math.PI * 5; return new THREE.Vector3(Math.sin(t) * (1.65 + .25 * Math.cos(t * 2)), Math.cos(t * 1.7) * 1.2, Math.cos(t) * (1.65 + .25 * Math.sin(t * 3))); });
      const fold = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(foldPoints, true, "centripetal"), 240, .19, 10, true);
      protein.add(new THREE.Mesh(fold, material())); protein.add(new THREE.Mesh(fold, wire()));

      const dna = register(new THREE.Group()), dnaAtom = new THREE.SphereGeometry(.14, 10, 10);
      for (let index = 0; index < 30; index++) { const t = index / 29, angle = t * Math.PI * 6, y = (t - .5) * 10, x = Math.cos(angle) * 1.7, z = Math.sin(angle) * 1.7; const a = new THREE.Mesh(dnaAtom, material()), b = new THREE.Mesh(dnaAtom, material(0x6ea8ff, 0x142033)); a.position.set(x,y,z); b.position.set(-x,y,-z); dna.add(a,b); if (index % 2 === 0) { const rung = new THREE.Mesh(new THREE.CylinderGeometry(.025,.025,3.4,6), dim()); rung.position.y = y; rung.rotation.z = Math.PI / 2; rung.rotation.y = -angle; dna.add(rung); } }

      const organ = register(new THREE.Group());
      [[0,0,0,2.2,1.2,.85],[1.25,.25,.25,1.45,.85,.7],[-1.45,-.2,.15,1.2,.75,.65]].forEach(([x,y,z,sx,sy,sz]) => { const shape = new THREE.SphereGeometry(1, 32, 24), mesh = new THREE.Mesh(shape, material()); mesh.position.set(x,y,z); mesh.scale.set(sx,sy,sz); organ.add(mesh); const outline = new THREE.Mesh(shape, wire()); outline.position.copy(mesh.position); outline.scale.copy(mesh.scale); organ.add(outline); });

      const brain = register(new THREE.Group());
      [-1,1].forEach((side) => { const shape = new THREE.SphereGeometry(1.55, 32, 24), position = shape.attributes.position; for (let index = 0; index < position.count; index++) { const x = position.getX(index), y = position.getY(index), z = position.getZ(index), noise = (Math.sin(x * 5) + Math.cos(y * 4) + Math.sin(z * 6)) * .045; position.setXYZ(index, x * (1 + noise), y * (1 + noise), z * (1 + noise)); } shape.computeVertexNormals(); const lobe = new THREE.Mesh(shape, material(0x4fd1c5, 0x123c38)); lobe.position.x = side * .88; lobe.scale.set(1, .92, 1.08); brain.add(lobe); const outline = new THREE.Mesh(shape, wire()); outline.position.copy(lobe.position); outline.scale.copy(lobe.scale); brain.add(outline); });

      const population = register(new THREE.Group()), populationCount = innerWidth < 680 ? 900 : 2400, populationGeometry = new THREE.BufferGeometry(), populationPositions = new Float32Array(populationCount * 3);
      for (let index = 0; index < populationCount; index++) { const radius = 7 + Math.random() * 2, theta = Math.random() * Math.PI * 2, phi = Math.acos(2 * Math.random() - 1); populationPositions[index*3] = radius * Math.sin(phi) * Math.cos(theta); populationPositions[index*3+1] = radius * Math.sin(phi) * Math.sin(theta); populationPositions[index*3+2] = radius * Math.cos(phi); }
      populationGeometry.setAttribute("position", new THREE.BufferAttribute(populationPositions, 3)); const populationMaterial = new THREE.PointsMaterial({ color:0x4fd1c5, size:.085, transparent:true, blending:THREE.AdditiveBlending }); materials.push(populationMaterial); population.add(new THREE.Points(populationGeometry, populationMaterial));

      const twin = register(new THREE.Group()), twinMaterial = material(0x4fd1c5, 0x1f5a54), addPart = (geometry, x, y, z, scale = [1,1,1], rotation = 0) => { const part = new THREE.Mesh(geometry, twinMaterial); part.position.set(x,y,z); part.scale.set(...scale); part.rotation.z = rotation; twin.add(part); };
      addPart(new THREE.SphereGeometry(.5,20,20),0,3.35,0); addPart(new THREE.CapsuleGeometry(.65,2.1,4,12),0,1.6,0); addPart(new THREE.CapsuleGeometry(.19,1.7,4,8),-1,1.85,0,[1,1,1],.35); addPart(new THREE.CapsuleGeometry(.19,1.7,4,8),1,1.85,0,[1,1,1],-.35); addPart(new THREE.CapsuleGeometry(.24,1.9,4,8),-.38,-.65,0); addPart(new THREE.CapsuleGeometry(.24,1.9,4,8),.38,-.65,0);

      const stars = new THREE.Group(), starCount = 700, starGeometry = new THREE.BufferGeometry(), starPositions = new Float32Array(starCount * 3);
      for (let index = 0; index < starCount; index++) { starPositions[index*3] = (Math.random() - .5) * 90; starPositions[index*3+1] = (Math.random() - .5) * 90; starPositions[index*3+2] = (Math.random() - .5) * 90 - 20; }
      starGeometry.setAttribute("position", new THREE.BufferAttribute(starPositions, 3)); stars.add(new THREE.Points(starGeometry, new THREE.PointsMaterial({ color:0x1c2733, size:.08 }))); scene.add(stars);
      groups.forEach((group) => setOpacity(group, 0));

      const waypoints = [[0,.5,15],[1.6,.3,5],[0,.3,6.5],[2.4,0,7.5],[-1,.6,7],[0,0,5.5],[0,0,15],[0,.5,8.5]].map((point) => new THREE.Vector3(...point));
      const marks = [...document.querySelectorAll("#marks span")], fill = document.getElementById("fill"), target = new THREE.Vector3();
      const progress = () => Math.min(Math.max(scrollY / Math.max(document.documentElement.scrollHeight - innerHeight, 1), 0), 1) * 7;
      const update = () => { const t = progress(), index = Math.min(Math.floor(t), 6), local = t - index; camera.position.lerpVectors(waypoints[index], waypoints[index + 1], local); camera.lookAt(0,0,0); fill.style.height = `${t / 7 * 100}%`; marks.forEach((mark, markIndex) => mark.classList.toggle("active", markIndex === Math.min(Math.max(Math.round(t) - 1, 0), 6))); groups.forEach((group, groupIndex) => setOpacity(group, Math.max(0, 1 - Math.abs(t - (groupIndex ? groupIndex + 1 : .75)) / 1.15))); };
      const clock = new THREE.Clock();
      const animate = () => { requestAnimationFrame(animate); const delta = clock.getDelta(); stars.rotation.y += .0002; molecule.rotation.y += .05 * delta; protein.rotation.y += .15 * delta; dna.rotation.y += .08 * delta; organ.rotation.y += .06 * delta; brain.rotation.y += .05 * delta; population.rotation.y += .02 * delta; twin.rotation.y += .1 * delta; renderer.render(scene, camera); };
      addEventListener("scroll", update, { passive:true }); addEventListener("resize", () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setPixelRatio(Math.min(devicePixelRatio, innerWidth < 680 ? 1.25 : 2)); renderer.setSize(innerWidth, innerHeight); }); update(); animate();
    })();
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
