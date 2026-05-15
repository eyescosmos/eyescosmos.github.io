const src = (label, url) => ({ label, url });
const srcId = (id, label, url) => ({ id, label, url });
const para = (text, cites = [], extra = {}) => ({
  text,
  ...(cites.length ? { cites } : {}),
  ...extra,
});

const sections = (headings, paragraphs) =>
  headings.map((heading, index) => ({
    heading,
    paragraphs: paragraphs.slice(index * 2, index * 2 + 2),
  }));

const FOUNDATIONS_HEADINGS = [
  'どこから生まれたのか',
  '技法と制度',
  '写真史で何を変えたか',
  '批判とその後',
];

const AVANT_HEADINGS = [
  'どこから生まれたのか',
  '視覚の方法',
  '展開の場',
  '批判と継承',
];

const DOCUMENTARY_HEADINGS = [
  '記録の制度',
  '方法と媒体',
  '写真史で何を変えたか',
  '批判とその後',
];

const JAPAN_HEADINGS = [
  'どんな状況から出てきたのか',
  '方法と媒体',
  '写真家と写真集',
  '批判と継承',
];

const COLOR_HEADINGS = [
  'どこから生まれたのか',
  '色とスケールの使い方',
  '制度と市場',
  '批判とその後',
];

const POST_HEADINGS = [
  'どこから生まれたのか',
  'イメージの扱い方',
  '制度と流通',
  '批判と継承',
];

const PICTORIALISM_SOURCES = [
  src('V&A — Julia Margaret Cameron’s working methods', 'https://www.vam.ac.uk/articles/julia-margaret-camerons-working-methods'),
  src('MoMA — Julia Margaret Cameron', 'https://www.moma.org/artists/992'),
  src('The Met — Peter Henry Emerson, Poling the Marsh Hay', 'https://www.metmuseum.org/art/collection/search/283227'),
  src('Tate Papers — Emerson’s Evolution', 'https://www.tate.org.uk/research/tate-papers/27/emersons-evolution'),
  src('The Met — Alfred Stieglitz and American Photography', 'https://www.metmuseum.org/essays/alfred-stieglitz-1864-1946-and-american-photography'),
  src('V&A — Alfred Stieglitz: Pioneer of Modern Photography', 'https://www.vam.ac.uk/articles/alfred-stieglitz-pioneer-of-modern-photography'),
  src('Art Institute of Chicago — Alfred Stieglitz Collection', 'https://archive.artic.edu/stieglitz/about/'),
  src('Art Institute of Chicago — Gertrude Käsebier', 'https://archive.artic.edu/stieglitz/gertrude-kaesebier/'),
];

const PHOTO_SECESSION_SOURCES = [
  src('The Met — Alfred Stieglitz and American Photography', 'https://www.metmuseum.org/essays/alfred-stieglitz-1864-1946-and-american-photography'),
  src('National Gallery of Art — Alfred Stieglitz Key Set Introduction', 'https://www.nga.gov/research/publications/alfred-stieglitz-key-set/introduction-key-set'),
  src('Art Institute of Chicago — Alfred Stieglitz Collection', 'https://archive.artic.edu/stieglitz/about/'),
  src('V&A — Alfred Stieglitz: Pioneer of Modern Photography', 'https://www.vam.ac.uk/articles/alfred-stieglitz-pioneer-of-modern-photography'),
  src('Art Institute of Chicago — Gertrude Käsebier', 'https://archive.artic.edu/stieglitz/gertrude-kaesebier/'),
  src('The Met — Paul Strand', 'https://www.metmuseum.org/toah/hd/strn/hd_strn.htm'),
  src('MoMA — Alfred Stieglitz', 'https://www.moma.org/artists/5664-alfred-stieglitz'),
  src('J. Paul Getty Museum — Alfred Stieglitz', 'https://www.getty.edu/art/collection/person/103KH0'),
];

const STRAIGHT_SOURCES = [
  src('The Met — Alfred Stieglitz and American Photography', 'https://www.metmuseum.org/essays/alfred-stieglitz-1864-1946-and-american-photography'),
  src('The Met — Paul Strand', 'https://www.metmuseum.org/toah/hd/strn/hd_strn.htm'),
  src('Smarthistory — Paul Strand, White Fence', 'https://smarthistory.org/paul-strand-white-fence/'),
  src('George Eastman Museum — Paul Strand', 'https://www.eastman.org/collections/photography/strand-paul'),
  src('MoMA — Frederick H. Evans, A Sea of Steps', 'https://www.moma.org/collection/works/53618'),
  src('National Gallery of Art — Charles Sheeler', 'https://www.nga.gov/artists/2745-charles-sheeler'),
  src('The Met — Charles Sheeler', 'https://www.metmuseum.org/en/essays/charles-sheeler-1883-1965'),
  src('V&A — Alfred Stieglitz: Pioneer of Modern Photography', 'https://www.vam.ac.uk/articles/alfred-stieglitz-pioneer-of-modern-photography'),
];

const MODERNISM_SOURCES = [
  src('The Met — Paul Strand', 'https://www.metmuseum.org/toah/hd/strn/hd_strn.htm'),
  src('The Met — New Vision Photography', 'https://www.metmuseum.org/essays/the-new-vision-of-photography'),
  src('The Met — Photography at the Bauhaus', 'https://www.metmuseum.org/essays/photography-at-the-bauhaus'),
  src('MoMA Object:Photo — Albert Renger-Patzsch', 'https://www.moma.org/interactives/objectphoto/artists/4866.html'),
  src('MoMA Object:Photo — Die Welt ist schön', 'https://www.moma.org/interactives/objectphoto/publications/780.html'),
  src('Tate — László Moholy-Nagy', 'https://www.tate.org.uk/art/artists/laszlo-moholy-nagy-1599'),
  src('The Met — Moholy-Nagy', 'https://www.metmuseum.org/toah/hd/moho/hd_moho.htm'),
  src('The Met — Photography in Düsseldorf', 'https://www.metmuseum.org/toah/hd/phdu/hd_phdu.htm'),
];

const NEW_VISION_SOURCES = [
  src('The Met — New Vision Photography', 'https://www.metmuseum.org/essays/the-new-vision-of-photography'),
  src('MoMA — The Shaping of New Visions', 'https://www.moma.org/calendar/exhibitions/1230'),
  src('The Met — Photography at the Bauhaus', 'https://www.metmuseum.org/essays/photography-at-the-bauhaus'),
  src('The Met — Moholy-Nagy and Lucia Moholy', 'https://www.metmuseum.org/research-centers/leonard-a-lauder-research-center/research-resources/modern-art-index-project/lazslo-moholy-nagy-and-lucia-moholy'),
  src('The Met — László Moholy-Nagy, Decorating Work, Switzerland', 'https://www.metmuseum.org/fr/art/collection/search/285429'),
  src('MoMA — Production/Reproduction', 'https://www.moma.org/interactives/exhibitions/2014/productionreproduction/'),
  src('The Met — Dancing on the Roof: Photography and the Bauhaus', 'https://www.metmuseum.org/exhibitions/listings/2001/photography-and-the-bauhaus'),
  src('MoMA — Object:Photo / The Project', 'https://www.moma.org/interactives/objectphoto/the_project.html'),
];

const BAUHAUS_SOURCES = [
  src('The Met — Photography at the Bauhaus', 'https://www.metmuseum.org/essays/photography-at-the-bauhaus'),
  src('The Met — Dancing on the Roof: Photography and the Bauhaus', 'https://www.metmuseum.org/exhibitions/listings/2001/photography-and-the-bauhaus'),
  src('The Met — Moholy-Nagy and Lucia Moholy', 'https://www.metmuseum.org/research-centers/leonard-a-lauder-research-center/research-resources/modern-art-index-project/lazslo-moholy-nagy-and-lucia-moholy'),
  src('The Met — László Moholy-Nagy [Climbing the Mast]', 'https://www.metmuseum.org/fr/art/collection/search/285429'),
  src('The Met — New Vision Photography', 'https://www.metmuseum.org/essays/the-new-vision-of-photography'),
  src('The Met — The Structure of Photographic Metaphors', 'https://www.metmuseum.org/toah/hd/pmet/hob_1995.563.htm'),
  src('Tate — László Moholy-Nagy', 'https://www.tate.org.uk/art/artists/laszlo-moholy-nagy-1599'),
  src('MoMA — The Shaping of New Visions', 'https://www.moma.org/calendar/exhibitions/1230'),
];

const VORTICISM_SOURCES = [
  src('MoMA Object:Photo — Vortograph', 'https://www.moma.org/interactives/objectphoto/objects/83725.html'),
  src('MoMA — Alvin Langdon Coburn, Vortograph', 'https://www.moma.org/collection/works/83725'),
  src('Tate — Vortograph (Ezra Pound)', 'https://www.tate.org.uk/art/artworks/coburn-vortograph-p04469'),
  src('George Eastman Museum — Alvin Langdon Coburn', 'https://www.eastman.org/collections/photography/coburn-alvin-langdon'),
  src('MoMA — Vortograph checklist reference', 'https://www.moma.org/interactives/exhibitions/2012/inventingabstraction/inventingabstractionchecklist.pdf'),
  src('MoMA — 1951 Collection Press Archive (Coburn Vortograph)', 'https://www.moma.org/docs/press_archives/1513/releases/MOMA_1951_0031_1951-04-25_510425-24.pdf'),
  src('The Met — New Vision Photography', 'https://www.metmuseum.org/essays/the-new-vision-of-photography'),
  src('MoMA — Vortograph installation reference', 'https://www.moma.org/momaorg/shared/pdfs/docs/press_archives/2561/releases/MOMA_1959_0127_104e.pdf'),
  src('MoMA — 1964 Collection Press Archive (Coburn)', 'https://www.moma.org/momaorg/shared/pdfs/docs/press_archives/3241/releases/MOMA_1964_0028_1964-05-25.pdf'),
  src('MoMA — Vortograph (collection work)', 'https://www.moma.org/collection/works/46633'),
];

const DADA_SOURCES = [
  src('MoMA — The Photomontages of Hannah Höch', 'https://www.moma.org/calendar/exhibitions/241'),
  src('The Met — Hannah Höch, Weltrevolution', 'https://www.metmuseum.org/ko/art/collection/search/265169'),
  src('The Met — Hannah Höch, Der Traum seinen Lebens', 'https://www.metmuseum.org/art/collection/search/210014296'),
  src('MoMA — Photomontage term', 'https://www.moma.org/collection/terms/photomontage'),
  src('Getty — Agitated Images: John Heartfield', 'https://www.getty.edu/art/exhibitions/heartfield/'),
  src('The Met — Man Ray', 'https://www.metmuseum.org/toah/hd/manr/hd_manr.htm'),
  src('Tate — Man Ray', 'https://www.tate.org.uk/art/artists/man-ray-1542'),
  src('MoMA — Rayographs / Man Ray', 'https://www.moma.org/artists/3787'),
  src('MoMA — Hannah Höch artist page', 'https://www.moma.org/artists/2675'),
  src('MoMA audio — Cut with a Kitchen Knife', 'https://www.moma.org/audio/playlist/198/2633'),
];

const SURREALISM_SOURCES = [
  src('The Met — Photography and Surrealism', 'https://www.metmuseum.org/en/essays/photography-and-surrealism'),
  src('The Met — Surrealism', 'https://www.metmuseum.org/essays/surrealism'),
  src('The Met — Man Ray', 'https://www.metmuseum.org/toah/hd/manr/hd_manr.htm'),
  src('Tate — Man Ray', 'https://www.tate.org.uk/art/artists/man-ray-1542'),
  src('MoMA — Man Ray / Rayographs', 'https://www.moma.org/artists/3787'),
  src('The Met — Raoul Ubac, Portrait Dans un Miroir', 'https://www.metmuseum.org/art/collection/search/265064'),
  src('The Met — New Vision Photography', 'https://www.metmuseum.org/essays/the-new-vision-of-photography'),
  src('MoMA — The Shaping of New Visions', 'https://www.moma.org/calendar/exhibitions/1230'),
  src('The Met Collection — Eugène Atget', 'https://www.metmuseum.org/art/collection/search?q=eugene+atget'),
  src('The Met Collection — Dora Maar', 'https://www.metmuseum.org/art/collection/search?q=dora+maar'),
];

const NATURALISM_SOURCES = [
  src('The Met — Peter Henry Emerson, Poling the Marsh Hay', 'https://www.metmuseum.org/art/collection/search/283227'),
  src('The Met — Peter Henry Emerson, Towing the Reed', 'https://www.metmuseum.org/art/collection/search/267098'),
  src('Tate Papers — Emerson’s Evolution', 'https://www.tate.org.uk/research/tate-papers/27/emersons-evolution'),
  src('V&A — Julia Margaret Cameron’s working methods', 'https://www.vam.ac.uk/articles/julia-margaret-camerons-working-methods'),
  src('The Met — Alfred Stieglitz and American Photography', 'https://www.metmuseum.org/essays/alfred-stieglitz-1864-1946-and-american-photography'),
  src('MoMA — Alfred Stieglitz', 'https://www.moma.org/artists/5664-alfred-stieglitz'),
  src('The Met — Paul Strand', 'https://www.metmuseum.org/toah/hd/strn/hd_strn.htm'),
  src('V&A — Alfred Stieglitz: Pioneer of Modern Photography', 'https://www.vam.ac.uk/articles/alfred-stieglitz-pioneer-of-modern-photography'),
  src('Getty — The Old Order and the New: P. H. Emerson and Photography, 1885–1895', 'https://www.getty.edu/art/exhibitions/emerson/'),
  src('V&A Blog — Back to nature', 'https://www.vam.ac.uk/blog/museum-life/back-to-nature'),
];

const DOCUMENTARY_SOURCES = [
  src('Library of Congress — Fenton Crimean War Photographs', 'https://www.loc.gov/collections/fenton-crimean-war-photographs/about-this-collection/'),
  src('The Met — Roger Fenton', 'https://www.metmuseum.org/essays/roger-fenton-1819-1869'),
  src('MoMA — Jacob Riis', 'https://www.moma.org/artists/4978'),
  src('Library of Congress — Jacob Riis Collection', 'https://www.loc.gov/pictures/collection/ggbain/item/ggb2005025700/'),
  src('The Met — Walker Evans', 'https://www.metmuseum.org/essays/walker-evans-1903-1975'),
  src('ICP — Walker Evans', 'https://www.icp.org/browse/archive/constituents/walker-evans'),
  src('Library of Congress — Migrant Mother Research Guide', 'https://guides.loc.gov/migrant-mother'),
  src('Smarthistory — Dorothea Lange, Migrant Mother', 'https://smarthistory.org/dorothea-lange-migrant-mother/'),
];

const SOCIAL_DOCUMENTARY_SOURCES = [
  src('National Galleries of Scotland — Thomas Annan, Close No. 37 High Street', 'https://www.nationalgalleries.org/art-and-artists/9021'),
  src('MoMA — Jacob Riis', 'https://www.moma.org/artists/4978'),
  src('Library of Congress — Jacob Riis Collection', 'https://www.loc.gov/pictures/collection/ggbain/item/ggb2005025700/'),
  src('Library of Congress — National Child Labor Committee Collection', 'https://www.loc.gov/pictures/collection/nclc/'),
  src('National Archives — Lewis Hine: Documentation of Child Labor', 'https://www.archives.gov/education/lessons/hine-photos'),
  src('Library of Congress — FSA/OWI Black-and-White Negatives', 'https://www.loc.gov/collections/fsa-owi-black-and-white-negatives/about-this-collection/'),
  src('Library of Congress — Migrant Mother Research Guide', 'https://guides.loc.gov/migrant-mother'),
  src('ICP — W. Eugene Smith', 'https://www.icp.org/browse/archive/constituents/w-eugene-smith'),
  src('MoMA — Ernest Cole', 'https://www.moma.org/artists/2680'),
  src('The Met — Walker Evans', 'https://www.metmuseum.org/essays/walker-evans-1903-1975'),
  src('ICP — Walker Evans', 'https://www.icp.org/browse/archive/constituents/walker-evans'),
  src('Smarthistory — Dorothea Lange, Migrant Mother', 'https://smarthistory.org/dorothea-lange-migrant-mother/'),
];

const PHOTOJOURNALISM_SOURCES = [
  src('ICP — Henri Cartier-Bresson', 'https://www.icp.org/browse/archive/constituents/henri-cartier-bresson'),
  src('Fondation HCB — Biography', 'https://www.henricartierbresson.org/en/hcb/biography/'),
  src('The Met — Robert Capa, The Falling Soldier', 'https://www.metmuseum.org/art/collection/search/283315'),
  src('ICP — Robert Capa', 'https://www.icp.org/browse/archive/constituents/robert-capa'),
  src('ICP — W. Eugene Smith', 'https://www.icp.org/browse/archive/constituents/w-eugene-smith'),
  src('ICP — William Klein', 'https://www.icp.org/browse/archive/constituents/william-klein'),
  src('The Met — William Klein', 'https://www.metmuseum.org/art/collection/search/266102'),
  src('Fondation HCB — The Decisive Moment (new edition)', 'https://www.henricartierbresson.org/en/publications/henri-cartier-bresson-the-decisive-moment-new-edition/'),
  src('Fondation HCB — On "The Decisive Moment"', 'https://www.henricartierbresson.org/en/actualites/about-the-decisive-moment/'),
  src('Fondation HCB — Le Feuilletage #6 / Images à la Sauvette', 'https://www.henricartierbresson.org/en/rencontres/feuilletage-6-the-decisve-moment-by-henri-cartier-bresson-presented-by-clement-cheroux/'),
];

const JAPAN_REALISM_SOURCES = [
  src('土門拳記念館 — 土門拳', 'http://www.domonken-kinenkan.jp/domonken/'),
  src('土門拳記念館 — 土門拳とその作品（戦後）', 'http://www.domonken-kinenkan.jp/domonken/sengo/'),
  src('東京都写真美術館 — 土門拳の古寺巡礼', 'https://topmuseum.jp/exhibition/4317/'),
  src('東京都写真美術館 — ローカルカラー／リアリズム関連解説', 'https://topmuseum.jp/contents/exhibition/topic-766.html'),
  src('東京都写真美術館 — 土門拳収蔵品検索', 'https://collection.topmuseum.jp/Publish/detailPage/40642/'),
  src('東京都写真美術館 — 土門拳の古寺巡礼（英語ページ）', 'https://topmuseum.jp/exhibition/4317/?lang=en'),
  src('MoMA — From Postwar to Postmodern: Art in Japan (preview)', 'https://assets.moma.org/d/pdfs/W1siZiIsIjIwMjAvMDMvMzEvOHhxc3MxZTVrOV9Nb01BX0Zyb21fUG9zdHdhcl90b19Qb3N0bW9kZXJuX0FydF9pbl9KYXBhbl9QUkVWSUVXLnBkZiJdXQ/MoMA_From_Postwar_to_Postmodern_Art_in_Japan_PREVIEW.pdf?sha=cbffe586543cdd6d'),
  src('東京都写真美術館紀要 — 日本写真の1968', 'https://topmuseum.jp/contents/images/info/journal/kiyou_13/03.pdf'),
  src('東京都写真美術館 — こどもの情景 コレクション展', 'https://topmuseum.jp/upload/2/1500/kodomo.pdf'),
  src('東京都写真美術館年報 2004–2005', 'https://topmuseum.jp/contents/images/info/repo/repo001.pdf'),
];

const PROVOKE_SOURCES = [
  src('MoMA — For the Sake of Thought: Provoke, 1968–1970', 'https://www.moma.org/explore/inside_out/2013/01/25/for-the-sake-of-thought-provoke-1968-1970/'),
  src('MoMA post — Takuma Nakahira and the 1971 Paris Biennial', 'https://post.moma.org/takuma-nakahiras-photographs-for-the-1971-paris-biennial/'),
  src('Tate — Daido Moriyama', 'https://www.tate.org.uk/art/artists/daido-moriyama-11595'),
  src('Tate — Farewell Photography', 'https://www.tate.org.uk/art/artworks/moriyama-farewell-photography-p79977'),
  src('Hasselblad Foundation — Daido Moriyama', 'https://www.hasselbladfoundation.org/en/hasselblad-award-winner-2019/'),
  src('MoMA — Daido Moriyama', 'https://www.moma.org/artists/4099'),
  src('MoMA — From Postwar to Postmodern: Art in Japan (preview)', 'https://assets.moma.org/d/pdfs/W1siZiIsIjIwMjAvMDMvMzEvOHhxc3MxZTVrOV9Nb01BX0Zyb21fUG9zdHdhcl90b19Qb3N0bW9kZXJuX0FydF9pbl9KYXBhbl9QUkVWSUVXLnBkZiJdXQ/MoMA_From_Postwar_to_Postmodern_Art_in_Japan_PREVIEW.pdf?sha=cbffe586543cdd6d'),
  src('東京都写真美術館紀要 — 日本写真の1968', 'https://topmuseum.jp/contents/images/info/journal/kiyou_13/03.pdf'),
  src('東京都写真美術館 — トピック解説 1968とProvoke', 'https://topmuseum.jp/contents/exhibition/topic-1870.html'),
  src('東京都写真美術館 — 森山大道展 2008', 'https://topmuseum.jp/exhibition/377/?lang=en'),
];

const I_PHOTOGRAPHY_SOURCES = [
  src('Whitney — Nan Goldin artist page', 'https://whitney.org/artists/3720'),
  src('Whitney — The Ballad of Sexual Dependency', 'https://whitney.org/collection/works/8274'),
  src('Whitney — Self-Portrait with Milagro', 'https://whitney.org/media/705'),
  src('Whitney — Nan Goldin: I’ll Be Your Mirror', 'https://whitney.org/exhibitions/nan-goldin'),
  src('MoMA — Nobuyoshi Araki, Untitled', 'https://www.moma.org/collection/works/128866'),
  src('MoMA — Nobuyoshi Araki, Untitled from "Nostalgic Night"', 'https://www.moma.org/collection/works/128433'),
  src('東京都写真美術館 — 深瀬昌久 1961-1991', 'https://topmuseum.jp/exhibition/4274/'),
  src('東京都写真美術館 — 私のいる場所－新進作家展vol.4', 'https://topmuseum.jp/contents/exhibition/index-746.html'),
];

const COLOR_SOURCES = [
  src('MoMA — William Eggleston 1976 press release', 'https://www.moma.org/docs/press_archives/5391/releases/MOMA_1976_0051_40.pdf'),
  src('MoMA — William Eggleston press release (alternate archive)', 'https://www.moma.org/documents/moma_press-release_326994.pdf'),
  src('Whitney — William Eggleston: Democratic Camera', 'https://whitney.org/exhibitions/william-eggleston'),
  src('Hasselblad Foundation — William Eggleston', 'https://www.hasselbladfoundation.org/en/portfolio_page/william-eggleston/'),
  src('Whitney — Stephen Shore artist page', 'https://whitney.org/artists/3904'),
  src('MoMA — Stephen Shore: American Surfaces', 'https://www.moma.org/calendar/exhibitions/4839'),
  src('The Met — Stephen Shore, Astoria, Queens, New York', 'https://www.metmuseum.org/art/collection/search/307072'),
  src('MoMA course PDF — A New Documentary Style / New Color', 'https://www.moma.org/momaorg/shared/pdfs/docs/learn/courses/quentin-bajac-a-new-documentary-style-in-photography-at-moma-1960-now.pdf'),
  src('Whitney Shop — American Surfaces: Revised & Expanded Edition', 'https://shop.whitney.org/products/american-surfaces-revised-expanded-edition'),
  src('The Met — Stephen Shore, New York City, New York', 'https://www.metmuseum.org/art/collection/search/854898'),
];

const LARGE_FORMAT_SOURCES = [
  src('MoMA — Andreas Gursky retrospective', 'https://www.moma.org/calendar/exhibitions/170'),
  src('The Met — Photography in Düsseldorf', 'https://www.metmuseum.org/ru/essays/photography-in-dusseldorf'),
  src('The Met — Depth of Field: Modern Photography at the Metropolitan', 'https://www.metmuseum.org/exhibitions/listings/2007/depth-of-field/photo-gallery'),
  src('SFMOMA — Jeff Wall', 'https://www.sfmoma.org/exhibition/jeff-wall/'),
  src('MoMA — Jeff Wall retrospective', 'https://www.moma.org/calendar/exhibitions/12'),
  src('SFMOMA press release — Jeff Wall retrospective', 'https://www.sfmoma.org/press-release/sfmoma-presents-jeff-wall-retrospective-exhibitio/'),
  src('The Met — Recent Acquisitions / Dye transfer in color photography', 'https://www.metmuseum.org/-/media/files/about-the-met/conservation-and-scientific-research/photograph-conservation/stay-connected-bulletins/2020-08_photograph-conservation-bulletin-no-19.pdf?hash=944C440B2FC08309C5D516313211675B&la=en'),
  src('MoMA — Philip-Lorca diCorcia: Strangers', 'https://www.moma.org/calendar/exhibitions/394'),
];

const DUSSELDORF_SOURCES = [
  src('The Met — Photography in Düsseldorf', 'https://www.metmuseum.org/toah/hd/phdu/hd_phdu.htm'),
  src('The Met — Bernd & Hilla Becher exhibition', 'https://www.metmuseum.org/pt/exhibitions/becher'),
  src('The Met — Bernd and Hilla Becher, Water Towers', 'https://www.metmuseum.org/art/collection/search/262779'),
  src('MoMA — Bernd and Hilla Becher: Landscape/Typology', 'https://www.moma.org/calendar/exhibitions/95'),
  src('The Met — Depth of Field / Dusseldorf School', 'https://www.metmuseum.org/exhibitions/listings/2007/depth-of-field/photo-gallery'),
  src('Tate — Bernd and Hilla Becher', 'https://www.tate.org.uk/art/artists/bernd-and-hilla-becher-718'),
  src('Hasselblad Foundation — Bernd and Hilla Becher', 'https://hasselbladfoundation.org/wp/laureates/bernd-och-hilla-becher/'),
  src('The Met — New gallery press release mentioning Dusseldorf School', 'https://www.metmuseum.org/press-releases/new-gallery-for-modern-and-contemporary-photography-to-be-inaugurated-at-metropolitan-museum-in-september-2007-news'),
  src('MoMA — Bernd and Hilla Becher: Landscape/Typology press archive', 'https://press.moma.org/wp-content/press-archives/PRESS_RELEASE_ARCHIVE/Becher.pdf'),
  src('Getty — Interview with Hilla Becher', 'https://www.getty.edu/art/exhibitions/becher/hilla_becher_interview.pdf'),
];

const CONCEPTUAL_SOURCES = [
  src('The Met — Conceptual Art and Photography', 'https://www.metmuseum.org/essays/conceptual-art-and-photography'),
  src('MoMA — Ed Ruscha / NOW THEN', 'https://www.moma.org/calendar/exhibitions/5582'),
  src('Getty — In Focus: Ed Ruscha', 'https://www.getty.edu/art/exhibitions/focus_ruscha'),
  src('MoMA slideshow — Ruscha photo books', 'https://www.moma.org/slideshows/1/23'),
  src('ICP — Pictures Generation, 1974–1984', 'https://www.icp.org/content/pictures-generation-1974-1984'),
  src('Whitney — Barbara Kruger', 'https://whitney.org/artists/2635'),
  src('MoMA — Barbara Kruger: Thinking of You. I Mean Me. I Mean You.', 'https://www.moma.org/calendar/exhibitions/5394'),
  src('Tate — Jeff Wall', 'https://www.tate.org.uk/art/artists/jeff-wall-2476'),
];

