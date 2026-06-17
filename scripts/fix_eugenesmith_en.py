#!/usr/bin/env python3
"""Mirror the restored/expanded JA eugenesmith page into the EN content JSON.
Edits data/photographers-en-content.json (key 'eugenesmith.html') only, then the
EN page is regenerated with build_photographers_en.py --slug eugenesmith.
Idempotent: re-running detects already-applied changes and skips.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CJ = os.path.join(ROOT, 'data', 'photographers-en-content.json')

THESIS = ("Smith pushed photojournalism beyond the single news image, expanding it into "
          "<em>long-form testimony</em> that lets readers follow a subject's labor, life, and "
          "social institutions through sustained reporting, and he claimed the darkroom print and "
          "the magazine's editing sequence as part of the work itself. That intense subjectivity "
          "gave photography a moral force, while also leaving an open question about the risk of "
          "absorbing the subject into the photographer's own narrative—an ethics that later "
          "documentary photography continues to weigh.")

BIO_OLD = ("From 1955 he spent more than two years photographing Pittsburgh, and in 1971 he "
           "traveled to Japan to document the Minamata disease disaster. He died in Tucson, "
           "Arizona, in 1978.")
BIO_NEW = ("From 1955 he spent more than two years photographing Pittsburgh; in 1957 he moved into "
           "a New York loft, where he continued a vast record in photographs and sound recordings "
           "until 1965. In 1971 he traveled to Japan to document the Minamata disease disaster. He "
           "died in Tucson, Arizona, in 1978.")

MINAMATA_H3 = '<h3>The Minamata Project: Photography as Testimony and Representation</h3>'
LOFT_BLOCK = (
    '<h3>The Loft: an excessive record outside reportage</h3>\n'
    '<p>As he left <em>LIFE</em> and his Pittsburgh work swelled into an unfinished large-scale '
    'project, Smith was pursuing another kind of record in a New York loft. The Tokyo Photographic '
    'Art Museum explains that after leaving <em>LIFE</em>, Smith moved into a Manhattan space known '
    'as “the loft,” where he photographed jam sessions and the comings and goings of '
    'figures such as Thelonious Monk, Miles Davis, Salvador Dalí, Abstract Expressionist '
    'painters, Robert Frank, and Diane Arbus.<sup class="sup-ref"><a href="#cite-25">*25</a></sup> '
    'The Center for Creative Photography records that Smith moved in 1957 into a dilapidated '
    'five-story loft at 821 Sixth Avenue and, through 1965, shot roughly 40,000 frames of the '
    'building’s nocturnal jazz scene and the street outside, while wiring the building for '
    'sound and leaving some 1,740 reels—about 4,000 hours—of tape.<sup class="sup-ref">'
    '<a href="#cite-26">*26</a></sup> The Nasher Museum at Duke University similarly frames this '
    'period as one in which Smith, surrounded by jazz musicians, filmmakers, writers, and artists, '
    'preserved the hours of Monk, Norman Mailer, Dalí, and others in photographs and '
    'recordings.<sup class="sup-ref"><a href="#cite-27">*27</a></sup> What matters here is not to '
    'read the loft years simply as “leaving reportage for art photography.” Rather, Smith '
    'had stepped away from the photo essay as something completed for a magazine article and was '
    'testing a method that held the time, sound, human relationships, and the nocturnal city '
    'outside the window in their unsorted density. The social storytelling honed at <em>LIFE</em> '
    'expanded, through Pittsburgh and the loft, into long residencies, the grasp of a whole place, '
    'and excessive recording.</p>\n' + MINAMATA_H3
)

WORKS_SECTION = {
    "num": None,
    "title": "Representative works, method & medium",
    "body_html": (
        '<div class="essay">\n'
        '<h3>FIG. 01 Country Doctor (1948)</h3>\n'
        '<p>A <em>LIFE</em> photo essay following Dr. Ernest Ceriani in Kremmling, Colorado. Smith '
        'arranged house calls, surgery, and night emergencies as a continuous sequence, letting the '
        'shortage of rural medicine be read as the weight of a single life. Gelatin silver print.'
        '<sup class="sup-ref"><a href="#cite-6">*6</a></sup></p>\n'
        '<h3>FIG. 02 Spanish Village (1951)</h3>\n'
        '<p>A series made in a poor Spanish village that rendered poverty, faith, and labor through '
        'the gestures of its elderly residents—reading society from the texture of daily life '
        'rather than abstract politics.<sup class="sup-ref"><a href="#cite-7">*7</a></sup></p>\n'
        '<h3>FIG. 03 Nurse Midwife (1951)</h3>\n'
        '<p>A photo essay centered on the midwife Maude Callen in Pineville, South Carolina, folding '
        'medicine, poverty, the labor of a Black woman, and community trust into a single narrative.'
        '<sup class="sup-ref"><a href="#cite-8">*8</a></sup></p>\n'
        '<h3>FIG. 04 The Walk to Paradise Garden (1946)</h3>\n'
        '<p>An image of children stepping from shadow into light, made during Smith’s recovery '
        'from his war wounds; it shows a feeling for light that his later, heavier social records '
        'alone cannot explain. Gelatin silver print, MoMA.<sup class="sup-ref"><a href="#cite-12">'
        '*12</a></sup></p>\n'
        '<h3>FIG. 05 Pittsburgh (1955–57)</h3>\n'
        '<p>Commissioned for a book on the city, the project swelled over more than two years into '
        'over 10,000 negatives—“a long poem about Pittsburgh.” Smith tried to make '
        'the city itself the protagonist, leaving open the question of how autonomous and how '
        'excessive a photo essay could become.<sup class="sup-ref"><a href="#cite-9">*9</a></sup></p>\n'
        '<h3>FIG. 06 The Jazz Loft (1957–65)</h3>\n'
        '<p>In a New York loft Smith shot roughly 40,000 frames of the nighttime jazz scene and the '
        'street, wiring the building for sound to leave some 4,000 hours of tape—a vast record '
        'in both photography and audio.<sup class="sup-ref"><a href="#cite-26">*26</a></sup></p>\n'
        '<h3>FIG. 07 Minamata / Tomoko in Bath (1971–72)</h3>\n'
        '<p>The concentrated late project documenting Minamata disease, made together with Aileen '
        'Mioko Smith; a planned three-month stay grew to three years. Tomoko in Bath, showing a '
        'mother bathing her daughter Tomoko, became a symbol of illness and dignity while also '
        'leaving an ethical tension about turning a victim into an icon.<sup class="sup-ref">'
        '<a href="#cite-28">*28</a></sup></p>\n'
        '<h3>Method and medium</h3>\n'
        '<p>Smith’s method unites long residency in his subjects’ lives, dense darkroom '
        'printing, and control over page sequence and captions. His principal medium was the photo '
        'essay in the weekly picture magazine <em>LIFE</em>, expanding in his later years into books '
        'and sound recording. Most of his works are gelatin silver prints, whose dramatic tonal '
        'range itself worked as editorial pressure to keep readers from looking away from real pain.'
        '<sup class="sup-ref"><a href="#cite-9">*9</a></sup></p>\n'
        '</div>'
    ),
}

CITE_OLD = '<div class="cite-item" id="cite-28">'
CITE_NEW = (
    '<div class="cite-item" id="cite-25"><div class="cite-num">*25</div>'
    '<a href="https://topmuseum.jp/exhibition/5095/" target="_blank" rel="noopener">'
    'Tokyo Photographic Art Museum — W. Eugene Smith and the New York Loft Years</a></div>'
    '<div class="cite-item" id="cite-26"><div class="cite-num">*26</div>'
    '<a href="https://ccp.arizona.edu/events/jazz-loft-project-w-eugene-smith-nyc-1957-1965/" target="_blank" rel="noopener">'
    'Center for Creative Photography — The Jazz Loft Project: W. Eugene Smith in NYC, 1957–1965</a></div>'
    '<div class="cite-item" id="cite-27"><div class="cite-num">*27</div>'
    '<a href="https://nasher.duke.edu/exhibitions/jazz-loft-project-w-eugene-smith-new-york-city-1957-1965/" target="_blank" rel="noopener">'
    'Nasher Museum of Art at Duke University — The Jazz Loft Project: W. Eugene Smith in New York City, 1957–1965</a></div>'
    + CITE_OLD
)

SITE_DIR = (
    '<nav class="site-directory-links" aria-label="Site links" data-nosnippet>\n'
    '        <div class="site-directory-group site-directory-group-contextual">\n'
    '          <div class="site-directory-label">Related people &amp; photographers</div>\n'
    '          <div class="site-directory-items">'
    '<a href="/en/photographers/capa.html">Robert Capa</a>'
    '<a href="/en/photographers/cartierbresson.html">Henri Cartier-Bresson</a>'
    '<a href="/en/photographers/lange.html">Dorothea Lange</a>'
    '<a href="/en/photographers/salgado.html">Sebastião Salgado</a>'
    '<a href="/en/photographers/domon.html">Ken Domon</a></div>\n'
    '        </div>\n'
    '        <div class="site-directory-group site-directory-group-contextual">\n'
    '          <div class="site-directory-label">Related movements</div>\n'
    '          <div class="site-directory-items">'
    '<a href="/en/movements/photojournalism.html">Photojournalism</a>'
    '<a href="/en/movements/social-documentary.html">Social Documentary</a>'
    '<a href="/en/movements/documentary.html">Documentary</a></div>\n'
    '        </div>\n'
    '      </nav>'
)


def main():
    data = json.load(open(CJ, encoding='utf-8'))
    p = data['pages']['eugenesmith.html']
    rep = []

    p['thesis_html'] = THESIS
    p['thesis_label'] = None
    rep.append('thesis_html set')

    secs = p['sections']
    # Biography loft clause
    if BIO_OLD in secs[0]['body_html']:
        secs[0]['body_html'] = secs[0]['body_html'].replace(BIO_OLD, BIO_NEW)
        rep.append('bio loft clause added')
    elif BIO_NEW.split('—')[0][:30] in secs[0]['body_html'] or '1957 he moved into' in secs[0]['body_html']:
        rep.append('bio already done')
    else:
        rep.append('!! BIO_OLD not found')

    # Loft block into Work and method (sec index 1)
    if 'The Loft: an excessive record' not in secs[1]['body_html']:
        if MINAMATA_H3 in secs[1]['body_html']:
            secs[1]['body_html'] = secs[1]['body_html'].replace(MINAMATA_H3, LOFT_BLOCK, 1)
            rep.append('loft block inserted')
        else:
            rep.append('!! Minamata h3 anchor not found')
    else:
        rep.append('loft already present')

    # Insert Representative works section before Criticism (last)
    titles = [s.get('title') for s in secs]
    if 'Representative works, method & medium' not in titles:
        # criticism is last
        crit_idx = next((i for i, s in enumerate(secs) if s.get('title') == 'Criticism and reception'), len(secs))
        secs.insert(crit_idx, WORKS_SECTION)
        rep.append(f'works section inserted at {crit_idx}')
    else:
        rep.append('works section already present')

    # Sources: add cite 25,26,27
    if 'id="cite-25"' not in p['sources_html']:
        if CITE_OLD in p['sources_html']:
            p['sources_html'] = p['sources_html'].replace(CITE_OLD, CITE_NEW, 1)
            rep.append('cites 25-27 added')
        else:
            rep.append('!! cite-28 anchor not found')
    else:
        rep.append('cites 25-27 already present')

    # cite_ids / supref_ids
    for k in ('cite_ids', 'supref_ids'):
        ids = set(p.get(k) or [])
        ids.update([25, 26, 27])
        p[k] = sorted(ids)
    rep.append('cite_ids/supref_ids updated')

    # site_directory_html
    p['site_directory_html'] = SITE_DIR
    rep.append('site_directory_html rebuilt (5 people, 3 movements)')

    json.dump(data, open(CJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('\n'.join(rep))
    print('section titles ->', [s.get('title') for s in secs])
    print('cite_ids ->', p['cite_ids'])


if __name__ == '__main__':
    main()
