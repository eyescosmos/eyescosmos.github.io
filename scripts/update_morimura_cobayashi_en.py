#!/usr/bin/env python3
"""
Update yasumasa-morimura.html entry (content keys only, keep meta intact)
and create kenta-cobayashi.html entry (full new entry).
sources_html uses cite-item/cite-num format required by build_photographers_en.py parse_sources().
"""
import json, os

JSON_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data', 'photographers-en-content.json'))

with open(JSON_PATH, encoding='utf-8') as f:
    data = json.load(f)

pages = data['pages'] if 'pages' in data else data


def ci(n, url, label):
    """Build a cite-item in the format parse_sources() expects."""
    return (f'<div class="cite-item" id="cite-{n}">'
            f'<div class="cite-num">*{n}</div>'
            f'<a href="{url}" target="_blank" rel="noopener">{label}</a>'
            f'</div>')


def sources(pairs):
    """Wrap cite-items in .sources div."""
    return '<div class="sources">' + ''.join(ci(n, u, l) for n, u, l in pairs) + '</div>'


# ============================================================
# TASK A: UPDATE yasumasa-morimura.html — content keys only
# keep: title, meta_description, canonical, hreflang, og, twitter,
#       has_ga, h1, years, jsonld, footer_html
# ============================================================

m = pages['yasumasa-morimura.html']

m['lead_html'] = (
    '<p class="lead">Yasumasa Morimura inserts his own body into masterpieces, film stars, and historical photographs. '
    'In doing so, he turns photography from an act of resemblance into a site where the authority of images, gender, race, '
    'and the memory of postwar Japan are performed again. Through disguise, sets, quotation, and deliberate dissonance, '
    'his work asks how viewers come to trust history and the self through images.</p>'
)

m['thesis_label'] = 'What this photographer changed'

m['thesis_html'] = (
    "Morimura’s contribution to photography lies in recasting self-portraiture. Instead of presenting the artist’s bare face, "
    "he used his own body to perform figures that had already been given value within art history, cinema, and news photography. "
    "Morimura has said that art education in postwar Japan was organized around Euro-American values, and that students had more "
    "opportunities to study Van Gogh, Monet, and Renoir than Japanese art history. "
    '<sup class="sup-ref"><a href="#cite-27">*27</a></sup> '
    "Against this background, performing Van Gogh or Manet was neither a simple act of admiration for Western art nor an outside "
    "rejection of it. By placing his Japanese male face and body inside the “art to be seen” that had been given to him through "
    "reproductions and education, he brought the desire to assimilate and the unease of not fully belonging into the same image. "
    "Morimura also connects self-portraiture to the media history of mirrors, photography, cinema, television, and the internet. "
    "He used the self-portrait less as confession than as a way to examine how images of each period make the “self.” "
    '<sup class="sup-ref"><a href="#cite-20">*20</a></sup> '
    "As the Getty Museum’s text on photographic reenactment suggests, Morimura’s reenactments also bring questions of "
    "gender, race, and cultural identity into view. "
    '<sup class="sup-ref"><a href="#cite-8">*8</a></sup>'
)

m['keywords_html'] = (
    '<div class="page-keywords"><b>Keywords:</b>'
    '<a href="/en/movements/conceptual-art.html">Conceptual Art</a>'
    '<span class="kw-sep">/</span>Self-portraiture'
    '<span class="kw-sep">/</span>Appropriation'
    '<span class="kw-sep">/</span><a href="/en/movements/staged-photography.html">Staged Photography</a>'
    '<span class="kw-sep">/</span>Reenactment'
    '<span class="kw-sep">/</span>Art history'
    '<span class="kw-sep">/</span>Gender'
    '<span class="kw-sep">/</span>Postwar Japan'
    '</div>'
)

m['view_works_note'] = 'This site does not reproduce artwork images. Please view the works through the museum, official gallery, and collection pages below.'

m['view_works_links_html'] = (
    '<div class="links">'
    '<a class="chip-link" href="https://shugoarts.com/en/artists/morimura-yasumasa/" target="_blank" rel="noopener">ShugoArts — Portrait (Van Gogh) ↗</a>'
    '<a class="chip-link" href="https://www.mori.art.museum/en/collection/5084/index.html" target="_blank" rel="noopener">Mori Art Museum — Portrait (Futago) ↗</a>'
    '<a class="chip-link" href="https://www.sfmoma.org/artwork/97.788/" target="_blank" rel="noopener">SFMOMA — Portrait (Futago) ↗</a>'
    '<a class="chip-link" href="https://www.ngv.vic.gov.au/explore/collection/work/148227/" target="_blank" rel="noopener">NGV — An inner dialogue with Frida Kahlo ↗</a>'
    '<a class="chip-link" href="https://www.artizon.museum/en/exhibition/detail/73" target="_blank" rel="noopener">Artizon Museum — Jam Session ↗</a>'
    '<a class="chip-link" href="https://shugoarts.com/en/artists/morimura-yasumasa/" target="_blank" rel="noopener">ShugoArts — works overview ↗</a>'
    '</div>'
)

# ---- SECTION BODIES ----

SEC01 = (
    '<div class="essay"><p>'
    "Morimura’s method begins with "
    '<a href="https://shugoarts.com/en/artists/morimura-yasumasa/" rel="noopener" target="_blank">Portrait (Van Gogh)</a>'
    " of 1985. ShugoArts describes the work after this point as a sustained series of self-portraits in which Morimura becomes "
    "“something” or “someone,” incorporating research, dioramas, sets, costumes, and makeup into the production process. "
    '<sup class="sup-ref"><a href="#cite-1">*1</a></sup>'
    " This form grew out of the art education and visual culture of postwar Japan in which Morimura came of age. "
    "In a lecture, Morimura stated that art education in Japan had been Westernized since the Meiji period and became even more deeply "
    "shaped by Euro-American values after the defeat in World War II. As a student, he said, he mainly studied Van Gogh, Monet, and Renoir, "
    "with few opportunities to encounter Japanese art history. "
    '<sup class="sup-ref"><a href="#cite-27">*27</a></sup>'
    " Hara Museum also presents his education in postwar Osaka, born under Allied occupation and amid a void where prewar teachings had been "
    "pushed aside and Western values entered, as an important background to <i>Ego Obscura</i>. "
    '<sup class="sup-ref"><a href="#cite-7">*7</a></sup>'
    " Even with this historical background, the 1985 starting point did not appear as a fully formed critique of art history. "
    "In a 2016 interview, Morimura said that he did not yet know Western art history in depth, and that he had received Van Gogh through "
    "reproductions and the popular image of “the man of fire.” "
    '<sup class="sup-ref"><a href="#cite-20">*20</a></sup>'
    " In another interview, he explained that he identified the young, suffering Van Gogh with his own discomfort, and that when he saw "
    "Van Gogh’s self-portrait, it felt like seeing himself in a mirror. "
    '<sup class="sup-ref"><a href="#cite-22">*22</a></sup>'
    " This experience led toward a form in which the self is seen through an already known image of another person. "
    "In an ARTLOGUE interview, Morimura also recalled that a large color self-portrait appeared suddenly in 1985 and became the beginning "
    "of his current style. "
    '<sup class="sup-ref"><a href="#cite-21">*21</a></sup>'
    " The National Museum of Art, Osaka places <i>Portrait (Van Gogh)</i>, first shown at Gallery 16 in Kyoto in 1985, as an early key "
    "work that opened Morimura’s self-portraiture toward art history. "
    '<sup class="sup-ref"><a href="#cite-2">*2</a></sup>'
    " In 1988, he took part in the Aperto section of the Venice Biennale and, with "
    '<a href="https://www.mori.art.museum/en/collection/5084/index.html" rel="noopener" target="_blank">Portrait (Futago)</a>'
    ", based on Manet’s <i>Olympia</i>, placed a familiar masterpiece of Western art and the body of a Japanese man in the same image. "
    '<sup class="sup-ref"><a href="#cite-4">*4</a></sup>'
    " At the same time, artists associated with the "
    '<a href="/en/movements/pictures-generation.html">Pictures Generation</a>'
    " in Europe and the United States were using advertising, cinema, and existing photographs to examine photography as a medium that "
    "produces shared social patterns instead of simply transmitting reality. "
    '<sup class="sup-ref"><a href="#cite-23">*23</a></sup>'
    " Morimura did not repeat that movement in Japan as it stood. He built a method that transferred the figures he had received through "
    "reproductions of Western art, Hollywood cinema, and news photographs into his own body through costume, makeup, sets, and performance. "
    "Hara Museum’s retrospective text explains that he has reenacted painting, cinema, and historical moments, constructing his work "
    "as a meta-commentary that crosses time, race, and gender. "
    '<sup class="sup-ref"><a href="#cite-7">*7</a></sup>'
    " For that reason, it is not enough to summarize Morimura as an artist who “dressed as masterpieces.” His photographs need "
    "to be read as work that shows what shifts inside the photographic image when postwar Japanese culture receives Western art, Hollywood "
    "cinema, and news photographs, and then performs them again through the artist’s own body."
    '</p></div>'
)