const PICTURES_SOURCES = [
  src('ICP — Pictures Generation, 1974–1984', 'https://www.icp.org/content/pictures-generation-1974-1984'),
  src('MoMA — Cindy Sherman', 'https://www.moma.org/collection/artists/5392'),
  src('MoMA — Cindy Sherman: The Complete Untitled Film Stills', 'https://www.moma.org/calendar/exhibitions/253'),
  src('Whitney — Barbara Kruger', 'https://whitney.org/artists/2635'),
  src('MoMA — Barbara Kruger: Thinking of You. I Mean Me. I Mean You.', 'https://www.moma.org/calendar/exhibitions/5394'),
  src('The Met — Depth of Field / Pictures Generation mention', 'https://www.metmuseum.org/press-releases/new-gallery-for-modern-and-contemporary-photography-to-be-inaugurated-at-metropolitan-museum-in-september-2007-news'),
  src('The Met — Between Here and There', 'https://www.metmuseum.org/perspectives/between-here-and-there-contemporary-photography-at-the-met'),
  src('The Met — Conceptual Art and Photography', 'https://www.metmuseum.org/essays/conceptual-art-and-photography'),
];

const STAGED_SOURCES = [
  src('MoMA — Jeff Wall retrospective', 'https://www.moma.org/calendar/exhibitions/12'),
  src('SFMOMA — Jeff Wall', 'https://www.sfmoma.org/exhibition/jeff-wall/'),
  src('SFMOMA artist page — Jeff Wall', 'https://www.sfmoma.org/artist/Jeff_Wall/'),
  src('Tate — Jeff Wall', 'https://www.tate.org.uk/art/artists/jeff-wall-2476'),
  src('MoMA — Philip-Lorca diCorcia: Strangers', 'https://www.moma.org/calendar/exhibitions/394'),
  src('MoMA — New Photography 2: Philip-Lorca diCorcia', 'https://www.moma.org/calendar/exhibitions/1600'),
  src('MoMA slideshow — Philip-Lorca diCorcia / cinematic turn', 'https://www.moma.org/slideshows/1/27'),
  src('MoMA course PDF — Between the Snapshot and Staged Photography', 'https://www.moma.org/momaorg/shared/pdfs/docs/learn/courses/david-campany-between-the-snapshot-and-staged-photography-in-photography-at-moma-1960-now.pdf'),
];

const FEMINISM_SOURCES = [
  src('Whitney — Barbara Kruger', 'https://whitney.org/artists/2635'),
  src('MoMA — Barbara Kruger: Thinking of You. I Mean Me. I Mean You.', 'https://www.moma.org/calendar/exhibitions/5394'),
  src('MoMA — Cindy Sherman', 'https://www.moma.org/collection/artists/5392'),
  src('MoMA — Cindy Sherman: The Complete Untitled Film Stills', 'https://www.moma.org/calendar/exhibitions/253'),
  src('Whitney — Nan Goldin artist page', 'https://whitney.org/artists/3720'),
  src('Whitney — The Ballad of Sexual Dependency', 'https://whitney.org/collection/works/8274'),
  src('MoMA — Staging Action: Performance in Photography since 1960', 'https://www.moma.org/visit/calendar/exhibitions/1100'),
  src('ICP — Pictures Generation, 1974–1984', 'https://www.icp.org/content/pictures-generation-1974-1984'),
];

