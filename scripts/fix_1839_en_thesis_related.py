#!/usr/bin/env python3
"""Durable EN fix for the 1839-era photographer pages (and the all-movements
contamination found elsewhere).

What it does — edits data/photographers-en-content.json ONLY (the source the
allowed EN builder build_photographers_en.py reads). It does NOT touch the JA
HTML (already source-of-truth) and does NOT run the forbidden JA generator.

1. thesis_html: set the English "What this photographer changed" text for the
   10 1839 pages that carry a JA thesis. (daguerre/beato/brady have no JA
   thesis and are intentionally left as None.)
2. site_directory_html for the 13 1839 pages: rebuilt from each JA page's
   §REL section so EN Related photographers / movements mirror JA exactly.
3. site_directory_html for the non-1839 pages contaminated with the full
   31-movement dropdown: strip the bogus "Related movements" group, keep the
   harvested "Related people" group.

Re-runnable / idempotent. After running, regenerate the affected EN pages with
build_photographers_en.py --slug ... then link_country_keywords.py.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from build_photographers_en import translate_movement_name  # noqa: E402

CONTENT_JSON = os.path.join(ROOT, 'data', 'photographers-en-content.json')
JA_DIR = os.path.join(ROOT, 'photographers')
EN_DIR = os.path.join(ROOT, 'en', 'photographers')
EN_MOV_DIR = os.path.join(ROOT, 'en', 'movements')

# ── EN thesis text (mirrors the JA ph-thesis__body; single <em>; follows the
#    CLAUDE.md thesis 断定度 rules — no perfected/definitive/the only/etc.) ──
THESIS_EN = {
    'talbot': (
        "Talbot invented the calotype, a negative–positive process, and "
        "introduced the principle of <em>photographic reproducibility</em> into "
        "the history of the medium. Where the daguerreotype was a unique, "
        "unrepeatable object, Talbot's process allowed any number of positive "
        "prints from a single negative, laying the foundation for the "
        "reproductive logic that would later underpin twentieth-century "
        "magazines, newspapers, books, and advertising. With “The Pencil "
        "of Nature” (1844–46) he realized the first commercially "
        "published, photographically illustrated book, showing that photography "
        "could function at once as record, art, and reproduction. His strict "
        "management of patents ironically slowed the spread of his methods, yet "
        "in conceptual and technical reach his contribution extends across "
        "twentieth-century photographic culture."
    ),
    'fenton': (
        "Fenton's photographs of the Crimean War are recorded as the first "
        "large-scale, organized instance of photography carried onto a "
        "battlefield. Made under a publisher's instruction not to photograph the "
        "dead, the work introduced into the history of the medium the problem "
        "that a photograph's meaning is shaped <em>not by what it shows but by "
        "what it withholds</em>. Together with his part in founding the Royal "
        "Photographic Society in 1853, Fenton embodies a moment in 1850s Britain "
        "in which the institutional, commercial, and political uses of "
        "photography intersected."
    ),
    'nadar': (
        "Nadar deliberately stripped away the markers of social rank — "
        "opulent backdrops, props, and costumes — that had governed portrait "
        "staging, working instead with a plain grey ground and natural light to "
        "draw out the sitter's inner presence, an <em>aesthetic reorientation of "
        "portrait photography</em>. This approach lay at the heart of "
        "photography's adoption as a means of visually fixing individual "
        "identity. His balloon-borne aerial photographs of 1858 and his "
        "electric-light photographs made underground in 1861 are recorded as "
        "technical experiments showing that photography could work beyond the "
        "constraints of available light, gravity, and space."
    ),
    'legray': (
        "Le Gray addressed one of photography's basic technical limits — the "
        "difference in exposure between sky and sea — through combination "
        "printing from multiple negatives, leaving works that continue to pose "
        "<em>the boundary between “truth” and “manipulation” in "
        "photography</em>. His refinement of the waxed-paper negative made "
        "outdoor work practical, and his teaching of successors such as Nadar "
        "helped form the technical ground of French photographic expression in "
        "the 1850s. The arc from his later obscurity to a market-driven "
        "reappraisal in the late twentieth century is still cited by researchers "
        "as emblematic of how nineteenth-century photographic history has been "
        "reorganized."
    ),
    'cameron': (
        "Cameron drew portraiture away from the recording of appearance and "
        "toward images charged with emotion, faith, and literary imagination. By "
        "treating soft focus, extreme closeness, and the material unevenness of "
        "the wet-plate process not as flaws to be eliminated but as means of "
        "bringing out the sitter's inner life, she showed at an early date that "
        "photography could engage <em>staging and emotional intensity</em> as "
        "well as visual precision. Against a contemporary standard that prized "
        "technical sharpness, she raised the question of what photography should "
        "strive for within the works themselves, widening through practice the "
        "range of expressive possibility that later Pictorialism would take up "
        "as a shared concern."
    ),
    'david-octavius-hill': (
        "Hill is regarded as the first substantial practitioner to use "
        "photography deliberately not as a means of record but as a field of "
        "pictorial composition. His tonal handling, drawing on Rembrandt's "
        "prints, together with his active reframing of the calotype's supposed "
        "“inferiority” as an artistic quality, opened in the early "
        "nineteenth century a way of <em>rethinking the relationship between "
        "photography and art</em>. His series of Newhaven fishermen, among the "
        "first organized records of a specific social group, is positioned as a "
        "forerunner of later documentary photography."
    ),
    'robert-adamson': (
        "Adamson worked as the <em>technical interpreter</em> who translated his "
        "collaborator's pictorial intentions into the material qualities of the "
        "calotype — its brown tonality, matte surface, and light-absorbing "
        "texture. His chain of decisions about paper, exposure, development, and "
        "print tone directly determined the visual character of the finished "
        "image, and later researchers have noted that he was a co-author of the "
        "work rather than a mere operator. In a working life of only about five "
        "years, ended by his death at twenty-six or twenty-seven, he left some "
        "three thousand images to which the history of photography repeatedly "
        "returns."
    ),
    'nicephore-niepce': (
        "Niépce was the first to demonstrate the principle of fixing the "
        "fleeting image projected by the camera obscura permanently onto a "
        "material support through a photochemical reaction. “View from the "
        "Window at Le Gras” (about 1826–27) is positioned as the first "
        "instance of a real scene inscribed directly by light without the "
        "intervention of the hand, at the conceptual origin of photography. "
        "Largely overlooked at the official announcement of 1839, he has been "
        "reassessed — through Gernsheim's rediscovery of the plate in 1952 "
        "and subsequent scholarship — as the first to achieve the "
        "<em>photochemical fixing of an image</em> that lies at the core of the "
        "medium. As his research partnership with Daguerre suggests, his method "
        "also formed a technical bridge toward the daguerreotype, placing the "
        "origin of photography's invention where several contributors overlap."
    ),
    'alexander-gardner': (
        "Through his records of the Civil War, Gardner brought the notion of "
        "<em>the photographer's individual authorship</em> into documentary "
        "photography. By making visible the names of photographers that had been "
        "absorbed under Brady's studio imprint — crediting eleven individual "
        "operators in his 1865–66 Sketch Book — he made one of the first "
        "institutional attempts to attribute photographic making and "
        "responsibility to specific people. His public exhibition of the "
        "Antietam dead showed that photography could mediate the reality of the "
        "battlefield to civil society, and the controversy over the staging of "
        "“Home of a Rebel Sharpshooter” inscribed the question of "
        "photographic testimony and ethics into the history of the medium."
    ),
    'timothy-osullivan': (
        "Across two bodies of work — war photography and geological survey "
        "photography — O'Sullivan built up a <em>visual language of "
        "directness that does not depend on staging or on conventions of the "
        "sublime</em>. “A Harvest of Death” records the war dead amid "
        "fog in a plain, uninflected manner, while his views of the tufa domes "
        "present a desolate terrain without lyricizing it. Having died without "
        "fame in his lifetime, he was rediscovered in the 1975 New Topographics "
        "exhibition as a predecessor of photographers such as Robert Adams "
        "— a clear example of how the history of photography is shaped by "
        "retrospective reassessment."
    ),
}

# 13 registered 1839-era photographers (EN file keys == JA file keys here)
ERA_1839 = [
    'daguerre', 'talbot', 'fenton', 'beato', 'nadar', 'legray', 'brady',
    'cameron', 'david-octavius-hill', 'robert-adamson', 'nicephore-niepce',
    'alexander-gardner', 'timothy-osullivan',
]

# Non-1839 pages whose harvested site_directory_html carries the full 31-movement
# dropdown as "Related movements" (their JA §REL is 準備中: keep people, drop movs)
CONTAMINATED_NON_1839 = [
    'daisuke-yokota', 'hachiro-suzuki', 'kohei-yasu', 'lieko-shiga', 'marey',
    'muybridge', 'norihiko-matsumoto', 'robert-adams', 'robert-doisneau',
    'yokoyama-matsusaburo', 'yurie-nagashima',
]

GROUP_RE = re.compile(
    r'<div class="site-directory-group site-directory-group-contextual">'
    r'(.*?)</div>\s*</div>', re.S)
LABEL_RE = re.compile(r'<div class="site-directory-label">([^<]+)</div>')


def card_name_map():
    cd = json.load(open(os.path.join(ROOT, 'card-data.json'), encoding='utf-8'))
    return {p['id']: p.get('nameEn', '') for p in cd['photographers']}


def parse_ja_rel(ja_id):
    """Return (people, movements) from a JA page's §REL section.
    people = [(photographer_id, ja_name)], movements = [(ja_slug_name, ja_name)]."""
    path = os.path.join(JA_DIR, ja_id + '.html')
    html = open(path, encoding='utf-8').read()
    m = re.search(r'§ REL</span>.*?<div class="ph-section__body">(.*?)</div>\s*</section>',
                  html, re.S)
    if not m:
        return [], []
    body = m.group(1)
    people = [(href.split('/')[-1].replace('.html', ''), name)
              for href, name in re.findall(r'<a href="(/photographers/[^"]+)">([^<]+)</a>', body)]
    movements = re.findall(r'<a href="/movements/([^"]+)\.html">([^<]+)</a>', body)
    return people, movements


def build_site_directory(people_links, movement_links):
    parts = ['<nav class="site-directory-links" aria-label="Site links" data-nosnippet>']
    if people_links:
        items = ''.join(f'<a href="/en/photographers/{pid}.html">{name}</a>'
                        for pid, name in people_links)
        parts.append('        <div class="site-directory-group site-directory-group-contextual">')
        parts.append('          <div class="site-directory-label">Related people &amp; photographers</div>')
        parts.append(f'          <div class="site-directory-items">{items}</div>')
        parts.append('        </div>')
    if movement_links:
        items = ''.join(f'<a href="/en/movements/{slug}.html">{name}</a>'
                        for slug, name in movement_links)
        parts.append('        <div class="site-directory-group site-directory-group-contextual">')
        parts.append('          <div class="site-directory-label">Related movements</div>')
        parts.append(f'          <div class="site-directory-items">{items}</div>')
        parts.append('        </div>')
    parts.append('      </nav>')
    return '\n'.join(parts)


def strip_movements_group(sd_html):
    """Remove the 'Related movements' contextual group; keep everything else."""
    def repl(m):
        lbl = LABEL_RE.search(m.group(1))
        if lbl and lbl.group(1).strip().startswith('Related movements'):
            return ''
        return m.group(0)
    out = GROUP_RE.sub(repl, sd_html)
    # tidy any doubled blank lines left behind
    out = re.sub(r'\n\s*\n\s*\n', '\n', out)
    return out


def main():
    names = card_name_map()
    content = json.load(open(CONTENT_JSON, encoding='utf-8'))
    pages = content['pages']
    report = []

    # 1 + 2 — 1839 pages: thesis + related rebuilt from JA
    for pid in ERA_1839:
        key = pid + '.html'
        page = pages.get(key)
        if page is None:
            report.append(f'!! {pid}: no JSON entry')
            continue
        # thesis
        if pid in THESIS_EN:
            page['thesis_html'] = THESIS_EN[pid]
        # related from JA §REL
        ja_people, ja_movs = parse_ja_rel(pid)
        people_links = []
        for rid, _ja in ja_people:
            if not os.path.exists(os.path.join(EN_DIR, rid + '.html')):
                report.append(f'   {pid}: skip person (no EN page): {rid}')
                continue
            en_name = names.get(rid)
            if not en_name:
                report.append(f'   {pid}: skip person (no nameEn): {rid}')
                continue
            people_links.append((rid, en_name))
        movement_links = []
        for ja_slug, ja_name in ja_movs:
            en_name, slug = translate_movement_name(ja_name)
            if not slug or not os.path.exists(os.path.join(EN_MOV_DIR, slug + '.html')):
                report.append(f'   {pid}: skip movement (no EN page): {ja_name}')
                continue
            movement_links.append((slug, en_name))
        page['site_directory_html'] = build_site_directory(people_links, movement_links)
        report.append(f'OK {pid}: thesis={"yes" if pid in THESIS_EN else "no"} '
                      f'people={len(people_links)} movements={len(movement_links)}')

    # 3 — contaminated non-1839 pages: drop bogus Related movements only
    for pid in CONTAMINATED_NON_1839:
        key = pid + '.html'
        page = pages.get(key)
        if page is None:
            report.append(f'!! {pid}: no JSON entry')
            continue
        sd = page.get('site_directory_html') or ''
        before = len(re.findall(r'/en/movements/', sd))
        page['site_directory_html'] = strip_movements_group(sd)
        after = len(re.findall(r'/en/movements/', page['site_directory_html']))
        people = len(re.findall(r'/en/photographers/', page['site_directory_html']))
        report.append(f'OK {pid}: stripped movements {before}->{after} (kept people={people})')

    with open(CONTENT_JSON, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    print('\n'.join(report))


if __name__ == '__main__':
    main()