SEC02 = (
    '<div class="essay">'
    '<h3 id="h3-01">Making the Body a Site of Quotation</h3>'
    '<p>Morimura’s self-portraits are not disguises made to conceal his bare face. They are acts of rebuilding, through his own body, '
    'faces and poses remembered from reproductions, cinema, and news photographs. ShugoArts describes his work as self-portraiture that '
    'involves careful research, dioramas and sets, costumes, and makeup. '
    '<sup class="sup-ref"><a href="#cite-1">*1</a></sup>'
    ' Photography here is not a medium that merely records a completed disguise. It fixes the body, costume, makeup, background, lighting, '
    'and print into a single image, making visible the gap between the source image and Morimura’s own body. If the likeness were '
    'complete, it would approach replication. If it were too distant, it would fail as quotation. Morimura’s photographs hold that '
    'intermediate dissonance, showing how deeply masterpieces, films, and historical photographs have been remembered as familiar types. '
    'Self-portraiture is thereby shifted from a form that directly reveals the artist’s interiority to one that rereads shared figures '
    'through the body.</p>'
    '<h3 id="h3-02">Portrait (Van Gogh) and the Entry into Masterpieces</h3>'
    '<p><a href="https://shugoarts.com/en/artists/morimura-yasumasa/" rel="noopener" target="_blank">Portrait (Van Gogh)</a> is one of the '
    'early works that most clearly shows Morimura’s method. The National Museum of Art, Osaka registers the work as a photograph from '
    '1985, providing a concrete point of departure for his early self-portraiture. '
    '<sup class="sup-ref"><a href="#cite-3">*3</a></sup>'
    ' The subject here is not the historical Van Gogh himself, but the image of Van Gogh widely shared through art books, exhibitions, '
    'reproductions, and explanatory texts. Morimura later said that, at the time of making the work, he did not know Van Gogh in depth and '
    'remembered him through reproductions and the phrase “the man of fire.” '
    '<sup class="sup-ref"><a href="#cite-20">*20</a></sup>'
    ' At the same time, he also said that when he saw Van Gogh’s self-portrait, it felt as if he were looking at himself in a mirror. '
    '<sup class="sup-ref"><a href="#cite-22">*22</a></sup>'
    ' <i>Portrait (Van Gogh)</i> therefore presents less an accurate recreation of Van Gogh than a transfer of the “Van Gogh-ness” '
    'Morimura had received into his own face and body. It brings to the surface the knowledge and stories through which the figure of the '
    'artist has been believed. In place of a photograph that proves the authenticity of the self, it begins a photography that thinks about '
    'the self through another face.</p>'
    '<h3 id="h3-03">Portrait (Futago) and the Assumptions of Looking at a Masterpiece</h3>'
    '<p><a href="https://www.mori.art.museum/en/collection/5084/index.html" rel="noopener" target="_blank">Portrait (Futago)</a> directs '
    'Morimura’s method toward art history, sex, and race with particular clarity. Mori Art Museum describes the work as based on '
    'Manet’s <i>Olympia</i> and notes that Morimura performs both the “white prostitute” and the “black maid” '
    'through the body of a Japanese man. '
    '<sup class="sup-ref"><a href="#cite-4">*4</a></sup>'
    ' Viewers who know Manet’s <i>Olympia</i> read the nude woman, the maid, the frontal gaze, and the difference in skin color '
    'through their knowledge of art history. When Morimura appears as a Japanese man performing both roles at once, the divisions that '
    'had seemed settled within the masterpiece become unstable. This substitution is not a simple critique of Manet. It is a way of '
    'exposing, within the image, the habits of knowledge and looking that viewers bring to the act of seeing a masterpiece. SFMOMA’s '
    'collection entry presents the work as a chromogenic print from 1988, also confirming its place in an international photographic '
    'collection. '
    '<sup class="sup-ref"><a href="#cite-5">*5</a></sup>'
    ' In this sense, <i>Portrait (Futago)</i> can be read less as a parody of Manet than as a work that rearranges the premises for '
    'looking at a masterpiece inside a single body.</p>'
    '<h3 id="h3-04">The “I” Extending to Actresses, Kahlo, and Historical Photographs</h3>'
    '<p>Morimura’s self-portraiture is not directed only toward Western painting. The National Museum of Art, Osaka’s '
    'retrospective text presents his transformations into protagonists of masterpieces, film actresses, and historical figures as '
    'Morimura’s “my art history.” '
    '<sup class="sup-ref"><a href="#cite-2">*2</a></sup>'
    ' <a href="https://www.ngv.vic.gov.au/explore/collection/work/148227/" rel="noopener" target="_blank">An inner dialogue with Frida '
    'Kahlo (Flower wreath and tears)</a>, held by NGV, reconstructs the emblematic modern self-image of Frida Kahlo through Morimura’s '
    'own body. '
    '<sup class="sup-ref"><a href="#cite-6">*6</a></sup>'
    ' Here, the “I” does not remain enclosed within the artist’s private interior. It emerges through another face, another '
    'costume, another pain, and another mythology. The force of Morimura’s photographs lies in the way they refuse to fix the object '
    'of disguise as either homage or satire. He neither simply takes the subject nor fully assimilates into it. He preserves a distance '
    'between the subject and himself, and within that distance he shows how unstable gender, nationality, and cultural memory can be.</p>'
    '<h3 id="h3-05">Photographic Reenactment and the Likeness That Never Fully Matches</h3>'
    '<p>The Getty Museum’s text for <i>Photo Reenactment</i> explains that since the early 1980s, Morimura has reenacted famous '
    'paintings and cast himself within them. '
    '<sup class="sup-ref"><a href="#cite-8">*8</a></sup>'
    ' The same text adds that his works do more than reproduce their sources: they include homage, satire, and anachronistic elements '
    'while raising questions of gender, race, and cultural identity. '
    '<sup class="sup-ref"><a href="#cite-8">*8</a></sup>'
    ' As this description suggests, Morimura’s reenactments are not attempts to return faithfully to the source image. They are '
    'ways of testing how the authority of the source image has been maintained, by which bodies, in which periods, and through what forms '
    'of performance. Photographic reenactment can seem to bring the past into the present. In Morimura’s case, however, the past '
    'never returns unchanged. The texture of the face, the placement of the body, the excess of the costume, and the artificiality of '
    'the set remain somewhere in the image as a mismatch. That mismatch makes visible the roles and desires behind images that have been '
    'placed at the center of art history.</p>'
    '<h3 id="h3-06">Postwar Japan’s Reception of the West and the Position of the Self</h3>'
    '<p>Morimura’s work cannot be understood as a view of Western art history from the outside. It is grounded in an experience '
    'of learning, becoming familiar with, and feeling distance from Euro-American culture within postwar Japan. In a lecture, Morimura '
    'stated that under the American occupation after the war, Westernization extended across lifestyle, political thought, eating habits, '
    'and art education. At school, oil painting and Western art were given as the standard of “art” more often than '
    '<i>nihonga</i> or Japanese art history. '
    '<sup class="sup-ref"><a href="#cite-27">*27</a></sup>'
    ' ShugoArts’s text for <i>My Chronicle 1985–2018</i> also places the background of his work in a self born in the Showa '
    'era and the twentieth century, noting Japan’s encounter with Western civilization since the Meiji period and the strong '
    'influence of American culture after the defeat in World War II. '
    '<sup class="sup-ref"><a href="#cite-16">*16</a></sup>'
    ' Seen from this angle, Morimura’s performances of Van Gogh, Manet, or Velázquez are not simply attempts to approach '
    'Western art. They place his body inside Western images he had received from childhood as “art,” photographing both the '
    'self that had become familiar with those images and the self that appears as something out of place within them. In the same lecture, '
    'Morimura explained that his self-portraits place the Japanese face and body he possesses into figures from Western art history, '
    'bringing Japanese and Western elements into the same space while keeping their differences from being completely blended. '
    '<sup class="sup-ref"><a href="#cite-27">*27</a></sup>'
    ' As Artizon Museum’s <i>Jam Session</i> reread modern Japanese painting, including Aoki Shigeru’s <i>A Gift of the Sea</i>, '
    'through Morimura’s method, this question does not end with Western art. It also turns toward modern Japanese art and museum '
    'collections. '
    '<sup class="sup-ref"><a href="#cite-9">*9</a></sup>'
    ' Morimura’s photographs do not simply line up East and West as opposing terms. They show the dissonance that arises when a '
    'body formed within postwar Japan’s close reception of Euro-American culture is placed inside those images.</p>'
    '<h3 id="h3-07">Self-Portraiture as Place, Improvisation, and Process</h3>'
    '<p>Morimura’s self-portraiture is made through more than the reconstruction of finished masterpieces. ShugoArts’s text '
    'for <i>My Chronicle 1985–2018</i> presents his trajectory from early Polaroid-like on-site works to the art history and '
    'actress series. '
    '<sup class="sup-ref"><a href="#cite-16">*16</a></sup>'
    ' What matters here is that self-portraiture does not remain confined to the studio. It develops into a wider form that includes '
    'place, travel, exhibition, documentation, and process. For Morimura, the “I” is not a fixed subject. It is a provisional '
    'position remade again and again before places, images, and histories. In his photographs, even though the artist’s face appears '
    'repeatedly, the identity of the author does not become stronger. As the same face continues to enter different roles, the self '
    'appears as an accumulation of quotation and performance, not as a single core.</p>'
    '</div>'
)

