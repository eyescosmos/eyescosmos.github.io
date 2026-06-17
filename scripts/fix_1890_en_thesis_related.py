#!/usr/bin/env python3
"""Durable EN fix for the 1890-era photographer pages.

What it does — edits data/photographers-en-content.json ONLY (the source the
allowed EN builder build_photographers_en.py reads). It does NOT touch the JA
HTML (already source-of-truth) and does NOT run the forbidden JA generator.

1. thesis_html: set the English "What this photographer changed" text for all
   14 target pages.
2. site_directory_html: rebuilt from each JA page's §REL section so EN
   Related photographers / movements mirror JA exactly.
3. sections[0].body_html for emerson: full English translation of the JA §01
   essay (5 h3 headings + 12 sup-ref citations).
4. sources_html for emerson: 12 sources in cite-item format.
5. cite_ids / supref_ids for emerson.

Re-runnable / idempotent. After running, regenerate the affected EN pages with
build_photographers_en.py --slug ... then link_country_keywords.py.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from build_photographers_en import translate_movement_name, build_jp_slug_map, load_classification  # noqa: E402

CONTENT_JSON = os.path.join(ROOT, 'data', 'photographers-en-content.json')
JA_DIR = os.path.join(ROOT, 'photographers')
EN_DIR = os.path.join(ROOT, 'en', 'photographers')
EN_MOV_DIR = os.path.join(ROOT, 'en', 'movements')

# ── EN thesis text ─────────────────────────────────────────────────────────
# Follows CLAUDE.md断定度 rules: no perfected/definitive/the only/the true/
# culmination/pinnacle. Single <em>…</em> for the most important phrase.
THESIS_EN = {
    'emerson': (
        "Emerson was <em>the first photographer to argue systematically that "
        "photography deserved to be considered an independent art on the basis "
        "of human visual physiology rather than as an imitation of painting</em>. "
        "His 1889 theoretical treatise and the series of Norfolk Broads "
        "photobooks functioned as a sustained critique of the combination "
        "printing and painterly staging that dominated the era, and the "
        "questions he raised — about what photography should strive for and on "
        "what grounds its artistic claims rest — fed into the debates that "
        "later carried through Stieglitz's Photo-Secession and on to the "
        "straight photography theories of Strand and Weston."
    ),
    'kasebier': (
        "Drawing on a training in painting, Käsebier transplanted a developed "
        "sense of light and composition into portrait photography, demonstrating "
        "from <em>a position that straddled commercial studio practice and the "
        "artistic photography movement</em> that the medium could carry "
        "deliberate aesthetic intent. As a co-founder of the Photo-Secession "
        "with Stieglitz, and through participation in Camera Work, she helped "
        "build the institutional structures of early twentieth-century art "
        "photography from the inside. Work centered on maternity, faith, and "
        "individual character was undervalued until feminist art-historical "
        "scholarship recovered it; it is now held in major collections as a "
        "pioneering practice in the possibilities of portrait photography."
    ),
    'steichen': (
        "Steichen demonstrated the pictorial techniques of Pictorialism, "
        "co-founded the Photo-Secession, and then made a radical shift in his "
        "own position. <em>After his experience in aerial reconnaissance "
        "photography during the First World War</em>, his skepticism toward "
        "\"photographs that look like paintings\" deepened; commercial work "
        "for Condé Nast developed the possibilities of straight photography "
        "while reaching mass audiences. As director of MoMA's photography "
        "department, he organized The Family of Man exhibition, demonstrating "
        "that photography could function as a medium shared between the "
        "institution and the public. His trajectory — moving between "
        "Pictorialism and Modernism, art photography and commercial photography, "
        "maker and institutional builder — is singular in photographic history."
    ),
    'demachy': (
        "Through his exploration and theoretical advocacy of alternative "
        "processes — gum bichromate, oil print, photogravure-aquatint — "
        "Demachy introduced into photographic debate the proposition that "
        "<em>the photographer's manual intervention is what makes photography "
        "art</em>. His systematic argument for a manipulative approach in "
        "opposition to photographic realism is still cited as an early "
        "articulation of the tension between photography's indexical character "
        "and its claims to artistic expression. Working as a wealthy amateur "
        "unconstrained by commercial pressures, he contributed to Camera Work "
        "and international art-photography networks, helping to form the "
        "intellectual connections between Paris and New York."
    ),
    'eugene-atget': (
        "Atget set out with the practical aim of supplying \"documents for "
        "artists\", and yet in systematically recording the alleys, shopfronts, "
        "and shuttered houses of a disappearing Paris he arrived at "
        "<em>a place where the boundary between \"document\" and \"expression\" "
        "in photography is put in question</em>. His work reached twentieth-"
        "century photography through the Surrealists' reappraisal and Berenice "
        "Abbott's preservation and presentation, connecting into the documentary "
        "methodology carried forward by Walker Evans and others."
    ),
    'lewis-hine': (
        "Hine did not leave his photographs as appeals to emotion alone: by "
        "combining them with field-note data he organized photography into "
        "<em>investigative material that could function as legislative evidence</em>. "
        "From his records at Ellis Island to his cross-country survey of child "
        "labor, his methodology established a practical foundation for social "
        "documentary that was taken up by Dorothea Lange, Walker Evans, and "
        "others in the FSA photography program."
    ),
    'jacques-henri-lartigue': (
        "Lartigue spent a childhood making snapshots focused exclusively on "
        "capturing movement and the instant, demonstrating that "
        "<em>an amateur's private way of seeing can carry photographic-historical "
        "value distinct from documentary practice</em>. His \"discovery\" by "
        "MoMA in 1963 is cited critically in photographic history as a case "
        "showing how photographic legitimacy is reconstituted through "
        "institutional evaluation."
    ),
    'paul-geniaux': (
        "Geniaux recorded the street-trade workers (petits métiers) of Paris "
        "around 1900 and documented both the traditional agricultural and "
        "fishing life of Brittany and the modernizing city from "
        "<em>a perspective that moved between two places — rural region and "
        "metropolitan centre</em>. His inclusion alongside Atget and Louis Vaire "
        "in ICP exhibitions reframes the street photography of 1900s Paris not "
        "as the product of a single mythologized figure but as a practice "
        "carried out by multiple photographers."
    ),
    'louis-vaire': (
        "As an amateur associated with the Société Française de Photographie, "
        "Vaire recorded the street workers of Paris between 1900 and 1906, "
        "<em>treating individuals and their specific movements rather than "
        "social types</em>. His inclusion alongside Atget and Geniaux in ICP "
        "exhibitions opened a way of reconstructing 1900s Paris street "
        "photography as a practice with multiple contributors, rather than a "
        "history organized around Atget alone."
    ),
    'edward-weston': (
        "Weston moved away from the pictorial decoration of Pictorialism and, "
        "using the precise descriptive capacity of a large-format camera and "
        "extreme close focus, treated shells, vegetables, nudes, and rock "
        "formations as variations on the same formal problem, demonstrating in "
        "practice that <em>photography is a medium for re-reading the structure "
        "of the world rather than for reproducing appearances</em>. By "
        "organizing Group f/64 he positioned straight photography at the core "
        "of West Coast Modernism, and the approach — extended through his "
        "Mexican experience to landscape — has remained a point of reference "
        "for photographers who followed."
    ),
    'kajima-seibei': (
        "Kajima Seibei invested his wealth and time not in making photographs "
        "himself but in building the conditions for photography — founding a "
        "domestic dry-plate company, organizing the Japan Photographic Society, "
        "and running the Genrokukan studio — and through these activities "
        "<em>helped lay the institutional foundations of the Meiji-era "
        "photographic world</em>. His case shows that photography's "
        "establishment also required patrons who treated the medium as an "
        "industrial and social infrastructure rather than as a personal "
        "artistic practice."
    ),
    'koreaki-kamei': (
        "Kamei organized a team to photograph the Sino-Japanese War and "
        "compiled more than three hundred photographs into the album "
        "\"Meiji Twenty-Seven and Eight Year Campaign Photographs,\" submitted "
        "to the imperial court, thereby <em>pioneering the institutionalization "
        "of organized war photography in Japan</em>. This stands as an early "
        "Meiji photographic history example of photography being made to "
        "function as a national visual document beyond individual recording "
        "activity."
    ),
    'kohei-yasu': (
        "Born in late Edo-period Japan, Yasu traveled to Guatemala in Central "
        "America, opened the \"Fotografía Japonesa\" studio, and sustained a "
        "photographic practice rooted in local society for nearly forty years, "
        "providing through surviving photographs the earliest documented "
        "evidence that <em>Japanese photographers' activity could reach an "
        "international range not limited to Asia and the Pacific</em>."
    ),
    'ryuzo-torii': (
        "Torii taught himself the methods of fieldwork and left approximately "
        "2,500 glass-plate photographs made in Taiwan, Korea, Manchuria, "
        "Okinawa, and Ainu territories, becoming one of the earliest Japanese "
        "researchers to <em>use photography systematically as a medium for "
        "anthropological record</em>. That body of work is today also cited as "
        "primary material subject to critical examination as a visual apparatus "
        "of imperial knowledge production."
    ),
}

# ── Emerson EN essay body ─────────────────────────────────────────────────
EMERSON_BODY_HTML = """\
<h3 id="h3-01">Early life and the turn to photography</h3>
<p>Emerson was born on 13 May 1856 in Cuba. After a childhood spent in Cuba and the United States, he moved to England in his teens and later took a medical degree at Cambridge. He is said to have begun photographing around 1882, and his medical and scientific training fed directly into the visual theory he later developed.<sup class="sup-ref"><a href="#cite-6">*6</a></sup></p>