const MOVEMENT_PAGE_CONTENT = {
  'ピクトリアリズム': {
    leadJa: 'ピクトリアリズムは、19世紀末から20世紀初頭にかけて、写真を絵画や版画に並ぶ美術として認めさせようとした国際的な潮流です。柔らかな焦点や手作業の印画技法ばかりが注目されがちですが、その核心にあったのは、プリントを単なる複製ではなく作者の判断が刻まれた作品として提示することでした。のちにストレート写真から厳しく批判される一方で、写真が美術制度へ入るための足場もこの運動が整えました。',
    sectionsJa: sections(FOUNDATIONS_HEADINGS, [
      'ピクトリアリズムが強く意識されたのは、乾板や印刷技術の普及で写真が大量に複製されるようになった時代でした。写真が工業製品や報道資料として広がるほど、作者の美的判断はどこに宿るのかという問いも強まり、各地の写真クラブやサロンが「芸術写真」の条件を競って定義しはじめます。',
      'その文脈で重視されたのが、絵画や版画と同じように、プリントを最終作品として統御することでした。柔焦点レンズ、白金印画、ゴム重クロム酸塩印画、手彩色やレタッチは、単なる装飾ではなく、機械的再現を越えて作者の手を可視化するための方法として選ばれました。',
      'ただし、ピクトリアリズムを「写真が絵に似たがった古い時代」とだけ片づけると、何が賭けられていたのかを見誤ります。[[p:kasebier|ガートルード・ケーゼビア]]や[[p:stieglitz|アルフレッド・スティーグリッツ]]の実践では、展示、ポートフォリオ、雑誌、限定部数の印刷物を通じて、写真家を職人や記録者ではなく作者として見せる制度設計そのものが重要でした。',
      '一方で、すべてのピクトリアリストが同じ見た目を目指したわけでもありません。[[p:cameron|ジュリア・マーガレット・キャメロン]]の肖像はぼかしや露光の揺れを精神性の表現へ変え、[[p:frederick-h-evans|フレデリック・H・エヴァンズ]]の建築写真はきわめて精密な階調で宗教空間を扱いました。共通していたのは、プリントに作者の解釈を宿らせるという発想です。',
      '写真史上の意義は、写真の芸術性を「何を写したか」だけでなく「どう焼いたか」「どう見せたか」という問題へ押し広げた点にあります。オリジナルプリント、エディション、展示空間、ポートフォリオといった後の写真制度の基礎は、この時期の議論と実践を抜きに語れません。',
      'また、のちの[[m:写真分離派|写真分離派]]や[[m:ストレート写真|ストレート写真]]は、ピクトリアリズムを否定することで自らを定義しました。逆にいえば、写真が絵画からどう距離を取るべきかという20世紀の論争は、ピクトリアリズムが写真を美術の土俵へ押し上げたからこそ成立したとも言えます。',
      '批判も早くから存在しました。柔らかな焦点や寓意的主題は、しばしば上流階級的な趣味や理想化された女性像と結びつき、社会的現実や写真独自の記録性を覆い隠すという反発を招きます。[[m:ストレート写真|ストレート写真]]が問題にしたのは、加工の有無そのものより、写真が自分の媒体条件をどこまで自覚しているかでした。',
      'それでもピクトリアリズムは消え去ったわけではなく、ファインプリント志向、限定版写真集、印画工程への強い関心として別の形で生き延びました。いま見直すべきなのは、その絵画志向の是非だけではなく、写真が作者性と制度をどう獲得したかという歴史の出発点としての役割です。',
    ]),
    sources: [...PICTORIALISM_SOURCES],
  },
  '写真分離派': {
    leadJa: '写真分離派は、1902年に[[p:stieglitz|アルフレッド・スティーグリッツ]]がニューヨークで立ち上げたグループで、写真を絵画や版画と同等の美術として認めさせるための制度運動でした。重要だったのは、作風の統一よりも、雑誌『Camera Work』、ギャラリー291、展覧会、コレクションを通じて写真の見せ方そのものを組み替えたことです。ピクトリアリズムの完成点であると同時に、[[m:ストレート写真|ストレート写真]]や[[m:モダニズム|モダニズム]]へつながる橋でもありました。',
    sectionsJa: sections(FOUNDATIONS_HEADINGS, [
      '写真分離派が生まれた背景には、アメリカで写真クラブ文化が成熟する一方、写真が依然として工芸や商業の下位に置かれていた状況がありました。スティーグリッツは、絵画の審査制度を模したサロン的な場を利用しつつも、より選別的で国際的な前衛写真の共同体をつくろうとしました。',
      '「分離」という名称は、既存の写真団体から距離を取り、写真の芸術性を自前の基準で定義する姿勢を示していました。実際にはゆるやかなネットワークで、[[p:kasebier|ケーゼビア]]、[[p:steichen|エドワード・スタイケン]]、[[p:coburn|アルヴィン・ラングドン・コバーン]]らが、雑誌、展覧会、印刷物を共有しながら活動の輪郭をつくっていきます。',
      '中心にあったのは『Camera Work』と291ギャラリーです。『Camera Work』は高品質なフォトグラビュール印刷を用い、写真を複製図版ではなく収集に値するプリントとして読者に示しました。291は写真だけでなく近代絵画や彫刻も紹介し、写真を孤立したジャンルではなく同時代美術の一部として位置づけます。',
      'この制度設計が重要なのは、写真の価値を作品の見た目だけでなく、どの場で、どの紙に、どの編集で流通させるかまで含めて定義したからです。写真分離派は作風そのものより、写真の受容空間を変えることで歴史に残りました。',
      '同時に、それは[[m:ピクトリアリズム|ピクトリアリズム]]の延長でもありました。初期の写真分離派は柔焦点や詩的主題を共有していましたが、スティーグリッツが291でヨーロッパ近代美術を紹介し、1917年の『Camera Work』最終号で[[p:strand|ポール・ストランド]]を前面に出すころには、写真の進路は明らかに変わります。',
      'この転回によって、写真分離派は結果的に[[m:ストレート写真|ストレート写真]]や[[m:モダニズム|モダニズム]]の出発点にもなりました。写真は絵画に似ることで芸術になるのではなく、都市、機械、日常の構造を写真独自の明晰さで示せるのではないか、という次の問いがここから強く立ち上がります。',
      '批判点としては、スティーグリッツの審美眼に強く依存した閉鎖性や、選ばれる作家と排除される作家の偏りがありました。国際主義を掲げながら、制度の中心はきわめて限定的なサークルに集中しており、その権威性が後の反発も生みます。',
      'それでも写真分離派の歴史的意味は大きく、写真家が自らの媒体をどう展示し、どう印刷し、どう批評語で支えるかという近代写真の基本的な回路を可視化しました。写真史の中で見るべきなのは、単なるグループ紹介ではなく、写真が制度を通じて近代美術へ編入されるプロセスそのものです。',
    ]),
    sources: [...PHOTO_SECESSION_SOURCES],
  },
  'ストレート写真': {
    leadJa: 'ストレート写真は、[[m:ピクトリアリズム|ピクトリアリズム]]の絵画的加工や感傷的演出から距離を取り、レンズの鮮明さ、階調、構図、プリントの精度を通じて写真固有の表現を打ち立てようとした流れです。ここでいう「ストレート」は、写真が中立で無垢だという意味ではありません。何を写し、どこで切り取り、どう焼くかという選択はむしろ強く意識されており、その判断を写真の媒体条件に即して行う点に近代写真の転換がありました。',
    sectionsJa: sections(FOUNDATIONS_HEADINGS, [
      'ストレート写真が前景化したのは、19世紀末から20世紀初頭にかけて、写真が芸術として認められはじめる一方で、その条件がなお絵画的加工に依存していた時期でした。そこで問題になったのは、写真を美術にするために本当に絵画へ似せる必要があるのか、という問いです。',
      'この転換は、単に「加工をやめる」ことではありません。被写体の選択、視点、露出、現像、プリントまでを含めて、写真の強さをレンズの記述性と印画紙の階調の中に求めることでした。写真家の手が消えるのではなく、手の働き方が変わったと言ったほうが正確です。',
      '初期の実践としては、[[p:frederick-h-evans|フレデリック・H・エヴァンズ]]の建築写真が重要です。大聖堂内部の光と石の質感は、ぼかしや象徴的演出に頼らず、白金印画の精密な階調によって構成されています。写真が対象を明晰に見ること自体を造形へ変える道筋がここに見えます。',
      'さらに[[p:stieglitz|スティーグリッツ]]は、[[m:写真分離派|写真分離派]]と291の制度的成果を引き受けつつ、写真を近代美術の言語と接続しました。決定的だったのが[[p:strand|ポール・ストランド]]で、1910年代の作品は日常の断片を鋭い焦点と幾何学的構成へ変え、絵画的な雰囲気づくりから大きく離れます。',
      '写真史上の意義は、写真の芸術性を「どれだけ絵に見えるか」ではなく「どれだけ写真として構成されているか」へ置き換えたことにあります。都市、機械、窓、看板、顔、影といったありふれた対象が、線、面、光、質感の関係として読まれるようになり、[[m:モダニズム|モダニズム]]の視覚言語が準備されました。',
      '[[p:charles-sheeler|チャールズ・シェラー]]の工場や建築の写真は、その後の展開をよく示します。写真は報告書的な記録にとどまらず、工業社会そのものの秩序を視覚化する構成へ変わり、アメリカン・モダニズムやのちの建築写真、産業写真へも接続していきました。',
      'ただし、ストレート写真を「客観性の完成」とみなすのは行きすぎです。鮮明な焦点も正面性も価値中立ではなく、視点の選択や排除を通じてつくられます。のちに[[m:新即物主義|新即物主義]]やドキュメンタリーの議論で問われるように、明晰さはしばしば権威や客観性の身振りにもなりました。',
      'それでもストレート写真は、写真が絵画の代用品ではなく、自前の条件で近代の視覚文化を組み立てられることを示しました。[[m:ピクトリアリズム|ピクトリアリズム]]との対立だけでなく、[[m:モダニズム|モダニズム]]、[[m:新即物主義|新即物主義]]、さらにはf/64を含む後続の議論へどうつながるかを見ることで、その位置づけはより立体的になります。',
    ]),
    sources: [...STRAIGHT_SOURCES],
  },
  '自然主義写真': {
    leadJa: '自然主義写真は、19世紀末にP・H・エマーソンが提唱した写真思想で、作為的な合成や寓意的演出を退け、実際の視覚経験に近い焦点と階調で自然や生活世界を撮ろうとした立場です。後の[[m:ピクトリアリズム|ピクトリアリズム]]や[[m:ストレート写真|ストレート写真]]のあいだに挟まれがちですが、写真が科学的な視覚理論、美術的判断、地域の生活記録をどのように結びつけうるかを早い段階で問いにした点で重要です。',
    sectionsJa: sections(FOUNDATIONS_HEADINGS, [
      '自然主義写真が現れたのは、合成写真や劇的な演出が「高級芸術写真」として語られていた時代でした。エマーソンはそうした作りものの劇場性に反発し、現実の光景の中から、眼が実際に経験する奥行きと焦点の偏りを写真へ持ち込もうとしました。',
      'ここで参照されたのは、単なる素朴な写実ではなく、視覚生理学と絵画理論でした。エマーソンは、人間の眼は視野全体を均一に見ているのではなく、一部に焦点を結びながら周辺は相対的に曖昧になると考え、その選択的焦点を写真で再現できると主張しました。',
      'そのため自然主義写真は、後の「全面的にシャープな写真」とは必ずしも同じではありません。柔らかい周辺や繊細な階調を許容しつつ、それを人工的な絵画効果ではなく、視覚経験に近いものとして位置づけた点が特徴です。主題も神話や文学ではなく、ノーフォーク地方の湿地や労働、日常生活に向けられました。',
      'この立場は、[[m:ピクトリアリズム|ピクトリアリズム]]と単純に対立するだけではありません。写真を芸術として擁護する点では共通しながら、その方法を合成や寓意ではなく、光学と観察の側へ引き寄せたことで、後の[[m:ストレート写真|ストレート写真]]にもつながる別の系譜を開きました。',
      '写真史上の意義は、写真の真実らしさを「細部が全部見えること」ではなく「見えの経験に近いこと」として考えた点にあります。写真は機械だから客観的だという素朴な理解でも、絵画のように手を加えれば芸術だという理解でもなく、その中間で写真の固有性を論じたのです。',
      '同時に、エマーソンの理論は矛盾も抱えていました。人間の視覚経験は運動や注意の移動を含むため、一枚の写真に固定すること自体がすでに翻訳だからです。自然に忠実であるという主張は、結局のところ別の構成原理を選び直しているにすぎないという批判も生まれました。',
      'また、地方生活の記録も純粋な民俗誌ではなく、エマーソンの審美的な選択を強く受けています。農村の労働や自然環境は、社会調査というより、作家が「自然らしい」とみなした調和の中で切り取られており、その意味で自然主義もまた一つの美的制度でした。',
      'それでも自然主義写真は、写真がどの程度まで現実に近づけるのかをめぐる近代の議論を先取りしました。[[m:ピクトリアリズム|ピクトリアリズム]]、[[m:ストレート写真|ストレート写真]]、[[m:リアリズム写真|リアリズム写真]]へ続く「写真の自然さ」の論争を読むとき、このページはその原型を見るための入口になります。',
    ]),
    sources: [...NATURALISM_SOURCES],
  },
  'モダニズム': {
    leadJa: 'モダニズム写真は、20世紀前半の都市化、工業化、印刷文化の拡大のなかで、写真を近代生活にふさわしい視覚言語へ変えようとした広い流れです。抽象、急角度、クローズアップ、反復、明晰な記述といった見た目だけが核ではありません。雑誌、ポスター、展覧会、教育制度を通じて、写真が都市、機械、身体、広告、政治と結びつく仕方そのものを変えた点に、写真史上の重みがあります。',
    sectionsJa: sections(AVANT_HEADINGS, [
      'モダニズム写真は単一の宣言から始まった運動ではなく、1920年代から30年代にかけて各地で重なった複数の実践の総称として見るほうが実態に近いものです。[[m:ストレート写真|ストレート写真]]、[[m:新しいヴィジョン|新しいヴィジョン]]、[[m:新即物主義|新即物主義]]、[[m:バウハウス|バウハウス]]などが、それぞれ異なる文脈から近代の視覚条件を押し広げました。',
      '背景にあったのは、都市の高層化、交通の高速化、機械生産、広告と雑誌の氾濫です。写真はもはや静かな記念肖像だけでは足りず、上空からの眺め、路上の断片、工業製品の表面、群衆のリズムを捉える媒体として再編されていきます。',
      'そのためモダニズムの方法は一様ではありません。[[p:strand|ポール・ストランド]]のように日常の断片を厳密な構成へ変える方向もあれば、[[p:moholy|モホリ＝ナジ]]やロトチェンコのように急角度やフォトグラムで知覚そのものを揺さぶる方向もありました。共通していたのは、写真を絵画の模倣から切り離し、近代社会の見え方に対応させることです。',
      'またモダニズム写真は、単独の作品だけで完結しません。ポスター、雑誌レイアウト、写真集、展覧会デザイン、教育カリキュラムが、その視覚を社会へ流通させる装置でした。写真家は一枚の作者であると同時に、印刷や展示の編集者でもありました。',
      '写真史上の変化として大きいのは、写真が記録と造形のどちらかに属するのではなく、その往復の中で価値を持つようになったことです。機械、建築、街路、顔、手、影は、現実の断片でありながら、同時に近代的な構成として読まれるようになります。',
      'この流れはその後の[[m:ドキュメンタリー|ドキュメンタリー]]や[[m:ストリート写真|ストリート写真]]にも影響しました。鮮明さや反復、偶然性の扱いは、報道や記録の場でも新しい美学として働き、写真の公共性と芸術性の境界を揺らしていきます。',
      'ただしモダニズムには、機械文明への楽観や技術中心主義という限界もありました。急角度や断片化はしばしば新鮮な視覚として称賛されましたが、それが誰の身体感覚を標準にしているのか、都市の不平等や政治的暴力をどこまで可視化できるのかは別問題でした。',
      'その後モダニズムは、戦後のドキュメンタリー、ニューカラー、コンセプチュアルな写真へと再解釈されます。いま読むべきなのは、抽象や直線の美しさだけでなく、写真が近代生活の制度と言語の中へどう埋め込まれたのかという大きな構図です。',
    ]),
    sources: [...MODERNISM_SOURCES],
  },
  '新即物主義': {
    leadJa: '新即物主義は、1920年代ドイツで広がった芸術潮流で、感傷や表現主義的誇張を避け、事物や人物を冷静で明晰な視線のもとに置こうとした写真の実践です。しばしば「客観的」と要約されますが、その客観性は自然にそこにあるのではなく、正面性、均質な光、反復、シリーズ化、印刷物への配置によって構成された視覚でした。[[m:ストレート写真|ストレート写真]]や[[m:タイポロジー写真|タイポロジー写真]]の系譜を考えるうえでも重要な節目です。',
    sectionsJa: sections(AVANT_HEADINGS, [
      '新即物主義の背景には、第一次世界大戦後のドイツ社会と、表現主義の激しい身振りへの反動がありました。絵画やデザインの領域で感情の爆発より冷静な観察が求められるのと並行して、写真もまた、対象を明晰に見せること自体を新しいリアリティとして押し出します。',
      '写真では[[p:sander|アウグスト・ザンダー]]と[[p:renger|アルベルト・レンガー＝パッチュ]]が象徴的です。ザンダーは社会階層や職業を横断する肖像の体系化によってドイツ社会の顔貌を並べ、レンガー＝パッチュは植物、機械、工場、道具の表面と構造を、装飾を排した近距離で写しました。',
      '重要なのは、対象の前に立って「そのまま」写したというより、何を同じ条件で並べるかが厳密に選ばれていることです。正面性、均質な光、背景処理、シリーズ構成は、対象を比較可能な単位へ変え、見る側に分類と観察の態度を要求しました。',
      'この方法は[[m:ピクトリアリズム|ピクトリアリズム]]の柔らかな演出とも、[[m:新しいヴィジョン|新しいヴィジョン]]の急角度や実験性とも異なります。奇抜さではなく、対象の形態そのものが持つ秩序を前景化し、写真を近代的な知の装置へ近づけた点に特徴があります。',
      '写真史上の意義は、「写真が真実を記録する」という古い言い方を、分類、比較、シリーズ化という近代的手法に置き換えたことです。写真は単独の感動的イメージではなく、似たものを並べることで差異と構造を読むメディアへ変わりました。',
      'この考え方は、のちの[[m:タイポロジー写真|タイポロジー写真]]や[[m:デュッセルドルフ派|デュッセルドルフ派]]へ直接つながります。とくにベッヒャー夫妻が産業建築をグリッド状に並べた方法は、ザンダーとレンガー＝パッチュの系譜を戦後の制度へ持ち込んだものとして理解できます。',
      'ただし、「客観性」の神話は慎重に扱う必要があります。ザンダーの社会分類もレンガー＝パッチュの産業的秩序も、どの対象を典型として選ぶかという判断を含み、見る者に一定の社会像を与えます。透明な記録ではなく、明晰さを価値とする思想の表れです。',
      'そのため新即物主義を読むときは、冷たい記録美学と見るだけでなく、近代社会が自分自身を分類し、把握し、可視化しようとした視線として読む必要があります。[[m:ストレート写真|ストレート写真]]、[[m:タイポロジー写真|タイポロジー写真]]、[[m:デュッセルドルフ派|デュッセルドルフ派]]とのつながりは、そこで初めてはっきりします。',
    ]),
    sources: [...MODERNISM_SOURCES],
  },
  '新しいヴィジョン': {
    leadJa: '新しいヴィジョンは、1920年代から30年代にかけて、写真が人間の習慣的な見方を破り、近代の身体と都市にふさわしい知覚を訓練しうるという考えのもとで展開した視覚の潮流です。俯瞰、仰角、極端なクローズアップ、フォトグラム、モンタージュなどの技法は単なる奇抜さではなく、写真が世界を「別様に見る」ための装置だという思想に支えられていました。[[m:バウハウス|バウハウス]]や構成主義、印刷文化との接続が欠かせません。',
    sectionsJa: sections(AVANT_HEADINGS, [
      '新しいヴィジョンが強く意識されたのは、機械文明と大衆印刷文化が視覚経験を作り替えつつあった時代でした。航空写真、新聞写真、映画、広告、科学画像が日常に入り込み、地上の一点から静かに眺める旧来の視点だけでは近代世界を捉えきれなくなります。',
      'その変化を理論化した代表が[[p:moholy|モホリ＝ナジ]]です。彼は写真を、現実をそのまま写す補助媒体ではなく、視覚そのものを再教育する装置として考えました。急角度、強いトリミング、反転、フォトグラム、文字と写真の組み合わせは、見る者の慣れた遠近感を崩すための方法でした。',
      'ここで重要なのは、奇妙なアングル自体ではなく、それがどのような身体感覚をつくるかです。高所からの俯瞰や至近距離の断片化は、都市の速度や工業製品の表面、交通のリズムを新しいスケールで経験させ、写真が近代生活に対応した知覚を教える媒体になることを示しました。',
      '新しいヴィジョンはまた、印刷物の文化と切り離せません。雑誌レイアウト、ポスター、写真集、展覧会カタログでは、単独の傑作写真より、複数の像をどう組み合わせるかが重視され、写真はタイポグラフィやグラフィックデザインと一体になって流通しました。',
      '写真史上の意義は、写真の特質を「現実を写す能力」だけでなく「現実の見え方を組み替える能力」として押し広げたことにあります。[[m:ストレート写真|ストレート写真]]が明晰さを重視したのに対し、新しいヴィジョンは視点の飛躍や光学実験を通して、写真が知覚そのものを変えうると示しました。',
      'この考え方は[[m:バウハウス|バウハウス]]の教育、[[m:モダニズム|モダニズム]]の印刷文化、さらには報道写真やストリート写真の軽快な機動性にも影響します。35mmカメラの普及は、こうした視点の自由度をいっそう強めました。',
      '一方で、新しいヴィジョンには技術礼賛の限界もあります。視覚の刷新が近代化そのものへの無条件な賛美に接近すると、社会的不平等や政治的暴力を見落とす危険がありました。革新的な視覚と進歩史観は、必ずしも同じではありません。',
      'それでも新しいヴィジョンは、写真を単なる記録機械から、世界をどう知覚するかを設計するメディアへ変えました。[[m:バウハウス|バウハウス]]、[[m:モダニズム|モダニズム]]、[[m:シュルレアリスム|シュルレアリスム]]を読み比べると、この視覚の再訓練という問題がいかに広く共有されていたかが見えてきます。',
    ]),
    sources: [...NEW_VISION_SOURCES],
  },
  'バウハウス': {
    leadJa: 'バウハウスの写真は、写真を独立した芸術ジャンルとして称揚しただけではなく、デザイン、タイポグラフィ、広告、建築、教育のあいだで機能する近代的な視覚訓練として位置づけた点に特徴があります。学校内に早い段階から正式な写真科があったわけではありませんが、[[p:moholy|モホリ＝ナジ]]やルチア・モホリの活動を通じて、写真は光、素材、空間、印刷を横断する中心的な媒体になりました。[[m:新しいヴィジョン|新しいヴィジョン]]と切り離しては読めません。',
    sectionsJa: sections(AVANT_HEADINGS, [
      '1919年に創設されたバウハウスは、工芸と美術、教育と産業を結び直す学校でした。写真がただちに制度の中心にあったわけではありませんが、伝統的な材料や造形原理を根本から見直す空気のなかで、写真もまた再評価される余地を得ます。',
      '決定的だったのが、1923年以後の[[p:moholy|モホリ＝ナジ]]です。彼は金属工房や予備課程を担当しながら、フォトグラム、急角度、ネガ反転、文字との組み合わせなどを通じて、写真を再現の道具ではなく、光の操作と空間認識の実験場として理論化しました。',
      'ルチア・モホリの役割も大きく、校舎や制作物、教員や学生の活動を記録した写真は、バウハウスそのものの自己像をつくりあげます。ここでは写真は単に作品を残す記録ではなく、学校の理念を外部へ伝える広報媒体であり、近代的なブランド装置でもありました。',
      'バウハウス写真の特色は、一枚の写真作品だけでなく、印刷物や展示、教育との接続にあります。写真はタイポグラフィと並置され、ポスターや雑誌の中で機能し、近代的生活をどう見てどう設計するかという実践へ組み込まれました。',
      '写真史上の意義は、写真が「何を写すか」より「どう視覚を組織するか」を担う媒体になったことです。これは[[m:新しいヴィジョン|新しいヴィジョン]]の思想を教育制度の中で具体化したもので、後のデザイン教育、広告写真、映像教育にまで長く影響しました。',
      'また、バウハウスは[[m:モダニズム|モダニズム]]写真の交差点でもあります。実験的なフォトグラムから即物的な建築写真まで、多様な方向性が同居し、写真が近代社会の共通言語になりうるという期待がここで可視化されました。',
      '批判点としては、近代化の視覚を合理性や機能性の側からまとめることで、誰の身体や生活が標準とされるのかを問いにくくしてしまう点があります。実験の自由は大きかった一方で、それが社会の現実へどう接続するかは必ずしも自明ではありませんでした。',
      'それでもバウハウスの写真は、学校という制度が写真をどう組み込むかを示した先例です。[[m:新しいヴィジョン|新しいヴィジョン]]、[[m:モダニズム|モダニズム]]、戦後シカゴのニュー・バウハウスへ続く流れをたどると、ここでつくられた視覚教育の枠組みの大きさが見えてきます。',
    ]).concat([{
      heading: '教育とその外部',
      paragraphs: [
        '興味深いのは、バウハウスに写真が正式な専攻として定着する前から、学生や教員のあいだで写真が事実上の共通言語になっていたことです。建築模型の記録、舞台実験、織物や金属作品の紹介、ポスターや雑誌の制作に写真が入り込み、学校全体の視覚的コミュニケーションを支えました。',
        'この教育的環境は、学校閉鎖後にも別のかたちで生き残ります。シカゴのニュー・バウハウスやデザイン教育の場では、写真は芸術作品というより、現代社会の視覚を組み立てる基礎訓練として継承されました。バウハウスの重要さは、一時代の作風にとどまらず、写真を学びの中心へ置いた制度の持続性にもあります。',
      ],
    }]),
    sources: [...BAUHAUS_SOURCES],
  },
  'ヴォルテクシズム': {
    leadJa: 'ヴォルテクシズムは、1910年代ロンドンで機械、都市、速度のエネルギーを抽象的な形へ凝縮しようとした前衛運動です。写真史でこの名が重要になるのは、[[p:coburn|アルヴィン・ラングドン・コバーン]]のヴォルトグラフが、被写体の再現から離れた初期の抽象写真として語られるからです。短命な運動であり、写真家の数も多くありませんが、写真が「何かを写すこと」から「光学的構成をつくること」へ向かう可能性を早く示した点で見逃せません。',
    sectionsJa: sections(AVANT_HEADINGS, [
      'ヴォルテクシズムは、キュビスムや未来派への応答として、ロンドンの芸術家や詩人たちが1914年前後に組み立てた運動でした。中心にいたのはウィンダム・ルイスやエズラ・パウンドで、都市の衝撃や機械のリズムを渦のような構成として捉えようとしました。',
      '写真との接点は大きな流派を形成したわけではなく、むしろコバーンの短い実験に凝縮されています。彼は鏡を三角形に組んだ装置をレンズ前に置き、対象を分割・反射させることで、既知の事物の姿を消し、鋭い面の交差だけが残る像を作りました。',
      'ヴォルトグラフの重要さは、写真が現実の証拠や肖像の似姿であるという前提を、内部から崩した点にあります。暗室での合成ではなく、撮影の瞬間に光学装置を通じて抽象像を得たことで、写真が抽象芸術の一部になりうることを示したのです。',
      'この試みは量的にはごく限られていましたが、写真史の中では、後のフォトグラム、光学実験、アブストラクト・フォトグラフィの先触れとして繰り返し参照されます。[[m:モダニズム|モダニズム]]や[[m:新しいヴィジョン|新しいヴィジョン]]の広がりを考えるうえでも、早い実験例として位置づけられます。',
      '写真史上で何を変えたかといえば、写真が対象を忠実に写すことだけを使命としなくてもよい、と明確に示した点です。被写体の識別可能性をあえて失わせることで、写真は面、角、反射、リズムそのものを扱うことができると証明されました。',
      '同時に、ヴォルテクシズム写真は大きな制度や共同体を持たなかったため、継続的な運動というより、歴史の中に鋭く差し込まれた短いエピソードでもあります。だからこそ、あとから写真史が抽象写真の起点を探すとき、コバーンの実験が特権的に取り上げられてきました。',
      '限界もはっきりしています。ヴォルトグラフはきわめて特殊な装置実験で、都市や政治の現実と広く結びついたわけではありません。ヴォルテクシズム全体も第一次世界大戦によって早々に断ち切られ、継承の回路は断片的でした。',
      'それでもこのページを残す意味は、写真が抽象へ踏み出す瞬間が、のちの[[m:ダダ|ダダ]]や[[m:新しいヴィジョン|新しいヴィジョン]]のような大きな潮流の前にもすでに試みられていたことを示せるからです。写真の抽象化は戦後の実験から突然始まったのではありません。',
    ]),
    sources: [...VORTICISM_SOURCES],
  },
  'ダダ': {
    leadJa: 'ダダの写真は、写真を現実の証拠や美しいプリントとして扱うのではなく、切断し、貼り合わせ、再配置し、印刷物の中で政治的に機能させる素材へ変えました。第一次世界大戦への幻滅から生まれた反芸術の運動として知られますが、写真史上で重要なのは、フォトモンタージュによって大量複製されたメディア画像を批判の武器へ転用したことです。写真の真実らしさは、ここで初めて大規模に分解されました。',
    sectionsJa: sections(AVANT_HEADINGS, [
      'ダダは1916年のチューリヒから始まり、その後ベルリン、パリ、ニューヨークなどへ広がりました。背景にあるのは、第一次世界大戦が近代文明の進歩神話を崩したことです。理性、国家、芸術の権威そのものが疑われ、断片、ナンセンス、偶発性が反抗の形式になりました。',
      '写真にとって転換的だったのは、新聞や雑誌から切り抜いたイメージを組み替えるフォトモンタージュです。[[p:manray|マン・レイ]]のような写真実験も重要ですが、ベルリンではハンナ・ヘッヒやハートフィールド、ハウスマンが、大量印刷された顔、文字、機械部品を組み替えて、政治とメディアの言語を反転させました。',
      'ここで写真は、現場を忠実に記録するものではなく、すでに流通しているイメージを奪い返して別の文脈へ投げ込む素材になります。切断と再配置によって、写真の「本物らしさ」は批評の効果へと変換されました。',
      'ダダの写真実践は、美術館の一枚物よりも、ポスター、雑誌、パンフレット、展覧会空間といった複合的な媒体の中で力を持ちました。印刷物に介入することで、写真は作品であると同時に宣言や攻撃文にもなります。',
      '写真史上の意義は、写真の真実性が自動的なものではなく、編集と配置によっていくらでも組み替えられることを露わにした点にあります。これは後の[[m:シュルレアリスム|シュルレアリスム]]、[[m:コンセプチュアルアート|コンセプチュアルアート]]、[[m:ピクチャーズ世代|ピクチャーズ世代]]へつながる大きな転換でした。',
      'また、写真を複製メディアとして積極的に利用したことで、ダダは一点物の芸術作品という考え方にも揺さぶりをかけました。写真が新聞、広告、プロパガンダの回路を通って政治的に働くという理解は、この時期に急速に深まります。',
      'その一方で、ダダは破壊と否定の身振りが強いため、長期的な構築原理を持ちにくいという限界もありました。運動の内部でも政治的立場やメディア戦略は一枚岩ではなく、反芸術の語りが後から制度化されるという逆説も生じます。',
      'それでもダダの写真を読む意味は大きく、写真が「写すこと」だけでなく「すでにある像を再編すること」によっても歴史を動かせると示したからです。[[m:シュルレアリスム|シュルレアリスム]]や[[m:レイオグラフ|レイオグラフ]]と併せて見ると、その破壊のあとにどんな新しい写真言語が開いたのかがはっきりします。',
    ]),
    sources: [...DADA_SOURCES],
  },
  'シュルレアリスム': {
    leadJa: 'シュルレアリスムの写真は、夢、無意識、偶然、欲望といった主題を扱っただけではなく、写真という現実に強く結びついた媒体が、かえって不気味さや不確かさを生み出しうることを示しました。多重露光、ソラリゼーション、歪曲、モンタージュのような技法も重要ですが、日常のごく普通の写真が文脈を変えるだけで異様に見えるという発見こそが核心です。[[m:ダダ|ダダ]]から受け取った断片化を、より持続的なイメージの政治へ変えました。',
    sectionsJa: sections(AVANT_HEADINGS, [
      'シュルレアリスムは1920年代のパリで、アンドレ・ブルトンらを中心に形成された運動です。背景にはフロイトの精神分析、第一次世界大戦後の価値観の崩れ、そして[[m:ダダ|ダダ]]の反合理主義があります。理性が把握しきれない欲望や夢を、日常の現実の中に見つけ出すことが課題になりました。',
      '写真はその課題に非常によく適していました。なぜなら、写真には現実をそのまま写したように見える強い説得力があるからです。だからこそ、その現実らしさにわずかなずれや切断を加えるだけで、像は急に不穏で二重底のものになります。',
      '[[p:manray|マン・レイ]]のレイオグラフやソラリゼーションは代表例ですが、シュルレアリスム写真は技巧だけではありません。アジェの街路、ドーラ・マールの不気味な静物、ベルメールの人形のように、既存の写真の文脈をずらすことで、都市や身体を「夢の残骸」として読む視線が広がりました。',
      '雑誌『La Révolution surréaliste』や『Minotaure』は、その視線を流通させる重要な場でした。人類学写真、医学写真、警察写真、スナップショットのような実用画像も、誌面の中で新しい配置を与えられることで、現実の資料から欲望の証拠へ変わります。',
      '写真史上の意義は、写真の記録性がそのまま真実の保証ではなく、むしろ異化の条件にもなると示したことです。現実に見えるからこそ奇妙である、という逆説は、のちの広告写真、ファッション写真、現代美術写真にまで長く影響します。',
      'またシュルレアリスムは、都市や身体を発見の場として再編しました。ありふれた街路、鏡、ショーウィンドー、マネキン、人体断片は、ただの対象ではなく、欲望と記憶が投影される表面として読まれます。写真はその感覚を、視覚的な証拠の形で固定しました。',
      'ただし批判もあります。女性の身体や異文化のイメージが、しばしば男性中心の欲望や異国趣味の対象として消費されたことは無視できません。無意識や偶然を賛美する語りも、誰が見る主体であるかを曖昧にしてしまうことがあります。',
      'それでもシュルレアリスムは、写真を単なる記録から、現実の表面に潜む別の論理を探る装置へ変えました。[[m:ダダ|ダダ]]、[[m:レイオグラフ|レイオグラフ]]、[[m:シネマトグラフィック写真|シネマトグラフィック写真]]と連続して読むと、写真が物語の気配や心理的空間をどう扱ってきたかが見えてきます。',
    ]),
    sources: [...SURREALISM_SOURCES],
  },
  'レイオグラフ': {
    leadJa: 'レイオグラフは、[[p:manray|マン・レイ]]が自らのカメラレス写真に与えた名称で、印画紙の上に直接ものを置き、光を当てることで像を得る技法です。技法説明だけならフォトグラムと大きく変わりませんが、ダダやシュルレアリスムの文脈では、対象を「写す」のではなく、物と光の接触そのものを像へ変える行為として理解されました。写真の原理をむき出しにしたまま、現実の不思議さを引き出す点が特徴です。',
    sectionsJa: sections(AVANT_HEADINGS, [
      'レイオグラフが現れたのは、[[m:ダダ|ダダ]]と[[m:シュルレアリスム|シュルレアリスム]]の実験が広がる1920年代です。カメラやレンズを介さずに像を得るこの方法は、写真の自明な前提とされてきた「目の前の世界を光学的に写す」という考え方を根本からずらしました。',
      'マン・レイの実践では、ピン、コップ、ハサミ、螺旋、手といった身近な物体が印画紙の上で半透明の影や鋭い輪郭として現れます。そこではものの名前や用途より、透過、接触、重なり、距離の差が直接イメージの構造になります。',
      'この技法が重要なのは、写真を絵画へ似せるのでも、記録へ戻すのでもなく、光と感光材料の出会いそのものを作品化した点です。写真の最小単位に立ち返ることで、像はかえって物語的で詩的な力を帯び、日用品は未知の生物のような姿に変わります。',
      '[[p:moholy|モホリ＝ナジ]]もフォトグラムを独自に発展させましたが、バウハウスの実験が視覚教育や光学の可能性へ向かうのに対し、マン・レイのレイオグラフは、偶然性や連想、無意識の働きをより前景化しました。同じカメラレス写真でも、置かれる文脈によって意味はかなり異なります。',
      '写真史上の意義は、写真が外界の再現だけではなく、自らの物質条件を露出させるメディアでもあると示したことです。レンズを通さずに像が成立することで、「写真らしさ」とは何かという問いそのものが開かれました。',
      'また、レイオグラフは暗室作業を創作の中心へ押し上げました。撮影は現場で起こるという考えから離れ、暗室が構成と偶然の場になることで、写真制作の時間と場所の理解も変わります。',
      '限界としては、レイオグラフだけで大きな社会的共同体が形成されたわけではなく、運動名というより特定の技法と感覚の結びつきとして歴史に残った点があります。作品が技巧へ回収されやすいという問題もあります。',
      'それでもこのページを独立させる意味は、[[m:ダダ|ダダ]]、[[m:シュルレアリスム|シュルレアリスム]]、[[m:新しいヴィジョン|新しいヴィジョン]]のあいだで、写真の原理をどう異なる思想が使い分けたかを見渡せるからです。レイオグラフは小さな技法ではなく、写真観の分岐点そのものです。',
    ]),
    sources: [...SURREALISM_SOURCES],
  },
  'ドキュメンタリー': {
    leadJa: 'ドキュメンタリー写真は、現実の出来事や生活世界を記録する写真全般を指す広い語ですが、その意味は時代ごとに大きく変わってきました。19世紀の調査や戦争記録、社会改革写真、FSA、雑誌報道、戦後の批判的ドキュメンタリーまでを通して共通するのは、写真が事実の証拠として扱われる一方で、編集、キャプション、制度、撮影者の立場によって意味づけられるという緊張です。客観性の神話と公共性の希望の両方を抱えた領域だと言えます。',
    sectionsJa: sections(DOCUMENTARY_HEADINGS, [
      'ドキュメンタリー写真の起点は一つではありません。都市改造の記録、植民地調査、戦争写真、貧民街の可視化、工場や学校の調査など、近代国家が「現実を見える形にして把握したい」と望んだ場面で、写真は早くから用いられてきました。',
      'そのためドキュメンタリーは、初めから純粋な中立記録ではありません。誰が依頼し、何を記録し、どのような順序や説明文で見せるかが、像の意味を大きく左右します。写真は現実と接触しているがゆえに説得力を持ちますが、その説得力は制度の中で方向づけられます。',
      '19世紀末から20世紀前半にかけては、[[m:社会ドキュメンタリー|社会ドキュメンタリー]]としての性格が強まりました。貧困、労働、移民、児童労働を可視化する写真は、単なる記録ではなく改革のための証拠として用いられ、[[p:evans|ウォーカー・エヴァンズ]]や[[p:lange|ドロシア・ラング]]のような実践へつながっていきます。',
      '同時に、ドキュメンタリーは美学を持たないわけではありません。フレーミング、連作の組み方、写真集の編集、印刷のトーン、被写体との距離は、どの写真が重要だと感じられるかを決めます。記録の説得力は、しばしばその構成力によって支えられています。',
      '写真史上の意義は、写真が公共圏においてどのような証言能力を持つかをめぐる基本的な場をつくったことです。報道写真、調査報告、写真集、展覧会、ウェブアーカイブまで、写真の社会的機能を考える多くの議論はドキュメンタリーの系譜から出ています。',
      'しかし20世紀後半には、その客観性への懐疑も強まりました。編集者の選択、国家や財団の意図、撮影者と被写体の力関係、苦難のイメージが見る者の感情をどう消費するかといった問題が、ドキュメンタリーの内部から問われます。',
      'この批判は、ドキュメンタリーを無効にしたのではなく、むしろその条件を自覚させました。写真が真実に近づくには、透明性の主張だけでなく、どの立場から誰に向けて作られているかを開示する必要があるという理解が広がります。',
      'いまドキュメンタリー写真を読む意味は、記録と構成、証拠と解釈、公的使命と個人的視点のあいだにある揺れをたどることです。[[m:社会ドキュメンタリー|社会ドキュメンタリー]]、[[m:フォトジャーナリズム|フォトジャーナリズム]]、[[m:FSA写真|FSA写真]]、[[m:ストリート写真|ストリート写真]]を横断して見ると、その揺れ方の違いがよく見えます。',
    ]),
    sources: [...DOCUMENTARY_SOURCES],
  },
  '社会ドキュメンタリー': {
    leadJa: '社会ドキュメンタリーは、貧困、労働、住宅、移民、差別、災害といった社会問題を可視化し、改革や世論形成へつなげようとする写真実践です。単に現実を写すだけでなく、どの現実を公の場へ持ち出すかが最初から政治的な選択になっています。写真の説得力が社会改革の武器になる一方で、苦境にある人びとを対象化してしまう危うさも常に抱えてきました。その両義性こそが、この領域の歴史を読むうえで重要です。',
    sectionsJa: sections(DOCUMENTARY_HEADINGS, [
      '社会ドキュメンタリーの系譜は、19世紀末から20世紀初頭に都市問題や労働問題が可視化される過程と深く結びついています。スラム住宅、移民の居住環境、児童労働、失業といった事象は、統計や文章だけでは伝わりにくく、写真が改革の証拠として動員されました。',
      'この写真の特徴は、被写体が個人でありながら、同時に社会構造の症候として読まれることです。たとえば母親、労働者、子ども、移民の姿は、単独の肖像であると同時に、政策や制度の失敗を示す図像として配置されます。',
      'そのため媒体の役割は非常に大きく、新聞、パンフレット、慈善団体の報告書、展覧会、写真集の編集が、イメージの意味を決めました。写真一枚の力よりも、キャプションや順序を含む「見せ方」が社会的効力を支えていたのです。',
      '[[m:FSA写真|FSA写真]]はその代表例ですが、社会ドキュメンタリーは国家プロジェクトに限りません。地域の住宅問題や公衆衛生、労働運動と結びついた写真も多く、記録の現場はつねに具体的な社会課題と接していました。',
      '写真史上で重要なのは、写真が「かわいそうな人びと」を見せる道具ではなく、社会問題を誰の責任として語るかをめぐる政治的媒体になったことです。どこまで感情に訴えるか、どこまで構造的説明を与えるかという問題は、この領域でくり返し調整されてきました。',
      'また、社会ドキュメンタリーは美学の問題も抱えます。強い構図や美しい階調が、被写体の苦しみを審美化してしまうのではないかという批判は古くからあります。説得力のための美しさが、しばしば倫理的な不安を伴うのです。',
      'さらに、撮る側と撮られる側の非対称性も避けて通れません。外部からコミュニティへ入る写真家が、その人びとの声を代弁してしまう危険、あるいは貧困や差別のイメージが消費される危険は、現代の議論でも中心にあります。',
      'それでも社会ドキュメンタリーは、写真が公共の論争に介入できることを最もはっきり示した領域です。[[m:ドキュメンタリー|ドキュメンタリー]]全般の中でも、とりわけ社会改革と写真の関係を考える入口として、このページは独立した意味を持ちます。',
    ]),
    sources: [...SOCIAL_DOCUMENTARY_SOURCES],
  },
  'フォトジャーナリズム': {
    leadJa: 'フォトジャーナリズムは、時事的な出来事を写真で伝える実践ですが、その本体は一枚の決定的な写真だけにあるのではありません。雑誌や新聞の編集、キャプション、レイアウト、配信、著作権、取材の移動手段まで含めて成立する報道の制度です。20世紀前半の図版雑誌、戦争報道、マグナムの成立を通じて、写真家は単なる現場記録者から、世界の見え方を組み立てる語り手へ変わりました。その反面、速報性や劇的効果が真実性をゆがめる危険も常につきまといます。',
    sectionsJa: sections(DOCUMENTARY_HEADINGS, [
      'フォトジャーナリズムの成立には、印刷技術の進歩と図版雑誌の拡大が欠かせません。写真が新聞や雑誌に大量に載るようになると、出来事を「見ること」は文章を読むことと並ぶニュース体験になり、写真家の働き方も現場の証人として再編されます。',
      'そのとき重要だったのは、単発の写真だけでなく、複数画像とキャプションから成るフォトエッセイでした。雑誌は連続写真、見出し、本文、誌面設計を組み合わせ、読者に事件の時間と空間を追体験させる仕組みをつくります。',
      '[[p:capa|ロバート・キャパ]]や[[p:cartierbresson|アンリ・カルティエ＝ブレッソン]]、[[p:eugenesmith|W・ユージン・スミス]]の名が大きいのは、現場で撮ったからだけではなく、写真がどのような編集で公共圏に届くかを体現したからです。戦争、街頭、産業災害、都市生活は、誌面の上で物語として構成されました。',
      '1947年のマグナム設立は、その制度面を象徴します。写真家がネガの管理や使用権に発言権を持つことで、報道写真は通信社や雑誌の下請けではなく、一定の自律性を持つ職能として位置づけられました。',
      '写真史上での変化は、写真が出来事の補足資料ではなく、出来事理解の中心的な回路になったことです。戦争や災害、政治闘争、日常生活は、写真で見られることによって初めて「世界の出来事」として共有されるようになります。',
      '一方で、フォトジャーナリズムは速報性と劇的効果を重視するため、構図の強さや象徴性が、複雑な背景を単純化してしまう危険があります。編集部の方針、国家の検閲、軍のアクセス制限も、何が見えるかを決定します。',
      'また、写真家の英雄化にも注意が必要です。危険地帯へ入る勇気が称賛される一方で、その写真が誰の苦痛をどのように見世物化しているかは後景に退きがちです。写真の即時性は、しばしば長期的な文脈の説明を欠いたまま流通します。',
      'それでもフォトジャーナリズムは、写真が現場と公共圏を結ぶ手段としてどこまで働きうるかを最も濃密に試してきた領域です。[[m:ドキュメンタリー|ドキュメンタリー]]、[[m:決定的瞬間|決定的瞬間]]、[[m:ストリート写真|ストリート写真]]と並べると、何を速報し、何を編集し、何を公共圏へ渡す表現なのかという差が見えてきます。',
    ]),
    sources: [...PHOTOJOURNALISM_SOURCES],
  },
  'FSA写真': {
    leadJa: 'FSA写真は、1930年代のニューディール政策のもとで進められたアメリカ政府の写真記録事業で、大恐慌下の農村、移住労働者、地方都市の暮らしを組織的に撮影したプロジェクトです。[[p:lange|ドロシア・ラング]]や[[p:evans|ウォーカー・エヴァンズ]]の名作だけで語られがちですが、重要なのは、それらが個人の作品であると同時に、国家の広報、アーカイブ、社会調査の一部でもあったことです。記録と政策、芸術と行政がもっとも濃く交差したドキュメンタリーの現場でした。',
    sectionsJa: sections(DOCUMENTARY_HEADINGS, [
      'FSA写真の前身は、農村再建局から農業安定局へと引き継がれた連邦政府の広報活動でした。大恐慌によって疲弊した農村の現実を記録し、政策の必要性を可視化することが、プロジェクトの実務的な出発点です。',
      'この事業を統括したロイ・ストライカーは、撮影者に具体的なテーマを与えつつも、単なる宣伝写真では終わらない広がりを残しました。農家、移住労働者、農業機械、教会、商店、学校、看板まで、多様な対象が体系的にアーカイブ化され、のちに「アメリカの肖像」として読まれる膨大な画像群が形成されます。',
      '[[p:lange|ラング]]、[[p:evans|エヴァンズ]]、ラッセル・リー、アーサー・ロススタインらの差異も重要です。写真家ごとに距離感や構図は異なり、同じ制度の中でも、被写体への共感、形式への関心、地域観察の方法は一様ではありませんでした。',
      'そのためFSA写真は、国家プロジェクトでありながら、近代ドキュメンタリーの美学的実験場でもありました。正面性、連作、キャプション、フィールドノート、ファイル分類は、写真が証拠であると同時に作品でもあるという二重性を生みます。',
      '写真史上の意義は、ドキュメンタリー写真が単独作家の倫理だけではなく、政策、アーカイブ、編集、配給のシステムによって支えられることを可視化した点にあります。写真はその場で撮られて終わるのではなく、保存され、番号を振られ、再利用されることで社会的な意味を獲得しました。',
      'また、FSA写真はアメリカ像の形成にも深く関わります。荒廃、勤勉、移動、共同体、国土といったモチーフは、後から見ると国家の自己表象とも読めます。貧困の可視化が、同時に回復可能な国民像の構築でもあったことは見逃せません。',
      'この点から、FSA写真には宣伝性や被写体の固定化という批判もあります。どの顔が代表として選ばれるのか、どの地域が「典型的アメリカ」として見せられるのかは、制度の選択によって決まります。写真家の自由と行政の目的はつねに緊張関係にありました。',
      'それでもFSA写真は、[[m:ドキュメンタリー|ドキュメンタリー]]と[[m:社会ドキュメンタリー|社会ドキュメンタリー]]を考えるうえで避けて通れない基準点です。芸術写真としての評価だけでなく、ファイル化された国家的視覚装置として読むことで、その複雑さがはっきりします。',
    ]),
    sources: [...DOCUMENTARY_SOURCES],
  },
  '決定的瞬間': {
    leadJa: '決定的瞬間は、[[p:cartierbresson|アンリ・カルティエ＝ブレッソン]]の1952年の写真集題名とともに広まった概念で、形、動き、意味がひとつの瞬間に凝縮する時点を逃さず捉える写真の理想を指します。しばしば天才的な反射神経の神話として語られますが、実際には小型カメラの機動性、路上での身体訓練、連続する観察、そして出版文化が支えた方法でした。偶然の一瞬というより、構図と時間が交差する瞬間の編集技術として見る必要があります。',
    sectionsJa: sections(DOCUMENTARY_HEADINGS, [
      'この概念が強い説得力を持ったのは、35mmカメラが街頭や報道の現場で機動力を発揮しはじめた時代でした。写真家は大きな三脚から解放され、人の流れや身体の動きに反応しながら、その場で構図を組み立てられるようになります。',
      'カルティエ＝ブレッソンの写真で重要なのは、事件性より幾何学です。跳ぶ人、曲がる道、窓枠、影、視線の交差が、ほんの一瞬だけ均衡するところを捉えることで、写真は事実の記録であると同時に、時間の結晶として読まれます。',
      'ここでいう「決定的」は、被写体の人生で唯一の瞬間という意味ではありません。むしろ、写真家の側が画面の秩序と出来事の動きが重なる局面を見抜き、それを一枚へ圧縮することに重点があります。偶然は重要ですが、偶然に身を委ねるだけでは成り立ちません。',
      'また、この概念は写真集と雑誌によって広まりました。『The Decisive Moment』という英語題が定着したことで、ブレッソンの方法は個人の作法を超えて、報道写真や[[m:ストリート写真|ストリート写真]]の理想像として流通します。出版が概念を固定したのです。',
      '写真史上の意義は、スナップショットを低次の偶然写真ではなく、高度に構成された視覚的判断として評価し直したことです。街頭の瞬間や日常の交差点が、歴史や人間の気配を宿す場として見直されました。',
      'しかし、この概念には神話化の問題もあります。すべてを一瞬に還元する語りは、連作、編集、後景の社会条件を見えにくくします。英雄的な男性写真家の身体感覚が普遍化され、別の撮影方法が周縁化されるという批判もあります。',
      'さらに、瞬間の美しさが被写体との倫理的距離を覆い隠す場合もあります。写真家が「ちょうどよい構図」を優先するとき、撮られる側の経験や文脈は画面の外へ押し出されることがあるからです。',
      'それでも決定的瞬間は、写真が時間をどう扱うかをめぐる基本概念であり続けています。[[m:フォトジャーナリズム|フォトジャーナリズム]]、[[m:ストリート写真|ストリート写真]]、[[m:シネマトグラフィック写真|シネマトグラフィック写真]]を比べると、一瞬を切ることと、時間の気配を残すことの違いが見えてきます。',
    ]),
    sources: [...PHOTOJOURNALISM_SOURCES],
  },
  'ストリート写真': {
    leadJa: 'ストリート写真は、公共空間で起こる偶然の交差、人の身振り、看板、交通、匿名的な関係をとらえる写真実践です。単に街で撮れば成立するわけではなく、都市のリズムの中でどこに身を置き、どの瞬間にシャッターを切り、見知らぬ他者との距離をどう保つかという倫理と方法が問われます。[[m:決定的瞬間|決定的瞬間]]や[[m:フォトジャーナリズム|フォトジャーナリズム]]と重なりながらも、ニュース価値より都市経験そのものの複雑さを読むことに重心があります。',
    sectionsJa: sections(DOCUMENTARY_HEADINGS, [
      'ストリート写真の源流は19世紀の都市記録にまでさかのぼれますが、現在イメージされる形が整うのは、小型カメラと感度の高いフィルムが普及し、街路で素早く撮ることが現実的になってからです。街は単なる背景ではなく、匿名性と偶然が絶えず発生する舞台になります。',
      'この実践では、出来事の大きさより、視線や身振りの交差、看板や窓の反射、歩行のリズムといった小さなズレが重要です。日常は平凡に見えても、画面の中では複数の関係が一瞬だけ噛み合い、都市の複雑さが露出します。',
      '[[p:evans|ウォーカー・エヴァンズ]]や[[p:cartierbresson|カルティエ＝ブレッソン]]、ウィノグランド、フリードランダー、[[p:moriyama|森山大道]]らを並べると、同じ街路でも方法はかなり違います。正面性を保つ作家もいれば、ぶれや切断を積極的に使う作家もおり、ストリート写真は一つの様式ではなく、都市経験の異なる読解法です。',
      'また、ストリート写真は出版や展覧会を通じて評価軸を得ました。路上での素早い撮影はしばしば「生の現実」への接近として語られますが、その意味は写真集の編集や美術館展示によって後から形づくられます。街で撮ることと作品になることのあいだには制度があります。',
      '写真史上の意義は、都市の日常が芸術的主題になりうること、そして匿名の他者とのすれ違いそのものが近代的経験の核心として読まれるようになったことです。名所や事件ではなく、通りすがりの断片が都市の真相を語るという発想は、20世紀写真の重要な変化でした。',
      '一方で、この実践にはつねに監視や無断撮影の問題がつきまといます。撮る自由と撮られない権利の境界は時代と場所で異なり、ストリート写真の美学はしばしば他者の可視化権力の上に成り立っています。',
      'さらに、美術館化されたストリート写真は、もともとの都市的な偶然性を後から洗練された形式へ回収してしまう危険もあります。粗さや即興性が、制度の中で逆にブランド化されることは珍しくありません。',
      'それでもストリート写真は、写真が都市生活の無数の関係をどこまで掬い上げられるかを試し続けてきました。[[m:決定的瞬間|決定的瞬間]]、[[m:フォトジャーナリズム|フォトジャーナリズム]]、[[m:プロヴォーク|プロヴォーク]]と見比べると、街路をどう読むかの差が鮮明になります。',
    ]),
    sources: [...DOCUMENTARY_SOURCES, ...PHOTOJOURNALISM_SOURCES],
  },
  'リアリズム写真': {
    leadJa: 'リアリズム写真は、日本の戦後写真史で強い力を持った言葉で、とくに[[p:domon|土門拳]]が唱えた「絶対非演出の絶対スナップ」に象徴されるように、演出や情緒的加工を避け、社会の現実へ正面から向き合う倫理を指しました。ただし、それは単純な無操作主義ではありません。何を社会の現実として選び、どの距離と構図で見せるかという判断を伴う、戦後日本の公共性と記録観をめぐる論争の言葉でした。',
    sectionsJa: sections(JAPAN_HEADINGS, [
      'この言葉が強く働いたのは、敗戦後の日本で、社会の再建と民主化の中で写真に新しい公共的役割が期待されたからです。サロン写真的な美化や戦時の宣伝写真に対する反省のもとで、写真は現実に対して誠実であるべきだという倫理が強く前面に出ます。',
      'そのとき[[p:domon|土門拳]]は、やらせや過剰な演出を排し、対象と正面から向き合うことを強調しました。子ども、労働、街路、寺院、仏像といった主題は一見ばらばらですが、そこには「現実の核心を逃さない」という共通の態度がありました。',
      '重要なのは、このリアリズムが単なる受動的記録ではないことです。被写体の選択、撮影位置、連作構成、雑誌発表の仕方によって、何が「現実」として読まれるかは大きく変わります。非演出の標語自体が、ある種の写真観を積極的に打ち出す言葉でもありました。',
      'また、日本のリアリズム写真は、戦後の報道写真や地方の記録運動とも結びつきます。社会の周縁や労働の場をどう可視化するか、写真が国民的記憶とどう関わるかという問題は、写真雑誌や地方写真家の活動の中でも重要な論点になりました。',
      '写真史上の意義は、写真の倫理を「美しいかどうか」ではなく「社会との関わりに誠実かどうか」という軸で考え直した点にあります。これは[[m:ドキュメンタリー|ドキュメンタリー]]や[[m:社会ドキュメンタリー|社会ドキュメンタリー]]と共通しつつ、日本固有の戦後状況の中でより強い規範として働きました。',
      'しかしこの規範には、客観性の神話という限界もあります。演出を排したと主張しても、撮影者の位置取りや編集が消えるわけではありません。何をリアルと見なすかは常に社会的に構成されており、その自覚が乏しいと、リアリズムは別の硬直した様式へ変わります。',
      'さらに、のちの[[m:プロヴォーク|プロヴォーク]]や[[m:私写真|私写真]]の世代は、この規範が現実を十分に捉えきれないと感じました。高度成長やメディア化の進んだ社会では、鮮明さや正面性だけでは、むしろ世界の不安定さがこぼれ落ちてしまうと考えたのです。',
      'それでもリアリズム写真は、戦後日本で写真がどのような責任を負うべきかをめぐる核心的な言葉でした。[[m:ドキュメンタリー|ドキュメンタリー]]、[[m:社会ドキュメンタリー|社会ドキュメンタリー]]、[[m:プロヴォーク|プロヴォーク]]へどう接続し、どう批判されたかを追うことで、その歴史的位置が見えてきます。',
    ]),
    sources: [...JAPAN_REALISM_SOURCES],
  },
  'プロヴォーク': {
    leadJa: 'プロヴォークは、1968年に創刊された同名の写真・思想誌を中心に展開した日本の写真運動で、「アレ・ブレ・ボケ」という見た目だけでは捉えきれません。背景にあったのは、言語が現実を十分にとらえられないという不信、安保闘争後の政治的閉塞、高度成長期の都市経験の不安定さでした。写真を鮮明な証拠としてではなく、世界に触れた痕跡として印刷媒体の中で提示した点に、戦後写真史を折り返す力がありました。',
    sectionsJa: sections(JAPAN_HEADINGS, [
      'プロヴォークが生まれたのは、1968年前後の日本で、政治闘争と言語への懐疑が同時に高まっていた時期です。写真は現実を説明する道具であるより、説明しきれなさそのものを露出させるべきではないか、という問いが写真家や批評家のあいだで共有されます。',
      '誌面の中心にいたのは[[p:takuma-nakahira|中平卓馬]]、高梨豊、多木浩二、岡田隆彦で、のちに[[p:moriyama|森山大道]]も加わります。彼らは写真を単独の傑作として磨くより、荒れた粒子やぶれた輪郭を含んだ印刷像として流通させることに重心を置きました。',
      'ここで「アレ・ブレ・ボケ」は、技術的失敗の肯定ではありません。むしろ、鮮明で整った写真が現実を把握したかのように振る舞うことへの不信を示す記号でした。像の不安定さは、世界がすでに不安定であり、言語もまたそれを固定できないという認識と結びついています。',
      'だからこそ媒体としての雑誌が決定的でした。写真集や展覧会より先に、印刷物の連続するページの中で、写真と言葉の関係が実験されます。プロヴォークは作品の集積ではなく、写真をめぐる思考の場そのものだったと言えます。',
      '写真史上の意義は、戦後日本のリアリズム規範に対し、記録の不可能性や知覚の断裂を中心主題として持ち込んだことです。写真は現実をそのまま伝えるのではなく、現実に触れたときに生じるずれやノイズを可視化する媒体へ変わりました。',
      'また、この運動はのちの写真集文化にも大きく影響します。ページ構成、粒子の粗さ、連作の呼吸、文字との緊張関係が、写真を見る体験そのものを変え、1970年代以降の日本写真の編集感覚を押し広げました。',
      '一方で、プロヴォークの神話化には注意が必要です。反権威的な姿勢が強く語られる一方、運動内部には男性中心的な言説や、都市の暴力を美学化する危うさもありました。あえて読みにくい像を選ぶことが、誰にとって開かれた言語だったのかは問い直す必要があります。',
      'それでもプロヴォークは、[[m:リアリズム写真|リアリズム写真]]の後に写真が何を信じ、何を疑うべきかを根底から組み替えました。[[m:ストリート写真|ストリート写真]]や[[m:私写真|私写真]]と接続して読むと、その断絶と継承の両方がよく見えます。',
    ]).concat([{
      heading: '印刷媒体としての写真',
      paragraphs: [
        'プロヴォークでは、オリジナルプリントより誌面が先に来ます。網点に置き換えられた粒子、荒れた黒、文章との干渉、見開きのリズムが、写真を「情報」ではなく思考の摩擦として経験させました。この感覚は展覧会だけでは成立しにくく、雑誌という複製媒体だからこそ可能になったものでした。',
        'その意味でプロヴォークは、作品の内容だけでなく、写真がどの媒体で流通するとどんな意味を持つかを問う運動でもありました。のちの写真集文化やインディペンデント出版へ与えた影響は大きく、写真を一枚の完成品ではなく、編集と配列の中で読むという感覚を日本に根づかせました。',
      ],
    }]),
    sources: [...PROVOKE_SOURCES],
  },
  '私写真': {
    leadJa: '私写真は、1970年代以降の日本で強く意識された写真表現で、家族、恋人、部屋、身体、記憶、死といったきわめて近い領域を主題にしながら、単なる私記録ではなく、見ることと生きることの距離そのものを作品化した実践です。ひとりの作家の宣言で始まった統一運動ではなく、写真集、スライドショー、日記的連作を通じて広がった複数の方法の束と考えたほうが実態に近いでしょう。親密さがそのまま倫理的正しさを保証しないという問題も、ここでは重要になります。',
    sectionsJa: sections(JAPAN_HEADINGS, [
      '私写真が前面化した背景には、戦後写真の公的な記録倫理だけでは捉えきれない生活世界への関心の高まりがありました。高度成長のただ中で、写真家たちは大きな社会像ではなく、自分の部屋、恋愛、家族、孤独、死の気配へカメラを向け始めます。',
      'このとき「私」は内面告白の意味にとどまりません。写真家自身も作品の関係の中に巻き込まれ、撮る者と撮られる者の境界が揺れます。私写真は、対象を外から説明するのではなく、関係の内部から像をつくる方法でした。',
      '[[p:araki|荒木経惟]]の『センチメンタルな旅』、[[p:masahisa-fukase|深瀬昌久]]の家族や鴉の連作、牛腸茂雄の親密な観察は、方向こそ異なりますが、写真が人生の記録であると同時に、その人生の編集でもあることを示しています。写真集という形式がとりわけ大きな役割を果たしました。',
      '私写真では、一枚ごとの完結より、ページをめくる流れ、反復される身振り、時間差のある像の連なりが重要です。日記に似ていても、実際には後から再配列され、関係や記憶の意味が組み直されています。私的であることは即興や無構成を意味しません。',
      '写真史上の意義は、写真が社会の外側ではなく、親密圏の内部にも権力と距離の問題を持ち込むことを可視化した点にあります。家族や恋人を撮ることは、最も身近な現実を扱う行為であると同時に、最も複雑な倫理の場でもあります。',
      'また、私写真は日本の写真集文化や展示文化の中で独自の位置を占めました。作品はしばしば作者の人生と切り離しがたく語られますが、その語り自体が市場や批評の装置の中で作られている点も見逃せません。',
      '批判としては、プライバシーの侵害、被写体との力関係、女性や家族の搾取的表象がしばしば指摘されます。親密さを掲げることでかえって支配の非対称性が見えにくくなる場合があり、私的であることは免罪符にはなりません。',
      'それでも私写真は、[[m:リアリズム写真|リアリズム写真]]や[[m:プロヴォーク|プロヴォーク]]のあとで、写真が世界との距離をどこに設定するかを根本から変えました。社会と個人の二分法ではなく、関係の内部から立ち上がる写真のかたちとして読み直す必要があります。',
    ]),
    sources: [...I_PHOTOGRAPHY_SOURCES],
  },
  'ニューカラー': {
    leadJa: 'ニューカラーは、1970年代のアメリカで、色彩を単なる装飾や商業的効果ではなく、日常世界の意味を組み立てる中心的要素として扱った写真の流れです。[[p:eggleston|ウィリアム・エグルストン]]やスティーヴン・ショアの名がよく挙がりますが、重要なのは「きれいな色写真」になったことではありません。郊外、ロードサイド、家庭用品、看板、車、食べ物といったありふれた対象が、色を通じてアメリカの生活感覚そのものを語りはじめたことです。',
    sectionsJa: sections(COLOR_HEADINGS, [
      'ニューカラーが登場したころ、美術館の写真部門では依然としてモノクロームが標準と見なされていました。カラーは広告や雑誌、観光写真の領域には浸透していても、ファインアート写真としては軽く見られる傾向が強かったのです。',
      'そこで[[p:eggleston|エグルストン]]やスティーヴン・ショアは、カラーを派手な飾りではなく、日常のものの関係を読むための基礎に据えました。赤い天井、紫の影、スーパーの包装、ロードサイドの看板は、色なしでは見えないアメリカの質感を運びます。',
      'ニューカラーの対象は意外なほど平凡です。郊外の住宅、ガソリンスタンド、食卓、駐車場、交差点といった風景は、ドラマティックな事件が起きていないからこそ、消費社会や移動の文化を静かに語ります。色はその平凡さを情報へ変える回路になりました。',
      'この流れは、[[m:ドキュメンタリー|ドキュメンタリー]]やロードフォトグラフィとの接点も持ちますが、報道的な重要性を主題にしない点で異なります。何でもない瞬間や場所の密度を、色の配置と階調で読ませることが核心でした。',
      '写真史上の意義は、カラーを「黒白にあとから加わる属性」ではなく、構図や視線と同じくらい本質的な構成要素へ押し上げたことです。これによって、日常生活、郊外、消費、家の内外といった主題が、美術館の写真の中心へ入ってきます。',
      'また、ニューカラーは後の大判カラー写真やドイツの大型プリントにも影響しました。色が空間経験や社会のスケールを伝える手段として認識されたことで、写真は展示空間の中でより大きな存在感を持つようになります。',
      '一方で、平凡な日常の色彩を扱うことは、政治性の希薄さや中産階級的な視線という批判も招きました。鮮やかな色が、社会の対立や暴力を見えにくくすることもありえます。',
      'それでもニューカラーは、カラー写真を商業や報道の周辺から引き離し、美術写真の中心課題へ押し上げました。[[m:カラー写真|カラー写真]]全体の歴史や[[m:大判カラー写真|大判カラー写真]]の展開を考える際、この転換点は欠かせません。',
    ]),
    sources: [...COLOR_SOURCES],
  },
  'カラー写真': {
    leadJa: 'カラー写真は単に「モノクロではない写真」ではなく、色が写真の意味と流通をどう変えてきたかという長い歴史を含む領域です。19世紀の手彩色、オートクローム、コダクローム、広告や雑誌での普及、美術館での受容の遅れを通して見ると、色は技術的な追加要素ではなく、写真を商業、私的記録、芸術のどこへ位置づけるかを左右してきました。ニューカラー以前からの長い葛藤を含めて読む必要があります。',
    sectionsJa: sections(COLOR_HEADINGS, [
      '写真の発明直後から、人びとは色の欠如を補おうとしてきました。手彩色の肖像や風景は、写真の現実感に絵画的な魅力を重ねる方法であり、のちの自動カラー技法とは別の意味で、写真と色の関係を早くから示しています。',
      '20世紀に入るとオートクロームやカラーフィルムが普及し、雑誌、広告、家庭用スナップの領域では色が急速に広がりました。しかし、この広がりはすぐには美術写真の中心にはなりません。むしろ「商業的」「派手」「記録として軽い」という偏見が長く残りました。',
      'そのためカラー写真の歴史は、技術の発明史であると同時に、価値づけの歴史でもあります。色が再現の忠実さを増すと考えられる一方で、黒白に比べて構成の厳しさを失うと見なされることもあり、受容は一貫していませんでした。',
      '転換点の一つが、1970年代の[[m:ニューカラー|ニューカラー]]です。ここでカラーは、雑誌的な鮮やかさではなく、日常や郊外、人工照明、包装材の質感を読み取るための批評的な言語として扱われ、美術館での評価が一気に変わります。',
      '写真史上の意義は、カラーが写真の現実感を増すだけでなく、世界の価値の見え方自体を変える点にあります。食べ物、肌、看板、商品、自然光と人工光の差は、色によって初めて別の意味を持ちます。黒白では見えない文化的温度が生まれるのです。',
      'また、カラー写真は家庭アルバム、観光、広告、報道と強く結びつくため、常に高芸術と大衆文化の境界問題を抱えます。美術館がカラーを受け入れる過程そのものが、写真が何を芸術とみなすかの再定義でもありました。',
      '批判としては、色の魅力が対象の社会的文脈を覆い隠す危険や、技術革新がそのまま表現の進歩であるかのような語りがあります。色は豊かな情報をもたらす一方で、視覚的快楽が批評的な読みを鈍らせることもあります。',
      'それでもカラー写真の歴史は、写真が現実とどう関係し、どの制度で価値づけられるかを考えるための軸です。[[m:ニューカラー|ニューカラー]]、[[m:大判カラー写真|大判カラー写真]]、広告や雑誌の歴史をつなげて読むと、その意味がより具体的になります。',
    ]).concat([{
      heading: 'なぜ受容が遅れたのか',
      paragraphs: [
        'カラーが美術館で長く周縁に置かれた理由は、技術の未熟さだけではありません。雑誌広告、旅行写真、家庭アルバムといった大量消費のイメージと強く結びついていたため、色は高級な芸術写真にふさわしくないという偏見を背負わされました。つまり問題は画質ではなく、どの社会階層の視覚と結びついていたかでもあったのです。',
        'この偏見が崩れると、カラー写真は逆に写真の制度そのものを照らし返します。何が「商業的」で何が「芸術的」なのか、誰の視覚経験が標準とされてきたのかという問いが、色をめぐる評価の変化から見えてくるからです。カラー写真史は、技術史であると同時に、写真の序列をめぐる文化史でもあります。',
      ],
    }]),
    sources: [...COLOR_SOURCES],
  },
  '大判カラー写真': {
    leadJa: '大判カラー写真は、大型カメラの精密さとカラーの情報量を組み合わせ、写真を展覧会空間で絵画や映画と競合するスケールへ押し上げた実践です。単にサイズが大きいというだけでなく、細部の密度、距離感、展示空間での身体的経験が作品の意味を支える点に特徴があります。[[m:ニューカラー|ニューカラー]]の延長でありながら、現代美術市場や大型インクジェット／クロモジェニックプリントの制度とも深く結びついています。',
    sectionsJa: sections(COLOR_HEADINGS, [
      '大判カラー写真が強い存在感を持つようになるのは、1970年代以降、カラー写真が美術館で正面から受け入れられ、同時に現代美術の展示空間が写真へ大きな壁面を与えるようになってからです。写真は本のページから壁面へと主戦場を移していきます。',
      '大型カメラは被写体を細部まで記録できる一方、撮影に時間がかかります。その遅さは、瞬間を奪うスナップとは異なり、風景、建築、群衆、人工照明の空間を、層の厚い表面として見せることに向いていました。色はそこで情報量をさらに増幅します。',
      'この流れは[[m:ニューカラー|ニューカラー]]の延長線上にありますが、展示方法はより彫刻的です。写真の前に立った観客は、遠くから全体構成を見て、近づいて細部へ入り込むという二重の身体経験を強いられ、作品は一枚の窓というより一つの場になります。',
      '[[p:gursky|アンドレアス・グルスキー]]や[[p:wall|ジェフ・ウォール]]の作品が象徴的なのは、巨大な画面が現代社会のスケールや視覚の過剰を表現するからです。市場、工場、道路、光箱の内部は、見る者を呑み込むほどの情報密度で構成されます。',
      '写真史上の意義は、写真が絵画的な大画面と真正面から競合できるメディアとして再定義されたことです。サイズと色が結びつくことで、写真は単なる記録媒体ではなく、展示空間全体の経験を設計するものへ変わりました。',
      'また、大判カラー写真はデジタル処理やポストプロダクションとも接続します。大きな画面は合成やレタッチの痕跡を含みやすく、写真の現実性と作為性の境界が改めて問い直されました。',
      '批判点としては、壮観なスケールが市場価値と結びつきやすく、写真の社会的文脈より視覚的スペクタクルが優先される危険があります。見る者を圧倒すること自体が価値になり、世界の複雑さが消費される場合もあります。',
      'それでも大判カラー写真は、[[m:ニューカラー|ニューカラー]]から[[m:デュッセルドルフ派|デュッセルドルフ派]]、[[m:シネマトグラフィック写真|シネマトグラフィック写真]]へ至る現代写真の大きな軸です。サイズと色が意味をどう変えるかを考えるための重要なページになります。',
    ]),
    sources: [...LARGE_FORMAT_SOURCES],
  },
  'デュッセルドルフ派': {
    leadJa: 'デュッセルドルフ派は、[[p:becher|ベルント＆ヒラ・ベッヒャー]]がデュッセルドルフ芸術アカデミーで行った教育を起点に、1970年代以降のドイツで展開した写真の潮流です。無表情な記録に見える作品が多いものの、その核心は単なる客観性ではなく、類型、シリーズ、巨大な展示プリント、現代美術制度との結びつきにあります。産業建築から世界市場までを扱いながら、写真が記録とコンセプトを同時に担えることを示した流れでした。',
    sectionsJa: sections(COLOR_HEADINGS, [
      'この潮流の出発点は、ベッヒャー夫妻が1950年代末から続けた産業建築の系統的撮影にあります。冷却塔、貯水塔、ガスタンク、巻上塔といった構造物を、正面に近い視点、曇天、均質な明るさで撮り、比較可能な単位へ揃えていく方法が基礎になりました。',
      'その教育がデュッセルドルフ芸術アカデミーで制度化されると、[[p:gursky|グルスキー]]、トーマス・ルフ、トーマス・シュトゥルートらの世代が現れます。彼らはベッヒャー的な構造意識を引き継ぎながら、都市、博物館、市場、群衆、メディア空間へ対象を広げていきました。',
      '重要なのは、記録的な無表情さがそのまま価値なのではなく、シリーズ化や大判化によって写真が分析的な見方を要求することです。個々の像は冷静でも、複数を並べることで歴史、制度、経済の構造が浮かび上がるよう設計されています。',
      'また、デュッセルドルフ派は[[m:タイポロジー写真|タイポロジー写真]]や[[m:新即物主義|新即物主義]]の延長にありながら、現代美術市場と深く結びついた点が決定的です。巨大なカラー／モノクロプリントは、美術館やアートフェアでの鑑賞を前提にし、写真をコレクションの中心へ押し出しました。',
      '写真史上の意義は、ドキュメンタリー、コンセプチュアル、展示制度を一本の回路にまとめたことです。写真は記録か美術かという二者択一ではなく、構造的な視覚分析を行う美術として成立しうることが、この流れで広く認知されました。',
      '同時に、デュッセルドルフ派の作品はグローバル資本主義の視覚とも結びつきます。市場、倉庫、オフィス、交通網、博物館の内部は、単なる景観ではなく、現代社会の情報と労働のインフラとして示されます。',
      '批判としては、冷静さや規格化が世界の暴力や不平等を見えにくくすること、巨大なプリントが市場価値と過度に結びつくことが挙げられます。客観的に見える視線も、実際には高度に制度化されたものです。',
      'それでもデュッセルドルフ派は、[[m:タイポロジー写真|タイポロジー写真]]を戦後の現代美術へ接続し、写真の展示スケールと批評言語を大きく変えました。[[m:大判カラー写真|大判カラー写真]]や[[m:コンセプチュアルアート|コンセプチュアルアート]]との重なりを見ると、その位置づけがいっそう明確になります。',
    ]),
    sources: [...DUSSELDORF_SOURCES],
  },
  'タイポロジー写真': {
    leadJa: 'タイポロジー写真は、似た種類の対象を同じ条件で反復撮影し、並べて比較することで、個々の物や人の差異と構造を読み取る写真の方法です。標本的で無表情に見えますが、その目的は個性を消すことではなく、反復によって個性の出方そのものを見えるようにすることにあります。[[m:新即物主義|新即物主義]]や[[m:デュッセルドルフ派|デュッセルドルフ派]]、アーカイブ的思考との接点が大きいページです。',
    sectionsJa: sections(COLOR_HEADINGS, [
      'タイポロジーという発想は、19世紀の科学的分類や民族誌的記録と無縁ではありませんが、写真表現として強い輪郭を持つのは、20世紀に比較とシリーズが美的判断の中心へ入ってからです。単独像の感動より、複数像の並置が意味を持つようになります。',
      'その代表が[[p:sander|アウグスト・ザンダー]]や[[p:becher|ベッヒャー夫妻]]です。ザンダーは社会的類型としての人物像を、ベッヒャー夫妻は産業建築を、それぞれ一定の条件で撮り続け、並べることで似ているものの違いを読ませました。',
      'ここで重要なのは、条件をそろえること自体が目的ではないという点です。光、距離、正面性をある程度そろえるからこそ、個々の顔や建築の差異が、単なる逸話ではなく構造の差として見えてきます。タイポロジーは差を消すのでなく、差の見え方を再設計します。',
      'また、タイポロジー写真は印刷と展示の形式と深く結びつきます。グリッド状の展示、一覧性のあるページ構成、連番や見出しは、写真を読むというよりデータを見る経験に近い態度を鑑賞者へ求めます。',
      '写真史上の意義は、写真が単独の名作主義から離れ、比較・分類・アーカイブの思考を美学へ組み込んだことです。これは社会学、博物学、産業史、美術制度のあいだを横断する視覚の形式でした。',
      'そのためタイポロジーは、[[m:ドキュメンタリー|ドキュメンタリー]]とも[[m:コンセプチュアルアート|コンセプチュアルアート]]とも接続します。現実の記録でありながら、同時に「どう並べるか」という概念的な判断が強く働くからです。',
      '一方で、分類の視線は対象を平均化し、制度の側から世界を整序してしまう危険があります。人物や建築をタイプとして見ることは、個別の歴史や文脈をそぎ落とすことにもつながります。',
      'それでもタイポロジー写真は、現代写真がシリーズやデータベース的思考をどう獲得したかを考える鍵です。[[m:新即物主義|新即物主義]]、[[m:デュッセルドルフ派|デュッセルドルフ派]]、[[m:コンセプチュアルアート|コンセプチュアルアート]]のあいだをつなぐ節として読むのが有効です。',
    ]).concat([{
      heading: 'アーカイブと権力',
      paragraphs: [
        'タイポロジーはしばしば中立的な分類に見えますが、何を同じ系列として束ねるのかは制度的な判断です。人物を職業や階層で並べるのか、建築を機能や形態で並べるのかによって、写真は世界を理解する道具であると同時に、世界へ秩序を与える装置にもなります。',
        'だからこそタイポロジー写真は、アーカイブやデータベースの問題とも切り離せません。反復と比較は知識の基盤を与える一方、例外や逸脱を周縁化する力も持ちます。美術作品としてのタイポロジーは、その権力作用をどこまで可視化できるかによって、単なる整理表と批評的なシリーズのあいだで大きく分かれます。',
      ],
    }]),
    sources: [...DUSSELDORF_SOURCES],
  },
  'コンセプチュアルアート': {
    leadJa: 'コンセプチュアルアートにおける写真は、美しい像を作るためのものというより、アイデア、指示、記録、制度批評を成立させるための媒体として使われました。1960年代後半から70年代にかけて、作品の物質性より概念や手続きが重視されるようになると、写真はその実行や証拠を担う柔軟な道具になります。ここで重要なのは、写真が美術から追い出されたのではなく、むしろ美術の定義を広げる役割を与えられたことです。',
    sectionsJa: sections(POST_HEADINGS, [
      'コンセプチュアルアートの背景には、抽象表現主義以後の美術が、作品の唯一性や作者の表現神話を疑いはじめたことがあります。美術は物として美しいかよりも、どのようなルールや言語によって成立するのかが問われ、写真はその問いに最も都合のよい媒体の一つでした。',
      'たとえばエド・ルシェのアーティスト・ブックでは、ガソリンスタンドや街路の連続写真が、名所写真ではなく、概念的な数え上げや地理の測定として機能します。ダグラス・ヒューブラーやダン・グラハムでは、写真は行為や場所、時間の変化を示す記録であり、作品そのものの一部です。',
      'ここで写真は、唯一無二のプリントである必要を失います。コピー可能で、安価に配布でき、文章や地図と並べられ、展示の外にも広がれることが強みになります。写真は「作品を支える補助」ではなく、概念を社会へ流通させるインフラになりました。',
      'また、コンセプチュアルアートにおける写真は、見る快楽を否定するというより、見ることがどの制度に支えられているかを可視化します。図版、新聞、書物、スライド、索引、アーカイブの形式が、作品の内容そのものへ組み込まれました。',
      '写真史上の意義は、写真が記録と証拠のメディアであるという性格を、美術の中心問題へ反転させたことです。写真は現実の痕跡であるからこそ、行為、場所、概念、制度の連鎖を可視化するのに向いていると理解されました。',
      'この流れは、[[m:ピクチャーズ世代|ピクチャーズ世代]]や[[m:ステージド写真|ステージド写真]]、[[m:フェミニズム写真|フェミニズム写真]]にも影響します。写真を「写真的な美しさ」から解放し、引用、再配置、批評の場へ開いたからです。',
      'ただし、コンセプチュアルな方法が理論や制度への言及に偏りすぎると、作品が経験から遠ざかり、観客の身体的な関与を弱めるという批判もあります。写真が証拠であることを前提にしすぎると、その見え方自体の政治性が見えなくなることもあります。',
      'それでもコンセプチュアルアートは、写真を単なるジャンルから、美術の思考実験を支える汎用的な媒体へ押し広げました。[[m:ピクチャーズ世代|ピクチャーズ世代]]や[[m:フェミニズム写真|フェミニズム写真]]を読む前提として、このページは大きな意味を持ちます。',
    ]),
    sources: [...CONCEPTUAL_SOURCES],
  },
  'ピクチャーズ世代': {
    leadJa: 'ピクチャーズ世代は、1977年の展覧会「Pictures」を起点に語られる作家群で、広告、映画、雑誌、テレビの既成イメージを引用しながら、作者性、オリジナル、ジェンダー表象、消費文化の仕組みを批判しました。写真を「現実を写すもの」とみなす前提はここで大きく後退し、むしろ写真はすでに流通している像をどう再配置するかの問題になります。ポストモダン期の写真を考えるうえで避けて通れない節目です。',
    sectionsJa: sections(POST_HEADINGS, [
      'この世代が登場した背景には、1960年代末から70年代にかけて、広告、テレビ、映画の画像が日常を強く支配するようになったことがあります。もはや写真は世界を直接記録するより、すでに画像化された世界の中で意味をつくる媒体になっていました。',
      '[[p:sherman|シンディ・シャーマン]]、[[p:kruger|バーバラ・クルーガー]]、シェリー・レヴィーン、リチャード・プリンスらは、既存のイメージを模倣、引用、切り取り、言葉と結びつけることで、写真のオリジナル性や作者性を疑います。重要なのは新しい被写体を探すことより、像の制度を読解することでした。',
      'ここでは写真が証拠であることより、コードであることが重視されます。映画のワンシーンらしさ、広告の誘惑、雑誌のレイアウト、性別役割の決まり文句が、写真の中で意識的に再演され、私たちがどのような像を「自然」と感じるかが暴かれます。',
      'また、ピクチャーズ世代は[[m:コンセプチュアルアート|コンセプチュアルアート]]の延長にありつつ、より大衆文化と強く接続しています。理論や制度批評の言葉が、ファッション、ハリウッド、報道写真のような身近な画像文化へ流れ込んだことで、写真批評の射程が一気に広がりました。',
      '写真史上の意義は、写真が「現実をどう写すか」だけでなく「既存の像をどう読むか」という問題へ軸足を移したことです。作者がゼロから世界を表現するという近代的な神話は、大量複製時代のイメージの中で大きく揺らぎました。',
      'とくにジェンダー表象への介入は重要です。女性像、スター像、広告コピーのような反復的イメージは、単なる引用対象ではなく、権力が働く場所として扱われました。これは[[m:フェミニズム写真|フェミニズム写真]]とも深く重なります。',
      '一方で、引用や盗用の戦略は、市場の中で洗練されたスタイルとして回収される危険もあります。批判的な身振りがブランド化され、メディア批判自体が消費されるという逆説は、この世代につねにつきまといました。',
      'それでもピクチャーズ世代は、写真をめぐる思考をポストモダン的に大きく組み替えました。[[m:コンセプチュアルアート|コンセプチュアルアート]]、[[m:フェミニズム写真|フェミニズム写真]]、[[m:ステージド写真|ステージド写真]]をつなぐ結節点として読むべきページです。',
    ]),
    sources: [...PICTURES_SOURCES],
  },
  'ステージド写真': {
    leadJa: 'ステージド写真は、目の前で偶然起こる現実を待つのではなく、場面、光、人物配置、道具、時にはデジタル合成まで含めて状況を構成したうえで撮る写真です。写真は真実を機械的に写すという前提に対し、演出された場面でも写真が強い現実感を持ってしまうことを逆手に取る実践だと言えます。19世紀の寓意写真から現代美術の大画面作品まで系譜は長いものの、1980年代以降は現代美術と映画的表現の接点として特に重要になりました。',
    sectionsJa: sections(POST_HEADINGS, [
      '写真に演出が入り込むこと自体は古くからありました。19世紀の組み写真や文学的主題、スタジオ肖像も広い意味では演出です。ただし現代においてステージド写真が前面化するのは、写真の記録性そのものを問い返す戦略として意識的に使われるからです。',
      '1980年代以降の[[p:wall|ジェフ・ウォール]]やシンディ・シャーマン、グレゴリー・クリュードソン、フィリップ＝ロルカ・ディコルシアの実践では、舞台設定や照明、演技、ポストプロダクションが、写真の「ありそうな現実」を作り出します。作られた場面なのに、写真であるがゆえに現実の断片として信じてしまうという逆説が核心です。',
      'この方法では、ドキュメンタリー的な偶然性より、時間をかけた構成が意味を持ちます。人物の立ち位置、室内の小道具、光源の色、視線の向きは、物語のすべてを説明しないまま、前後に続く見えない時間を暗示します。',
      'また、ステージド写真は映画と深く関わります。映画の一場面のように見えながら、実際には前後の動きを持たない一枚へ圧縮されることで、観客は止まった像の中に物語を読み込まされます。写真の静止性が、かえって物語の欠落を強く意識させます。',
      '写真史上の意義は、写真の信憑性が「現場で偶然起きた出来事」に依存しなくても成立してしまうことを露わにした点にあります。写真は証拠である前に、世界があったように見せる強い装置でもあるという理解が広まりました。',
      'この流れは[[m:コンセプチュアルアート|コンセプチュアルアート]]や[[m:ピクチャーズ世代|ピクチャーズ世代]]とも重なります。写真の現実感を利用しつつ、その現実感がどれほど構成的なものかを暴き、見る者の信頼をゆさぶるからです。',
      '批判としては、演出の規模が大きくなるほど、作品が映画的スペクタクルや市場価値へ回収されやすいことが挙げられます。綿密な構成が、現実への批評よりも制作費や技巧の誇示として読まれる危険もあります。',
      'それでもステージド写真は、写真のリアリティを最も意識的に使いながら、その基盤を問い返す実践です。[[m:シネマトグラフィック写真|シネマトグラフィック写真]]や[[m:ピクチャーズ世代|ピクチャーズ世代]]と並べることで、演出の意味の違いが見えてきます。',
    ]),
    sources: [...STAGED_SOURCES],
  },
  'フェミニズム写真': {
    leadJa: 'フェミニズム写真は、女性写真家の作品を集めたラベルではなく、写真が女性の身体、家事、欲望、広告、家族、労働をどのように表象してきたかを批判的に問う実践です。1970年代以降の第二波フェミニズムの文脈で、写真は単なる記録媒体ではなく、視線の権力が働く場として捉え直されました。イメージを作ること自体が政治であるという認識が、このページの出発点になります。',
    sectionsJa: sections(POST_HEADINGS, [
      'フェミニズム写真の背景には、女性の身体や役割が広告、映画、家族アルバム、美術史の中で反復的に定義されてきたことへの異議申し立てがあります。写真は現実を写すだけでなく、何が女性らしいと見なされるかを日常的に再生産していました。',
      'そのためフェミニズム写真の方法は一様ではありません。[[p:sherman|シンディ・シャーマン]]のように女性像のステレオタイプを再演する方向もあれば、[[p:kruger|バーバラ・クルーガー]]のように写真と言葉を組み合わせて権力関係を露出させる方向、[[p:goldin|ナン・ゴールディン]]のように親密圏の内部から別の関係性を可視化する方向もあります。',
      '重要なのは、写真が何を写すかだけでなく、誰が見る位置に立ち、誰が見られる位置に置かれるかを問い直したことです。家事、ファッション、母性、性的魅力のような日常的イメージは、自然な現実ではなく、社会的に作られたコードとして再読されます。',
      'フェミニズム写真はまた、[[m:ピクチャーズ世代|ピクチャーズ世代]]や[[m:コンセプチュアルアート|コンセプチュアルアート]]とも交差します。既存の画像を引用し、言葉を差し込み、演出を用いながら、写真を批評の装置として再設計したからです。',
      '写真史上の意義は、写真批評の中心を「表現の巧拙」から「表象が誰に何を強いるか」へ移した点にあります。女性像や家庭像は、美しいかどうか以前に、権力関係と結びついた社会的装置として読まれるようになりました。',
      'また、フェミニズム写真は、私的経験が公的な議論になりうることも示しました。家庭内の暴力、親密さ、セルフポートレイト、性的実践は、私事として隠されるのではなく、社会構造を映すものとして提示されます。',
      '一方で、フェミニズムの語り自体が白人中産階級の経験に偏ってきたこと、ジェンダーを二元論で扱いがちなことへの批判もあります。写真が解放の言語であると同時に、新しい規範を作る危険を持つ点は無視できません。',
      'それでもフェミニズム写真は、写真が身体と視線をどう制度化してきたかを可視化し、その制度へ介入する回路を開きました。[[m:ピクチャーズ世代|ピクチャーズ世代]]、[[m:私写真|私写真]]、[[m:ステージド写真|ステージド写真]]との接点も含めて読むべき領域です。',
    ]),
    sources: [...FEMINISM_SOURCES],
  },
  'シネマトグラフィック写真': {
    leadJa: 'シネマトグラフィック写真は、厳密な宣言を持つ単一運動名というより、映画のような照明、場面構成、時間の気配、物語の余白を静止画の中へ圧縮する写真の傾向を指します。重要なのは「映画みたいに見える」こと自体ではなく、一枚の写真に前後の時間や見えない出来事を感じさせる演出が、写真のリアリティをどう変えるかという点です。[[m:ステージド写真|ステージド写真]]と重なりつつ、時間感覚への関心がより強いカテゴリーとして読むのが適切です。',
    sectionsJa: sections(POST_HEADINGS, [
      'この傾向が目立つようになるのは、1970年代末以降、現代写真が映画、テレビ、広告の視覚コードを積極的に参照しはじめてからです。観客はすでに映画的な照明やフレーミングに慣れており、写真はその記憶を利用して、静止画の中に物語の前後を想像させます。',
      '[[p:wall|ジェフ・ウォール]]、グレゴリー・クリュードソン、フィリップ＝ロルカ・ディコルシアなどの作品では、人物の配置、人工光、色温度、視線のずれが、何かが起きた直後あるいは起きる直前のような緊張を作ります。画面は完結していても、時間は閉じていません。',
      'ここで写真が映画と違うのは、動かないことです。連続するショットや音がないぶん、観客は一枚の中の細部を往復しながら、自分で物語を補わなければなりません。静止は欠如ではなく、想像を駆動する装置になります。',
      'また、シネマトグラフィック写真はしばしば大判プリントや光箱を用い、観客を没入させる展示形式を取ります。これは映画館の暗い空間とは異なりますが、視覚の主導権を作品側が強く握る点では似ています。',
      '写真史上の意義は、写真が瞬間の記録だけでなく、時間の厚みや物語の気配を扱えることを示した点にあります。写真の静止性は、映画に比べて不足ではなく、独自のサスペンスを生む条件として再評価されました。',
      'この傾向は[[m:ステージド写真|ステージド写真]]や[[m:ピクチャーズ世代|ピクチャーズ世代]]ともつながりますが、引用や批評より、観客の知覚の中で時間を立ち上げることにより重点があります。映画を参照しつつ、映画の代用品にはならないのです。',
      '批判としては、映画的な気配が過剰に洗練されると、社会的文脈よりスタイルの魅力が前面に出てしまうことがあります。物語の含みが、意味の曖昧さや市場向けの高級感として消費される危険もあります。',
      'それでもシネマトグラフィック写真を一つの傾向として捉えると、静止画が映画的な時間をどう引き受けたのかを具体的に比較できます。[[m:決定的瞬間|決定的瞬間]]が一点の時間の凝縮であるなら、こちらは前後に開いた場面の余白を一枚へ留める方法として対照的に読めます。',
    ]),
    sources: [...STAGED_SOURCES],
  },
};