SEC03 = (
    '<div class="essay">'
    '<h3 id="h3-08">Portrait (Van Gogh), 1985</h3>'
    '<p><a href="https://shugoarts.com/en/artists/morimura-yasumasa/" rel="noopener" target="_blank">Portrait (Van Gogh)</a> is an early '
    'work in which Morimura clarified his method of inserting his own body into Western art history. The National Museum of Art, Osaka '
    'registers the work as a photograph from 1985 and identifies its materials as C-print and offset print. '
    '<sup class="sup-ref"><a href="#cite-3">*3</a></sup>'
    ' The work is an attempt to recreate a masterpiece through photography, and at the same time to transform the painter’s '
    'self-portrait into the photographer’s own performance. In a painted self-portrait, the painter is both the subject who depicts '
    'and the object depicted. In Morimura’s case, that doubleness is layered with the performance of becoming another person, the '
    'documentary fixity of the photograph, and the viewer’s sense of recognition.</p>'
    '<h3 id="h3-09">Portrait (Futago), 1988 and 1989</h3>'
    '<p><a href="https://www.mori.art.museum/en/collection/5084/index.html" rel="noopener" target="_blank">Portrait (Futago)</a> is one '
    'of the representative works in which Morimura’s intervention into art history appears most sharply. Mori Art Museum holds the '
    'work as a 1989 piece and describes it as based on Manet’s <i>Olympia</i>, with Morimura performing the two roles in the image. '
    '<sup class="sup-ref"><a href="#cite-4">*4</a></sup>'
    ' SFMOMA’s collection page, meanwhile, registers a 1988 <i>Portrait (Futago)</i> as a chromogenic print, confirming that the '
    'same subject has circulated internationally through multiple versions and collections. '
    '<sup class="sup-ref"><a href="#cite-5">*5</a></sup>'
    ' In this work, questions of who is looked at, who is placed in a role of service, and who is treated as a subject of art history '
    'are layered within one body. Morimura’s photographs exceed the category of “disguise photography” because these '
    'overlapping roles destabilize the viewer’s position as well.</p>'
    '<h3 id="h3-10">An inner dialogue with Frida Kahlo, 2001</h3>'
    '<p><a href="https://www.ngv.vic.gov.au/explore/collection/work/148227/" rel="noopener" target="_blank">An inner dialogue with Frida '
    'Kahlo (Flower wreath and tears)</a> shows how Morimura’s self-portraiture extended beyond Western masterpieces to modern images '
    'of female authorship and pain. The National Museum of Art, Osaka’s retrospective text describes the “Frida in Me (Flower '
    'Wreath)” series as works that celebrate the love and death in Frida Kahlo’s life from Morimura’s own perspective. '
    '<sup class="sup-ref"><a href="#cite-2">*2</a></sup>'
    ' NGV’s collection entry also presents the work as a color photograph from 2001, confirming the reception of Morimura’s '
    'transformation into Kahlo within an international collection. '
    '<sup class="sup-ref"><a href="#cite-6">*6</a></sup>'
    ' Here, Morimura does not simply borrow Kahlo’s pain or self-image. He passes the strong image of Kahlo as an artist through '
    'his own body, showing how the “I” multiplies and wavers when it wears another face.</p>'
    '<h3 id="h3-11">From Photography to Video, Performance, and the Museum</h3>'
    '<p>Morimura’s method extends beyond individual photographs into video, performance, exhibition structure, and dialogue with '
    'museums. Kyoto City KYOCERA Museum of Art’s <i>Morimura Yasumasa: My Self-Portraits as a Theater of Labyrinths</i> introduces '
    'him as a pioneer of self-portraiture and explains that his transformations into masterpieces, historical figures, and film actresses '
    'make visible multiple identities, including gender and race. '
    '<sup class="sup-ref"><a href="#cite-10">*10</a></sup>'
    ' Hara Museum’s <i>Ego Obscura</i> was structured as a retrospective that included photographs alongside video, '
    'lecture-performance, and references to modern Japanese history. '
    '<sup class="sup-ref"><a href="#cite-7">*7</a></sup>'
    ' This expansion shows that Morimura’s photography is not completed within a single image. For him, photography is a medium that '
    'preserves the disguised body and, at the same time, a central device for creating a theatrical field that includes exhibition space, '
    'language, history, and the viewer.</p>'
    '</div>'
)

SEC04 = (
    '<div class="essay">'
    '<h3 id="h3-12">Photographic Quotation and Appropriation Through the Body</h3>'
    '<p>Morimura can be read alongside appropriation and the '
    '<a href="/en/movements/pictures-generation.html">Pictures Generation</a>'
    ' from the 1980s onward. Yet if his work is grouped too quickly under the “use of existing images,” his method becomes '
    'harder to see. In a 2018 interview, Morimura said that since 1985 he had used artificial eyes, makeup, and sets in an attempt to '
    'go beyond classifications such as male and female, East and West. '
    '<sup class="sup-ref"><a href="#cite-12">*12</a></sup>'
    ' The Metropolitan Museum of Art explains that Cindy Sherman, Richard Prince, Sherrie Levine, and others used film scenes, advertising '
    'photographs, and masterpieces of modern photography to examine codes of representation. '
    '<sup class="sup-ref"><a href="#cite-23">*23</a></sup>'
    ' Levine’s <i>After Walker Evans</i>, in which she rephotographed Walker Evans’s photographs from a catalogue, is also '
    'described by the Centre Pompidou as a work that questions authorship, originality, and authenticity. '
    '<sup class="sup-ref"><a href="#cite-24">*24</a></sup>'
    ' Morimura, by contrast, does more than rephotograph a source image as another photograph. He takes on the figure inside the image '
    'as his own role. The center of quotation shifts from photographic reproduction itself to the body, skin, gender, costume, and the '
    'position of the gaze.</p>'
    '<p>The comparison with Sherman becomes clearer when this difference is kept in view. MoMA explains that although Sherman is her own '
    'model, <i>Untitled Film Stills</i> are not considered self-portraits; instead, she places herself in dialogue with stereotypes of '
    'femininity. '
    '<sup class="sup-ref"><a href="#cite-18">*18</a></sup>'
    ' M+’s two-person exhibition, by contrast, presents Morimura and Sherman as artists who both use masquerade to explore relations '
    'among identity, mass media, and history, while remaking images from masterpieces, cinema, and popular culture from their own cultural '
    'backgrounds. '
    '<sup class="sup-ref"><a href="#cite-17">*17</a></sup>'
    ' The Art Newspaper also notes that the two were not aware of each other from the beginning of their careers, and that Morimura later '
    'learned about Sherman through a Japanese magazine. '
    '<sup class="sup-ref"><a href="#cite-19">*19</a></sup>'
    ' Their relation is therefore better understood as a parallel development rather than a single line of influence from the late 1970s '
    'through the 1980s, when photography began to address identity through performance, cinema, and reproduced images.</p>'
    '<p>Morimura has also been read in relation to Duchamp’s use of aliases and disguise. MEM’s exhibition text introduces the '
    '<i>Doublonage</i> series Morimura made in the 1980s, based on Duchamp’s <i>Chocolate Grinder</i> and <i>Fresh Widow</i>. '
    '<sup class="sup-ref"><a href="#cite-25">*25</a></sup>'
    ' QAGOMA’s commentary also reads <i>Doublonnage (Marcel)</i> as a work in which Morimura takes up the pose of Duchamp’s '
    'female alter ego Rrose Sélavy, as photographed by Man Ray, connecting it to reversals of gender roles and tensions between '
    'Eastern and Western images. '
    '<sup class="sup-ref"><a href="#cite-26">*26</a></sup>'
    ' In this light, Morimura’s photographs are not simply imitations of masterpieces. They can be placed as attempts to rearrange, '
    'through the body, who becomes the author, who becomes the model, and who is positioned as the viewer within existing images.</p>'
    '<h3 id="h3-13">Institutional Reception and International Reassessment</h3>'
    '<p>Morimura’s works have been received through museums, galleries, international exhibitions, and photographic collections. '
    'MoMA’s artist page registers Morimura as a Japanese artist and presents <i>Ambiguous Beauty (Aimai-no-bi)</i> as part of its '
    'collection. '
    '<sup class="sup-ref"><a href="#cite-13">*13</a></sup>'
    ' NGV’s artist page identifies him as a Japanese artist born in Osaka and shows, through multiple collection works, that his '
    'work has entered international museum collections. '
    '<sup class="sup-ref"><a href="#cite-14">*14</a></sup>'
    ' In Japan, institutions including The National Museum of Art, Osaka, Kyoto City KYOCERA Museum of Art, Hara Museum, and Artizon '
    'Museum have reread Morimura’s self-portraiture as a dialogue with art history, cinema, modern Japan, and institutional '
    'collections. Luhring Augustine’s CV lists his solo exhibitions, international exhibitions, and major collections, confirming '
    'the institutional reception of his work across photography, art, and performance. '
    '<sup class="sup-ref"><a href="#cite-11">*11</a></sup>'
    ' This breadth of reception helps explain why Morimura’s work is referenced within both Japanese contemporary art and '
    'discussions of photography after postmodernism.</p>'
    '<h3 id="h3-14">What Morimura Changed in Photographic History</h3>'
    '<p>Morimura matters in photographic history because he changed self-portraiture from a form that “photographs me” into one '
    'that shows which historical image the “I” takes on and where it slips out of that role. The Getty Museum’s exhibition '
    'on photographic reenactment places Morimura among artists who revisit art history and identity through photography. '
    '<sup class="sup-ref"><a href="#cite-8">*8</a></sup>'
    ' Japan Society’s catalogue introduction for <i>Ego Obscura</i> also presents more than thirty years of his work as a '
    'reassessment within global contemporary art. '
    '<sup class="sup-ref"><a href="#cite-15">*15</a></sup>'
    ' Morimura’s photographs do not record reality, nor do they simply express the artist’s interior life. By placing his own '
    'body inside figures from masterpieces, film stars, and news photographs, they show how photography makes history believable, how it '
    'produces subjects, and how it organizes the viewer’s desires. His work can therefore be positioned as an expansion of the act '
    'of photographing into looking, performing, quoting, and questioning.</p>'
    '</div>'
)