<h3 id="h3-02">The Norfolk Broads photobooks</h3>
<p>Emerson's practical starting point was the rural landscape and wetlands of Norfolk in eastern England. The 1886 photobook <em>Life and Landscape on the Norfolk Broads</em>, made with T. F. Goodall, contained forty platinum prints and was issued in a limited edition of two hundred copies.<sup class="sup-ref"><a href="#cite-7">*7</a></sup> The 1888 follow-up <em>Pictures of East Anglian Life</em> gathered thirty-two photogravures and was highly regarded as a record of the labor and everyday life of farmers and fishermen captured in natural compositions.<sup class="sup-ref"><a href="#cite-8">*8</a></sup> In 1890 Emerson selected ten photographs from this book to form a portfolio, which he donated to every photographic society in the country as a way of disseminating his theory and practice.<sup class="sup-ref"><a href="#cite-9">*9</a></sup></p>

<h3 id="h3-03">Visual physiology and the theory of differential focus</h3>
<p>Emerson's grounds for criticizing studio arrangement as "dishonest" and insisting on single-negative, single-exposure photography as a condition for art were drawn from the visual physiology of the German physiologist Hermann von Helmholtz. Helmholtz had established that only the fovea centralis sees sharply while the peripheral visual field is automatically softened, and Emerson applied this theory to photography in his 1889 book <em>Naturalistic Photography for Students of the Art</em>.<sup class="sup-ref"><a href="#cite-1">*1</a></sup> His "differential focus" method — keeping the principal subject sharp while softening the surroundings slightly — was the logic he offered for the claim that this was the approach most faithful to human vision and therefore possessed artistic value. The philosophical basis was Herbert Spencer's evolutionary psychology — the position that "the mind passively receives external stimuli" — and he argued that the optical process of the camera could scientifically reproduce human perception.<sup class="sup-ref"><a href="#cite-2">*2</a></sup> Combination printing from multiple negatives and artificially arranged studio compositions were regarded as operations that distorted this natural visual experience. A lecture delivered at the Camera Club in London in 1886, "Photography: A Pictorial Art," is recorded as the first public statement of this theory.<sup class="sup-ref"><a href="#cite-10">*10</a></sup></p>