const flattenMovementParagraphs = (sectionsList = []) =>
  sectionsList.flatMap((section) => (section && section.paragraphs ? section.paragraphs : [])).filter(Boolean);

const essaySectionsJa = (mainParagraphs = [], receptionParagraphs = [], relatedParagraphs = []) => {
  const sectionsList = [];
  if (mainParagraphs.length) {
    sectionsList.push({ heading: '表現解説', paragraphs: mainParagraphs.filter(Boolean) });
  }
  if (receptionParagraphs.length) {
    sectionsList.push({ heading: '批評と受容', paragraphs: receptionParagraphs.filter(Boolean) });
  }
  if (relatedParagraphs.length) {
    sectionsList.push({ heading: '関連する表現', paragraphs: relatedParagraphs.filter(Boolean) });
  }
  return sectionsList;
};

const mergeSources = (...groups) => {
  const seen = new Set();
  return groups
    .flat()
    .filter(Boolean)
    .filter((record) => {
      const key = record.url || `${record.id || ''}:${record.label || ''}`;
      if (!key || seen.has(key)) return false;
      seen.add(key);
      return true;
    });
};

const findSection = (entry, heading) =>
  (entry.sectionsJa || []).find((section) => section.heading === heading);

const appendSectionParagraphs = (entry, heading, paragraphs) => {
  if (!paragraphs || !paragraphs.length) return;
  const section = findSection(entry, heading);
  if (!section) {
    entry.sectionsJa.push({ heading, paragraphs: paragraphs.filter(Boolean) });
    return;
  }
  section.paragraphs.push(...paragraphs.filter(Boolean));
};