m['sections'] = [
    {"num": "§ 01 / 04", "title": "Background and Period", "body_html": SEC01},
    {"num": "§ 02 / 04", "title": "Core of the Work", "body_html": SEC02},
    {"num": "§ 03 / 04", "title": "Key Works, Method, and Medium", "body_html": SEC03},
    {"num": "§ 04 / 04", "title": "Reception and Place in Photographic History", "body_html": SEC04},
]

m['sources_html'] = sources([
    (1,  'https://shugoarts.com/en/artists/morimura-yasumasa/', 'ShugoArts — MORIMURA Yasumasa'),
    (2,  'https://www.nmao.go.jp/archive/en/exhibition/2016/the_self-portraits_of_yasumasa_morimura_my_art_my_story_my_art_history.html',
         'The National Museum of Art, Osaka — The Self-Portraits of YASUMASA MORIMURA'),
    (3,  'https://search.nmao.go.jp/en/detailLink?cls=col1&pkey=70245',
         'The National Museum of Art, Osaka — Portrait (Van Gogh)'),
    (4,  'https://www.mori.art.museum/en/collection/5084/index.html', 'Mori Art Museum — Portrait (Futago)'),
    (5,  'https://www.sfmoma.org/artwork/97.788/', 'SFMOMA — Portrait (Futago)'),
    (6,  'https://www.ngv.vic.gov.au/explore/collection/work/148227/',
         'National Gallery of Victoria — An inner dialogue with Frida Kahlo'),
    (7,  'https://www.haramuseum.or.jp/en/hara/exhibition/737/',
         'Hara Museum — Yasumasa Morimura: Ego Obscura, Tokyo 2020'),
    (8,  'https://www.getty.edu/art/exhibitions/photo_reenactment/downloads/reenactment_gallery_text.pdf',
         'J. Paul Getty Museum — Photo Reenactment gallery text'),
    (9,  'https://www.artizon.museum/en/exhibition/detail/73',
         'Artizon Museum — Jam Session: The Ishibashi Foundation Collection x Morimura Yasumasa'),
    (10, 'https://kyotocity-kyocera.museum/en/exhibition/20220312-0605',
         'Kyoto City KYOCERA Museum of Art — Morimura Yasumasa: My Self-Portraits as a Theater of Labyrinths'),
    (11, 'https://www.luhringaugustine.com/attachment/en/556d89b2cfaf3421548b4568/TextOneColumnWithFile/5ff8af530cb4d3558713ef83',
         'Luhring Augustine — Yasumasa Morimura CV'),
    (12, 'https://www.luhringaugustine.com/press/interviews-yasumasa-morimura',
         'Luhring Augustine / Artforum — Interviews: Yasumasa Morimura'),
    (13, 'https://www.moma.org/artists/7631-yasumasa-morimura', 'MoMA — Yasumasa Morimura'),
    (14, 'https://www.ngv.vic.gov.au/explore/collection/artist/9992/',
         'National Gallery of Victoria — Yasumasa Morimura'),
    (15, 'https://shop.japansociety.org/catalogues/yasumasa-morimura-ego-obscura',
         'Japan Society — Yasumasa Morimura: Ego Obscura catalogue'),
    (16, 'https://shugoarts.com/en/exhibitions/e00418/',
         'ShugoArts — Morimura Yasumasa: My Chronicle 1985–2018'),
    (17, 'https://www.mplus.org.hk/en/exhibitions/morimura-sherman/',
         'M+ Museum — Yasumasa Morimura and Cindy Sherman: Masquerades'),
    (18, 'https://www.moma.org/collection/works/56618', 'MoMA — Cindy Sherman, Untitled Film Still #21'),
    (19, 'https://www.theartnewspaper.com/2025/03/27/cindy-sherman-and-yasumasa-morimura-joining-the-dots-between-a-pair-of-photographic-visionaries',
         'The Art Newspaper — Cindy Sherman and Yasumasa Morimura: joining the dots between a pair of photographic visionaries'),
    (20, 'https://realkyoto.jp/article/interview_morimura-yasumasa/', 'REALKYOTO — Interview: Morimura Yasumasa'),
    (21, 'https://www.artlogue.org/node/3979', 'ARTLOGUE — Interview: Morimura Yasumasa No. 02'),
    (22, 'https://www.kateigaho.com/culture/hobby/179428',
         'Kateigaho — Why did Van Gogh paint so many self-portraits? Morimura Yasumasa interview'),
    (23, 'https://www.metmuseum.org/art/collection/search/267214',
         'The Metropolitan Museum of Art — Sherrie Levine, After Walker Evans: 4'),
    (24, 'https://www.centrepompidou.fr/en/ressources/oeuvre/crbd8MA',
         'Centre Pompidou — Sherrie Levine, After Walker Evans'),
    (25, 'https://mem-inc.jp/2004/10/20/fujimoto_morimura2_e/', 'MEM — This isn’t a Duchamp, or is it?'),
    (26, 'https://collection.qagoma.qld.gov.au/node/54691', 'QAGOMA — Morimura’s alter-egos'),
    (27, 'https://www.keenecenter.org/download_files/MorimuraSpeech.pdf',
         'Donald Keene Center — Yasumasa Morimura, Why I Posed as Yukio Mishima'),
])

m['cite_ids'] = list(range(1, 28))
m['supref_ids'] = list(range(1, 28))

m['site_directory_html'] = (
    '<nav class="site-directory-links" aria-label="Site links" data-nosnippet>\n'
    '        <div class="site-directory-group site-directory-group-contextual">\n'
    '          <div class="site-directory-label">Related people &amp; photographers</div>\n'
    '          <div class="site-directory-items">'
    '<a href="/en/photographers/sherman.html">Cindy Sherman</a>'
    '<a href="/en/photographers/sherrie-levine.html">Sherrie Levine</a>'
    '</div>\n'
    '        </div>\n'
    '        <div class="site-directory-group site-directory-group-contextual">\n'
    '          <div class="site-directory-label">Related movements</div>\n'
    '          <div class="site-directory-items">'
    '<a href="/en/movements/conceptual-art.html">Conceptual Art</a>'
    '<a href="/en/movements/staged-photography.html">Staged Photography</a>'
    '<a href="/en/movements/pictures-generation.html">Pictures Generation</a>'
    '</div>\n'
    '        </div>\n'
    '      </nav>'
)