<h3 id="h3-04">"The Death of Naturalistic Photography" — the retraction</h3>
<p>In 1891, however, the research of Hurter and Driffield proved the mechanical laws of exposure mathematically, and William James's psychology argued against Spencer's position by demonstrating that the mind actively engages with external stimuli — thereby undermining the philosophical foundations of Emerson's theory.<sup class="sup-ref"><a href="#cite-1">*1</a></sup> Emerson sent the photographic world a black-bordered pamphlet titled "The Death of Naturalistic Photography," retracting his position. This document is preserved in the Royal Photographic Society collection and can also be accessed via the Internet Archive.<sup class="sup-ref"><a href="#cite-4">*4</a></sup> The impact of the retraction was considerable: Emerson was described as "a bomb thrown into a tea party," so controversial had he become.<sup class="sup-ref"><a href="#cite-3">*3</a></sup></p>

<h3 id="h3-05">Influence and the relationship with Stieglitz</h3>
<p>The retraction meant that Emerson abandoned his claim for photography's artistic status, yet "the first attempt to argue systematically that photography should not imitate painting but should ground its artistic claims on photography's own visual principles" became a precursor question for the straight photography theories of <a href="/en/photographers/strand.html">Paul Strand</a> and <a href="/en/photographers/edward-weston.html">Edward Weston</a> that followed.<sup class="sup-ref"><a href="#cite-5">*5</a></sup> He also recognized the young <a href="/en/photographers/stieglitz.html">Alfred Stieglitz</a>, and records survive of his awarding Stieglitz a prize in a photographic competition.<sup class="sup-ref"><a href="#cite-11">*11</a></sup> The 1895 photobook <em>Marsh Leaves</em>, published near the end of his active career, is regarded as the practical culmination of his work, and the National Science and Media Museum holds related exhibition documentation.<sup class="sup-ref"><a href="#cite-12">*12</a></sup></p>"""