const LEAD_OVERRIDES_JA = {
  'バウハウス': 'バウハウスは、単独の写真流派というより、学校、印刷、広告、建築、舞台、デザイン教育が交差する場のなかで、写真の役割が大きく組み替えられた歴史を指します。[[p:moholy|モホリ＝ナジ]]が理論化した実験的な視覚だけでなく、ルチア・モホリが残した記録写真や出版物の流通まで含めて見ると、写真は作品制作の周辺ではなく、近代的な視覚文化そのものを組織する媒体になっていました。',
  'カラー写真': 'カラー写真の歴史は、色を再現する技術の発明史だけではありません。手彩色、オートクローム、コダクローム、雑誌広告、家庭用スナップ、美術館での受容をたどると、色は写真の意味を変えるたびに、何が商業で何が芸術かという境界も揺らしてきました。[[m:ニューカラー|ニューカラー]]や[[m:大判カラー写真|大判カラー写真]]に先立って、色そのものが写真の制度と視覚文化をどう作り替えたかを読む必要があります。',
  'シネマトグラフィック写真': 'シネマトグラフィック写真は、映画に似た見た目の静止画を並べる呼び名ではなく、一枚の写真が場面の前後、照明の人工性、登場人物の関係、物語の欠落をどこまで引き受けられるかをめぐる現代写真の傾向です。[[p:wall|ジェフ・ウォール]]の光箱、フィリップ＝ロルカ・ディコルシアの演出された街頭像、グレゴリー・クリュードソンの大規模な夜景は、それぞれ別の仕方で、静止画のうちに映画的な時間を持ち込もうとしました。',
  'ストレート写真': 'ストレート写真は、[[m:ピクトリアリズム|ピクトリアリズム]]の絵画的加工から距離を取り、レンズの鮮明さ、階調、構図、プリントの精度によって、写真固有の言語を組み立てようとした流れです。そこで重視されたのは「ありのまま」を素朴に信じることではなく、何を選び、どの距離で捉え、どのように焼き付けるかという写真家の判断を、写真の媒体条件の側へ引き戻すことでした。',
  'ニューカラー': 'ニューカラーは、1970年代アメリカで、カラーを広告や観光の派手な飾りではなく、郊外、ロードサイド、家庭用品、看板、舗装路の質感を読むための本格的な美術写真の言語へ押し上げた流れです。[[p:eggleston|ウィリアム・エグルストン]]とスティーヴン・ショアを中心に、色は世界をきれいに見せる属性ではなく、日常生活そのものの温度と俗っぽさを担う構造へ変わりました。',
  'デュッセルドルフ派': 'デュッセルドルフ派は、[[p:becher|ベルント＆ヒラ・ベッヒャー]]の教育を起点に、戦後ドイツの産業風景、博物館、群衆、市場、建築を、大判プリントとシリーズによって分析的に見せる写真の潮流です。無表情な客観性として要約されがちですが、その本質は、タイポロジー、展示スケール、現代美術市場、デジタル処理の導入を通じて、写真の制度そのものを変えたところにあります。',
};

const RELATED_MOVEMENT_TEXT_JA = {
  'ピクトリアリズム': '[[m:写真分離派|写真分離派]]がこの芸術写真の制度をどう組み替えたのか、[[m:ストレート写真|ストレート写真]]がそこから何を退けたのかを並べて読むと、絵画模倣の是非だけではなく、写真がどのような場で「作品」になったのかが見えてきます。',
  '写真分離派': '[[m:ピクトリアリズム|ピクトリアリズム]]が築いた芸術写真の基盤を、[[m:ストレート写真|ストレート写真]]や[[m:モダニズム|モダニズム]]へどう橋渡ししたのかを見るうえで、写真分離派は制度上の分岐点になります。',
  'ストレート写真': '[[m:ピクトリアリズム|ピクトリアリズム]]から距離を取る過程を、[[m:写真分離派|写真分離派]]の展示と出版の回路、さらに[[m:モダニズム|モダニズム]]や[[m:新即物主義|新即物主義]]の明晰な視覚へ接続して読むと、この言葉の意味はぐっと具体的になります。',
  '自然主義写真': '[[m:ピクトリアリズム|ピクトリアリズム]]と完全に対立するのではなく、過剰な演出を退けつつ写真を芸術として擁護した点で、自然主義写真は[[m:ストレート写真|ストレート写真]]や[[m:ドキュメンタリー|ドキュメンタリー]]の前史として読むことができます。',
  'モダニズム': '[[m:ストレート写真|ストレート写真]]、[[m:新しいヴィジョン|新しいヴィジョン]]、[[m:新即物主義|新即物主義]]、[[m:バウハウス|バウハウス]]を横断すると、モダニズムが単独の様式ではなく、近代社会にふさわしい視覚をめぐる複数の実験の束だったことがはっきりします。',
  '新即物主義': '[[m:ストレート写真|ストレート写真]]の明晰さと[[m:新しいヴィジョン|新しいヴィジョン]]の実験性のあいだで、新即物主義は対象の形態と分類を重視しました。[[m:タイポロジー写真|タイポロジー写真]]や[[m:デュッセルドルフ派|デュッセルドルフ派]]への接続は、その後の展開を考えるうえでとくに重要です。',
  '新しいヴィジョン': '[[m:バウハウス|バウハウス]]が制度と教育の場であったのに対し、[[m:新しいヴィジョン|新しいヴィジョン]]はカメラが視覚を再教育するという理論的な主張を担いました。[[m:レイオグラフ|レイオグラフ]]や[[m:モダニズム|モダニズム]]とあわせて読むと、その実験の広がりが見えてきます。',
  'バウハウス': '[[m:新しいヴィジョン|新しいヴィジョン]]が「どう見るか」を問い直した理論だとすれば、バウハウスはその視覚が学校、印刷、広告、建築の実践へどう組み込まれたのかを示す場でした。[[m:レイオグラフ|レイオグラフ]]や[[m:モダニズム|モダニズム]]との接点もそこから見えてきます。',
  'ヴォルテクシズム': '[[m:ピクトリアリズム|ピクトリアリズム]]から[[m:モダニズム|モダニズム]]抽象へ移る橋のように読むと、ヴォルテクシズムの歴史的なサイズが見誤りにくくなります。のちの[[m:新しいヴィジョン|新しいヴィジョン]]ほど制度化はされませんでしたが、写真が対象の記録から離れうることを早い段階で示しました。',
  'ダダ': '[[m:シュルレアリスム|シュルレアリスム]]が夢や欲望へ向かったのに対し、ダダはまず切断と政治的風刺に向かいました。[[m:レイオグラフ|レイオグラフ]]や後の[[m:コンセプチュアルアート|コンセプチュアルアート]]へ開いた回路も、この反芸術の身振りから読み直せます。',
  'シュルレアリスム': '[[m:ダダ|ダダ]]の切断や偶然性を引き継ぎながら、[[m:シュルレアリスム|シュルレアリスム]]は夢と無意識へ比重を移しました。[[m:レイオグラフ|レイオグラフ]]、[[m:シネマトグラフィック写真|シネマトグラフィック写真]]と並べると、写真の不気味さがどのように別の時代で再利用されたかが見えてきます。',
  'レイオグラフ': '[[m:ダダ|ダダ]]における反芸術の衝撃、[[m:シュルレアリスム|シュルレアリスム]]における偶然と欲望、[[m:新しいヴィジョン|新しいヴィジョン]]における光の実験をつなぐ技法として読むと、レイオグラフを過度に大きな運動名へ膨らませずに済みます。',
  'ドキュメンタリー': '[[m:社会ドキュメンタリー|社会ドキュメンタリー]]が改革の意志を強く持ち、[[m:フォトジャーナリズム|フォトジャーナリズム]]がニュース媒体の制度に乗り、[[m:FSA写真|FSA写真]]が国家的アーカイブとして編成されたことを比べると、ドキュメンタリーという広い語の内側の違いが整理しやすくなります。',
  '社会ドキュメンタリー': '[[m:ドキュメンタリー|ドキュメンタリー]]の広い記録実践のなかでも、[[m:社会ドキュメンタリー|社会ドキュメンタリー]]は告発や改革をはっきり目指した点で異なります。[[m:FSA写真|FSA写真]]や[[m:フォトジャーナリズム|フォトジャーナリズム]]と比べると、その介入の仕方の違いが見えてきます。',
  'フォトジャーナリズム': '[[m:ドキュメンタリー|ドキュメンタリー]]が広い記録の形式を指すのに対し、フォトジャーナリズムは雑誌、新聞、通信社、編集者、キャプションの制度の上に立っています。[[m:決定的瞬間|決定的瞬間]]や[[m:ストリート写真|ストリート写真]]との重なりも、媒体の違いから整理できます。',
  'FSA写真': '[[m:ドキュメンタリー|ドキュメンタリー]]や[[m:社会ドキュメンタリー|社会ドキュメンタリー]]と重なりつつも、FSA写真はニューディール政策、ロイ・ストライカーの指示、連邦アーカイブの仕組みを伴う点で特異です。[[m:フォトジャーナリズム|フォトジャーナリズム]]との違いも、速報性よりファイル化の論理にあります。',
  '決定的瞬間': '[[m:ストリート写真|ストリート写真]]では都市の偶然が、[[m:フォトジャーナリズム|フォトジャーナリズム]]では出来事の速報性が前に出ますが、決定的瞬間は構図と時間がぴたりと噛み合う一点への強い信仰を持ちます。[[m:シネマトグラフィック写真|シネマトグラフィック写真]]と比べると、時間の扱い方の違いがよく見えます。',
  'ストリート写真': '[[m:決定的瞬間|決定的瞬間]]が一瞬の均衡を称揚し、[[m:ドキュメンタリー|ドキュメンタリー]]が社会的証言を志向し、[[m:プロヴォーク|プロヴォーク]]が都市の断裂を押し出したのに対し、ストリート写真は公共空間での偶然と匿名性をどう読むかに重心があります。',
  'リアリズム写真': '[[m:社会ドキュメンタリー|社会ドキュメンタリー]]や[[m:ドキュメンタリー|ドキュメンタリー]]と共有する倫理を持ちながら、リアリズム写真は戦後日本で「非演出」がなぜ公共的な規範になったのかという問題を引き受けます。[[m:プロヴォーク|プロヴォーク]]の反発はその後半の重要な読み替えです。',
  'プロヴォーク': '[[m:リアリズム写真|リアリズム写真]]が信じた明晰な記録を疑い、[[m:ストリート写真|ストリート写真]]の都市経験を印刷媒体の中でさらに切断したのがプロヴォークです。[[m:私写真|私写真]]や日本の写真集文化に残した編集感覚も、この延長で読むと見通しがよくなります。',
  '私写真': '日本の[[m:私写真|私写真]]は、親密圏を撮るという点で海外の親密圏写真と重なるものの、写真集文化や戦後写真批評の中で育った点で独自です。[[m:フェミニズム写真|フェミニズム写真]]や[[m:ドキュメンタリー|ドキュメンタリー]]と比べると、私性の政治性がどう違って語られてきたかが見えてきます。',
  'ニューカラー': '[[m:カラー写真|カラー写真]]が色をめぐる長い技術史と受容史を抱えているのに対し、ニューカラーは1970年代アメリカにおける美術写真の転換点を指します。[[m:大判カラー写真|大判カラー写真]]はそこからさらに展示空間と市場へ接続した段階として読むと整理しやすくなります。',
  'カラー写真': '[[m:ニューカラー|ニューカラー]]はカラーが美術写真の中心へ入る転換点、[[m:大判カラー写真|大判カラー写真]]は色と巨大な展示空間の結びつきです。カラー写真のページでは、その前提となる長い技術史と価値づけの歴史を土台から押さえることができます。',
  '大判カラー写真': '[[m:ニューカラー|ニューカラー]]が日常の色彩を美術館へ押し上げたあと、[[m:大判カラー写真|大判カラー写真]]はその色を巨大な展示面へ拡張しました。[[m:デュッセルドルフ派|デュッセルドルフ派]]や[[m:シネマトグラフィック写真|シネマトグラフィック写真]]との交差は、展示制度と市場の問題を考えるうえで欠かせません。',
  'デュッセルドルフ派': '[[m:タイポロジー写真|タイポロジー写真]]が比較と反復の方法を支え、[[m:新即物主義|新即物主義]]が明晰さの美学を先取りしていました。デュッセルドルフ派はそれを[[m:大判カラー写真|大判カラー写真]]や[[m:コンセプチュアルアート|コンセプチュアルアート]]の制度へつなげた戦後の形として読むとわかりやすくなります。',
  'タイポロジー写真': '19世紀の分類写真と混同せずに読むためには、[[m:新即物主義|新即物主義]]の比較の論理と、[[m:デュッセルドルフ派|デュッセルドルフ派]]の展示形式を押さえるのが有効です。[[m:コンセプチュアルアート|コンセプチュアルアート]]との接点は、写真がデータベース的に働く条件を明らかにします。',
  'コンセプチュアルアート': '[[m:ピクチャーズ世代|ピクチャーズ世代]]が既成イメージの再配置へ向かい、[[m:フェミニズム写真|フェミニズム写真]]が視線の政治を前景化したとき、その足場の一部を提供していたのがコンセプチュアルアートです。[[m:ステージド写真|ステージド写真]]との違いは、写真が概念の手続きなのか、現実感の問いなのかにあります。',
  'ピクチャーズ世代': '[[m:コンセプチュアルアート|コンセプチュアルアート]]が手続きと言語を押し出したあと、ピクチャーズ世代は広告や映画や雑誌のイメージそのものを舞台にしました。[[m:フェミニズム写真|フェミニズム写真]]、[[m:ステージド写真|ステージド写真]]との違いを見ると、引用と演出の使い方が整理しやすくなります。',
  'ステージド写真': '[[m:コンセプチュアルアート|コンセプチュアルアート]]が写真を手続きや記録へ開いたのに対し、[[m:ステージド写真|ステージド写真]]は演出によって写真の真実性を問い直しました。[[m:シネマトグラフィック写真|シネマトグラフィック写真]]や[[m:ピクチャーズ世代|ピクチャーズ世代]]と並べると、物語性と引用性の差が見えてきます。',
  'フェミニズム写真': '[[m:ピクチャーズ世代|ピクチャーズ世代]]や[[m:コンセプチュアルアート|コンセプチュアルアート]]が与えた引用やテキストの方法を、フェミニズム写真は身体、家族、労働、セクシュアリティの問題へ接続しました。[[m:私写真|私写真]]と並べると、私性がどの局面で政治へ変わるのかがより具体的に見えてきます。',
  'シネマトグラフィック写真': '[[m:ステージド写真|ステージド写真]]が写真の真実性を演出によって問い返す広い実践だとすれば、シネマトグラフィック写真はそのなかでも時間の前後や場面の未完性を強く意識します。[[m:ピクチャーズ世代|ピクチャーズ世代]]や[[m:大判カラー写真|大判カラー写真]]と並べると、映画との距離の取り方の違いが見えてきます。',
};