m['further_reading_html'] = (
    '<ul class="ph-further-links">\n'
    '<li><a href="https://www.moma.org/artists/7631-yasumasa-morimura" rel="noopener" target="_blank">MoMA — Yasumasa Morimura (artist page)</a></li>\n'
    '<li><a href="https://www.ngv.vic.gov.au/explore/collection/artist/9992/" rel="noopener" target="_blank">National Gallery of Victoria — Yasumasa Morimura</a></li>\n'
    '<li><a href="https://www.haramuseum.or.jp/en/hara/exhibition/737/" rel="noopener" target="_blank">Hara Museum — Ego Obscura</a></li>\n'
    '<li><a href="https://www.luhringaugustine.com/attachment/en/556d89b2cfaf3421548b4568/TextOneColumnWithFile/5ff8af530cb4d3558713ef83" rel="noopener" target="_blank">Luhring Augustine — Yasumasa Morimura CV</a></li>\n'
    '<li><a href="https://shop.japansociety.org/catalogues/yasumasa-morimura-ego-obscura" rel="noopener" target="_blank">Japan Society — Ego Obscura catalogue</a></li>\n'
    '</ul>'
)


# ============================================================
# TASK B: CREATE kenta-cobayashi.html — full new entry
# ============================================================

KC_ENTRY_META = (
    '<dl class="entry-meta">\n'
    '      <dt>Entry</dt><dd>No. 049</dd>\n'
    '      <dt>Category</dt><dd>Photographer</dd>\n'
    '      <dt>Country</dt><dd><a href="/en/countries/japan.html">Japan</a></dd>\n'
    '      <dt>Years</dt><dd>1992–</dd>\n'
    '      <dt>Period</dt><dd><a href="/en/eras/2010.html">2010s</a> — <a href="/en/eras/2020.html">2020s</a></dd>\n'
    '      <dt>Movement</dt><dd>Digital Photography</dd>\n'
    '      <dt>Updated</dt><dd>2026.06.20</dd>\n'
    '    </dl>'
)

KC_JSONLD = [
    json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": "https://eyescosmos.github.io/en/photographers/kenta-cobayashi.html",
                "url": "https://eyescosmos.github.io/en/photographers/kenta-cobayashi.html",
                "name": "Kenta Cobayashi | #smudge, GUI, and Photography in the AI Era | Photo Coordinates",
                "description": "Kenta Cobayashi works with photography through #smudge, Tokyo Débris, and #copycat as a mutable image formed among image-editing software, pixels, bodily gestures, AI generation, and print.",
                "inLanguage": "en",
                "isPartOf": {"@type": "WebSite", "name": "Photo Coordinates", "url": "https://eyescosmos.github.io/en/"},
                "about": {"@id": "https://eyescosmos.github.io/en/photographers/kenta-cobayashi.html#person"}
            },
            {
                "@type": "Person",
                "@id": "https://eyescosmos.github.io/en/photographers/kenta-cobayashi.html#person",
                "name": "Kenta Cobayashi",
                "alternateName": "小林健太",
                "description": "Kenta Cobayashi works with photography through #smudge, Tokyo Débris, and #copycat as a mutable image formed among image-editing software, pixels, bodily gestures, AI generation, and print.",
                "url": "https://eyescosmos.github.io/en/photographers/kenta-cobayashi.html",
                "jobTitle": "Photographer",
                "birthDate": "1992",
                "nationality": {"@type": "Country", "name": "Japan"},
                "subjectOf": {"@id": "https://eyescosmos.github.io/en/photographers/kenta-cobayashi.html"}
            }
        ]
    }, ensure_ascii=False, indent=2),
    json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Photo Coordinates", "item": "https://eyescosmos.github.io/en/"},
            {"@type": "ListItem", "position": 2, "name": "Photographers", "item": "https://eyescosmos.github.io/en/archive.html"},
            {"@type": "ListItem", "position": 3, "name": "Kenta Cobayashi"}
        ]
    }, ensure_ascii=False, indent=2)
]

KC_SEC01 = (
    '<div class="essay"><p>'
    'Kenta Cobayashi was born in Kanagawa Prefecture in 1992 and is based in Tokyo and Shonan. His official profile describes him as an '
    'artist whose work moves across photography, digital media, sculpture, and installation, and records <i>Everything_1</i> in 2016, '
    '<i>Everything_2</i> in 2020, and acquisitions by Fondazione Prada, Fondation Louis Vuitton, and the Asian Art Museum.'
    '<sup class="sup-ref"><a href="#cite-1">*1</a></sup>'
    ' In an interview with HUNGER, Cobayashi recalls that his grandfather and father liked Apple computers, that he encountered '
    'Macintosh and iMac applications from childhood, and that one of his first memories of digitally altered photography was drawing '
    'in Kid Pix on a photograph reduced to 256 colors.'
    '<sup class="sup-ref"><a href="#cite-2">*2</a></sup>'
    ' This background suggests the sensibility of a generation for whom photographs were never only objects altered after the fact, '
    'but images that could be touched, stored, and shared on screen from the beginning. In a TOKION interview, Cobayashi says that '
    'he became interested in contemporary art in high school, studied painting and drawing at university, and met Taisuke Koyama and '
    '<a href="/en/photographers/daisuke-yokota.html">Daisuke Yokota</a> in a university class in 2012.'
    '<sup class="sup-ref"><a href="#cite-3">*3</a></sup>'
    ' That encounter led to zines made from film photographs, blogs, and group exhibitions, creating an early environment in which '
    'cameras, painting, the internet, printed matter, and collaboration occupied the same space. '
    '<i><a href="https://newfavebooks.com/everything1-kenta-cobayashi-html/" rel="noopener" target="_blank">Everything_1</a></i>, '
    'published in 2016, was introduced against the background of images becoming impossible to control once released into cyberspace, '
    'showing that his photography was situated from the start between printed matter and networked circulation.'
    '<sup class="sup-ref"><a href="#cite-5">*5</a></sup>'
    ' Bijutsu Techo introduces Cobayashi as an artist known for <i>#smudge</i>, in which parts of photographs he shot himself are '
    'transformed through image-editing software into painterly strokes, and notes that he has expanded photographic expression into '
    'objects, performance, CG, VR, NFTs, and fashion.'
    '<sup class="sup-ref"><a href="#cite-6">*6</a></sup>'
    '</p></div>'
)