# ── Emerson EN sources ───────────────────────────────────────────────────
EMERSON_SOURCES_HTML = (
    '<div class="sources">'
    '<div class="cite-item" id="cite-1"><div class="cite-num">*1</div>'
    '<a href="https://www.tate.org.uk/research/tate-papers/27/emersons-evolution" target="_blank" rel="noopener">'
    'Tate Papers — Emerson\'s Evolution (Carl Fuldner)</a></div>'
    '<div class="cite-item" id="cite-2"><div class="cite-num">*2</div>'
    '<a href="https://arthistoryunstuffed.com/peter-henry-emerson-1856-1936/" target="_blank" rel="noopener">'
    'Art History Unstuffed — Peter Henry Emerson (1856–1936)</a></div>'
    '<div class="cite-item" id="cite-3"><div class="cite-num">*3</div>'
    '<a href="https://www.onlandscape.co.uk/2020/09/peter-henry-emerson/" target="_blank" rel="noopener">'
    'On Landscape — Peter Henry Emerson (critical biography; the retraction\'s impact)</a></div>'
    '<div class="cite-item" id="cite-4"><div class="cite-num">*4</div>'
    '<a href="https://archive.org/details/1890Death_naturalistic_photography-BP21-6" target="_blank" rel="noopener">'
    'Internet Archive — The Death of Naturalistic Photography [1890] (V&amp;A / Royal Photographic Society)</a></div>'
    '<div class="cite-item" id="cite-5"><div class="cite-num">*5</div>'
    '<a href="https://www.artgallery.nsw.gov.au/collection/works/245.1984/" target="_blank" rel="noopener">'
    'Art Gallery of New South Wales — A Stiff Pull (1886–87, printed 1888)</a></div>'
    '<div class="cite-item" id="cite-6"><div class="cite-num">*6</div>'
    '<a href="https://www.luminous-lint.com/phoenix.php/photographers/single/Peter_Henry__Emerson/" target="_blank" rel="noopener">'
    'Luminous-Lint — Peter Henry Emerson (life chronology; publications list)</a></div>'
    '<div class="cite-item" id="cite-7"><div class="cite-num">*7</div>'
    '<a href="https://www.nationalarchives.gov.uk/explore-the-collection/explore-by-time-period/victorians/peter-henry-emerson-rural-photography/" target="_blank" rel="noopener">'
    'National Archives UK — Peter Henry Emerson: Rural Photography</a></div>'
    '<div class="cite-item" id="cite-8"><div class="cite-num">*8</div>'
    '<a href="https://collections.vam.ac.uk/item/O1313848/pictures-of-east-anglian-life-photograph-emerson-peter-henry/" target="_blank" rel="noopener">'
    'V&amp;A Collection — Pictures of East Anglian Life (portfolio, 1890)</a></div>'
    '<div class="cite-item" id="cite-9"><div class="cite-num">*9</div>'
    '<a href="https://collections.vam.ac.uk/item/O90983/in-the-haysel-photograph-emerson-peter-henry" target="_blank" rel="noopener">'
    'V&amp;A Collection — In the Haysel (1888)</a></div>'
    '<div class="cite-item" id="cite-10"><div class="cite-num">*10</div>'
    '<a href="https://www.iphf.org/hof-peter-henry-emerson" target="_blank" rel="noopener">'
    'International Photography Hall of Fame — Peter Henry Emerson</a></div>'
    '<div class="cite-item" id="cite-11"><div class="cite-num">*11</div>'
    '<a href="https://www.icp.org/browse/archive/constituents/peter-henry-emerson" target="_blank" rel="noopener">'
    'International Center of Photography — Peter Henry Emerson</a></div>'
    '<div class="cite-item" id="cite-12"><div class="cite-num">*12</div>'
    '<a href="https://collection.sciencemuseumgroup.org.uk/documents/aa110108239/exhibition-file-for-life-and-landscape-p-h-emerson" target="_blank" rel="noopener">'
    'Science Museum Group / National Science and Media Museum — Exhibition file: Life and Landscape – P.H. Emerson</a></div>'
    '</div>'
)