const MOVEMENT_SOURCE_ADDITIONS = {
  'シネマトグラフィック写真': [
    srcId('cinema-wall', 'SFMOMA — Jeff Wall', 'https://www.sfmoma.org/exhibition/jeff-wall/'),
    srcId('cinema-dicorcia', 'MoMA — Philip-Lorca diCorcia: Strangers', 'https://www.moma.org/calendar/exhibitions/394'),
    srcId('cinema-crewdson', 'Getty — At the Window', 'https://www.getty.edu/art/exhibitions/window/'),
    srcId('cinema-sherman', 'Whitney — Cindy Sherman', 'https://whitney.org/artists/2909'),
  ],
  'カラー写真': [
    srcId('color-leiter', 'Saul Leiter Foundation — Color', 'https://www.saulleiterfoundation.org/color'),
    srcId('color-leiter-bio', 'Saul Leiter Foundation — Biography', 'https://www.saulleiterfoundation.org/'),
    srcId('color-parr', 'Tate — Martin Parr', 'https://www.tate.org.uk/art/artists/martin-parr-1737'),
  ],
  'コンセプチュアルアート': [
    srcId('concept-kosuth', 'MoMA audio — Joseph Kosuth, One and Three Chairs', 'https://www.moma.org/multimedia/embed/audio/291/98'),
    srcId('concept-baldessari', 'MoMA — Christopher Williams: The Production Line of Happiness', 'https://www.moma.org/calendar/exhibitions/1376'),
    srcId('concept-siegelaub', 'MoMA — Seth Siegelaub Papers as Institutional Critique', 'https://www.moma.org/interactives/exhibitions/2013/siegelaub/'),
  ],
  'ドキュメンタリー': [
    srcId('doc-new-documents', 'MoMA — New Documents', 'https://www.moma.org/calendar/exhibitions/3487'),
  ],
  'フォトジャーナリズム': [
    srcId('photojournalism-life', 'ICP — W. Eugene Smith', 'https://www.icp.org/browse/archive/constituents/w-eugene-smith'),
    srcId('photojournalism-hcb', 'Fondation HCB — Biography', 'https://www.henricartierbresson.org/en/hcb/biography/'),
  ],
  'FSA写真': [
    srcId('fsa-about', 'Library of Congress — About this Collection', 'https://www.loc.gov/collections/fsa-owi-black-and-white-negatives/about-this-collection/'),
    srcId('fsa-captions', 'Library of Congress — Caption Sheets', 'https://guides.loc.gov/farm-security-administration-written-records/caption-sheets'),
    srcId('fsa-parks', 'Library of Congress — Gordon Parks, Government Charwoman', 'https://www.loc.gov/pictures/static/data/fsa/resources/docchap7.html'),
  ],
  'フェミニズム写真': [
    srcId('feminism-rosler', 'Whitney — Martha Rosler', 'https://whitney.org/artists/3786'),
    srcId('feminism-kruger', 'MoMA — Barbara Kruger: Thinking of You. I Mean Me. I Mean You.', 'https://www.moma.org/calendar/exhibitions/5394'),
  ],
  'ニューカラー': [
    srcId('newcolor-eggleston-whitney', 'Whitney — William Eggleston: Democratic Camera', 'https://whitney.org/exhibitions/william-eggleston'),
    srcId('newcolor-eggleston-moma', 'MoMA — William Eggleston 1976 press release', 'https://www.moma.org/docs/press_archives/5391/releases/MOMA_1976_0051_40.pdf'),
    srcId('newcolor-parr', 'Tate — Martin Parr', 'https://www.tate.org.uk/art/artists/martin-parr-1737'),
  ],
  '大判カラー写真': [
    srcId('largeformat-dicorcia', 'MoMA — Philip-Lorca diCorcia: Strangers', 'https://www.moma.org/calendar/exhibitions/394'),
    srcId('largeformat-crewdson', 'Getty — At the Window', 'https://www.getty.edu/art/exhibitions/window/'),
  ],
  'デュッセルドルフ派': [
    srcId('dusseldorf-tate-bechers', 'Tate — Bernd and Hilla Becher', 'https://www.tate.org.uk/art/artists/bernd-and-hilla-becher-718'),
  ],
  'ピクチャーズ世代': [
    srcId('pictures-icp', 'ICP — Pictures Generation, 1974–1984', 'https://www.icp.org/content/pictures-generation-1974-1984'),
    srcId('pictures-lawler', 'Whitney — Louise Lawler', 'https://whitney.org/artists/4043'),
  ],
  '社会ドキュメンタリー': [
    srcId('socialdoc-smith', 'ICP — W. Eugene Smith', 'https://www.icp.org/browse/archive/constituents/w-eugene-smith'),
  ],
  'ストレート写真': [
    srcId('straight-weston', 'MoMA — Edward Weston', 'https://www.moma.org/artists/6346'),
    srcId('straight-ansel', 'National Gallery of Art — Ansel Adams', 'https://www.nga.gov/artists/14-ansel-adams'),
  ],
  'ストリート写真': [
    srcId('street-levitt', 'MoMA — Helen Levitt', 'https://www.moma.org/artists/3544'),
    srcId('street-winogrand', 'MoMA — Garry Winogrand', 'https://www.moma.org/artists/6399-garry-winogrand'),
  ],
  'シュルレアリスム': [
    srcId('surrealism-cahun', 'The Met Collection — Claude Cahun', 'https://www.metmuseum.org/art/collection/search?q=Claude+Cahun'),
    srcId('surrealism-atget', 'The Met Collection — Eugène Atget', 'https://www.metmuseum.org/art/collection/search?q=eugene+atget'),
  ],
};

const MOVEMENT_SOURCE_ADDITIONS_ROUND2 = {
  'ピクトリアリズム': [
    srcId('pictorialism-steichen-met', 'The Met — Edward J. Steichen: The Photo-Secession Years', 'https://www.metmuseum.org/essays/edward-j-steichen-1879-1973-the-photo-secession-years'),
    srcId('pictorialism-photo-secession-moma', 'MoMA — Photo-Secession', 'https://www.moma.org/collection/terms/photo-secession'),
  ],
  '写真分離派': [
    srcId('photosecession-camerawork-moma', 'MoMA — Camera Work | Object:Photo', 'https://www.moma.org/interactives/objectphoto/publications/770.html'),
    srcId('photosecession-291-nga', 'National Gallery of Art — 1905 New York (291)', 'https://www.nga.gov/research/publications/1905-new-york-291'),
  ],
  'モダニズム': [
    srcId('modernism-strand-eastman', 'George Eastman Museum — Paul Strand', 'https://www.eastman.org/collections/photography/strand-paul'),
    srcId('modernism-moholy-moma', 'MoMA — László Moholy-Nagy', 'https://www.moma.org/collection/artists/4048'),
  ],
  '新即物主義': [
    srcId('neuesachlichkeit-sander-met', 'The Met — August Sander', 'https://www.metmuseum.org/toah/hd/sand/hd_sand.htm'),
    srcId('neuesachlichkeit-renger-getty', 'J. Paul Getty Museum — Albert Renger-Patzsch', 'https://www.getty.edu/art/collection/person/103KHR'),
  ],
  '新しいヴィジョン': [
    srcId('newvision-moholy-tate', 'Tate — László Moholy-Nagy', 'https://www.tate.org.uk/art/artists/laszlo-moholy-nagy-1599'),
    srcId('newvision-moholy-moma', 'MoMA — László Moholy-Nagy', 'https://www.moma.org/collection/artists/4048'),
  ],
  '私写真': [
    srcId('ishiuichi-sfmoma', 'SFMOMA — Miyako Ishiuchi', 'https://www.sfmoma.org/artist/Miyako_Ishiuchi'),
    srcId('goldin-hasselblad', 'Hasselblad Foundation — Nan Goldin', 'https://hasselbladfoundation.org/wp/laureates/nan-goldin/'),
  ],
  '大判カラー写真': [
    srcId('largeformat-wall-sfmoma', 'SFMOMA artist page — Jeff Wall', 'https://www.sfmoma.org/artist/Jeff_Wall/'),
    srcId('largeformat-tate-wall', 'Tate — Jeff Wall', 'https://www.tate.org.uk/art/artists/jeff-wall-2476'),
  ],
  'ピクチャーズ世代': [
    srcId('pictures-levine-whitney', 'Whitney Museum — Sherrie Levine', 'https://whitney.org/artists/2978'),
    srcId('pictures-levine-mayhem', 'Whitney — Sherrie Levine: Mayhem', 'https://whitney.org/exhibitions/sherrie-levine/art'),
  ],
  'ステージド写真': [
    srcId('staged-sherman-moma', 'MoMA — Cindy Sherman', 'https://www.moma.org/collection/artists/5392'),
    srcId('staged-sherman-filmstills', 'MoMA — Cindy Sherman: The Complete Untitled Film Stills', 'https://www.moma.org/calendar/exhibitions/253'),
  ],
  'フェミニズム写真': [
    srcId('feminism-goldin-hasselblad', 'Hasselblad Foundation — Nan Goldin', 'https://hasselbladfoundation.org/wp/laureates/nan-goldin/'),
    srcId('feminism-sherman-whitney', 'Whitney — Cindy Sherman', 'https://whitney.org/artists/2909'),
  ],
  'ヴォルテクシズム': [
    srcId('vorticism-coburn-nga', 'National Gallery of Art — Alvin Langdon Coburn', 'https://www.nga.gov/artists/19222-alvin-langdon-coburn'),
  ],
};

const MOVEMENT_EXTRA_PARAGRAPHS_JA = {
  'ドキュメンタリー': {
    '表現解説': [
      para('19世紀の都市改造や戦争記録から出発した写真は、やがてジェイコブ・リースやルイス・ハインの改革的実践、[[m:FSA写真|FSA写真]]の国家的アーカイブ、[[p:evans|ウォーカー・エヴァンズ]]やロバート・フランクの写真集、そして1967年の「New Documents」に代表される個人的なドキュメンタリーへと読み替えられていきました。つまりドキュメンタリーの歴史は、社会を説明する写真から、写真家が社会の中でどの位置を占めるかを問う写真への移動でもあります。', ['doc-new-documents']),
    ],
    '批評と受容': [
      para('現代ドキュメンタリーでは、記録の正しさだけでなく、誰が撮り、誰が保存し、どの展示や出版の形式で届けるのかが批評の中心にあります。被写体の苦痛を見せることが改革につながるのか、それとも見る側の感情消費へ回収されるのかという論点は、古典的な社会写真から現在まで途切れず続いています。', ['doc-new-documents']),
    ],
  },
  '社会ドキュメンタリー': {
    '表現解説': [
      para('トーマス・アナンのグラスゴーのスラム、リースのニューヨーク、ハインの児童労働、[[m:FSA写真|FSA写真]]の農村、W・ユージン・スミスの地域報告、アーネスト・コールのアパルトヘイト記録を並べると、社会ドキュメンタリーは「弱者を撮る写真」ではなく、制度の暴力を可視化して公共の議論へ持ち込む連鎖として理解しやすくなります。', ['socialdoc-smith']),
    ],
  },
  'FSA写真': {
    '表現解説': [
      para('FSAのアーカイブは[[p:lange|ラング]]や[[p:evans|エヴァンズ]]だけでなく、アーサー・ロススタイン、ラッセル・リー、マリオン・ポスト・ウォルコット、ゴードン・パークスらの異なる視線を同じ行政ファイルの中に並置しました。とくにパークスのワシントンD.C.での仕事は、人種差別そのものをニューディール国家の内部から写し返した点で、プロジェクトの意味を大きく広げています。', ['fsa-about', 'fsa-parks']),
      para('この事業ではキャプションと整理番号が決定的でした。写真は撮影後にロットへ分類され、説明文を付され、新聞や機関誌で再利用されることで政策資料になっていきます。FSA写真の力はイメージ単体より、写真、説明文、アーカイブ管理が組み合わさった行政的な読み方に支えられていました。', ['fsa-captions', 'fsa-about']),
    ],
    '批評と受容': [
      para('後世の美術館や写真集がこのコレクションを名作の宝庫として読んできたこと自体も、FSA写真の複雑さの一部です。もともとは広報と調査のために作られた画像が、のちにはアメリカの記憶そのものとして展示されるようになり、行政資料と芸術作品の境界が歴史の中で組み替えられました。', ['fsa-about']),
    ],
  },
  'フォトジャーナリズム': {
    '表現解説': [
      para('1920年代から30年代のグラフ雑誌、35mmライカの普及、戦時報道、そして『LIFE』やマグナムの成立が重なることで、フォトジャーナリズムは一枚のスクープ写真ではなく、連続画像と文章を組み合わせるフォト・エッセイの制度として成熟しました。[[p:capa|キャパ]]の戦場、[[p:eugenesmith|スミス]]のルポルタージュ、[[p:cartierbresson|カルティエ＝ブレッソン]]の移動の速さは、その制度の異なる使い方でした。', ['photojournalism-life', 'photojournalism-hcb']),
    ],
    '批評と受容': [
      para('戦争写真の演出疑惑や、被写体の苦痛が誌面で劇的に消費される問題は、この領域の中心的な批判です。どの写真が表紙に選ばれ、どのキャプションが付くのかは編集部と国家と企業の力学で決まり、写真家の現場経験だけでは報道の意味を説明しきれません。', ['photojournalism-life']),
    ],
  },
  '決定的瞬間': {
    '表現解説': [
      '小型ライカの軽さ、街路での歩行のリズム、[[p:cartierbresson|カルティエ＝ブレッソン]]が若いころに吸収したシュルレアリスム的な偶然への感覚、さらにマグナム以後の出版回路が重なってはじめて、この理念は広く流通する写真観になりました。決定的瞬間とは、視覚の神話である前に、身体訓練と編集文化の結節点でもあります。',
    ],
  },
  'ストリート写真': {
    '表現解説': [
      para('アジェの都市の痕跡、ヘレン・レヴィットの子どもたちの身振り、ウィリアム・クラインの攻撃的な近接、ウィノグランドやフリードランダーの過密なフレーム、[[p:moriyama|森山大道]]のざらついた都市像は、同じ「街路」の写真でも目的がかなり違います。公共空間を偶然の劇場として読むのか、監視と消費の場として読むのかで、ストリート写真の倫理は大きく変わります。', ['street-levitt', 'street-winogrand']),
    ],
    '批評と受容': [
      '現在では、無断撮影や男性中心的な視線の問題を抜きにストリート写真を称揚することは難しくなりました。都市の他者を「面白い場面」として収集する視線が、階級やジェンダーや人種の不均衡とどう結びつくかを問うことが、このジャンルの現代的な読み替えにつながっています。',
    ],
  },
  'ストレート写真': {
    '表現解説': [
      para('この系譜は[[p:strand|ポール・ストランド]]から[[p:edward-weston|エドワード・ウェストン]]、さらにGroup f/64や[[p:ansel-adams|アンセル・アダムス]]へつながっていきます。貝殻や工業製品、砂丘や山岳、都市の壁面は、写真が対象を正確に記述するだけでなく、プリントの階調と構図によって一つの近代的な言語へ変換できることを示しました。', ['straight-weston', 'straight-ansel']),
    ],
    '批評と受容': [
      'だからこそ「ありのまま」という言い方には注意が要ります。鮮明な焦点や豊かな階調は、対象そのものの中立性ではなく、どのレンズを選び、どこまで焼き込み、どの制度で見せるかという判断の積み重ねによって成立しており、その判断を見えなくしてしまうとストレート写真の歴史的な緊張も消えてしまいます。',
    ],
  },
  'モダニズム': {
    '表現解説': [
      'ただしモダニズムの意味は地域ごとに違います。アメリカでは[[p:strand|ストランド]]や[[p:charles-sheeler|シェラー]]が都市と工業の秩序を明晰な写真へ変え、ドイツでは[[p:moholy|モホリ＝ナジ]]や[[m:バウハウス|バウハウス]]が知覚の再教育を押し出し、ソ連ではロトチェンコが革命後の視覚政治と結びつけ、日本では新興写真の動きが印刷文化と都市経験のなかで別のモダニズムを育てました。',
    ],
    '批評と受容': [
      'そのためモダニズムを単純な進歩史観として語ると、地域差や政治的条件が見えなくなります。機械視覚や普遍的な形式という語りは魅力的ですが、それが誰の都市感覚を前提にしていたのかを問わなければ、近代の一枚岩の神話を繰り返すだけになります。',
    ],
  },
  'バウハウス': {
    '表現解説': [
      'ここで[[m:新しいヴィジョン|新しいヴィジョン]]と区別しておきたいのは、バウハウスが「写真の新しい見方」そのものの名前ではなく、その見方が教育、出版、広告、舞台、建築記録の実務へ移される場だったことです。ルチア・モホリの校舎写真や制作物の記録は、作品紹介である以上に、学校が自らの姿を外部へどう見せるかを決める制度的な写真でもありました。',
    ],
    '批評と受容': [
      '今日の批判点としては、合理性や機能性の語りが、誰の身体や生活を標準にしたのかという問題があります。バウハウスの視覚は解放的な実験でもありましたが、同時に近代的な設計と管理の言語でもあり、その二面性を見失うと学校の理想像だけが先に立ってしまいます。',
    ],
  },
  '新しいヴィジョン': {
    '表現解説': [
      'モホリ＝ナジが繰り返し主張したのは、カメラは人間の裸眼を補助するだけでなく、俯瞰や仰角、極端なクローズアップ、フォトグラムによって知覚そのものを再教育できるという点でした。[[m:バウハウス|バウハウス]]がその実験を制度化した場であり、[[m:レイオグラフ|レイオグラフ]]はそこから分かれたカメラを用いない光の実験として位置づけると整理しやすくなります。',
    ],
    '批評と受容': [
      'この視覚の解放性は、近代の合理化と隣り合わせでもありました。上空から俯瞰する視線や構造を見抜く視線は、世界を新しく感じさせる一方で、対象を管理可能なデータとして見る近代的な知とも結びついています。',
    ],
  },
  '新即物主義': {
    '表現解説': [
      '[[p:renger|レンガー＝パッチュ]]の工業製品と植物、[[p:sander|ザンダー]]の職業肖像、カール・ブロスフェルトの植物標本は、どれも「物そのもの」への接近として語られますが、そこで示される構造は同じではありません。形態の反復、社会的分類、機械時代の秩序という異なる読みが、新即物主義の内部でせめぎ合っています。',
    ],
    '批評と受容': [
      'その即物性は政治的に中立ではありません。対象を整列させ、比較可能なタイプへ還元する態度は、社会を秩序化し固定化する視線ともつながりうるからです。明晰さの美学が支配の言語へ滑る可能性を含んでいる点を、この流れはよく示しています。',
    ],
  },
  '自然主義写真': {
    '表現解説': [
      'さらに重要なのは、エマーソン自身が後年、自説の一部を揺るがせたことです。自然な見え方を写真にそのまま移せるという確信は長く保たれず、写真の翻訳不可能性が彼自身の思考の中に入り込みました。自然主義写真は完成された理論というより、写真の自然さをめぐる近代の不安そのものを映しています。',
    ],
  },
  'カラー写真': {
    '表現解説': [
      para('マックスウェルの三色分解からオートクローム、さらにコダクローム以後のフィルムへと続く技術史はもちろん重要ですが、このページの核心は「色があると世界の何が変わって見えるのか」という問いにあります。ソール・ライターの早いカラー実験が都市の親密な偶然を引き寄せ、のちにエグルストンやショアが日常と郊外を正面から扱えたのも、色が商業の属性ではなく経験の質そのものを運ぶと理解されたからでした。', ['color-leiter', 'color-leiter-bio']),
    ],
    '批評と受容': [
      para('一方で、カラーが長く広告、観光、家庭アルバムと結びついてきたため、美術写真としての受容には階級的な偏見も介在していました。のちの[[p:parr|マーティン・パー]]のように、その商業的で俗っぽい見え方自体を利用して社会批評を行う実践は、この長い偏見の裏返しとして理解できます。', ['color-parr']),
    ],
  },
  'ニューカラー': {
    '表現解説': [
      para('転換点としてよく言及される1976年のMoMA「William Eggleston\'s Guide」は、カラーが美術館に入ったこと自体より、何でもない日常の断片を色の強度だけで写真の中心主題にできると示した点で大きな意味を持ちました。[[p:stephen-shore|スティーヴン・ショア]]がロードサイドと郊外の時間を平たい色面の連鎖として見せたのに対し、のちの[[p:parr|マーティン・パー]]はそのカラーを風刺と消費社会批評の側へずらしていきます。', ['newcolor-eggleston-moma', 'newcolor-eggleston-whitney', 'newcolor-parr']),
    ],
  },
  '大判カラー写真': {
    '表現解説': [
      para('ここでは「大判カメラ」と「大型プリント」と「カラー展示」が必ずしも同じではありません。[[p:wall|ジェフ・ウォール]]は光箱によって一枚の場面を映画のような光で立ち上げ、[[p:gursky|グルスキー]]は巨大な視野で市場や群衆を解析し、トーマス・シュトゥルートやカンディダ・ヘーファーは建築や美術館の空気を静かな正面性へ変え、グレゴリー・クリュードソンやフィリップ＝ロルカ・ディコルシアは演出された時間の気配を厚くしました。サイズの効果は共通していても、作品が引き受ける時間や制度はかなり違います。', ['largeformat-crewdson', 'largeformat-dicorcia']),
    ],
  },
  'デュッセルドルフ派': {
    '表現解説': [
      para('ベッヒャー夫妻の学生たちも一枚岩ではありません。[[p:gursky|グルスキー]]は世界市場の俯瞰へ、トーマス・ルフはポートレートやデジタル画像の条件へ、カンディダ・ヘーファーは制度空間の無人性へ、トーマス・シュトゥルートは都市と美術館の複層的な視線へ、それぞれ別の方向へ進みました。デュッセルドルフ派を単なる客観写真の学校とみなすと、この分岐の豊かさが見えなくなります。', ['dusseldorf-tate-bechers']),
    ],
    '批評と受容': [
      'さらに、デジタル処理が大判プリントの内部へ入り込んだことで、「冷静な客観性」が実際にはどこまで加工された構成なのかという問題も前景化しました。現代美術市場での成功が大きいからこそ、その透明さがどの程度まで演出されたものなのかを問い返す必要があります。',
    ],
  },
  'コンセプチュアルアート': {
    '表現解説': [
      para('エド・ルシェのアーティストブック、ダグラス・ヒューブラーの位置作品、ダン・グラハムの郊外住宅の連載、ジョセフ・コスースの《One and Three Chairs》、ジョン・バルデッサリの写真と言葉のずらしを並べると、写真は「作品の記録」ではなく、概念を成立させる手続きそのものへ変わっていきます。地図、索引、ノート、新聞、複製物が作品の中心へ入ってくることで、写真は物質的な一点物より、思考を流通させる媒体として機能しました。', ['concept-kosuth', 'concept-siegelaub', 'concept-baldessari']),
    ],
    '批評と受容': [
      'その代わり、理論化や制度批評が強まるほど、写真の経験や身体性が薄れるという批判も生まれます。作品が賢く整理された手続きとして読めるほど、見ることの偶然や感情の厚みが後景に退くという問題は、のちのピクチャーズ世代やフェミニズム写真が再び引き受ける論点になりました。',
    ],
  },
  'ピクチャーズ世代': {
    '表現解説': [
      para('1977年の「Pictures」展とダグラス・クリンプの批評は、写真を「現実の記録」ではなく、すでに流通しているイメージの再配置として読む枠組みを与えました。[[p:sherman|シンディ・シャーマン]]が映画的女性像を演じ直し、[[p:sherrie-levine|シェリー・レヴィーン]]が作者性そのものを盗用で揺さぶり、リチャード・プリンスが広告の語法を奪い、[[p:kruger|バーバラ・クルーガー]]やルイーズ・ローラーが制度の視線を言葉と展示の側から切り返したように、同じ世代でも戦略はかなり異なります。', ['pictures-icp', 'pictures-lawler']),
    ],
    '批評と受容': [
      '引用と盗用の境界、作者性を批判しながら作家名が市場でブランド化する矛盾、政治的批判が洗練されたスタイルとして回収される危険は、この世代の核心的な問題です。だからこそピクチャーズ世代は、ポストモダンの勝利というより、批判が制度の中でどのように消費されるかを示した症例として読み直されます。',
    ],
  },
  'フェミニズム写真': {
    '表現解説': [
      para('[[p:sherman|シンディ・シャーマン]]や[[p:kruger|バーバラ・クルーガー]]だけでなく、マーサ・ロスラーのフォトテクスト、メアリー・ケリーやジョー・スペンスの家族・母性・労働をめぐる実践を並べると、フェミニズム写真の中心にあったのが「女性をどう表象するか」だけではなく、写真と言葉、家庭と公共圏、自己記録と制度批評の関係そのものだったことが見えてきます。', ['feminism-rosler', 'feminism-kruger']),
    ],
    '批評と受容': [
      'さらに近年では、白人中産階級中心の経験に偏っていたこと、ジェンダー二元論が前提になりがちだったこと、クィアや有色人種やポストコロニアルな視点が後景化されてきたことも強く批判されています。フェミニズム写真は完結した達成ではなく、自らの枠組みを内部から更新し続ける運動として読むべきでしょう。',
    ],
  },
  '私写真': {
    '表現解説': [
      '日本の私写真は、[[p:araki|荒木経惟]]や[[p:masahisa-fukase|深瀬昌久]]だけでなく、牛腸茂雄、[[p:miyako-ishiuchi|石内都]]、[[p:yurie-nagashima|長島有里枝]]、HIROMIXのように、家族、身体、恋愛、少女文化、死の記憶をそれぞれ異なる写真集の形式で掘り下げてきました。ナン・ゴールディンの親密圏写真と響き合う面はあっても、日本の私写真は戦後の写真批評と出版文化の中で育った点で同一ではありません。',
    ],
    '批評と受容': [
      'とりわけ、男性写真家の私性がしばしば大胆さや告白性として称揚され、女性写真家の私性がナルシシズムやスキャンダルとして読まれやすかったことは、私写真の受容に残る大きな偏りです。親密さを語る言葉そのものが、ジェンダー化された制度の中で配分されてきました。',
    ],
  },
  'ダダ': {
    '表現解説': [
      'ベルリン・ダダにおけるハンナ・ヘッヒ、ジョン・ハートフィールド、ラウル・ハウスマンのフォトモンタージュは、雑誌や新聞のイメージを切断して、戦後ドイツの政治とメディアそのものを風刺する装置でした。マン・レイの実験が個々のイメージの不安定さへ向かったのに対し、ベルリンの写真実践は印刷メディアの大量流通へ直接介入する点で、より露骨に政治的です。',
    ],
  },
  'シュルレアリスム': {
    '表現解説': [
      para('シュルレアリストたちがアジェの街路写真を愛読したのは、そこに奇妙な無人性と現実のずれを見たからでした。マン・レイやリー・ミラー、ドーラ・マール、クロード・カアンの実践、さらに『La Révolution surréaliste』や『Minotaure』のような雑誌の配置まで視野に入れると、シュルレアリスム写真は単なる技法の一覧ではなく、写真の現実らしさが不気味さの条件になるという逆説の場として立ち上がります。', ['surrealism-atget', 'surrealism-cahun']),
    ],
    '批評と受容': [
      'その一方で、女性身体の客体化や異国趣味的なイメージの利用、男性中心の欲望の構図に対する批判も避けて通れません。夢や無意識を称揚する語りが、誰の欲望を中心に組み立てられていたのかを問うことが、現在のシュルレアリスム研究では欠かせなくなっています。',
    ],
  },
  'タイポロジー写真': {
    '表現解説': [
      'ここで混同したくないのは、19世紀の科学的分類写真と、20世紀に美術として成立するタイポロジー写真の差です。後者では、条件を揃えて反復すること自体が最終目的ではなく、反復によって差異と構造が立ち上がることが重視されます。[[p:sander|ザンダー]]、ブロスフェルト、[[p:becher|ベッヒャー夫妻]]の仕事が現代美術のシリーズへ引き継がれたのは、その反復が知識の形式であると同時に、美的判断そのものにもなったからでした。',
    ],
    '批評と受容': [
      'しかし分類は常に権力の作用を伴います。人物や建築をタイプへ還元することは、個別の歴史や文脈を見えにくくし、標準から外れるものを逸脱として周縁化する危険を持っています。タイポロジー写真の批評性は、その暴力性をどこまで可視化できるかにかかっています。',
    ],
  },
  'ステージド写真': {
    '表現解説': [
      '[[p:sherman|シンディ・シャーマン]]がセルフイメージとメディアの型をずらし、[[p:wall|ジェフ・ウォール]]が光箱の大画面で都市の一場面を再構成し、グレゴリー・クリュードソンが映画の撮影隊のような規模で郊外の夜を作り込み、フィリップ＝ロルカ・ディコルシアが街路や親密圏を演出された現場へ変えるように、ステージド写真の差は単なる「演出の多さ」では測れません。何を現実らしく見せ、その現実らしさをどこで疑わせるかがそれぞれ違います。',
    ],
  },
  'シネマトグラフィック写真': {
    '表現解説': [
      para('[[p:wall|ジェフ・ウォール]]の光箱は絵画史と都市の一場面を同じ画面に収め、フィリップ＝ロルカ・ディコルシアは街頭やポートレートを「映画の一コマのように見えるが実際には前後を欠いた写真」へ変え、グレゴリー・クリュードソンは撮影隊と照明装置を使って郊外の夜を巨大な静止劇として構築しました。[[p:sherman|シンディ・シャーマン]]の映画的セルフイメージは、映画の場面を再演しながらも、俳優も監督も一人で引き受ける点でまた別の方向を示しています。', ['cinema-wall', 'cinema-dicorcia', 'cinema-crewdson', 'cinema-sherman']),
    ],
    '批評と受容': [
      para('こうした映画的演出は、社会的な文脈を曖昧にして高級なスタイルへ回収される危険とも隣り合わせです。とくに大規模な制作や大判プリントが市場で強い価値を持つと、写真の記録性との緊張より、スペクタクルとしての完成度ばかりが評価されることがあります。そのためシネマトグラフィック写真を読むときは、何が美しく演出されているのかだけでなく、どの現実がその演出の外へ追いやられているのかを見る必要があります。', ['cinema-wall', 'cinema-dicorcia', 'cinema-crewdson']),
    ],
  },
};