KC_SEC02 = (
    '<div class="essay">'
    '<h3 id="h3-01">The Word Shashin, Vision, and the Editing Screen</h3>'
    '<p>When Cobayashi refers to <i>shin</i>, or “truth,” he is not adding an abstract idea from outside the work. '
    'In a TOKION interview, he says that photography made it possible to externalize vision and share it with others, and that the '
    'bitmap and layer structures of Photoshop reflect the activities of human visual cognition.'
    '<sup class="sup-ref"><a href="#cite-3">*3</a></sup>'
    ' In the same passage, he reads the Japanese word <i>shashin</i> as “copying the truth” and asks what truth is, '
    'describing it as something close to reality as it is lived and experienced.'
    '<sup class="sup-ref"><a href="#cite-3">*3</a></sup>'
    ' This statement appears less as the starting point of his work than as a question he returns to after snapshots, blogs, zines, '
    'Photo Booth, the iPhone, and Photoshop operations have shaped his way of making images. The shashasha description of '
    '<i><a href="https://www.shashasha.co/en/book/everything-2" rel="noopener" target="_blank">Everything_2</a></i> also states that '
    'Cobayashi filters impressions of the city, fashion, and faces through technology, history, and his own sensibility, while '
    'exploring the photograph’s ability to depict truth as “the reality captured” in the Japanese word.'
    '<sup class="sup-ref"><a href="#cite-7">*7</a></sup>'
    ' C4 Journal expands this etymological point by noting that while the English word “photography” leans toward a '
    'mechanical metaphor of writing with light, the Japanese word <i>shashin</i> carries the question of copying truth or reality.'
    '<sup class="sup-ref"><a href="#cite-8">*8</a></sup>'
    ' In Cobayashi’s work, “truth” is not a test of whether an image is correct. It names the sense of reality that '
    'can remain after an image has passed through the editing screen, the print, the exhibition space, and the environments in which '
    'it is shared.</p>'
    '<h3 id="h3-02">#smudge: Making the Act of Editing Visible</h3>'
    '<p><i><a href="https://www.kentacobayashi.com/portfolio2025-en" rel="noopener" target="_blank">#smudge</a></i> stretches and '
    'mixes the color data of photographs with Photoshop’s smudge tool, making the boundaries between figures, city, light, and '
    'background fluid. His official portfolio explains that the series dissolves the meanings assigned to the photograph and brings '
    'forward the act of editing, which is usually hidden behind photographic production.'
    '<sup class="sup-ref"><a href="#cite-4">*4</a></sup>'
    ' The processing does not function as a special effect that breaks reality into fantasy. It returns to the surface of the '
    'photograph the conditions under which images are now viewed through smartphones, computers, social media, and '
    'image-generation tools. In the TOKION interview, Cobayashi says that he uses the smudge tool as a function for blurring '
    'boundaries, adjusting its settings while treating it as an action close to what he did when he studied painting.'
    '<sup class="sup-ref"><a href="#cite-3">*3</a></sup>'
    ' These strokes are not painterly decoration. They are a way of leaving traces of the body in a digital image through a mouse '
    'or finger, a screen, and the response of software.</p>'
    '<h3 id="h3-03">The Pixel Grid, the Body, and Urban Memory</h3>'
    '<p>Cobayashi also pays close attention to the grid that appears when a digital image is enlarged. In TOKION, he states that '
    'the bitmap and layer structures of Photoshop reflect human visual cognition, and that this inquiry leads into his exploration '
    'of photographic expression.'
    '<sup class="sup-ref"><a href="#cite-3">*3</a></sup>'
    ' In the “Insectautomobilogy / What is an aesthetic?” section of his official portfolio, he treats the pixel, the '
    'smallest unit in Photoshop, as a “Universe of the Grid,” and describes it as a computational logic of homogeneity '
    'and reproducibility.'
    '<sup class="sup-ref"><a href="#cite-4">*4</a></sup>'
    ' In an interview with Art Squiggle Yokohama, he describes how the nine grids he saw in the Lascaux exhibition and his '
    'middle-school experience with a web service made in Adobe Flash led him to think of the grid not only as digital, but as a '
    'form humans have used to communicate concepts.'
    '<sup class="sup-ref"><a href="#cite-10">*10</a></sup>'
    ' This grid does not turn the photograph into a stable window onto reality. It becomes a field where urban memory, software '
    'operations, accidental color, and noise collide. When Cobayashi alters familiar images such as Shibuya streets, hair, signs, '
    'glass, flowers, and cats, the subjects move toward abstraction while still preserving the sensation of images being produced '
    'in the city, circulated, and returned to the body.</p>'
    '<h3 id="h3-04">Photography Extending from Flat Image to Object and Space</h3>'
    '<p>Cobayashi’s photographs do not end as flat prints. His 2021 exhibition “#smudge” combined still images, '
    'murals, video, reliefs, lenticular works, and lighting, using fluid color to blur the boundaries of the space.'
    '<sup class="sup-ref"><a href="#cite-4">*4</a></sup>'
    ' In <i><a href="https://www.kentacobayashi.com/portfolio2025-en" rel="noopener" target="_blank">Tokyo Débris</a></i> '
    'in 2022, earlier works and new images were decomposed and reassembled as an installation involving sculpture, video, '
    'flooring, and reflection.'
    '<sup class="sup-ref"><a href="#cite-4">*4</a></sup>'
    ' His official portfolio describes the exhibition as an interaction among physical objects, virtual images, and spatial elements.'
    '<sup class="sup-ref"><a href="#cite-4">*4</a></sup>'
    ' UESHIMA MUSEUM COLLECTION also explains that Cobayashi processes snapshots he has taken himself through CG and other means, '
    'interpreting photography as a plastic medium.'
    '<sup class="sup-ref"><a href="#cite-13">*13</a></sup>'
    ' Here photography becomes less a single image fixed on paper than something that moves between matter and information through '
    'acrylic, metal, CG, video, NFTs, and reflected light.</p>'
    '<h3 id="h3-05">Comparative Lines Drawn by International Criticism</h3>'
    '<p>International criticism has read Cobayashi’s work as an intersection of photography, painting, software, and urban '
    'experience. In its discussion of <i>Everything_2</i>, C4 Journal refers to Roy Lichtenstein’s <i>Brushstrokes</i> as an '
    'example in which the brushstroke itself becomes a sign of media.'
    '<sup class="sup-ref"><a href="#cite-8">*8</a></sup>'
    ' In Lichtenstein’s work, the gestural mark of Abstract Expressionism is translated into screenprint, simulated halftone, '
    'and sculpture, turning the painterly gesture into a sign shaped by mass reproduction. In Cobayashi’s work, the stroke also '
    'appears through functions that carry the metaphors of older tools: Photoshop’s brush, dodge, burn, eraser, and stamp. '
    'C4 Journal further contrasts Ryoji Ikeda’s conversion of sound into informational structure with Cobayashi’s response '
    'to urban noise and daily floods of images, where the excessive plasticity of digital images comes to the foreground.'
    '<sup class="sup-ref"><a href="#cite-8">*8</a></sup>'
    ' In its review of <i>Everything_2</i>, Collector Daily argues that one of the tasks for a twenty-first-century photographer is '
    'to turn the expanding functions of photo-editing software into a personal visual language.'
    '<sup class="sup-ref"><a href="#cite-9">*9</a></sup>'
    ' The review invokes Gerhard Richter because Cobayashi extracts bands of pixels from parts of an image and stretches them across '
    'the screen, building layers of color in a way that recalls paint spread with a squeegee. Collector Daily also notes that screens '
    'seen as if from above and architectural compositions blur like water, with the fluidization of geometry recalling Lucas '
    'Samaras’s manipulated Polaroids.'
    '<sup class="sup-ref"><a href="#cite-9">*9</a></sup></p>'
    '<h3 id="h3-06">Photo Diaries, Social Media, and the International Exhibition Context</h3>'
    '<p>The 2016 Fondazione Prada Osservatorio exhibition “GIVE ME YESTERDAY” is important for understanding '
    'Cobayashi’s international context. The exhibition addressed the changing form of the photo diary among younger generations, '
    'against the spread of photographic devices since the 2000s and the circulation of images on digital platforms.'
    '<sup class="sup-ref"><a href="#cite-11">*11</a></sup>'
    ' The exhibition text names Nan Goldin, Larry Clark, Richard Billingham, and Wolfgang Tillmans as predecessors, and explains '
    'that documentary immediacy and spontaneity had shifted toward the control of the gaze between those who look and those who are '
    'looked at.'
    '<sup class="sup-ref"><a href="#cite-11">*11</a></sup>'
    ' Tillmans matters here because his photographs of everyday life and youth culture showed how images rooted in private record '
    'could take on structures beyond the diary when placed in exhibition space. The Philadelphia Museum of Art explains that Tillmans '
    'has connected different kinds of photographs, including social images, darkroom abstractions, and copies, while examining the '
    'process by which photography becomes a meaningful image.'
    '<sup class="sup-ref"><a href="#cite-17">*17</a></sup>'
    ' Within the Fondazione Prada context, Cobayashi can be understood as an artist who begins from photo diaries and snapshots, '
    'yet moves away from simply presenting intimacy. Through image editing, he shifts the boundaries among what is seen, what is '
    'remembered, and what is shared.</p>'
    '<h3 id="h3-07">#copycat: Reproduction and Perception in the Age of AI</h3>'
    '<p>Cobayashi’s 2025 solo exhibition '
    '<i><a href="https://waitingroom.jp/en/exhibitions/copycat/" rel="noopener" target="_blank">#copycat</a></i>'
    ' at WAITINGROOM shows his interest moving toward the relation between AI-generated images and photography history. The '
    'exhibition text describes Cobayashi as an artist who has dramatically transformed his own images through digital means, '
    'exploring what it means to “capture truth” amid the fluidity of urban images and memories of digital environments.'
    '<sup class="sup-ref"><a href="#cite-12">*12</a></sup>'
    ' The exhibition introduced a new series in which data from earlier works was fed into generative AI and layered with images '
    'of cats; AI and cats were positioned as “other species looking at humans” that slip away from human control.'
    '<sup class="sup-ref"><a href="#cite-12">*12</a></sup>'
    ' The English exhibition text focuses on Midjourney’s function of generating four variations from a single prompt at once, '
    'and explains that presenting multiple images derived from one prompt as belonging to a single work points to another form of '
    'reproductive art in the age of AI.'
    '<sup class="sup-ref"><a href="#cite-12">*12</a></sup>'
    ' The exhibition text by Yagi Yoshida also refers to Eadweard Muybridge’s sequential photography, which broke motion into '
    'parts and gave humans a way to see time, and reads Cobayashi’s work as an attempt to redefine spatial perception in the '
    'age of AI.'
    '<sup class="sup-ref"><a href="#cite-12">*12</a></sup>'
    ' Photography history appears here not as a citation of past forms, but as a way to reconsider, through the AI interface, the '
    'questions that have emerged whenever photography has altered the terms of perception, motion, editing, and reproduction.</p>'
    '</div>'
)

