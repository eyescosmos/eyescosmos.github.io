#!/usr/bin/env python3
"""Durable EN fix for the 1870-era photographer pages (thesis + §REL).

Edits data/photographers-en-content.json ONLY (the source build_photographers_en.py
reads). Mirrors each JA page's hand-written §REL into EN Related photographers/
movements, and sets the English "What this photographer changed" text.

Handles jp-* pages whose JA file name (kanji) differs from the EN slug (romaji),
both for the content-JSON key and for related-person links.

Re-runnable / idempotent. After running:
  python3 scripts/build_photographers_en.py --slug <JA-slug> ...
  python3 scripts/link_country_keywords.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from build_photographers_en import translate_movement_name  # noqa: E402

CONTENT_JSON = os.path.join(ROOT, 'data', 'photographers-en-content.json')
CLASSIFICATION_JSON = os.path.join(ROOT, 'data', 'photographers-en-classification.json')
JA_DIR = os.path.join(ROOT, 'photographers')
EN_DIR = os.path.join(ROOT, 'en', 'photographers')
EN_MOV_DIR = os.path.join(ROOT, 'en', 'movements')

# 9 era=1870 JA ids (JA file stems; jp-* are kanji)
ERA_1870 = [
    'muybridge', 'marey', 'marville', 'riis', 'annan', 'frederick-h-evans',
    'jp-横山松三郎', 'jp-冨重利平', 'jp-冨重徳次',
]

# EN thesis (mirrors JA ph-thesis__body; single <em>; follows 断定度 rules).
THESIS_EN = {
    'muybridge': (
        "By positioning multiple cameras at equal intervals and triggering them "
        "in sequence, Muybridge developed a method of recording motion as <em>a "
        "series of still images unfolded along the time axis</em>. Unlike "
        "conventional photography that captured a single instant, this sequential "
        "approach brought the structure of time itself into visual question. "
        "Projection via the Zoopraxiscope — replaying still images as motion — "
        "marked a practical step toward the bifurcation of still photography and "
        "the moving image. His large-scale collaborative research at the "
        "University of Pennsylvania also established a precedent for deploying "
        "photography as a cross-disciplinary archive spanning science, medicine, "
        "and art education."
    ),
    'marey': (
        "By layering multiple exposures onto a single plate, Marey developed "
        "chronophotography — a method that <em>condensed motion into an "
        "analytical diagram within a single image</em> — and transformed the "
        "movements of bodies, birds in flight, and fluids into measurable visual "
        "forms. Where Muybridge unfolded time into a sequence of independent "
        "frames, Marey chose the contrasting approach of folding time into space, "
        "providing a visual precedent that modernist painters would later draw on "
        "when rendering movement as divided planes. His insistence on photography "
        "as an instrument of physiological measurement rather than aesthetic "
        "expression connects to the formation of a modern scientific gaze toward "
        "the body, and his work continues to be discussed across both the history "
        "of photography and the history of science."
    ),
    'marville': (
        "Commissioned by the city of Paris during the Haussmann transformation, "
        "Marville systematically documented both the disappearance of the old "
        "city and the emergence of the new, demonstrating that <em>administrative "
        "photographic practice could function as a visual archive constituting "
        "the city's self-image</em>. The process by which a body of photographs "
        "produced as official records came to be reread by later generations as "
        "cultural testimony to memory and loss concretely illustrates the layered "
        "significance that documentary photography can carry. As the direct "
        "precedent to Atget's later personal traversal of the same Parisian "
        "streets, Marville established an early model for the planned, "
        "institutional visualization of urban transformation."
    ),
    'riis': (
        "By deploying photography, journalism, lectures, and lantern slides as an "
        "integrated whole, Riis transformed the living conditions of New York's "
        "slums into <em>a problem that the public could no longer look away "
        "from</em>. Identifying himself not as a photographer but as a "
        "multi-skilled communicator for social change, he established a model in "
        "which documentary photography connects directly to policy-making. His "
        "pioneering use of flash powder to illuminate spaces beyond the reach of "
        "conventional cameras brought the interior world of urban poverty into "
        "the frame, turning invisible suffering into a visible public issue. "
        "Together with the ethics of representation that later documentary "
        "photography has continued to interrogate, his practice broadly opened "
        "the possibilities of photography as social testimony."
    ),
    'annan': (
        "Within the institutional framework of a pre-demolition survey "
        "commissioned by the city's improvement authority, Annan organised the "
        "dense closes of Glasgow's old town into <em>a systematic archive</em>. "
        "His quiet, structural gaze — distinct from emotional indictment — holds "
        "a double character: grasping urban space as an object of improvement "
        "while simultaneously preserving its material weight, placing the work in "
        "the paradoxical position of an administrative record reread as testimony "
        "to urban poverty. This body of work opens, as a prehistory of "
        "documentary photography, the possibility that the record itself may "
        "exceed the intentions of the institution that commissioned it."
    ),
    'frederick-h-evans': (
        "Using the delicate tonal range of platinum printing to capture the light "
        "and space of Gothic cathedrals, Evans connected architectural "
        "photography to <em>a record of spiritual experience</em>. By grounding "
        "photographic spirituality in the structure of light and the rhythm of "
        "architecture rather than pictorial manipulation, he anticipated the "
        "question of whether photography could become art through its own means. "
        "His participation in the Linked Ring Brotherhood and publication in "
        "Camera Work demonstrate his connection to the contemporary movement to "
        "institutionalise photography as a fine art, placing his practice within "
        "Pictorialism while also questioning its limits from within."
    ),
    'jp-横山松三郎': (
        "Yokoyama Matsusaburo combined photography with oil painting, "
        "lithographic printing, and cultural-heritage survey, <em>connecting "
        "photography to the formation of the Meiji state's visual administrative "
        "order</em> rather than limiting it to portrait-making alone. Through his "
        "participation in the Jinshin Survey he helped pioneer the first "
        "systematic government-led effort to document shrines, temples, and "
        "cultural assets across Japan, opening a channel through which photography "
        "functioned as a foundation of national knowledge. His contributions to "
        "the Vienna World's Exposition and his experiments with photolithography "
        "embody the process by which photography became embedded in both outward "
        "self-representation and print culture. The ongoing recognition of the "
        "related photographic materials as Important Cultural Properties shows "
        "that his recording practice continues to be evaluated as one of the "
        "founding moments of Japanese photographic history."
    ),
    'jp-冨重利平': (
        "Tomishige Rihei founded the Tomishige Photography Studio in Kumamoto and "
        "took on the task of <em>institutionalizing photography in a provincial "
        "city</em>. Through a practice ranging from portrait photography and the "
        "documentation of Kumamoto Castle and the aftermath of the Satsuma "
        "Rebellion to portraits of Natsume Soseki and Lafcadio Hearn, he created "
        "a base from which local society could render itself visible through "
        "photography. The preservation of the studio's building as a Nationally "
        "Registered Tangible Cultural Property, and the continued scholarly study "
        "of its archival materials, show that his work is valued beyond "
        "individual authorship — as primary material for the visual-culture "
        "history of regional modernity. Its continuation through the succession "
        "to his disciple Tokuji deepens that institutional significance further."
    ),
    'jp-冨重徳次': (
        "As the second-generation head of the Tomishige Photography Studio, "
        "Tomishige Tokuji <em>sustained the institutional framework and "
        "documentary culture that Rihei had built, across the Meiji, Taisho, and "
        "early Showa periods</em>. He is positioned in photographic history less "
        "as an individual innovator than as the embodiment of studio succession "
        "in provincial modernity. The long-term maintenance of Kumamoto's "
        "portrait culture, regional documentation, and commercial-photography "
        "network through the Rihei-to-Tokuji succession shows that a local studio "
        "could take root as an institution rather than depending on a single "
        "generation's talent. That the documentary photographs attributed to "
        "Tokuji continue to be consulted by researchers shows how the practice of "
        "succession itself has generated materials for photographic history."
    ),
}

GROUP_OPEN = '<div class="site-directory-group site-directory-group-contextual">'


def card_name_map():
    cd = json.load(open(os.path.join(ROOT, 'card-data.json'), encoding='utf-8'))
    return {p['id']: p.get('nameEn', '') for p in cd['photographers']}


def ja_to_en_filemap():
    cl = json.load(open(CLASSIFICATION_JSON, encoding='utf-8'))
    m = {}
    for en_file, info in cl.get('jp_slug_mapping', {}).items():
        m[info['ja_file']] = en_file  # 'jp-冨重利平.html' -> 'tomishige-rihei.html'
    return m


def parse_ja_rel(ja_id):
    """Return (people, movements) from a JA page's §REL section.
    people = [photographer_id]; movements = [ja_display_name]."""
    path = os.path.join(JA_DIR, ja_id + '.html')
    html = open(path, encoding='utf-8').read()
    m = re.search(r'§ REL</span>.*?<div class="ph-section__body">(.*?)</div>\s*</section>',
                  html, re.S)
    if not m:
        return [], []
    body = m.group(1)
    people = [href.split('/')[-1].replace('.html', '')
              for href in re.findall(r'<a href="(/photographers/[^"]+)">', body)]
    movements = [name for _slug, name in
                 re.findall(r'<a href="/movements/([^"]+)\.html">([^<]+)</a>', body)]
    return people, movements


def build_site_directory(people_links, movement_links):
    parts = ['<nav class="site-directory-links" aria-label="Site links" data-nosnippet>']
    if people_links:
        items = ''.join(f'<a href="/en/photographers/{slug}.html">{name}</a>'
                        for slug, name in people_links)
        parts.append('        ' + GROUP_OPEN)
        parts.append('          <div class="site-directory-label">Related people &amp; photographers</div>')
        parts.append(f'          <div class="site-directory-items">{items}</div>')
        parts.append('        </div>')
    if movement_links:
        items = ''.join(f'<a href="/en/movements/{slug}.html">{name}</a>'
                        for slug, name in movement_links)
        parts.append('        ' + GROUP_OPEN)
        parts.append('          <div class="site-directory-label">Related movements</div>')
        parts.append(f'          <div class="site-directory-items">{items}</div>')
        parts.append('        </div>')
    parts.append('      </nav>')
    return '\n'.join(parts)


def main():
    names = card_name_map()
    jamap = ja_to_en_filemap()
    content = json.load(open(CONTENT_JSON, encoding='utf-8'))
    pages = content['pages']
    report = []

    for ja_id in ERA_1870:
        ja_file = ja_id + '.html'
        en_file = jamap.get(ja_file, ja_file)   # content-JSON key
        page = pages.get(en_file)
        if page is None:
            report.append(f'!! {ja_id}: no JSON entry ({en_file})')
            continue

        page['thesis_html'] = THESIS_EN.get(ja_id)

        ja_people, ja_movs = parse_ja_rel(ja_id)
        people_links = []
        for rid in ja_people:
            en_slug = jamap.get(rid + '.html', rid + '.html')[:-5]
            if not os.path.exists(os.path.join(EN_DIR, en_slug + '.html')):
                report.append(f'   {ja_id}: skip person (no EN page): {rid}')
                continue
            en_name = names.get(rid)
            if not en_name:
                report.append(f'   {ja_id}: skip person (no nameEn): {rid}')
                continue
            people_links.append((en_slug, en_name))

        movement_links = []
        for ja_name in ja_movs:
            en_name, slug = translate_movement_name(ja_name)
            if not slug or not os.path.exists(os.path.join(EN_MOV_DIR, slug + '.html')):
                report.append(f'   {ja_id}: skip movement (no EN page): {ja_name}')
                continue
            movement_links.append((slug, en_name))

        page['site_directory_html'] = build_site_directory(people_links, movement_links)
        report.append(f'OK {ja_id} -> {en_file}: thesis={"yes" if page["thesis_html"] else "no"} '
                      f'people={len(people_links)} movements={len(movement_links)}')

    with open(CONTENT_JSON, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    print('\n'.join(report))


if __name__ == '__main__':
    main()