const MOVEMENT_DEEPENING_JA = {
  'ピクトリアリズム': {
    '表現解説': [
      para('イギリスのLinked Ring、フランスのフォト・クラブ・ド・パリ、アメリカの写真分離派は、見た目の好みを共有したというより、写真をサロン、美術雑誌、限定ポートフォリオの中でどう扱うかを競い合う国際的な制度圏でした。日本の芸術写真もこの流れと無関係ではなく、写真が工芸品でも報道資料でもない第三の領域を持ちうるという期待をここから受け取っています。', ['pictorialism-steichen-met', 'pictorialism-photo-secession-moma']),
    ],
    '批評と受容': [
      '近年の再評価では、ピクトリアリズムは単に乗り越えられた旧様式ではなく、写真を一点物のプリント、作者名、展示制度、批評語と結びつけた基盤として読まれています。だからこそ、のちのストレート写真の批判も、外部からの否定ではなく、この制度を受け継いだ内部批判として理解する必要があります。',
    ],
  },
  '写真分離派': {
    '表現解説': [
      para('291が重要だったのは、写真だけを閉じたサークルで擁護したからではありません。スティーグリッツがマティスやピカソ、セザンヌを同じ空間で見せたことで、写真は近代美術の周辺的な技術ではなく、同時代の視覚言語の一部として語られ始めました。雑誌『Camera Work』の紙質や図版の選択まで含めて、写真分離派は写真をどう見せるかの制度を設計したのです。', ['photosecession-camerawork-moma', 'photosecession-291-nga']),
    ],
    '批評と受容': [
      'しかも、この運動の歴史はピクトリアリズムの固定化では終わりません。1917年の『Camera Work』最終号でストランドが前景化されると、スティーグリッツ自身の中で、絵画に似せる芸術写真から、写真固有の明晰さへ重心が移ったことがはっきりします。写真分離派は、一つの様式名というより、写真が自らの制度を組み替えながら近代化していく通路でした。',
    ],
  },
  'ストレート写真': {
    '表現解説': [
      'この系譜が強い説得力を持ったのは、鮮明さがそのまま素朴な客観性を意味しなかったからです。[[p:edward-weston|ウェストン]]の貝殻や野菜、[[p:ansel-adams|アンセル・アダムス]]の山岳、Group f/64の精密なプリントは、対象をそのまま写したというより、レンズ、絞り、用紙、焼き込みの判断によって、世界を写真の構造へ変換する行為でした。写真の固有性とは、加工をやめることではなく、写真の条件の中でどこまで形式を組み立てられるかという問いだったのです。',
    ],
    '批評と受容': [
      'そのため「ありのまま」という言い方だけが独り歩きすると、写真家の構図や距離感だけでなく、美術館、雑誌、写真学校が支えた近代的な価値判断まで見えなくなります。ストレート写真は中立な記録の勝利ではなく、記録らしさをどのような形式で美学へ変えるかをめぐる制度的な勝利でもありました。',
    ],
  },
  '自然主義写真': {
    '表現解説': [
      'ピーター・ヘンリー・エマーソンが重視したのは、単一ネガ、単一露光、そして視覚生理学に近い「自然な焦点」の考え方でした。複数ネガの合成や舞台装置のような演出を退けたのは、客観性を絶対視したからではなく、人間が風景をどう知覚するかという理論に写真を接続したかったからです。自然主義写真は写真的自然をめぐる理論であって、自然そのものの無媒介な写しではありませんでした。',
    ],
    '批評と受容': [
      'しかもエマーソンは後年、自説の限界を自ら認めます。自然な見え方が一つに定まるという確信は揺らぎ、写真の翻訳不可能な部分が前面に出てきたからです。そのため自然主義写真は、ストレート写真の前史であると同時に、「自然」という言葉自体がいかに構成的かを示す歴史的な症例でもあります。',
    ],
  },
  'モダニズム': {
    '表現解説': [
      para('モダニズムを一枚の地図で語れないのは、アメリカでは[[p:strand|ストランド]]や[[p:charles-sheeler|シェラー]]が都市と産業の秩序を明晰な写真へ変え、ドイツでは[[m:バウハウス|バウハウス]]や[[m:新しいヴィジョン|新しいヴィジョン]]が視覚の再教育を掲げ、ソ連ではロトチェンコが革命後の視覚政治と結びつき、日本では新興写真や印刷文化の中で別のモダニズムが育ったからです。共通しているのは進歩の語彙ではなく、写真が近代社会の経験をどのような形式へ置き換えるかという問いでした。', ['modernism-strand-eastman', 'modernism-moholy-moma']),
    ],
    '批評と受容': [
      'この語を便利に使いすぎると、機械視覚や抽象や都市の経験があたかも同じ方向へ進んだかのように見えてしまいます。実際には、都市化や革命、広告、雑誌印刷、植民地経験など、地域ごとの条件が視覚の意味を大きく変えていました。モダニズムは完成した様式ではなく、複数の近代が衝突する場として読むほうが実態に近いはずです。',
    ],
  },
  '新即物主義': {
    '表現解説': [
      para('[[p:renger|レンガー＝パッチュ]]、[[p:sander|アウグスト・ザンダー]]、カール・ブロスフェルトはしばしば同じ陣営に置かれますが、対象への向き合い方はかなり違います。植物の形態を純粋な構造として取り出す視線、職業と階層を顔貌の体系として並べる視線、工業製品や建築の表面を明晰に見せる視線が交差していたからこそ、新即物主義は単なる「物そのもの」への礼賛では終わりませんでした。', ['neuesachlichkeit-sander-met', 'neuesachlichkeit-renger-getty']),
    ],
    '批評と受容': [
      'その即物性は、政治から自由な透明性ではありません。タイプへ整列させることで、社会の差異を比較可能にしながら、同時に固定化してしまう危険も抱えています。のちのデュッセルドルフ派やタイポロジー写真がこの遺産を引き継いだのは、明晰さが美学であると同時に、分類の権力でもあることを受け継いだからでした。',
    ],
  },
  '新しいヴィジョン': {
    '表現解説': [
      para('モホリ＝ナジやロトチェンコが強調した俯瞰、仰角、極端なクローズアップ、フォトグラム、タイポフォトは、単なる奇抜な視点の競争ではありませんでした。カメラが人間の裸眼の習慣を破り、雑誌や広告や教育の場で新しい知覚を訓練できるという思想が、その背後にあります。[[m:バウハウス|バウハウス]]がこの思想を制度化し、[[m:レイオグラフ|レイオグラフ]]がカメラの外から光の実験を押し広げたことで、新しいヴィジョンは近代の視覚理論として広がりました。', ['newvision-moholy-tate', 'newvision-moholy-moma']),
    ],
    '批評と受容': [
      'ただし、人間の自然な視覚を更新するという解放の言葉は、対象を上から把握し、機能的に整理する近代的な管理の語彙とも重なります。視覚の再教育は自由であると同時に規律でもありうる。その二面性を見失うと、新しいヴィジョンは単なる前衛的デザインの明るい物語へ還元されてしまいます。',
    ],
  },
  'バウハウス': {
    '表現解説': [
      'また、ルチア・モホリの校舎写真や制作物の記録は、学校の自己像を作る点で決定的でした。机、椅子、窓、階段、工房、ポスターが整った秩序として見えるのは、建築そのものだけでなく、それをどう撮るかという写真の選択によるものです。バウハウスは写真の流派というより、写真がデザイン教育、印刷物、広告、建築記録に横断的に入り込む制度だったことが、この記録からはっきりします。',
    ],
    '批評と受容': [
      'その一方で、合理的で機能的な視覚が、誰の身体や暮らしを標準にしていたのかという問いも避けられません。整頓された家具や明るい建築のイメージは魅力的ですが、そこには近代的な生活の規範化が伴います。バウハウス写真を、自由な実験と生活の標準化が重なる場所として読むことが、現在の見直しでは重要になっています。',
    ],
  },
  'ダダ': {
    '表現解説': [
      'ジョン・ハートフィールドの政治的フォトモンタージュが、新聞やポスターの回路でファシズムや資本主義を直接風刺したのに対し、マン・レイの実験は写真の物質的な不確かさを押し出しました。ここにある差を押さえると、ダダは単なる奇抜な前衛ではなく、印刷メディアの政治利用と写真そのものの解体が同時に進んだ場だったと見えてきます。',
    ],
    '批評と受容': [
      'のちにダダが美術館や教科書の中で正典化されると、反芸術の衝撃はしばしば安全な歴史語りへ回収されました。政治性と遊戯性のあいだの緊張、印刷物に介入する攻撃性、既存の秩序を笑いで壊す身振りを見失うと、ダダの写真はただの面白いコラージュに縮んでしまいます。',
    ],
  },
  'シュルレアリスム': {
    '表現解説': [
      para('アジェの街路写真がシュルレアリストに愛読されたこと、マン・レイやリー・ミラー、ドーラ・マール、クロード・カアンの実践が雑誌『La Révolution surréaliste』や『Minotaure』の中で再配置されたことを考えると、シュルレアリスム写真は単独作品の集合より、印刷と配置の文化として理解したほうがよくわかります。写真の現実らしさが強いからこそ、その小さなずれや反転が不気味さを帯びるのです。', ['surrealism-atget', 'surrealism-cahun']),
    ],
    '批評と受容': [
      '同時に、夢や無意識の名のもとで女性身体や異国趣味的イメージが道具化されたことも、この流れの大きな問題でした。誰の欲望が中心に置かれ、誰が謎めいた他者として配置されたのかを問う視点がなければ、シュルレアリスムの解放性は簡単に男性中心の神話へ戻ってしまいます。',
    ],
  },
  'レイオグラフ': {
    '表現解説': [
      'レイオグラフを独立ページとして残す理由は、マン・レイの個人技法にとどまらず、写真がカメラとレンズによる記録だという前提を、印画紙の上の光そのもので崩したからです。モホリ＝ナジのフォトグラムと近い点もありますが、ダダやシュルレアリスムの文脈では、物が影と接触痕として現れる不気味さがより前景化されます。',
    ],
    '批評と受容': [
      'ただし、広い運動名のように膨らませる必要はありません。レイオグラフは短い技法史のページとして読むほうが適切で、その歴史的な意味は、写真の記録性を壊すためにこそ写真材料が使われたという逆説にあります。',
    ],
  },
  'ドキュメンタリー': {
    '表現解説': [
      '19世紀の戦争、都市改造、考古学、植民地記録から始まるこの系譜は、アジェの街路、リースやハインの改革的写真、FSAの国家的記録、ウォーカー・エヴァンズやロバート・フランクの写真集、さらに「New Documents」以後の主観的な観察へと何度も組み替えられてきました。ドキュメンタリーとは、現実を撮る一つの方法というより、現実に対して写真がどの位置に立つかをめぐる長い論争の名前です。',
    ],
    '批評と受容': [
      'だからこそ、キャプション、編集、アーカイブ、展覧会の順路が意味を大きく左右します。誰が語り、誰が撮られ、どの制度がその像を保存し再利用するのかという権力関係を抜きに、「客観的記録」だけを語ることはできません。現代のドキュメンタリー論は、この制度の層をあらわにするところから始まっています。',
    ],
  },
  '社会ドキュメンタリー': {
    '表現解説': [
      '社会ドキュメンタリーの流れをたどるなら、トーマス・アナンのスラム記録、ジェイコブ・リースの都市貧困、ルイス・ハインの児童労働、FSAの農村記録、ドロシア・ラングやW・ユージン・スミス、さらにアーネスト・コールのアパルトヘイト批判まで、写真が改革や告発の言葉として働いた場面を連続して見る必要があります。ここでは単に現実を見せるだけでなく、見せることで社会を動かしたいという意志が前提になっていました。',
      'その意味で、社会ドキュメンタリーはニュース媒体に依存するフォトジャーナリズムとも、国家機関のアーカイブであるFSA写真とも少し違います。展示、冊子、慈善団体、労働運動、雑誌特集といった複数の回路を使いながら、写真が社会問題の可視化そのものへ介入するところに、この系譜の特徴があります。',
    ],
    '批評と受容': [
      'しかし、他者の苦しみを正義の名で見せることが、そのまま被写体の尊厳を守るとは限りません。貧困や差別の像が、観客の同情や道徳感情を満たす消費物になってしまう危険は常にあります。社会を変えるための写真であるほど、撮る側と撮られる側の非対称をどう扱うかが厳しく問われます。',
    ],
  },
  'フォトジャーナリズム': {
    '表現解説': [
      'フォトジャーナリズムを成り立たせたのは、出来事そのものより、雑誌と編集の制度でした。1920年代から30年代のグラフ雑誌、小型カメラ、通信社、そして『LIFE』やマグナムの回路の中で、写真は単独の一枚ではなく、キャプション、見出し、ページレイアウトと組になって意味を持ちます。ロバート・キャパやW・ユージン・スミスの写真が強く記憶されるのも、現場の身体性だけでなく、その像がフォト・エッセイとして配列されたからです。',
    ],
    '批評と受容': [
      'そのため、客観報道という自己像も絶えず揺さぶられてきました。写真の選択、トリミング、キャプション、掲載順、検閲の有無が変われば、同じ現場の像でもまったく別の政治的意味を帯びるからです。ドキュメンタリーや決定的瞬間との違いを見ると、フォトジャーナリズムがニュースの制度に深く依存する表現であることがよくわかります。',
    ],
  },
  'FSA写真': {
    '表現解説': [
      para('FSA写真が特異なのは、単なる社会ドキュメンタリーではなく、1935年以後のニューディール政策のもとで、ロイ・ストライカーが撮影指示、分類、キャプション、配布まで管理した政府アーカイブだった点です。ドロシア・ラング、[[p:evans|ウォーカー・エヴァンズ]]、アーサー・ロススタイン、ラッセル・リー、ゴードン・パークスらの像は、貧困の証言であると同時に、国家が自らの社会像を組み立てる資料でもありました。', ['fsa-about', 'fsa-captions', 'fsa-parks']),
    ],
    '批評と受容': [
      para('そのためFSA写真は、改革のための視覚資料として称賛される一方、貧困をどのような顔で代表させるかを政府が選び取ったアーカイブでもあります。キャプションや配布先の違いによって意味が変わること、被写体の生活が国家の物語へ取り込まれること、その両方を見なければ、この写真群の政治性は読み切れません。', ['fsa-about', 'fsa-captions']),
    ],
  },
  '決定的瞬間': {
    '表現解説': [
      'さらに重要なのは、この理念が接触紙、選択、トリミング、雑誌や写真集での配置を通じて完成していたことです。カルティエ＝ブレッソンの身体感覚だけが奇跡的だったのではなく、撮影後にどのコマを決定的と読むかという編集の仕事が、この神話を支えていました。マグナムの国際的な流通は、その判断を世界標準の写真観として広める役割を果たします。',
      'また、シュルレアリスムに学んだ偶然への感受性と、街路の幾何学を読む訓練が同時に働いていたことも見逃せません。一瞬を切り取る感覚は、直感だけでなく、路上で歩きながら構図を予測する反復的な身体技術に支えられていました。',
    ],
    '批評と受容': [
      'だから決定的瞬間の神話は、写真家個人の天才性を過度に美化しやすいのです。そこで見えにくくなるのは、被写体との関係、撮り直されなかったコマ、編集者の選択、出版制度の力です。今日この言葉を使うなら、一枚の完成像より、その像がどのように決定されたのかまで含めて考える必要があります。',
    ],
  },
  'ストリート写真': {
    '表現解説': [
      'ストリート写真の前史にはアジェの都市記録があり、そこからヘレン・レヴィットの子どもたち、ウィリアム・クラインの過密な街路、ゲリー・ウィノグランドやリー・フリードランダーのずれたフレーミング、さらに森山大道の都市のざらつきへと枝分かれしていきます。共通するのは「路上で撮った」という事実ではなく、匿名の他者と偶然の出来事が絶えず交差する都市の経験そのものを、写真の形式へ引き受けた点です。',
    ],
    '批評と受容': [
      'その一方で、同意のない撮影、公共空間における監視と盗撮性、都市の他者を消費する視線、男性写真家中心の歴史といった問題も大きいままです。路上が自由な観察の場であるという神話を疑い、誰が誰を見ているのかを問うところから、現在のストリート写真論は始まっています。',
    ],
  },
  'リアリズム写真': {
    '表現解説': [
      '土門拳の「絶対非演出・絶対スナップ」という標語が重かったのは、戦前のサロン写真だけでなく、戦時中の報道とプロパガンダの経験が背後にあったからです。写真が国家の物語へ奉仕した記憶のあとで、何をもって誠実な写真と呼ぶべきかという倫理が戦後日本で切実になりました。『ヒロシマ』や『筑豊のこどもたち』は、単なる記録集ではなく、その倫理を写真集と雑誌を通じて公共圏へ持ち込む試みでした。',
      'また、戦後の写真誌やアマチュア写真の場では、リアリズムは個々の作家論以上に、写真が社会とどう関わるべきかをめぐる規範として働きました。地方の記録運動や報道実践とも接続しながら、「演出を避けること」が公共性の条件として共有されていったのです。',
    ],
    '批評と受容': [
      'しかし非演出という理念自体が、やがて別の神話にもなります。撮影者の選択、雑誌の編集、展覧会の文脈が見えなくなると、リアリズムは透明な事実の別名のように扱われてしまうからです。のちにプロヴォークがこの規範へ反発したのは、現実の不安定さが、明晰な正面性だけでは収まらないと感じられたからでした。',
    ],
  },
  'プロヴォーク': {
    '表現解説': [
      '1968年から69年の雑誌『Provoke』は、街路や政治運動の現場そのものだけでなく、印刷物のページ上で写真と言葉がどうぶつかるかを実験した場でした。中平卓馬、高梨豊、多木浩二、岡田隆彦、森山大道が共有していたのは、説明する言語がすでに現実から遅れているという感覚で、写真はその遅れや摩擦を別の言語として可視化しようとしました。',
    ],
    '批評と受容': [
      '後続世代にとって問題なのは、アレ・ブレ・ボケがしばしば政治的切迫を離れてスタイルだけ模倣されたことです。男性中心の都市神話や、荒れた像を見せること自体が批評になるという短絡もここで生まれました。プロヴォークの本当の強度は、荒れた見た目ではなく、写真と言葉の関係を根底から疑った点にあります。',
    ],
  },
  '私写真': {
    '表現解説': [
      para('私写真の重要さは、親密な主題そのものより、写真集の編集で時間と関係をどう組み替えたかにあります。荒木経惟の連鎖する日常、深瀬昌久の暗い反復、牛腸茂雄の近さ、石内都の身体の痕跡、長島有里枝のフェミニズム的な自己介入、HIROMIXの軽やかなスナップは、どれも「私」を見せる方法が違います。ナン・ゴールディンとの比較は有効ですが、日本の私写真は戦後写真批評とフォトブック文化に深く依存している点で同一ではありません。', ['ishiuichi-sfmoma', 'goldin-hasselblad']),
    ],
    '批評と受容': [
      'また、家族や恋人を撮ることは親密さの証明ではなく、倫理的な緊張でもあります。とりわけ男性写真家の私性が大胆な告白として称揚され、女性写真家の私性がナルシシズムや挑発として読まれやすかったことは、私写真の歴史に残る非対称です。私的であることがそのまま解放ではないという点を、この流れはむしろ鋭く示しています。',
    ],
  },
  'ニューカラー': {
    '表現解説': [
      para('ウィリアム・エグルストンが色を日常の熱として扱い、[[p:stephen-shore|スティーヴン・ショア]]がロードサイドの時間を平たい面の連鎖として組み立てたのに対し、のちの[[p:parr|マーティン・パー]]は彩度の高さそのものを消費社会の風刺へ転用しました。ニューカラーは一枚岩の作風ではなく、カラーが美術写真の文法になったあとで、何を日常の主題として選び取れるかをめぐる分岐の始点だったのです。', ['newcolor-eggleston-whitney', 'newcolor-eggleston-moma', 'newcolor-parr']),
    ],
    '批評と受容': [
      '1976年のMoMA展が典型ですが、当時の批判はしばしば「俗っぽい」「商業的すぎる」という語で行われました。つまり問題にされたのは技術ではなく、日常の包装、看板、食卓、郊外の色を美術館の中心へ持ち込む価値判断そのものでした。ニューカラーの転換点とは、カラーが許された瞬間というより、許されないとされていた日常が主題になった瞬間でもあります。',
    ],
  },
  'カラー写真': {
    '表現解説': [
      '手彩色、オートクローム、コダクロームといった技術史は出発点にすぎません。より重要なのは、色が入ることで写真が広告、旅行、ファッション、家族アルバムと強く結びつき、その結果として美術写真の制度から長く低く見られてきたことです。ソール・ライターの早い都市写真からエグルストン、ショア、さらにパーまでを見ると、色は世界を飾る属性ではなく、日常の価値づけそのものを変える条件として働いていました。',
    ],
    '批評と受容': [
      'カラーがしばしば商業的で軽いと見なされた歴史は、写真の価値判断が階級やメディア環境と切り離せないことを示します。広告や観光の色彩に近いほど低く見られたのは、写真の芸術性が依然として禁欲的なモノクロームと結びついていたからです。カラー写真の歴史は、色の技術史である以上に、その偏見の歴史でもあります。',
    ],
  },
  '大判カラー写真': {
    '表現解説': [
      para('ここで区別したいのは、大判カメラ、大型プリント、カラー展示、デジタル処理が必ずしも同じものではないという点です。[[p:wall|ジェフ・ウォール]]は光箱によって場面を映画的に立ち上げ、[[p:gursky|グルスキー]]は巨大な俯瞰で市場や群衆を解析し、トーマス・シュトゥルートやカンディダ・ヘーファーは制度空間の静けさを拡張し、グレゴリー・クリュードソンやフィリップ＝ロルカ・ディコルシアは演出された時間の厚みを押し広げました。共通するのはサイズではなく、壁面全体を使って写真の見る条件を変えたことです。', ['largeformat-wall-sfmoma', 'largeformat-tate-wall', 'largeformat-dicorcia', 'largeformat-crewdson']),
    ],
    '批評と受容': [
      'その反面、巨大サイズは社会的複雑さを高級な視覚体験へ変えてしまう危険も抱えます。大きいこと自体が価値になると、写真が問いかけていた制度や労働や都市の問題が、圧倒的な鑑賞体験の裏へ隠れてしまうからです。大判カラー写真は現代美術館の壁面と市場が写真の意味をどう変えたかを最もよく示す領域でもあります。',
    ],
  },
  'デュッセルドルフ派': {
    '表現解説': [
      'ベッヒャー夫妻の教育が重要なのは、学生たちに一つの見た目を教えたからではなく、シリーズで比較し、印刷物と展示で意味を変え、産業風景を戦後ドイツの記憶と結びつける見方を教えたからです。そこからグルスキーの市場と群衆、トーマス・ルフのポートレートとデジタル画像、カンディダ・ヘーファーの制度空間、トーマス・シュトゥルートの都市と美術館へと、かなり違う方向が生まれました。',
    ],
    '批評と受容': [
      'この流れが現代美術市場で強い成功を収めたからこそ、冷静な客観性が一種の高級な様式へ変わる危険も大きくなります。しかもデジタル処理が画面内部へ入り込むと、現実を淡々と示すように見える像が、実際にはどこまで構成されたものなのかという問いが避けられません。デュッセルドルフ派は、客観性が最も制度化された場所でもありました。',
    ],
  },
  'タイポロジー写真': {
    '表現解説': [
      '19世紀の科学写真や人類学的分類と、20世紀の美術としてのタイポロジーを分けて考える必要があるのは、後者が単に並べることではなく、並べることで差異の構造を見せるからです。ザンダーの職業肖像、ブロスフェルトの植物、ベッヒャー夫妻の産業建築は、対象を同一化するためではなく、反復の中から制度や歴史を見せるために比較の形式を用いました。',
    ],
    '批評と受容': [
      'しかし分類は、理解の手段であると同時に、規範を作る手段でもあります。人物や建築をタイプへ還元することは、そこから外れるものを例外として扱う暴力と背中合わせです。タイポロジー写真の面白さは、その整然とした表面の裏で、この暴力がどこまで露出しているかにあります。',
    ],
  },
  'コンセプチュアルアート': {
    '表現解説': [
      'アーティストブック、地図、索引、テキスト、写真記録が一体化したところに、コンセプチュアルアートにおける写真の特徴があります。エド・ルシェのガソリンスタンドの本、ダグラス・ヒューブラーの位置作品、ダン・グラハムの住宅批評、ジョセフ・コスースの言語作品は、写真が作品を証明する添え物ではなく、概念を手続きとして成立させる媒体になったことを示しました。',
    ],
    '批評と受容': [
      'その遺産はピクチャーズ世代、フェミニズム写真、タイポロジー的な展示形式に強く残りますが、同時に「理論が先に立ちすぎる」「見る経験や身体性が薄くなる」という批判も招きました。写真が賢い手続きになるほど、感情や偶然や触覚が作品の外へ押し出される。その緊張もまた、この運動の重要な歴史です。',
    ],
  },
  'ピクチャーズ世代': {
    '表現解説': [
      para('1977年の「Pictures」展とダグラス・クリンプの批評が重要なのは、広告、映画、テレビ、雑誌のイメージ環境そのものを作品の主題へ変えたからです。[[p:sherman|シンディ・シャーマン]]が女性像を演じ直し、シェリー・レヴィーンが作者性を盗用で崩し、リチャード・プリンスが広告の話法を奪い、[[p:kruger|バーバラ・クルーガー]]やルイーズ・ローラーが制度の視線を言葉や展示の側から切り返したように、ここでは写真は現実の記録ではなく、すでにあるイメージの再配置として働きます。', ['pictures-icp', 'pictures-lawler', 'pictures-levine-whitney', 'pictures-levine-mayhem']),
    ],
    '批評と受容': [
      'ただし、引用や盗用の政治性は、作品が市場で流通するほど洗練されたスタイルへも変わります。作者性を疑う運動が、作家名のブランド化によって再び市場価値を持ってしまうという矛盾は、この世代の宿命的な問題でした。そのためピクチャーズ世代は、ポストモダンの勝利ではなく、批判がどう制度に回収されるかを示す歴史として読むべきです。',
    ],
  },
  'ステージド写真': {
    '表現解説': [
      para('ステージド写真は、単に「演出した写真」ではなく、写真が本来持つ証拠性を逆手に取って、作られた場面をどこまで現実らしく信じさせられるかを試す方法です。シンディ・シャーマンは自己像とメディア像の関係を、ジェフ・ウォールは都市の場面と絵画史の関係を、グレゴリー・クリュードソンは映画撮影の規模を、フィリップ＝ロルカ・ディコルシアは街頭と演出の境界を、それぞれ違うやり方で押し広げました。', ['staged-sherman-moma', 'staged-sherman-filmstills']),
      'そのためステージド写真は、コンセプチュアルアートの手続きとも、ピクチャーズ世代の引用とも、シネマトグラフィック写真の時間感覚とも重なりつつ、どこで現実らしさを崩すかという一点で見分ける必要があります。演出の度合いではなく、演出が写真の真実性をどう揺らすかが核心です。',
    ],
    '批評と受容': [
      '批判としては、緻密な制作や大型展示が、それ自体で高級なスペクタクルへ転化しやすいことが挙げられます。現実を問い返すはずの演出が、むしろ現代美術市場向けの完成度として消費される危険です。だからこそステージド写真は、どれほど巧みに作られているかより、その巧みさが何を隠し何を露出するのかで読む必要があります。',
    ],
  },
  'フェミニズム写真': {
    '表現解説': [
      para('フェミニズム写真の厚みは、[[p:sherman|シャーマン]]や[[p:kruger|クルーガー]]だけでなく、マーサ・ロスラーのフォトテクスト、メアリー・ケリーやジョー・スペンスの家族と母性をめぐる実践、ローラ・マルヴィ以後の視線批判、ナン・ゴールディンの親密圏の記録が交差しているところにあります。広告、映画、家族写真、家事、身体、労働、セクシュアリティが、写真の中でどのように「自然なもの」として配列されてきたかを問い直すことが、この領域の中心でした。', ['feminism-rosler', 'feminism-kruger', 'feminism-goldin-hasselblad', 'feminism-sherman-whitney']),
    ],
    '批評と受容': [
      '現在では、白人中産階級の経験に偏っていたこと、ジェンダー二元論に依存しがちだったこと、クィアや有色人種やポストコロニアルな視点が十分に扱われなかったことも強く批判されています。フェミニズム写真は完成した成果というより、自らの前提を更新し続ける運動として読まれるべきでしょう。',
    ],
  },
  'シネマトグラフィック写真': {
    '表現解説': [
      'また、この傾向はジェフ・ウォールの光箱のように展示形式と切り離せません。暗い会場で発光する大画面は映画館を思わせつつ、時間の流れは一枚に凍結されている。ピクチャーズ世代の引用やステージド写真の演出と重なりながらも、シネマトグラフィック写真は「物語の前後を欠いたまま、どこまで時間を感じさせられるか」という点により強い関心を持っています。',
    ],
    '批評と受容': [
      'それでもこの傾向を一つの名前で捉える意味があるのは、決定的瞬間やステージド写真だけでは捉えにくい、静止画と映画的時間の関係を具体的に比較できるからです。重要なのは「映画のように見える」ことではなく、静止画がどのような前後関係や照明の人工性を引き受けているかを読むことです。',
    ],
  },
};