KC_SEC03 = (
    '<div class="essay">'
    '<h3 id="h3-08">#smudge</h3>'
    '<p><i><a href="https://www.kentacobayashi.com/portfolio2025-en" rel="noopener" target="_blank">#smudge</a></i> is one of '
    'Cobayashi’s central series. By stretching the color data of photographs with the smudge tool, it works in the area '
    'between photography and painting, screen operation and bodily movement. His official portfolio explains that all the photographs '
    'used in the series were shot by Cobayashi himself, linking his bodily experience as a photographer to a painterly mode of making.'
    '<sup class="sup-ref"><a href="#cite-4">*4</a></sup>'
    ' The series does not lose its photographic character through processing. Its core lies in the way the trace of processing moves '
    'to the side that produces photographic meaning.</p>'
    '<h3 id="h3-09">Tokyo Débris and Relief</h3>'
    '<p><i><a href="https://www.kentacobayashi.com/portfolio2025-en" rel="noopener" target="_blank">Tokyo Débris</a></i> '
    'combines fragments of the city, earlier images, CG environments, and reflective objects, reassembling photography as a spatial '
    'event. His official portfolio describes the series as an extension of the method of <i>#smudge</i>: digital collages, videos, '
    'and sculptures dealing with urban memory, digital debris, and reflective phantoms.'
    '<sup class="sup-ref"><a href="#cite-4">*4</a></sup>'
    ' The same portfolio records <i>Relief: Brushstrokes</i> as a series in which photographic prints are transferred onto iron, '
    'aluminum, and other materials, using the bending of metal to examine the point of contact between flatness and mass, vision '
    'and touch.'
    '<sup class="sup-ref"><a href="#cite-4">*4</a></sup>'
    ' UESHIMA MUSEUM COLLECTION also explains that Cobayashi processes snapshots he has taken himself through CG and other means, '
    'interpreting photography as a plastic medium.'
    '<sup class="sup-ref"><a href="#cite-13">*13</a></sup></p>'
    '<h3 id="h3-10">Everything_2, #copycat, and Flowers</h3>'
    '<p><i><a href="https://www.shashasha.co/en/book/everything-2" rel="noopener" target="_blank">Everything_2</a></i> can be '
    'read as a photobook that places impressions of city nights, people, fashion, faces, and technology between photography, image, '
    'and painting through digital manipulation. Collector Daily argues that in the book Cobayashi begins with nighttime snapshots '
    'and urban scenes, then uses software-based gestures, marks, and distortions to break down the original images and move '
    'representation toward abstraction.'
    '<sup class="sup-ref"><a href="#cite-9">*9</a></sup>'
    ' In <i>#copycat</i>, this problem shifts to the interface of generative AI. WAITINGROOM records lenticular works such as '
    '<i>Tokyo Debris with Garden</i>, <i>flowers</i>, and <i>Tokyo Debris and flowers</i>, along with the four-channel video '
    '<i>tokyo debris and flowers with cat #video</i>, as works in the exhibition.'
    '<sup class="sup-ref"><a href="#cite-12">*12</a></sup>'
    ' Writing about <i>Flowers</i>, a 2026 book by Kenta Cobayashi and Tyrone Williams, Collector Daily states that the two '
    'artists have been positioned at the leading edge of digital media over the past decade.'
    '<sup class="sup-ref"><a href="#cite-14">*14</a></sup>'
    ' Dazed introduces the book as showing AI-enhanced vision that retains texture and depth, and as pointing to the possibility '
    'of a new language for digital photographic technology.'
    '<sup class="sup-ref"><a href="#cite-15">*15</a></sup>'
    ' Seen through this sequence, Cobayashi’s work moves among photobooks, exhibitions, AI generation, and collaboration, '
    'showing how the unit of photography expands from a single print into data, series, interface, and forms of circulation.</p>'
    '</div>'
)

KC_SEC04 = (
    '<div class="essay"><p>'
    'When placing Kenta Cobayashi within photography history, it is not enough to describe him as an artist of digital processing. '
    'His work asks how a sense of reality is formed when reality itself is already experienced through smartphones, image-editing '
    'software, social media, CG, and AI interfaces. In relation to the Art Tower Mito exhibition “Hello World: For the '
    'Post-Human Age,” his official portfolio positions Cobayashi as an artist representing the digital-native generation and '
    'explains that he visualized the gaps and resonances between technology and bodily sensation.'
    '<sup class="sup-ref"><a href="#cite-4">*4</a></sup>'
    ' From this perspective, Cobayashi rethinks the conditions of photography in a direction different from '
    '<a href="/en/photographers/hiroshi-sugimoto.html">Hiroshi Sugimoto</a>'
    ', who turns toward the principles of time and light, and '
    '<a href="/en/photographers/daisuke-yokota.html">Daisuke Yokota</a>'
    ', who turns toward material repetition and damage. The connection to Thomas Ruff is clearest when approached through '
    'Cobayashi’s own account of his making. In TOKION, Cobayashi says that before producing the 1.6-by-2.3-meter '
    '<i>Megazine</i> in 2015, he read Ruff’s ideas on contemporary photography and became aware of the importance of size '
    'in photography.'
    '<sup class="sup-ref"><a href="#cite-3">*3</a></sup>'
    ' Ruff himself is described as an artist who has enlarged photographic prints to the monumental scale of painting and used '
    'methods ranging from manual retouching to digital processing to examine the grammar of photography.'
    '<sup class="sup-ref"><a href="#cite-16">*16</a></sup>'
    ' Ruff is therefore less a direct predecessor than a reference point for thinking about how photography moves from small '
    'record to large-scale image, and further becomes an artwork involving pixels and data processing. The connection to '
    'Wolfgang Tillmans is most clearly approached through the photo-diary context established by Fondazione Prada’s '
    '“GIVE ME YESTERDAY.” That exhibition examined how young artists transformed everyday life and private rituals '
    'into photographs in an environment where images were constantly shared on digital platforms.'
    '<sup class="sup-ref"><a href="#cite-11">*11</a></sup>'
    ' Tillmans is an artist who crosses social snapshots, still lifes, darkroom abstractions, copies, and exhibition arrangements, '
    'showing how photography can be a record of everyday life while also becoming a question of abstract composition and spatial '
    'display.'
    '<sup class="sup-ref"><a href="#cite-17">*17</a></sup>'
    ' Cobayashi does not simply inherit that intimate lineage of the photo diary. He breaks down snapshots through digital '
    'operations and turns them into memory and noise for an age of shared images. His position becomes clearer when his work is '
    'understood as a reconsideration of how photography produces a sense of reality within the current image environment, one '
    'that includes editing screens, pixels, prints, space, and AI.'
    '</p></div>'
)

KC_SOURCES = sources([
    (1,  'https://www.kentacobayashi.com/biography', 'Kenta Cobayashi official website — Biography'),
    (2,  'https://hungermag.com/editorial/kenta-cobayashi-blurring-the-line-between-digital-fantasy-and-reality',
         'HUNGER — Kenta Cobayashi, blurring the line between digital fantasy and reality'),
    (3,  'https://tokion.jp/en/2021/04/13/kenta-cobayashi-genre-defying-photography/',
         'TOKION — Kenta Cobayashi on the thinking behind his genre-defying photography'),
    (4,  'https://www.kentacobayashi.com/portfolio2025-en', 'Kenta Cobayashi official website — Portfolio 2025'),
    (5,  'https://newfavebooks.com/everything1-kenta-cobayashi-html/', 'Newfave — EVERYTHING_1 Kenta Cobayashi'),
    (6,  'https://bijutsutecho.com/artists/2065', 'Bijutsu Techo — Kenta Cobayashi'),
    (7,  'https://www.shashasha.co/en/book/everything-2', 'shashasha — EVERYTHING_2, Kenta COBAYASHI'),
    (8,  'https://c4journal.com/kenta-cobayashi/', "C4 Journal — CHROMATIC ANGULAR CACOPHONY: Kenta Cobayashi’s Everything 2"),
    (9,  'https://collectordaily.com/kenta-cobayashi-everything_2/', 'Collector Daily — Kenta Cobayashi, EVERYTHING_2'),
    (10, 'https://note.com/artsquiggle/n/n9137de475dcd?hl=en', 'Artist Note vol.4 Kenta Cobayashi — Art Squiggle Yokohama 2024'),
    (11, 'https://www.fondazioneprada.org/project/give-me-yesterday/?lang=en', 'Fondazione Prada — GIVE ME YESTERDAY'),
    (12, 'https://waitingroom.jp/en/exhibitions/copycat/', 'WAITINGROOM — Kenta Cobayashi #copycat'),
    (13, 'https://www.ueshima-collection.com/artist-list/102', 'UESHIMA MUSEUM COLLECTION — Kenta Cobayashi'),
    (14, 'https://collectordaily.com/kenta-cobayashi-tyrone-williams-flowers/', 'Collector Daily — Kenta Cobayashi / Tyrone Williams, Flowers'),
    (15, 'https://www.dazeddigital.com/art-photography/article/70010/1/springtime-photo-book-round-up-erotica-helmut-newton-inez-vinoodh',
         'Dazed — 8 new photo books for springtime / Flowers'),
    (16, 'https://www.davidzwirner.com/artists/thomas-ruff', 'David Zwirner — Thomas Ruff / Biography'),
    (17, 'https://www.philamuseum.org/exhibitions/in-dialogue-wolfgang-tillmans',
         'Philadelphia Museum of Art — In Dialogue: Wolfgang Tillmans'),
])