# ── Target pages: (JA id, EN key in JSON) ─────────────────────────────────
# JA id is the filename without .html; EN key is what's in the JSON pages dict
TARGET_PAGES = [
    ('emerson',             'emerson.html'),
    ('kasebier',            'kasebier.html'),
    ('steichen',            'steichen.html'),
    ('demachy',             'demachy.html'),
    ('eugene-atget',        'eugene-atget.html'),
    ('lewis-hine',          'lewis-hine.html'),
    ('jacques-henri-lartigue', 'jacques-henri-lartigue.html'),
    ('paul-geniaux',        'paul-geniaux.html'),
    ('louis-vaire',         'louis-vaire.html'),
    ('edward-weston',       'edward-weston.html'),
    # JP pages: JA id uses kanji, EN key uses romaji slug
    ('jp-鹿島清兵衛',       'kajima-seibei.html'),
    ('jp-亀井茲明',         'koreaki-kamei.html'),
    ('jp-屋須弘平',         'kohei-yasu.html'),
    ('jp-鳥居龍蔵',         'ryuzo-torii.html'),
]

# thesis dict key = short ID used in THESIS_EN dict (for JP pages, use romaji)
THESIS_KEY_MAP = {
    'jp-鹿島清兵衛': 'kajima-seibei',
    'jp-亀井茲明':   'koreaki-kamei',
    'jp-屋須弘平':   'kohei-yasu',
    'jp-鳥居龍蔵':   'ryuzo-torii',
}


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


def main():
    classification = load_classification()
    ja_to_en, _ = build_jp_slug_map(classification)
    names = card_name_map()
    content = json.load(open(CONTENT_JSON, encoding='utf-8'))
    pages = content['pages']
    report = []

    for ja_id, en_key in TARGET_PAGES:
        page = pages.get(en_key)
        if page is None:
            report.append(f'!! {en_key}: no JSON entry')
            continue

        thesis_key = THESIS_KEY_MAP.get(ja_id, ja_id)

        # ── thesis ─────────────────────────────────────────────────────
        if thesis_key in THESIS_EN:
            page['thesis_html'] = THESIS_EN[thesis_key]
            thesis_set = True
        else:
            thesis_set = False

        # ── site_directory_html from JA §REL ───────────────────────────
        ja_people, ja_movs = parse_ja_rel(ja_id)
        people_links = []
        for rid, _ja in ja_people:
            # JP kanji ids need to be converted to romaji EN slug
            if rid.startswith('jp-'):
                en_slug_html = ja_to_en.get(rid + '.html') or ja_to_en.get(rid)
                if not en_slug_html:
                    report.append(f'   {en_key}: skip person (no slug map): {rid}')
                    continue
                en_slug = en_slug_html.replace('.html', '')
            else:
                en_slug = rid

            if not os.path.exists(os.path.join(EN_DIR, en_slug + '.html')):
                report.append(f'   {en_key}: skip person (no EN page): {en_slug}')
                continue

            # Look up nameEn — try romaji slug first, then original JA id
            en_name = names.get(en_slug) or names.get(rid)
            if not en_name:
                # Try to get it from card-data by the JA id directly
                report.append(f'   {en_key}: skip person (no nameEn): {en_slug}/{rid}')
                continue
            people_links.append((en_slug, en_name))

        movement_links = []
        for ja_slug, ja_name in ja_movs:
            en_name, slug = translate_movement_name(ja_name)
            if not slug or not os.path.exists(os.path.join(EN_MOV_DIR, slug + '.html')):
                report.append(f'   {en_key}: skip movement (no EN page): {ja_name}')
                continue
            movement_links.append((slug, en_name))

        page['site_directory_html'] = build_site_directory(people_links, movement_links)

        # ── emerson-specific: sections body + sources ──────────────────
        if ja_id == 'emerson':
            if page.get('sections'):
                page['sections'][0]['body_html'] = EMERSON_BODY_HTML
            else:
                page['sections'] = [{'title': 'Essay', 'body_html': EMERSON_BODY_HTML}]
            page['sources_html'] = EMERSON_SOURCES_HTML
            page['cite_ids'] = list(range(1, 13))
            page['supref_ids'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        report.append(
            f'OK {en_key}: thesis={thesis_set} '
            f'people={len(people_links)} movements={len(movement_links)}'
            + (' +body+sources' if ja_id == 'emerson' else '')
        )

    with open(CONTENT_JSON, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    print('\n'.join(report))


if __name__ == '__main__':
    main()