const MOVEMENT_FINISHING_JA = {
  'ピクトリアリズム': {
    '批評と受容': [
      '日本の芸術写真や戦前のサロン文化まで視野を広げると、ピクトリアリズムは国ごとに違う寿命を持っていたこともわかります。だからこの言葉を一律に「前時代的」と断じるより、どの地域でどの制度と結びついて持続したのかを見たほうが、写真史の実態に近づけます。',
    ],
  },
  '写真分離派': {
    '批評と受容': [
      'さらにクラレンス・ホワイトやスタイケンの周辺まで目を広げると、写真分離派はスティーグリッツ一人の歴史ではなく、学校、雑誌、画廊、印刷技術が結びついた共同体の歴史として見えてきます。その厚みがあるからこそ、後のモダニズムはこの回路を切断するのではなく、別の方向へ使い替えることができました。',
    ],
  },
  'ニューカラー': {
    '批評と受容': [
      'ニューカラーを理解するうえで外せないのは、エグルストン展への初期反発が「色彩」そのものより、取るに足らない郊外や家庭用品が美術館の主題になることへの違和感だった点です。つまり議論の核心は色の技術ではなく、何を重要な経験として写真に値するものとみなすか、という価値判断の更新にありました。',
    ],
  },
  'ダダ': {
    '批評と受容': [
      'ベルリン・ダダのフォトモンタージュが雑誌『AIZ』などの政治的印刷物へ接続していく流れを見ると、ダダの写真は美術館の壁より、複製と配布の回路の中で本来の強さを持っていたことがよくわかります。制度内に収まった現在でも、その複製性こそがダダの急進性の核でした。',
    ],
  },
  'リアリズム写真': {
    '批評と受容': [
      '土門の語法が長く強い規範として残ったのは、写真が敗戦後の倫理を背負わされたからでもあります。だからリアリズム写真を読むときは、作風の問題としてだけでなく、戦後日本で公共性と責任がどのような言葉で語られたのかという歴史の一部として捉える必要があります。',
    ],
  },
  'レイオグラフ': {
    '関連する表現': [
      'モホリ＝ナジのフォトグラムが視覚教育や新しいヴィジョンの理論と結びついていたのに対し、レイオグラフはダダやシュルレアリスムの文脈で、物の影と偶然の接触をより不穏なものとして扱いました。同じカメラレス写真でも、何を知覚させたいのかはかなり違います。',
    ],
  },
  'ヴォルテクシズム': {
    '批評と受容': [
      'ヴォルテクシズムを独立ページとして残すのは、歴史的規模の大きさよりも、ピクトリアリズムから抽象的モダニズムへ移る接点としての意味がはっきりしているからです。コバーンのヴォートグラフは例外的な試みですが、写真が対象の記録から離れて構成そのものを作りうると早い段階で示した点で、写真史上の橋渡しとして読む価値があります。',
    ],
  },
};

const ESSAY_MAIN_COUNT_JA = {
  'レイオグラフ': 4,
  'ヴォルテクシズム': 4,
  'カラー写真': 6,
  'プロヴォーク': 6,
  'タイポロジー写真': 6,
};

const META_DESC_OVERRIDES_JA = {
  'カラー写真': 'カラー写真は、手彩色、オートクローム、コダクローム、広告、美術館受容を通じて、色が写真の価値づけをどう変えたかをたどる表現史である。ニューカラー以前の技術、商業、家庭写真をめぐる制度的葛藤も扱う。',
  'デュッセルドルフ派': 'デュッセルドルフ派は、ベッヒャー夫妻の教育、タイポロジー、大判プリント、現代美術市場を通じて、戦後写真の制度を組み替えた潮流である。記録とコンセプト、展示スケールの交差を読む。',
  '新しいヴィジョン': '新しいヴィジョンは、俯瞰、仰角、クローズアップ、フォトグラムによって、1920年代の都市と身体に新しい知覚を与えようとした写真の実験である。バウハウス、構成主義、印刷文化との接続も扱う。',
  'ダダ': 'ダダは、第一次世界大戦後の反芸術の文脈で、フォトモンタージュや印刷物を使い、写真の証拠性と政治的イメージを分解した表現史である。',
  'シュルレアリスム': 'シュルレアリスム写真は、マン・レイ、リー・ミラー、アジェらを通じて、現実に密着する写真が夢、偶然、無意識をどう生み出したかを扱う。',
  'モダニズム': 'モダニズム写真は、都市化、工業化、印刷文化、バウハウスや新しいヴィジョンを通じて、写真を近代的な視覚言語へ組み替えた流れである。',
  'コンセプチュアルアート': 'コンセプチュアルアートにおける写真は、作品の記録、指示、言語、制度批評を担い、美しいプリントとは別の回路で美術を支えた。',
};

const normalizeJaTone = (value) => String(value || '')
  .replace(/見えてきます/g, '見えてくる')
  .replace(/特徴があります/g, '特徴をもつ')
  .replace(/媒体になりました/g, '媒体となった')
  .replace(/学校でした/g, '学校だった')
  .replace(/重要です/g, '重要である')
  .replace(/にに/g, 'に')
  .replace(/指します/g, '指す')
  .replace(/示します/g, '示す')
  .replace(/示しました/g, '示した')
  .replace(/生みます/g, '生む')
  .replace(/広げています/g, '広げている')
  .replace(/広げた写真家です/g, '広げた写真家である')
  .replace(/写します/g, '写す')
  .replace(/映します/g, '映す')
  .replace(/促します/g, '促す')
  .replace(/残します/g, '残す')
  .replace(/押し出します/g, '押し出す')
  .replace(/作り出します/g, '作り出す')
  .replace(/取ります/g, '取る')
  .replace(/作ります/g, '作る')
  .replace(/作りました/g, '作った')
  .replace(/作りあげます/g, '作りあげる')
  .replace(/つくりあげます/g, 'つくりあげる')
  .replace(/運びます/g, '運ぶ')
  .replace(/据えました/g, '据えた')
  .replace(/語ります/g, '語る')
  .replace(/近づけます/g, '近づける')
  .replace(/ありえます/g, 'ありえる')
  .replace(/押し上げました/g, '押し上げた')
  .replace(/押し広げました/g, '押し広げた')
  .replace(/行われました/g, '行われた')
  .replace(/向け始めます/g, '向け始める')
  .replace(/向かいました/g, '向かった')
  .replace(/読み直せます/g, '読み直せる')
  .replace(/置かれます/g, '置かれる')
  .replace(/与えます/g, '与える')
  .replace(/与えました/g, '与えた')
  .replace(/つくります/g, 'つくる')
  .replace(/選ばれました/g, '選ばれた')
  .replace(/見誤ります/g, '見誤る')
  .replace(/言えます/g, '言える')
  .replace(/扱いました/g, '扱った')
  .replace(/想像させます/g, '想像させる')
  .replace(/組み替えました/g, '組み替えた')
  .replace(/決めます/g, '決める')
  .replace(/決めました/g, '決めた')
  .replace(/自覚させました/g, '自覚させた')
  .replace(/意識させます/g, '意識させる')
  .replace(/引き受けます/g, '引き受ける')
  .replace(/働きます/g, '働く')
  .replace(/広がります/g, '広がる')
  .replace(/伴います/g, '伴う')
  .replace(/生じます/g, '生じる')
  .replace(/実験されます/g, '実験される')
  .replace(/共有しながら活動の輪郭をつくっていきます/g, '共有しながら活動の輪郭をつくっていく')
  .replace(/位置づけます/g, '位置づける')
  .replace(/しはじめます/g, 'しはじめる')
  .replace(/戻ります/g, '戻る')
  .replace(/生まれます/g, '生まれる')
  .replace(/残ります/g, '残る')
  .replace(/前に出ます/g, '前に出る')
  .replace(/読み込まされます/g, '読み込まされる')
  .replace(/求めます/g, '求める')
  .replace(/決まります/g, '決まる')
  .replace(/深まります/g, '深まる')
  .replace(/違います/g, '違う')
  .replace(/関わります/g, '関わる')
  .replace(/結びつきます/g, '結びつく')
  .replace(/つながります/g, 'つながる')
  .replace(/つながっています/g, 'つながっている')
  .replace(/広がりました/g, '広がった')
  .replace(/強まりました/g, '強まった')
  .replace(/いきました/g, 'いった')
  .replace(/いきます/g, 'いく')
  .replace(/残りました/g, '残った')
  .replace(/進みました/g, '進んだ')
  .replace(/変わりました/g, '変わった')
  .replace(/入り込みました/g, '入り込んだ')
  .replace(/揺らぎました/g, '揺らいだ')
  .replace(/置きました/g, '置いた')
  .replace(/広まりました/g, '広まった')
  .replace(/働きました/g, '働いた')
  .replace(/支えました/g, '支えた')
  .replace(/持ちました/g, '持った')
  .replace(/招きました/g, '招いた')
  .replace(/受け取っています/g, '受け取っている')
  .replace(/読まれています/g, '読まれている')
  .replace(/支えられています/g, '支えられている')
  .replace(/出ています/g, '出ている')
  .replace(/用いられてきました/g, '用いられてきた')
  .replace(/持っています/g, '持っている')
  .replace(/抱えます/g, '抱える')
  .replace(/失います/g, '失う')
  .replace(/立ち上がります/g, '立ち上がる')
  .replace(/戻ってしまいます/g, '戻ってしまう')
  .replace(/さかのぼれます/g, 'さかのぼれる')
  .replace(/離れます/g, '離れる')
  .replace(/要ります/g, '要る')
  .replace(/分かれます/g, '分かれる')
  .replace(/知られます/g, '知られる')
  .replace(/得ます/g, '得る')
  .replace(/疑います/g, '疑う')
  .replace(/暴かれます/g, '暴かれる')
  .replace(/加わります/g, '加わる')
  .replace(/加わりました/g, '加わった')
  .replace(/現れます/g, '現れる')
  .replace(/決定します/g, '決定する')
  .replace(/揺れます/g, '揺れる')
  .replace(/認めます/g, '認める')
  .replace(/済みます/g, '済む')
  .replace(/かかります/g, 'かかる')
  .replace(/増幅します/g, '増幅する')
  .replace(/重視されます/g, '重視される')
  .replace(/指摘されます/g, '指摘される')
  .replace(/回収されやすいことが挙げられます/g, '回収されやすいことが挙げられる')
  .replace(/転化しやすいことが挙げられます/g, '転化しやすいことが挙げられる')
  .replace(/欠かせなくなっています/g, '欠かせなくなっている')
  .replace(/かかっています/g, 'かかっている')
  .replace(/になっています/g, 'になっている')
  .replace(/ています/g, 'ている')
  .replace(/でいます/g, 'でいる')
  .replace(/ていきます/g, 'ていく')
  .replace(/っていきます/g, 'っていく')
  .replace(/てきます/g, 'てくる')
  .replace(/てしまいます/g, 'てしまう')
  .replace(/でしまいます/g, 'でしまう')
  .replace(/てしまいました/g, 'てしまった')
  .replace(/でしまいました/g, 'でしまった')
  .replace(/始まっています/g, '始まっている')
  .replace(/続いています/g, '続いている')
  .replace(/成り立っています/g, '成り立っている')
  .replace(/生き残ります/g, '生き残る')
  .replace(/前面に出ます/g, '前面に出る')
  .replace(/先に来ます/g, '先に来る')
  .replace(/影響します/g, '影響する')
  .replace(/実験されます/g, '実験される')
  .replace(/共有されます/g, '共有される')
  .replace(/再編されます/g, '再編される')
  .replace(/読まれます/g, '読まれる')
  .replace(/問われます/g, '問われる')
  .replace(/語られます/g, '語られる')
  .replace(/配置されます/g, '配置される')
  .replace(/形成されます/g, '形成される')
  .replace(/示されます/g, '示される')
  .replace(/流通します/g, '流通する')
  .replace(/機能します/g, '機能する')
  .replace(/露出します/g, '露出する')
  .replace(/します/g, 'する')
  .replace(/しました/g, 'した')
  .replace(/されます/g, 'される')
  .replace(/られます/g, 'られる')
  .replace(/されました/g, 'された')
  .replace(/られました/g, 'られた')
  .replace(/れました/g, 'れた')
  .replace(/れます/g, 'れる')
  .replace(/だと言えます/g, 'だと言える')
  .replace(/と言えます/g, 'と言える')
  .replace(/再生産していました/g, '再生産していた')
  .replace(/意識します/g, '意識する')
  .replace(/しています/g, 'している')
  .replace(/していました/g, 'していた')
  .replace(/されています/g, 'されている')
  .replace(/していました/g, 'していた')
  .replace(/していません/g, 'していない')
  .replace(/しています/g, 'している')
  .replace(/してきました/g, 'してきた')
  .replace(/されてきました/g, 'されてきた')
  .replace(/きました/g, 'きた')
  .replace(/されました/g, 'された')
  .replace(/になりました/g, 'になった')
  .replace(/なりました/g, 'なった')
  .replace(/となりました/g, 'となった')
  .replace(/できました/g, 'できた')
  .replace(/ありました/g, 'あった')
  .replace(/いました/g, 'いた')
  .replace(/ではありませんでした/g, 'ではなかった')
  .replace(/ではありません/g, 'ではない')
  .replace(/ありません/g, 'ない')
  .replace(/あります/g, 'ある')
  .replace(/なります/g, 'なる')
  .replace(/できます/g, 'できる')
  .replace(/読めます/g, '読める')
  .replace(/見えます/g, '見える')
  .replace(/持ちます/g, '持つ')
  .replace(/変わります/g, '変わる')
  .replace(/つきまといます/g, 'つきまとう')
  .replace(/招きます/g, '招く')
  .replace(/分かります/g, 'わかる')
  .replace(/わかります/g, 'わかる')
  .replace(/読めません/g, '読めない')
  .replace(/欠かせません/g, '欠かせない')
  .replace(/なりません/g, 'ならない')
  .replace(/ません/g, 'ない')
  .replace(/でした/g, 'だった')
  .replace(/でしょう/g, 'だろう')
  .replace(/です/g, 'である')
  .replace(/ではないだった/g, 'ではなかった')
  .replace(/いないだった/g, 'いなかった')
  .replace(/終わりないだった/g, '終わらなかった')
  .replace(/限りない/g, '限らない')
  .replace(/とどまりない/g, 'とどまらない')
  .replace(/つきまといた/g, 'つきまとった')
  .replace(/暗示す/g, '暗示する');

const normalizeParagraphTone = (paragraph) => {
  if (typeof paragraph === 'string') return normalizeJaTone(paragraph);
  if (paragraph && typeof paragraph === 'object' && typeof paragraph.text === 'string') {
    return { ...paragraph, text: normalizeJaTone(paragraph.text) };
  }
  return paragraph;
};

const SIGNIFICANCE_OPENERS_JA = {
  'ピクトリアリズム': 'この運動が残したのは、',
  '写真分離派': '写真分離派の転換点は、',
  'ストレート写真': 'この流れで置き換えられたのは、',
  '自然主義写真': 'エマーソンの議論が早くから開いたのは、',
  'モダニズム': 'モダニズム写真が押し出したのは、',
  '新即物主義': '新即物主義が写真にもたらしたのは、',
  '新しいヴィジョン': 'この実験が強く示したのは、',
  'バウハウス': 'バウハウスで変わったのは、',
  'ヴォルテクシズム': '写真史上で何を変えたかといえば、',
  'ダダ': 'ダダの写真が露わにしたのは、',
  'シュルレアリスム': 'シュルレアリスム写真の重要な逆説は、',
  'レイオグラフ': 'レイオグラフが突きつけたのは、',
  'ドキュメンタリー': 'ドキュメンタリーが開いたのは、',
  'FSA写真': 'FSA写真で明らかになったのは、',
  '決定的瞬間': 'この概念が更新したのは、',
  'ストリート写真': 'ストリート写真が押し広げたのは、',
  'リアリズム写真': '戦後日本でこの言葉が動かしたのは、',
  'プロヴォーク': 'プロヴォークが持ち込んだのは、',
  '私写真': '私写真が可視化したのは、',
  'ニューカラー': 'ニューカラーが変えたのは、',
  'カラー写真': 'カラー写真をめぐる争点は、',
  '大判カラー写真': '大判カラー写真で再定義されたのは、',
  'デュッセルドルフ派': 'デュッセルドルフ派が結び直したのは、',
  'タイポロジー写真': 'タイポロジー写真が離れたのは、',
  'コンセプチュアルアート': 'コンセプチュアルアートが反転させたのは、',
  'ピクチャーズ世代': 'ピクチャーズ世代が軸足を移したのは、',
  'ステージド写真': 'ステージド写真が露わにしたのは、',
  'フェミニズム写真': 'フェミニズム写真が動かしたのは、',
  'シネマトグラフィック写真': 'シネマトグラフィック写真が示したのは、',
};

const deTemplateSignificance = (movement, paragraph) => {
  const opener = SIGNIFICANCE_OPENERS_JA[movement] || 'この表現で重要なのは、';
  const replaceText = (text) => String(text || '').replace(/^写真史上の意義は、/, opener);
  if (typeof paragraph === 'string') return replaceText(paragraph);
  if (paragraph && typeof paragraph === 'object' && typeof paragraph.text === 'string') {
    return { ...paragraph, text: replaceText(paragraph.text) };
  }
  return paragraph;
};

Object.entries(MOVEMENT_PAGE_CONTENT).forEach(([movement, entry]) => {
  entry.appendSupportSections = false;
  if (LEAD_OVERRIDES_JA[movement]) {
    entry.leadJa = LEAD_OVERRIDES_JA[movement];
  }
  if (META_DESC_OVERRIDES_JA[movement]) {
    entry.metaDescJa = META_DESC_OVERRIDES_JA[movement];
  }
  entry.leadJa = normalizeJaTone(entry.leadJa || '');
  const paragraphs = flattenMovementParagraphs(entry.sectionsJa || []);
  const mainCount = ESSAY_MAIN_COUNT_JA[movement]
    || (paragraphs.length >= 10 ? 6 : paragraphs.length >= 8 ? 5 : Math.max(3, Math.ceil(paragraphs.length * 0.6)));
  entry.sectionsJa = essaySectionsJa(
    paragraphs.slice(0, mainCount).map(normalizeParagraphTone).map((paragraph) => deTemplateSignificance(movement, paragraph)),
    paragraphs.slice(mainCount).map(normalizeParagraphTone).map((paragraph) => deTemplateSignificance(movement, paragraph)),
    RELATED_MOVEMENT_TEXT_JA[movement] ? [normalizeJaTone(RELATED_MOVEMENT_TEXT_JA[movement])] : []
  );
  entry.sources = mergeSources(
    entry.sources || [],
    MOVEMENT_SOURCE_ADDITIONS[movement] || [],
    MOVEMENT_SOURCE_ADDITIONS_ROUND2[movement] || []
  );
  const extras = MOVEMENT_EXTRA_PARAGRAPHS_JA[movement] || {};
  Object.entries(extras).forEach(([heading, extraParagraphs]) => {
    appendSectionParagraphs(entry, heading, extraParagraphs.map(normalizeParagraphTone));
  });
  const deepening = MOVEMENT_DEEPENING_JA[movement] || {};
  Object.entries(deepening).forEach(([heading, extraParagraphs]) => {
    appendSectionParagraphs(entry, heading, extraParagraphs.map(normalizeParagraphTone));
  });
  const finishing = MOVEMENT_FINISHING_JA[movement] || {};
  Object.entries(finishing).forEach(([heading, extraParagraphs]) => {
    appendSectionParagraphs(entry, heading, extraParagraphs.map(normalizeParagraphTone));
  });
});

if (typeof window !== 'undefined') {
  window.MOVEMENT_PAGE_CONTENT = MOVEMENT_PAGE_CONTENT;
}

if (typeof module !== 'undefined') {
  module.exports = { MOVEMENT_PAGE_CONTENT };
}