KC_SITE_DIR = (
    '<nav class="site-directory-links" aria-label="Site links" data-nosnippet>\n'
    '        <div class="site-directory-group site-directory-group-contextual">\n'
    '          <div class="site-directory-label">Related people &amp; photographers</div>\n'
    '          <div class="site-directory-items">'
    '<a href="/en/photographers/daisuke-yokota.html">Daisuke Yokota</a>'
    '<a href="/en/photographers/hiroshi-sugimoto.html">Hiroshi Sugimoto</a>'
    '<a href="/en/photographers/thomas-ruff.html">Thomas Ruff</a>'
    '<a href="/en/photographers/wolfgang-tillmans.html">Wolfgang Tillmans</a>'
    '</div>\n'
    '        </div>\n'
    '        <div class="site-directory-group site-directory-group-contextual">\n'
    '          <div class="site-directory-label">Related movements</div>\n'
    '          <div class="site-directory-items">'
    'Digital Photography'
    '<span class="kw-sep"> / </span>'
    'Post-Internet'
    '<span class="kw-sep"> / </span>'
    'Contemporary Photography'
    '</div>\n'
    '        </div>\n'
    '      </nav>'
)

KC_FURTHER = (
    '<div class="ph-book">'
    '<div class="ph-book__title"><a href="https://www.kentacobayashi.com/portfolio2025-en" rel="noopener" target="_blank">Portfolio 2025</a></div>'
    '<div class="ph-book__meta">Kenta Cobayashi official website</div>'
    '<div class="ph-book__note">A useful source for statements, major exhibitions, #smudge, Tokyo Débris, Relief, and AI-related works.</div>'
    '</div>'
    '<div class="ph-book">'
    '<div class="ph-book__title"><a href="https://www.shashasha.co/en/book/everything-2" rel="noopener" target="_blank">Everything_2</a></div>'
    '<div class="ph-book__meta">Newfave / shashasha, 2020</div>'
    '<div class="ph-book__note">A photobook that connects the etymological question of “photography as captured reality” with the city, fashion, faces, and technology.</div>'
    '</div>'
    '<div class="ph-book">'
    '<div class="ph-book__title"><a href="https://c4journal.com/kenta-cobayashi/" rel="noopener" target="_blank">CHROMATIC ANGULAR CACOPHONY: Kenta Cobayashi’s Everything 2</a></div>'
    '<div class="ph-book__meta">C4 Journal / American Suburb X, 2021</div>'
    '<div class="ph-book__note">A critical reference for reading Cobayashi through Lichtenstein, Ryoji Ikeda, and the tool metaphors of Photoshop.</div>'
    '</div>'
    '<div class="ph-book">'
    '<div class="ph-book__title"><a href="https://collectordaily.com/kenta-cobayashi-everything_2/" rel="noopener" target="_blank">Kenta Cobayashi, EVERYTHING_2</a></div>'
    '<div class="ph-book__meta">Collector Daily, 2020</div>'
    '<div class="ph-book__note">A review of <i>Everything_2</i> from the perspective of twenty-first-century image-editing software and personal visual language.</div>'
    '</div>'
)

pages['kenta-cobayashi.html'] = {
    "title": "Kenta Cobayashi | #smudge, GUI, and Photography in the AI Era | Photo Coordinates",
    "meta_description": (
        "Kenta Cobayashi works with photography through #smudge, Tokyo Débris, and #copycat as a mutable image formed among "
        "image-editing software, pixels, bodily gestures, AI generation, and print. His work opens the intimacy of the snapshot "
        "onto the ways reality is edited in digital environments."
    ),
    "canonical": "https://eyescosmos.github.io/en/photographers/kenta-cobayashi.html",
    "hreflang": {
        "ja": "https://eyescosmos.github.io/photographers/kenta-cobayashi.html",
        "en": "https://eyescosmos.github.io/en/photographers/kenta-cobayashi.html",
        "x-default": "https://eyescosmos.github.io/photographers/kenta-cobayashi.html"
    },
    "og": {
        "type": "article",
        "site_name": "Photo Coordinates",
        "title": "Kenta Cobayashi | #smudge, GUI, and Photography in the AI Era | Photo Coordinates",
        "description": "Kenta Cobayashi works with photography through #smudge, Tokyo Débris, and #copycat as a mutable image formed among image-editing software, pixels, bodily gestures, AI generation, and print.",
        "url": "https://eyescosmos.github.io/en/photographers/kenta-cobayashi.html",
        "locale": "en_US",
        "image": "https://eyescosmos.github.io/assets/ogp-default.png",
        "image:width": "1200",
        "image:height": "630",
        "image:alt": "Photo Coordinates"
    },
    "twitter": {
        "image": "https://eyescosmos.github.io/assets/ogp-default.png",
        "card": "summary_large_image",
        "title": "Kenta Cobayashi | #smudge, GUI, and Photography in the AI Era | Photo Coordinates",
        "description": "Kenta Cobayashi works with photography through #smudge, Tokyo Débris, and #copycat as a mutable image formed among image-editing software, pixels, bodily gestures, AI generation, and print."
    },
    "has_ga": True,
    "h1": "Kenta Cobayashi",
    "years": "1992–",
    "entry_meta_html": KC_ENTRY_META,
    "jsonld": KC_JSONLD,
    "lead_html": (
        '<p class="lead">Kenta Cobayashi works with photography through #smudge, Tokyo Débris, and #copycat as a mutable '
        'image formed among image-editing software, pixels, bodily gestures, AI generation, and print. His work opens the '
        'intimacy of the snapshot onto the ways reality is edited in digital environments.</p>'
    ),
    "thesis_label": "What this photographer changed",
    "thesis_html": (
        "Cobayashi shifted the site of photography from the world in front of the camera to include the editing screen, GUI, pixels, "
        "layers, and even the options presented by generative AI. In his work, the screen after the snapshot becomes a field of "
        "perception as important as the act of taking the photograph. The question of photography therefore moves from whether an "
        "object has been recorded accurately to the environments in which images are generated, altered, shared, and accepted as reality."
    ),
    "keywords_html": (
        '<div class="page-keywords"><b>Keywords:</b>'
        'Digital Photography'
        '<span class="kw-sep">/</span>#smudge'
        '<span class="kw-sep">/</span>GUI'
        '<span class="kw-sep">/</span>Pixels'
        '<span class="kw-sep">/</span>AI-Generated Images'
        '<span class="kw-sep">/</span>Post-Internet'
        '</div>'
    ),
    "view_works_note": "This site does not reproduce artwork images. Images and exhibition records can be viewed through the official, gallery, publisher, and collection pages below.",
    "view_works_links_html": (
        '<div class="links">'
        '<a class="chip-link" href="https://www.kentacobayashi.com/portfolio2025-en" target="_blank" rel="noopener">Official Portfolio 2025 — #smudge / Tokyo Débris / Relief ↗</a>'
        '<a class="chip-link" href="https://waitingroom.jp/en/exhibitions/copycat/" target="_blank" rel="noopener">WAITINGROOM — #copycat ↗</a>'
        '<a class="chip-link" href="https://newfavebooks.com/everything1-kenta-cobayashi-html/" target="_blank" rel="noopener">Newfave — EVERYTHING_1 ↗</a>'
        '<a class="chip-link" href="https://www.shashasha.co/en/book/everything-2" target="_blank" rel="noopener">shashasha — EVERYTHING_2 ↗</a>'
        '<a class="chip-link" href="https://www.ueshima-collection.com/artist-list/102" target="_blank" rel="noopener">UESHIMA MUSEUM COLLECTION — Kenta Cobayashi ↗</a>'
        '</div>'
    ),
    "sections": [
        {"num": "§ 01 / 04", "title": "Background and Period", "body_html": KC_SEC01},
        {"num": "§ 02 / 04", "title": "Expression and Method", "body_html": KC_SEC02},
        {"num": "§ 03 / 04", "title": "Major Works, Methods, and Media", "body_html": KC_SEC03},
        {"num": "§ 04 / 04", "title": "Critical Reception and Position in Photography History", "body_html": KC_SEC04},
    ],
    "sources_html": KC_SOURCES,
    "cite_ids": list(range(1, 18)),
    "supref_ids": list(range(1, 18)),
    "site_directory_html": KC_SITE_DIR,
    "further_reading_html": KC_FURTHER,
    "footer_html": (
        '<footer class="site-footer" data-nosnippet>\n'
        '      <div>This site is an editorial photography-history project that organizes photographers, movements, and historical context from public sources.</div>\n'
        '      <div class="footer-secondary">AI is used as an assistance tool for collecting and arranging sources, while citations are checked and updated over time.</div>\n'
        '      <div class="footer-links"><a href="/en/privacy-policy.html">Privacy Policy</a></div>\n'
        '    </footer>'
    ),
}

# ============================================================
# WRITE BACK
# ============================================================
with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')
print('JSON written OK')

# Validate round-trip
with open(JSON_PATH, encoding='utf-8') as f:
    json.load(f)
print('JSON round-trip validation OK')
