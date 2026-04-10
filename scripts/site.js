/* UI behavior for the photography history site. */

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   STATE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
let activeFilters = { search: '', country: '', movement: '' };
const EMPTY_BLOCK = '<div class="empty-copy" aria-hidden="true"></div>';
const languageApi = window.PhotoCoordinatesI18n;
let currentLanguage = languageApi ? languageApi.getLanguage() : 'ja';
const AFFILIATE_BOOKS = window.PHOTOGRAPHER_AFFILIATE_BOOKS || {};
const PHOTOGRAPHER_ENRICHMENTS_DATA = window.PHOTOGRAPHER_ENRICHMENTS || {};
const PHOTOGRAPHER_ESSAY_OVERRIDES = window.PHOTOGRAPHER_ESSAY_OVERRIDES || {};
const PHOTOGRAPHER_LINK_ALIAS_MAP = window.PHOTOGRAPHER_LINK_ALIASES
  || (typeof PHOTOGRAPHER_LINK_ALIASES !== 'undefined' ? PHOTOGRAPHER_LINK_ALIASES : {});
const NON_PHOTOGRAPHER_IDS = new Set([
  'anri-sala',
  'ana-torfs',
  'charles-wirgman',
  'claude-closky',
  'collectif-fact',
  'eve-sussman',
  'fabian-marti',
  'g-r-a-m',
  'gabriel-orozco',
  'multiplicity',
  'ohio',
  'the-atlas-group-walid-raad',
  'useful-photography',
  'wangechi-mutu'
]);

const UI_TEXT = {
  ja: {
    homeTitle: '写真の座標',
    homeBack: '写真の座標へ戻る',
    wip: '随時更新中',
    archiveHeaderLabel: 'Photo Coordinates / Archive',
    archiveSubtitle: '年代順にたどる写真史',
    archiveLead: '1839年から現代までの写真史を、各時代の写真家、表現、世界情勢、技術、時代背景の関係とともにたどります。',
    archiveDisclaimer: '※ 本サイトの情報はAIがウェブ上の公開資料をもとに収集・整理したものです。出典を明記していますが、曖昧さや誤りが含まれる可能性があります。気になった作家・表現・時代については、ぜひご自身でも確認してください。',
    randomLabel: '今日のランダム写真家',
    randomHint: '→ クリックして詳細を見る',
    coordinateButton: '座標で見る',
    coordinateDetail: '解説',
    eraTab: '年代順にみる',
    movementTab: '表現から見る',
    filterLabel: '絞り込み',
    filterSearchPlaceholder: '写真家名で検索',
    allCountries: 'すべての国',
    allMovements: 'すべてのムーブメント',
    reset: 'リセット',
    noResults: '条件に一致する写真家が見つかりません',
    emptyEra: 'この時代の写真家はこれから追加予定です。',
    worldEvents: '世界情勢',
    photoContext: '写真と時代',
    photographersInEra: 'この時代の写真家',
    movementOverview: '概要',
    movementPhotographers: 'この表現の写真家',
    relatedReading: 'つながりから読む',
    relatedPhotographers: '関連する写真家・人物',
    relatedMovement: '関連運動',
    readNext: '次に読むべきページ',
    notSet: '準備中',
    registeredCount: count => `登録: ${count}名`,
    explanation: '解説',
    externalLinks: '外部リンク',
    books: '写真集',
    sources: '出典',
    amazon: '写真集を Amazon で見る ↗',
    amazonPending: '写真集へのリンク（準備中）',
    sourcePrefix: '出典：',
    photographerPlaceholder: '追加予定',
    totalCount: total => `${total}人`,
    filteredCount: (visible, total) => `${visible} / ${total}人`
  },
  en: {
    homeTitle: 'Photo Coordinates',
    homeBack: 'Back to Photo Coordinates',
    wip: 'Updating',
    archiveHeaderLabel: 'Photo Coordinates / Archive',
    archiveSubtitle: 'History of Photography by Era',
    archiveLead: 'Browse the history of photography from 1839 to the present through photographers, artistic movements, world events, technology, and visual culture.',
    archiveDisclaimer: 'This site gathers and organizes information from publicly available web sources with AI assistance. Sources are listed, but ambiguity, errors, or outdated details may remain. Please verify topics that matter to you.',
    randomLabel: 'Photographer of the Day',
    randomHint: '→ Click to open the detail panel',
    coordinateButton: 'View in Coordinates',
    coordinateDetail: 'Notes',
    eraTab: 'Browse by Era',
    movementTab: 'Browse by Movement',
    filterLabel: 'Filters',
    filterSearchPlaceholder: 'Search photographers',
    allCountries: 'All countries',
    allMovements: 'All movements',
    reset: 'Reset',
    noResults: 'No photographers match the current filters.',
    emptyEra: 'Photographers for this era will be added soon.',
    worldEvents: 'World Events',
    photoContext: 'Photography and the Era',
    photographersInEra: 'Photographers in this era',
    movementOverview: 'Overview',
    movementPhotographers: 'Photographers in this movement',
    relatedReading: 'Connections',
    relatedPhotographers: 'Related photographers & figures',
    relatedMovement: 'Related movements',
    readNext: 'Read next',
    notSet: 'Coming soon',
    registeredCount: count => `${count} registered`,
    explanation: 'Essay',
    externalLinks: 'External Links',
    books: 'Photobooks',
    sources: 'Sources',
    amazon: 'View on Amazon ↗',
    amazonPending: 'Book link coming soon',
    sourcePrefix: 'Sources:',
    photographerPlaceholder: 'Coming soon',
    totalCount: total => `${total}`,
    filteredCount: (visible, total) => `${visible} / ${total}`
  }
};

const COUNTRY_TEXT = {
  FR: { ja: 'FR', en: 'France' },
  GB: { ja: 'GB', en: 'United Kingdom' },
  US: { ja: 'US', en: 'United States' },
  'IT / GB': { ja: 'IT / GB', en: 'Italy / United Kingdom' },
  'GB / US': { ja: 'GB / US', en: 'United Kingdom / United States' },
  'DK / US': { ja: 'DK / US', en: 'Denmark / United States' },
  DE: { ja: 'DE', en: 'Germany' },
  JP: { ja: 'JP', en: 'Japan' },
  BR: { ja: 'BR', en: 'Brazil' },
  CA: { ja: 'CA', en: 'Canada' }
};

const COUNTRY_ROUTE_META = {
  FR: { ja: 'フランス', en: 'France', slug: 'france' },
  GB: { ja: 'イギリス', en: 'United Kingdom', slug: 'united-kingdom' },
  US: { ja: 'アメリカ', en: 'United States', slug: 'united-states' },
  'IT / GB': { ja: 'イタリア / イギリス', en: 'Italy / United Kingdom', slug: 'italy-united-kingdom' },
  'GB / US': { ja: 'イギリス / アメリカ', en: 'United Kingdom / United States', slug: 'united-kingdom-united-states' },
  'DK / US': { ja: 'デンマーク / アメリカ', en: 'Denmark / United States', slug: 'denmark-united-states' },
  DE: { ja: 'ドイツ', en: 'Germany', slug: 'germany' },
  JP: { ja: '日本', en: 'Japan', slug: 'japan' },
  BR: { ja: 'ブラジル', en: 'Brazil', slug: 'brazil' },
  CA: { ja: 'カナダ', en: 'Canada', slug: 'canada' }
};

const MOVEMENT_NAME_OVERRIDES_EN = {
  'カロタイプ': 'Calotype',
  '肖像写真': 'Portrait Photography',
  'ヘリオグラフィー': 'Heliography',
  '建築写真': 'Architectural Photography',
  '写真石版': 'Photolithography',
  '明治ドキュメンタリー': 'Meiji Documentary'
};

const GENDER_TEXT = {
  男性: { ja: '男性', en: 'Male' },
  女性: { ja: '女性', en: 'Female' }
};

const VISIBLE_PHOTOGRAPHERS = PHOTOGRAPHERS.filter(photographer => !photographer.isPlaceholder && !NON_PHOTOGRAPHER_IDS.has(photographer.id));
const PHOTOGRAPHER_ORDER = new Map(VISIBLE_PHOTOGRAPHERS.map((photographer, index) => [photographer.id, index]));
const ERA_ORDER = new Map((typeof ERAS !== 'undefined' ? ERAS : []).map((era, index) => [era.id, index]));
const ALNUM_BOUNDARY_RE = /[A-Za-z0-9]/;
const PHOTOGRAPHER_LOOKUP = new Map(VISIBLE_PHOTOGRAPHERS.map(photographer => [photographer.id, photographer]));
const PHOTOGRAPHER_ALIAS_TARGETS = buildPhotographerAliasTargets();
const PHOTOGRAPHER_ALIAS_LOOKUP = new Map(PHOTOGRAPHER_ALIAS_TARGETS.map(target => [target.alias, target.photographer]));
const PHOTOGRAPHER_ALIAS_REGEX = PHOTOGRAPHER_ALIAS_TARGETS.length
  ? new RegExp(PHOTOGRAPHER_ALIAS_TARGETS.map(target => escapeRegExp(target.alias)).join('|'), 'g')
  : null;

function t(key, ...args) {
  const value = UI_TEXT[currentLanguage][key] ?? UI_TEXT.ja[key];
  return typeof value === 'function' ? value(...args) : value;
}

function localizeValue(valueJa, valueEn) {
  return currentLanguage === 'en'
    ? (valueEn || valueJa || '')
    : (valueJa || valueEn || '');
}

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function escapeRegExp(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function getPhotographerEnrichment(photographer) {
  const id = typeof photographer === 'string' ? photographer : photographer?.id;
  return PHOTOGRAPHER_ENRICHMENTS_DATA[id] || {};
}

function getPhotographerEssayOverride(photographer) {
  const id = typeof photographer === 'string' ? photographer : photographer?.id;
  return PHOTOGRAPHER_ESSAY_OVERRIDES[id] || null;
}

function localizedEssaySections(override) {
  if (!override?.sections) return [];
  if (!override) return [];
  return (override.sections || []).map(section => ({
    heading: localizeValue(section.headingJa, section.headingEn),
    paragraphs: currentLanguage === 'en'
      ? (section.paragraphsEn || section.paragraphsJa || [])
      : (section.paragraphsJa || section.paragraphsEn || [])
  }));
}

function flattenEssaySections(sections) {
  return (sections || [])
    .flatMap(section => [section.heading, ...(section.paragraphs || [])].filter(Boolean))
    .join('\n\n')
    .trim();
}

function getPhotographerLeadCopy(photographer) {
  const override = getPhotographerEssayOverride(photographer);
  if (override) {
    return localizeValue(override.leadJa, override.leadEn) || buildPhotographerIntro(photographer);
  }
  return buildPhotographerIntro(photographer);
}

function getPhotographerEssayPayload(photographer) {
  const override = getPhotographerEssayOverride(photographer);
  if (override) {
    const text = localizeValue(override.textJa, override.textEn);
    const sections = text ? [] : localizedEssaySections(override);
    return {
      text: text || flattenEssaySections(sections),
      citations: override.citations || [],
      links: override.links || []
    };
  }

  const expText = photographer.expression ? localizeValue(photographer.expression.text, photographer.expression.textEn) : '';
  const ctxText = photographer.context ? localizeValue(photographer.context.text, photographer.context.textEn) : '';
  const citations = photographer.context?.citations || null;
  const links = photographer.links || [];
  return {
    text: citations ? ctxText : [expText, ctxText].filter(Boolean).join(' '),
    citations,
    links
  };
}

function enrichmentValue(photographer, baseKey) {
  const enrichment = getPhotographerEnrichment(photographer);
  const primaryKey = `${baseKey}${currentLanguage === 'en' ? 'En' : 'Ja'}`;
  const fallbackKey = `${baseKey}${currentLanguage === 'en' ? 'Ja' : 'En'}`;
  return enrichment[primaryKey] || enrichment[fallbackKey] || '';
}

function expandedMovementNames(photographer, limit = 5) {
  const names = [];
  const seen = new Set();
  const enrichment = getPhotographerEnrichment(photographer);
  const values = [...(photographer.movements || []), ...(enrichment.extraMovements || [])];
  values.forEach(movement => {
    if (!movement || seen.has(movement)) return;
    seen.add(movement);
    names.push(displayMovementName(movement));
  });
  return names.slice(0, limit);
}

function descriptorFor(photographer) {
  return enrichmentValue(photographer, 'descriptor')
    || expandedMovementNames(photographer, 1)[0]
    || displayEraTitle(ERAS.find(era => era.id === photographer.era) || {})
    || '';
}

function normalizePlainText(value) {
  return String(value || '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\*\d+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function essayContainsName(text, names = []) {
  const plain = normalizePlainText(text);
  return names.some(name => name && plain.includes(name));
}

function buildPhotographerAliasTargets() {
  const aliasMap = new Map();
  const remember = (alias, photographer) => {
    if (!alias || !photographer || photographer.isPlaceholder || NON_PHOTOGRAPHER_IDS.has(photographer.id)) return;
    if (!aliasMap.has(alias)) aliasMap.set(alias, photographer);
  };

  VISIBLE_PHOTOGRAPHERS.forEach(photographer => {
    remember(photographer.nameJa, photographer);
    remember(photographer.name, photographer);
  });

  Object.entries(PHOTOGRAPHER_LINK_ALIAS_MAP).forEach(([alias, photographerId]) => {
    const photographer = PHOTOGRAPHER_LOOKUP.get(photographerId);
    remember(alias, photographer);
  });

  return [...aliasMap.entries()]
    .sort((left, right) => right[0].length - left[0].length)
    .map(([alias, photographer]) => ({ alias, photographer }));
}

function shouldSkipAliasBoundary(source, start, end, alias) {
  if (!alias || !ALNUM_BOUNDARY_RE.test(alias)) return false;
  return ALNUM_BOUNDARY_RE.test(source[start - 1] || '') || ALNUM_BOUNDARY_RE.test(source[end] || '');
}

function resolveAffiliateValue(record, jaKey, enKey, fallbackKey) {
  if (!record || typeof record !== 'object') return '';
  return currentLanguage === 'en'
    ? (record[enKey] || record[jaKey] || record[fallbackKey] || '')
    : (record[jaKey] || record[enKey] || record[fallbackKey] || '');
}

function getAffiliateEntry(photographerId) {
  return AFFILIATE_BOOKS[photographerId] || null;
}

function getArchiveAffiliateBooks(photographer) {
  const entry = getAffiliateEntry(photographer.id);
  if (!entry) {
    if (!photographer.amazon) return [];
    return [{
      title: t('books'),
      note: '',
      url: photographer.amazon
    }];
  }

  const books = Array.isArray(entry.books) ? entry.books : [];
  const normalized = books
    .map(book => ({
      title: resolveAffiliateValue(book, 'titleJa', 'titleEn', 'title'),
      note: resolveAffiliateValue(book, 'noteJa', 'noteEn', 'note'),
      url: resolveAffiliateValue(book, 'urlJa', 'urlEn', 'url')
    }))
    .filter(book => book.title && book.url);

  if (normalized.length) return normalized.slice(0, 3);

  const featured = currentLanguage === 'en'
    ? (entry.featured?.en || entry.featured?.ja || entry.featured || null)
    : (entry.featured?.ja || entry.featured?.en || entry.featured || null);
  if (featured?.url) {
    return [{
      title: featured.label || t('books'),
      note: '',
      url: featured.url
    }];
  }

  if (!photographer.amazon) return [];
  return [{
    title: t('books'),
    note: '',
    url: photographer.amazon
  }];
}

function renderArchiveAffiliateSection(photographer) {
  const books = getArchiveAffiliateBooks(photographer);
  if (!books.length) {
    return `
      <div class="detail-section detail-books-section">
        <div class="detail-section-title">${t('books')}</div>
        <div class="amazon-placeholder">${t('amazonPending')}</div>
      </div>`;
  }

  const cards = books.map(book => {
    const ctaLabel = currentLanguage === 'en' ? 'View on Amazon ↗' : '写真集を Amazon で見る ↗';
    return `
      <div class="detail-book-card">
        <div class="detail-book-title">${book.title}</div>
        ${book.note ? `<div class="detail-book-note">${book.note}</div>` : ''}
        <div class="detail-book-actions">
          <a class="detail-link detail-link-amazon" href="${book.url}" target="_blank" rel="noopener sponsored">${ctaLabel}</a>
        </div>
      </div>`;
  }).join('');

  return `
      <div class="detail-section detail-books-section">
        <div class="detail-section-title">${t('books')}</div>
        <div class="detail-books-grid">${cards}</div>
      </div>`;
}

function realPhotographers() {
  return VISIBLE_PHOTOGRAPHERS;
}

function archiveBasePath(lang = currentLanguage) {
  return lang === 'en' ? '/en/archive.html' : '/archive.html';
}

function coordinateBasePath(lang = currentLanguage) {
  return lang === 'en' ? '/en/index.html' : '/index.html';
}

function photographerPagePath(photographer, lang = currentLanguage) {
  const id = typeof photographer === 'string' ? photographer : photographer.id;
  const base = lang === 'en' ? '/en/photographers/' : '/photographers/';
  return `${base}${id}.html`;
}

function renderLinkedText(text, options = {}) {
  const source = String(text || '');
  if (!source) return '';
  if (!PHOTOGRAPHER_ALIAS_REGEX) return escapeHtml(source).replace(/\n/g, '<br>');

  const excludeId = options.excludeId || '';
  const linkedIds = options.linkedIds || new Set();
  let html = '';
  let cursor = 0;
  PHOTOGRAPHER_ALIAS_REGEX.lastIndex = 0;

  for (const match of source.matchAll(PHOTOGRAPHER_ALIAS_REGEX)) {
    const alias = match[0];
    const start = match.index ?? 0;
    const end = start + alias.length;
    const photographer = PHOTOGRAPHER_ALIAS_LOOKUP.get(alias);
    if (
      !photographer
      || photographer.id === excludeId
      || linkedIds.has(photographer.id)
      || shouldSkipAliasBoundary(source, start, end, alias)
    ) {
      continue;
    }

    html += escapeHtml(source.slice(cursor, start));
    html += `<a class="inline-photographer-link" href="${photographerPagePath(photographer)}">${escapeHtml(alias)}</a>`;
    cursor = end;
    linkedIds.add(photographer.id);
  }

  html += escapeHtml(source.slice(cursor));
  return html.replace(/\n/g, '<br>');
}

function renderOptionalText(text) {
  return text && text.trim() ? renderLinkedText(text) : EMPTY_BLOCK;
}

function renderSources(sources) {
  if (!sources || !sources.length) return '';
  const links = sources.map(s =>
    `<a href="${s.url}" target="_blank" rel="noopener">${s.text}</a>`
  ).join(' / ');
  return `<div class="context-source">${t('sourcePrefix')}${links}</div>`;
}

function renderEmptyPhotographerState() {
  return `<div class="empty-photographers">${t('emptyEra')}</div>`;
}

function displayName(p) {
  if (currentLanguage === 'en') return p.name || p.nameJa || t('photographerPlaceholder');
  return p.nameJa || p.name || t('photographerPlaceholder');
}

function displaySubName(p) {
  if (currentLanguage === 'en') return '';
  if (!p.nameJa || !p.name) return '';
  return `<div class="card-name-sub">${currentLanguage === 'en' ? p.nameJa : p.name}</div>`;
}

function displayYears(p) {
  const raw = String(p.years || '').trim();
  if (!raw) return '';
  if (currentLanguage === 'en') {
    let value = raw;
    if (value.includes(' / ')) value = value.split(' / ', 1)[0].trim();
    value = value.replace('明治期', 'Meiji period');
    value = value.replace(/年代/g, 's');
    return value.replace(/-/g, '–');
  }
  return raw;
}

function displayMeta(p) {
  const country = COUNTRY_TEXT[p.nationality];
  const label = country ? country[currentLanguage] : p.nationality;
  return [p.flag, label].filter(Boolean).join(' ').trim();
}

function displayGender(value) {
  if (!value) return '';
  const text = GENDER_TEXT[value];
  return text ? text[currentLanguage] : value;
}

function displayMovementName(movementName) {
  if (currentLanguage === 'en') {
    return MOVEMENTS_META[movementName]?.en || MOVEMENT_NAME_OVERRIDES_EN[movementName] || movementName;
  }
  return movementName;
}

function displayEraTitle(era) {
  return currentLanguage === 'en' ? era.titleEn || era.title : era.title;
}

function buildPhotographerKeywordLine(photographer) {
  const name = displayName(photographer);
  const descriptor = descriptorFor(photographer);
  return currentLanguage === 'en'
    ? `${name} | History of Photography | ${descriptor || 'Photo Coordinates'} | Photo Coordinates |`
    : `${name}｜写真史｜${descriptor || '写真の座標'}｜写真の座標｜`;
}

function buildPhotographerIntro(photographer) {
  const namePrimary = displayName(photographer);
  const altName = currentLanguage === 'en' ? '' : (photographer.name || '');
  const identity = altName ? (currentLanguage === 'en' ? `${namePrimary} (${altName})` : `${namePrimary}（${altName}）`) : namePrimary;
  const period = (ERAS.find(era => era.id === photographer.era)?.period) || photographer.years || '';
  const movementNames = expandedMovementNames(photographer, 5);
  const movementPhrase = joinList(movementNames.slice(0, 2), currentLanguage);
  const country = displayMeta(photographer);
  const descriptor = descriptorFor(photographer);
  const keywords = enrichmentValue(photographer, 'keywords');
  const representativeWork = enrichmentValue(photographer, 'representativeWork');
  const rawEssay = [
    photographer.expression ? localizeValue(photographer.expression.text, photographer.expression.textEn) : '',
    photographer.context ? localizeValue(photographer.context.text, photographer.context.textEn) : ''
  ].filter(Boolean).join(' ');
  const isPlaceholder = ['準備中。', 'Coming soon.'].includes(normalizePlainText(rawEssay));

  const focusPhrase = (() => {
    if (currentLanguage === 'en') {
      if (keywords && representativeWork) return `${keywords}, and the representative work ${representativeWork}`;
      if (keywords) return keywords;
      if (representativeWork) return `the representative work ${representativeWork}`;
      if (movementPhrase) return movementPhrase;
      return 'key works and related movements';
    }
    if (keywords && representativeWork) return `${keywords}、代表作の${representativeWork}`;
    if (keywords) return keywords;
    if (representativeWork) return `代表作の${representativeWork}`;
    if (movementPhrase) return movementPhrase;
    return '関連作家や主要な作品';
  })();

  if (currentLanguage === 'en') {
    let base = '';
    if (isPlaceholder) {
      base = movementPhrase
        ? `${identity} is part of Photo Coordinates, a site about the history of photography. This page will be expanded around ${movementPhrase} and the wider context of ${period}.`
        : `${identity} is part of Photo Coordinates, a site about the history of photography. This page will be expanded with historical context, related photographers and figures, and sources.`;
    } else if (movementPhrase) {
      base = `${identity} is a key figure for understanding the history of photography through ${movementPhrase}. This page follows the photographer's place in ${descriptor || 'photography history'} through ${focusPhrase}, related photographers, figures, movements, and sources.`;
    } else {
      base = `${identity} appears here as part of Photo Coordinates, a site about the history of photography. This page follows the photographer through ${focusPhrase}, related figures, and sources.`;
    }
    return base.trim();
  }

  let base = '';
  if (isPlaceholder) {
    base = movementPhrase
      ? `${identity}を写真史の流れの中で読むための準備ページです。${movementPhrase}や${period}の文脈とあわせて、関連作家・人物・出典を順次追加していきます。`
      : `${identity}を写真史の中で位置づけるための準備ページです。写真の座標では、関連作家・人物・時代背景・出典を今後順次整えていきます。`;
  } else if (movementPhrase) {
    base = `${identity}は、${movementPhrase}を考えるうえで欠かせない写真家です。このページでは、${focusPhrase}を手がかりに、${descriptor || country}の文脈も含めて、写真史の流れの中での位置づけをたどります。`;
  } else {
    base = `${identity}を写真史の流れの中で読み解くためのページです。このページでは、${focusPhrase}を手がかりに、関連作家・人物や出典とともにその位置づけをたどります。`;
  }
  return base.trim();
}

function displayBlockText(block) {
  return currentLanguage === 'en'
    ? (block.textEn || block.text || '')
    : (block.text || block.textEn || '');
}

function joinList(items, lang = currentLanguage) {
  const values = (items || []).filter(Boolean);
  if (!values.length) return '';
  if (values.length === 1) return values[0];
  if (values.length === 2) return lang === 'en' ? `${values[0]} and ${values[1]}` : `${values[0]}と${values[1]}`;
  return lang === 'en'
    ? `${values.slice(0, -1).join(', ')}, and ${values[values.length - 1]}`
    : `${values.slice(0, -1).join('、')}、${values[values.length - 1]}`;
}

function movementSlug(value) {
  return String(value || '').replace(/[^a-zA-Z\u3000-\u9fff]/g, '');
}

function photographerSortValue(photographer) {
  return [
    ERA_ORDER.get(photographer.era) ?? 999,
    PHOTOGRAPHER_ORDER.get(photographer.id) ?? 9999
  ];
}

function comparePhotographersChronologically(a, b) {
  const [eraA, orderA] = photographerSortValue(a);
  const [eraB, orderB] = photographerSortValue(b);
  if (eraA !== eraB) return eraA - eraB;
  return orderA - orderB;
}

function sharedMovements(a, b) {
  const bMovements = new Set(b.movements || []);
  return (a.movements || []).filter(movement => bMovements.has(movement));
}

function normalizeSearch(value) {
  return (value || '').toLowerCase().trim();
}

function hasActiveFilters() {
  return Boolean(activeFilters.search || activeFilters.country || activeFilters.movement);
}

function buildSearchIndex(p) {
  return normalizeSearch([
    p.name,
    p.nameJa,
    p.nationality,
    p.years,
    ...(p.movements || []),
    ...(p.movements || []).map(m => MOVEMENTS_META[m]?.en || ''),
  ].filter(Boolean).join(' '));
}

function setLocationHash(hashValue) {
  const next = hashValue ? `#${hashValue}` : '';
  if (window.location.hash === next) return;
  const url = new URL(window.location.href);
  url.hash = hashValue || '';
  history.replaceState(null, '', url.toString());
}

function updateLanguageButtons() {
  document.querySelectorAll('.lang-btn').forEach(button => {
    button.classList.toggle('active', button.dataset.lang === currentLanguage);
  });
}

function updateArchiveLanguageLinks() {
  const activeTab = document.querySelector('.tab-btn.active')?.dataset.tab || 'era';
  const currentHash = window.location.hash || `#tab-${activeTab}`;
  document.querySelectorAll('.lang-btn').forEach(button => {
    if (!(button instanceof HTMLAnchorElement)) return;
    if (button.dataset.lang === 'ja') button.href = `/archive.html${currentHash}`;
    if (button.dataset.lang === 'en') button.href = `/en/archive.html${currentHash}`;
  });
}

function applyStaticTranslations() {
  document.documentElement.lang = currentLanguage;
  document.title = currentLanguage === 'en'
    ? 'Photo Coordinates | Browse Photography History by Era, Country, and Movement'
    : '写真の座標 | 年代順・国別・表現でたどる写真史';

  const mappings = [
    ['archive-back-link', 'homeBack'],
    ['archive-wip-badge', 'wip'],
    ['archive-header-subtitle', 'archiveSubtitle'],
    ['archive-header-sub', 'archiveLead'],
    ['archive-ai-disclaimer', 'archiveDisclaimer'],
    ['random-label', 'randomLabel'],
    ['random-coordinate-button', 'coordinateButton'],
    ['random-hint', 'randomHint'],
    ['tab-era-button', 'eraTab'],
    ['tab-home-link', 'homeTitle'],
    ['filter-label', 'filterLabel'],
    ['filter-reset-button', 'reset'],
    ['no-results', 'noResults']
  ];

  mappings.forEach(([id, key]) => {
    const element = document.getElementById(id);
    if (element) element.textContent = t(key);
  });

  const titleEl = document.getElementById('archive-main-title');
  if (titleEl) {
    titleEl.innerHTML = currentLanguage === 'en' ? '<em>Photo Coordinates</em>' : '<em>写真の座標</em>';
  }

  const headerLabel = document.getElementById('archive-header-label');
  if (headerLabel) {
    headerLabel.textContent = currentLanguage === 'en' ? 'Photo Coordinates / Archive' : 'Photo Coordinates / Archive';
  }

  const searchInput = document.getElementById('filter-search');
  if (searchInput) searchInput.placeholder = t('filterSearchPlaceholder');

  populateArchiveNavigation();
}

function rerenderArchive() {
  const activeTab = document.querySelector('.tab-btn.active')?.dataset.tab || 'era';
  renderEraTab();
  initRandom();
  applyFilters();
  switchTab(activeTab);
  handleDeepLink();
}

function initializeLanguageControls() {
  updateLanguageButtons();
  updateArchiveLanguageLinks();
  applyStaticTranslations();
  document.querySelectorAll('.lang-btn').forEach(button => {
    button.addEventListener('click', () => {
      const next = button.dataset.lang;
      if (next === currentLanguage) return;
      currentLanguage = languageApi ? languageApi.setLanguage(next) : next;
      updateLanguageButtons();
      updateArchiveLanguageLinks();
      applyStaticTranslations();
      rerenderArchive();
    });
  });
}

function movementSlug(name) {
  return String(name || '').replace(/[^A-Za-z\u3000-\u9fff]/g, '');
}

function eraPagePath(eraId) {
  return `${currentLanguage === 'en' ? '/en' : ''}/eras/${eraId}.html`;
}

function countryPagePath(nationality) {
  const meta = COUNTRY_ROUTE_META[nationality];
  const slug = meta?.slug || 'unknown';
  return `${currentLanguage === 'en' ? '/en' : ''}/countries/${slug}.html`;
}

function movementPagePath(name) {
  return `${currentLanguage === 'en' ? '/en' : ''}/movements/${movementSlug(name)}.html`;
}

function navigateArchiveTaxonomy(value) {
  if (!value) return;
  window.location.href = value;
}

function populateArchiveNavigation() {
  const photographers = realPhotographers();
  const eraSelect = document.getElementById('nav-era-select');
  const countrySelect = document.getElementById('nav-country-select');
  const movementSelect = document.getElementById('nav-movement-select');

  if (eraSelect) {
    eraSelect.innerHTML = '';
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = t('eraTab');
    eraSelect.appendChild(defaultOption);
    ERAS.forEach(era => {
      const option = document.createElement('option');
      option.value = eraPagePath(era.id);
      option.textContent = currentLanguage === 'en'
        ? (era.titleEn || era.title)
        : era.title;
      eraSelect.appendChild(option);
    });
  }

  if (countrySelect) {
    countrySelect.innerHTML = '';
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = currentLanguage === 'en' ? 'Browse countries' : '国別でみる';
    countrySelect.appendChild(defaultOption);
    [...new Set(photographers.map(p => p.nationality).filter(n => COUNTRY_ROUTE_META[n]))]
      .sort((a, b) => (COUNTRY_ROUTE_META[a]?.[currentLanguage] || a).localeCompare(COUNTRY_ROUTE_META[b]?.[currentLanguage] || b, currentLanguage === 'en' ? 'en' : 'ja'))
      .forEach(nationality => {
        const option = document.createElement('option');
        option.value = countryPagePath(nationality);
        option.textContent = COUNTRY_ROUTE_META[nationality][currentLanguage];
        countrySelect.appendChild(option);
      });
  }

  if (movementSelect) {
    movementSelect.innerHTML = '';
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = currentLanguage === 'en' ? 'Browse by Movement' : '表現からみる';
    movementSelect.appendChild(defaultOption);
    [...new Set(photographers.flatMap(p => p.movements).filter(Boolean))]
      .sort((a, b) => displayMovementName(a).localeCompare(displayMovementName(b), currentLanguage === 'en' ? 'en' : 'ja'))
      .forEach(movement => {
        const option = document.createElement('option');
        option.value = movementPagePath(movement);
        option.textContent = displayMovementName(movement);
        movementSelect.appendChild(option);
      });
  }
}

function openCoordinatesForPhotographer(pid) {
  if (!pid) return;
  const url = `${coordinateBasePath()}?focus=${encodeURIComponent(`photographer:${pid}`)}`;
  const popup = window.open(url, '_blank');
  if (!popup) {
    window.location.href = url;
    return;
  }
  popup.opener = null;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   RENDER: ERA TAB
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function renderEraTab() {
  const main = document.getElementById('era-main');
  main.innerHTML = '';

  ERAS.forEach(era => {
    const photographers = realPhotographers().filter(p => p.era === era.id);
    const cardsHTML = photographers.length
      ? photographers.map(p => renderCard(p)).join('')
      : renderEmptyPhotographerState();

    const section = document.createElement('section');
    section.className = 'era';
    section.id = `era-${era.id}`;
    section.dataset.eraId = era.id;
    section.innerHTML = `
      <div class="era-toggle" onclick="toggleEra('${era.id}')">
        <div class="era-date">${era.id}<span>— ${era.period.split('—')[1].trim()}</span></div>
        <div class="era-title" style="margin:0">${displayEraTitle(era)}</div>
        <div class="era-toggle-arrow">▼</div>
      </div>
      <div class="era-body">
        <div class="era-body-content">
            <div class="era-info">
              <div class="context-block">
                <div class="context-label">${t('worldEvents')}</div>
                <div class="context-text">${renderOptionalText(displayBlockText(era.worldEvents))}</div>
                ${renderSources(era.worldEvents.sources)}
              </div>
              <div class="context-block">
                <div class="context-label">${t('photoContext')}</div>
                <div class="context-text">${renderOptionalText(displayBlockText(era.photoContext))}</div>
                ${renderSources(era.photoContext.sources)}
              </div>
            </div>
            <div class="photographers-label">${t('photographersInEra')}</div>
            <div class="photographers-grid" id="grid-${era.id}">${cardsHTML}</div>
            <div id="panels-${era.id}"></div>
          </div>
      </div>
    `;

    main.appendChild(section);
  });

  // Attach detail-panel click handlers
  document.querySelectorAll('.photographer-card').forEach(card => {
    const pid = card.dataset.pid;
    card.addEventListener('click', () => toggleDetail(pid, card));
  });

  populateFilters();
  setupObserver();
}

function renderCard(p, extraAttrs = '') {
  const tags = p.movements.length
    ? p.movements.map(m => `<span class="card-tag">${displayMovementName(m)}</span>`).join('')
    : '';
  const searchIndex = buildSearchIndex(p);
  const coordinateButton = p.isPlaceholder
    ? ''
    : `<button class="coordinate-link" type="button" onclick="event.stopPropagation(); openCoordinatesForPhotographer('${p.id}')">${t('coordinateButton')}</button>`;
  return `
    <div class="photographer-card${p.isPlaceholder ? ' placeholder' : ''}" data-pid="${p.id}" data-nationality="${p.nationality}" data-movements="${p.movements.join(',')}" data-search="${searchIndex}" data-placeholder="${p.isPlaceholder ? 'true' : 'false'}" ${extraAttrs}>
      <div class="card-action">
        <div class="card-action-label">${t('coordinateDetail')}</div>
        <div class="card-arrow">↗</div>
      </div>
      <div class="card-flag-nat">${displayMeta(p)}</div>
      <div class="card-name">${displayName(p)}</div>
      ${displaySubName(p)}
      <div class="card-years">${escapeHtml(displayYears(p))}</div>
      <div class="card-tags">${tags}</div>
      ${coordinateButton}
    </div>
  `;
}

/* 脚注マーカー *1 *2 をツールチップ付きの<span>に変換 */
function renderCiteText(text, citations, options = {}) {
  const linkedIds = options.linkedIds || new Set();
  return String(text || '')
    .split(/(\*\d+)/g)
    .map(part => {
      const citeMatch = /^\*(\d+)$/.exec(part);
      if (!citeMatch) return renderLinkedText(part, { ...options, linkedIds });

      const citation = (citations || []).find(item => String(item.num) === citeMatch[1]);
      if (!citation) return escapeHtml(part);

      const label = escapeHtml(citation.name || citation.text || citation.url || '');
      const tooltip = citation.url
        ? `<a class="cite-tooltip" href="${citation.url}" target="_blank" rel="noopener" onclick="event.stopPropagation()">${label} ↗</a>`
        : `<span class="cite-tooltip">${label}</span>`;
      return `<span class="cite-ref">${tooltip}<sup>*${citeMatch[1]}</sup></span>`;
    })
    .join('');
}

function findInfluencePhotographer(photographer, direction) {
  const candidates = realPhotographers()
    .filter(candidate => candidate.id !== photographer.id)
    .filter(candidate => direction < 0
      ? comparePhotographersChronologically(candidate, photographer) < 0
      : comparePhotographersChronologically(candidate, photographer) > 0);

  if (!candidates.length) return null;

  const scored = candidates.map(candidate => {
    const shared = sharedMovements(photographer, candidate);
    const eraGap = Math.abs((ERA_ORDER.get(candidate.era) ?? 999) - (ERA_ORDER.get(photographer.era) ?? 999));
    const orderGap = Math.abs((PHOTOGRAPHER_ORDER.get(candidate.id) ?? 9999) - (PHOTOGRAPHER_ORDER.get(photographer.id) ?? 9999));
    const nationalityBonus = candidate.nationality === photographer.nationality ? 6 : 0;
    return {
      candidate,
      eraGap,
      orderGap,
      score: shared.length * 100 - eraGap * 8 - Math.min(orderGap, 18) + nationalityBonus
    };
  });

  scored.sort((left, right) => {
    if (right.score !== left.score) return right.score - left.score;
    if (left.eraGap !== right.eraGap) return left.eraGap - right.eraGap;
    if (left.orderGap !== right.orderGap) return left.orderGap - right.orderGap;
    return comparePhotographersChronologically(left.candidate, right.candidate);
  });

  return scored[0]?.candidate || null;
}

function findReadNextTarget(photographer, influencedBy, influencedNext) {
  const used = new Set([photographer.id]);
  if (influencedBy) used.add(influencedBy.id);
  if (influencedNext) used.add(influencedNext.id);

  const alternateMovement = (photographer.movements || [])[1];
  if (alternateMovement) {
    const slug = movementSlug(alternateMovement);
    return {
      label: displayMovementName(alternateMovement),
      href: `#movement-${slug}`,
      onclick: `openRecommendedMovement(event,'${slug}')`
    };
  }

  const nextChronological = realPhotographers()
    .filter(candidate => !used.has(candidate.id))
    .sort(comparePhotographersChronologically)
    .find(candidate => comparePhotographersChronologically(candidate, photographer) > 0);

  if (nextChronological) {
    return {
      label: displayName(nextChronological),
      href: `#photographer-${nextChronological.id}`,
      onclick: `openRecommendedPhotographer(event,'${nextChronological.id}')`
    };
  }

  const primaryMovement = (photographer.movements || [])[0];
  if (primaryMovement) {
    const slug = movementSlug(primaryMovement);
    return {
      label: displayMovementName(primaryMovement),
      href: `#movement-${slug}`,
      onclick: `openRecommendedMovement(event,'${slug}')`
    };
  }

  return null;
}

function renderRecommendationLink(item) {
  if (!item) return `<span class="detail-related-empty">${t('notSet')}</span>`;
  return `<a class="detail-related-link" href="${item.href}" onclick="${item.onclick}">${item.label}</a>`;
}

function renderRecommendationLinks(items) {
  const validItems = (items || []).filter(Boolean);
  if (!validItems.length) return `<span class="detail-related-empty">${t('notSet')}</span>`;
  return validItems.map(renderRecommendationLink).join('');
}

function findRelatedPhotographers(photographer, limit = 5) {
  const targetEraIndex = ERA_ORDER.get(photographer.era) ?? 999;
  const targetOrderIndex = PHOTOGRAPHER_ORDER.get(photographer.id) ?? 9999;
  const targetMovements = new Set(photographer.movements || []);
  const scored = realPhotographers()
    .filter(candidate => candidate.id !== photographer.id)
    .map(candidate => {
      const shared = sharedMovements(photographer, candidate);
      const sameEra = candidate.era === photographer.era;
      const sameCountry = candidate.nationality && candidate.nationality === photographer.nationality;
      if (!shared.length && !sameEra && !sameCountry) return null;
      const eraGap = Math.abs((ERA_ORDER.get(candidate.era) ?? 999) - targetEraIndex);
      const orderGap = Math.abs((PHOTOGRAPHER_ORDER.get(candidate.id) ?? 9999) - targetOrderIndex);
      return {
        candidate,
        eraGap,
        orderGap,
        score: shared.length * 100 + (sameEra ? 18 : Math.max(0, 10 - eraGap * 3)) + (sameCountry ? 6 : 0) - Math.min(orderGap, 36)
      };
    })
    .filter(Boolean);

  scored.sort((left, right) => {
    if (right.score !== left.score) return right.score - left.score;
    if (left.eraGap !== right.eraGap) return left.eraGap - right.eraGap;
    if (left.orderGap !== right.orderGap) return left.orderGap - right.orderGap;
    return comparePhotographersChronologically(left.candidate, right.candidate);
  });

  return scored.slice(0, limit).map(item => item.candidate);
}

function buildRelatedPeopleEntries(photographer, bodyText = '') {
  const enrichment = getPhotographerEnrichment(photographer);
  const related = [];
  const used = new Set([photographer.id]);

  (enrichment.relatedPeople || []).slice(0, 2).forEach(person => {
    const label = currentLanguage === 'en'
      ? (person.nameEn || person.nameJa || '')
      : (person.nameJa || person.nameEn || '');
    const altLabel = currentLanguage === 'en' ? (person.nameJa || '') : (person.nameEn || '');
    const url = person.photographerId
      ? `#photographer-${person.photographerId}`
      : (currentLanguage === 'en' ? (person.urlEn || person.urlJa || '') : (person.urlJa || person.urlEn || ''));
    const onclick = person.photographerId ? `openRecommendedPhotographer(event,'${person.photographerId}')` : '';
    related.push({
      label,
      href: url,
      onclick,
      role: currentLanguage === 'en'
        ? (person.roleEn || person.roleJa || 'Figure')
        : (person.roleJa || person.roleEn || '人物'),
      showRole: !essayContainsName(bodyText, [label, altLabel])
    });
    if (person.photographerId) used.add(person.photographerId);
  });

  findRelatedPhotographers(photographer, 8).forEach(candidate => {
    if (used.has(candidate.id) || related.length >= 5) return;
    const label = displayName(candidate);
    const altLabel = currentLanguage === 'en' ? (candidate.nameJa || '') : (candidate.name || '');
    related.push({
      label,
      href: `#photographer-${candidate.id}`,
      onclick: `openRecommendedPhotographer(event,'${candidate.id}')`,
      role: currentLanguage === 'en' ? 'Photographer' : '写真家',
      showRole: !essayContainsName(bodyText, [label, altLabel])
    });
    used.add(candidate.id);
  });

  return related.slice(0, 5);
}

function renderRelatedPeopleEntries(entries) {
  if (!(entries || []).length) return `<span class="detail-related-empty">${t('notSet')}</span>`;
  return entries.map(item => {
    const role = item.showRole ? `<span class="detail-related-role">${escapeHtml(item.role)}</span>` : '';
    const anchor = item.href
      ? `<a class="detail-related-link" href="${item.href}"${item.onclick ? ` onclick="${item.onclick}"` : ' target="_blank" rel="noopener"' }>${escapeHtml(item.label)}</a>`
      : `<span class="detail-related-empty">${escapeHtml(item.label)}</span>`;
    return `<span class="detail-related-card">${role}${anchor}</span>`;
  }).join('');
}

function buildRelatedReadingSection(photographer, bodyText = '') {
  const relatedPeople = buildRelatedPeopleEntries(photographer, bodyText);
  const relatedMovements = expandedMovementNames(photographer, 5).map((movementLabel, index) => {
    const sourceMovement = ((photographer.movements || []).concat(getPhotographerEnrichment(photographer).extraMovements || []))[index] || movementLabel;
    const slug = movementSlug(sourceMovement);
    return {
      label: movementLabel,
      href: `#movement-${slug}`,
      onclick: `openRecommendedMovement(event,'${slug}')`
    };
  }).filter(Boolean);
  const influencedBy = findInfluencePhotographer(photographer, -1);
  const influencedNext = findInfluencePhotographer(photographer, 1);
  const readNext = findReadNextTarget(photographer, influencedBy, influencedNext);

  const items = [
    [t('relatedMovement'), renderRecommendationLinks(relatedMovements)],
    [t('relatedPhotographers'), renderRelatedPeopleEntries(relatedPeople)],
    [t('readNext'), renderRecommendationLink(readNext)]
  ];

  const rows = items.map(([label, content]) => `
      <div class="detail-related-item">
        <div class="detail-related-label">${label}</div>
        <div class="detail-related-value">${content}</div>
      </div>
    `).join('');

  return `
      <div class="detail-section">
        <div class="detail-section-title">${t('relatedReading')}</div>
        <div class="detail-related-grid">${rows}</div>
      </div>`;
}

function openRecommendedPhotographer(event, pid) {
  if (event) event.preventDefault();
  if (!pid) return false;
  setLocationHash(`photographer-${pid}`);
  updateArchiveLanguageLinks();
  revealPhotographerFromHash(pid);
  return false;
}

function openRecommendedMovement(event, mvId) {
  if (event) event.preventDefault();
  if (!mvId) return false;
  setLocationHash(`movement-${mvId}`);
  updateArchiveLanguageLinks();
  revealMovementFromHash(mvId);
  return false;
}

function detailPageLinkLabel(p) {
  const name = displayName(p);
  return currentLanguage === 'en'
    ? `Read ${name} on its page`
    : `${name}の独立ページを読む`;
}

function renderDetailPanel(p, idPrefix = 'panel-', customCloseFn = '') {
  const isMovement = idPrefix !== 'panel-';
  const panelId = `${idPrefix}${p.id}`;
  const closeFn = customCloseFn || (isMovement ? `closeMovementDetail('${p.id}')` : `closeDetail('${p.id}')`);
  const intro = getPhotographerLeadCopy(p);
  const keywordLine = buildPhotographerKeywordLine(p);
  const tags = expandedMovementNames(p, 5)
    .map((movementLabel, index) => {
      const sourceMovement = ((p.movements || []).concat(getPhotographerEnrichment(p).extraMovements || []))[index] || movementLabel;
      const slug = movementSlug(sourceMovement);
      return `<a class="detail-tag" href="#movement-${slug}" onclick="openRecommendedMovement(event,'${slug}')">${displayMovementName(sourceMovement)}</a>`;
    }).join('');
  const detailLinks = getPhotographerEssayPayload(p).links;
  const linksHTML = detailLinks.map(l =>
    `<a class="detail-link" href="${l.url}" target="_blank" rel="noopener">${l.label} ↗</a>`
  ).join('');
  const detailPageLink = `<a class="detail-link" href="${photographerPagePath(p)}">${detailPageLinkLabel(p)}</a>`;
  if (p.isPlaceholder) {
    return `
      <div class="detail-panel" id="${panelId}">
        <div class="detail-header">
          <div>
            <div class="detail-name">${displayName(p)}</div>
            <div class="detail-meta">${displayMeta(p)}</div>
          </div>
          <button class="close-btn" onclick="${closeFn}">✕</button>
        </div>
        <div class="detail-section">
          <div class="detail-section-title">${t('explanation')}</div>
          <div class="detail-text">${EMPTY_BLOCK}</div>
        </div>
      </div>
    `;
  }

  /* ── 解説セクション：新旧フォーマット両対応 ── */
  let contextHTML;
  let citationsHTML = '';
  let rawEssayText = '';
  const essayPayload = getPhotographerEssayPayload(p);
  if (essayPayload.citations) {
    /* 新フォーマット：context.text に *1 *2 マーカー、context.citations に出典 */
    rawEssayText = essayPayload.text;
    const ctxText = renderCiteText(rawEssayText, essayPayload.citations, { excludeId: p.id, linkedIds: new Set() });
    citationsHTML = essayPayload.citations.map(c =>
      `<div class="cite-item"><span class="cite-num">*${c.num}</span><a href="${c.url}" target="_blank" rel="noopener">${c.name}</a></div>`
    ).join('');
    contextHTML = `
      <div class="detail-section">
        <div class="detail-section-title">${t('explanation')}</div>
        <div class="detail-text">${ctxText}</div>
      </div>`;
  } else {
    /* 旧フォーマット：expression.text + context.text を結合し、全出典を自動番号化 */
    const expText = p.expression ? localizeValue(p.expression.text, p.expression.textEn) : '';
    const ctxText = p.context ? localizeValue(p.context.text, p.context.textEn) : '';
    rawEssayText = [expText, ctxText].filter(Boolean).join(' ');
    const linkedIds = new Set();
    const combined = [expText, ctxText]
      .filter(Boolean)
      .map(part => renderLinkedText(part, { excludeId: p.id, linkedIds }))
      .join('<br><br>');
    const allSrc = [
      ...((p.expression && p.expression.sources) || []),
      ...((p.context && p.context.sources) || []),
    ];
    /* 重複URLを除去 */
    const seen = new Set();
    const dedupSrc = allSrc.filter(s => { if (seen.has(s.url)) return false; seen.add(s.url); return true; });
    citationsHTML = dedupSrc.map((s, i) =>
      `<div class="cite-item"><span class="cite-num">*${i+1}</span><a href="${s.url}" target="_blank" rel="noopener">${s.text}</a></div>`
    ).join('');
    contextHTML = `
      <div class="detail-section">
        <div class="detail-section-title">${t('explanation')}</div>
        <div class="detail-text">${combined}</div>
      </div>`;
  }

  const sourcesSection = citationsHTML ? `
      <div class="detail-section">
        <div class="detail-section-title">${t('sources')}</div>
        <div class="cite-list">${citationsHTML}</div>
      </div>` : '';

  const linksSection = `
      <div class="detail-section">
        <div class="detail-section-title">${t('externalLinks')}</div>
        <div class="detail-links">${detailPageLink}${linksHTML}</div>
      </div>`;

  const booksSection = renderArchiveAffiliateSection(p);
  const relatedSection = buildRelatedReadingSection(p, rawEssayText);

  return `
    <div class="detail-panel" id="${panelId}">
      <div class="detail-header">
        <div>
          <div class="detail-name">${displayName(p)}${p.gender ? `<span style="font-size:12px;color:var(--text-muted);font-weight:normal;margin-left:10px;vertical-align:middle;letter-spacing:0.05em">${displayGender(p.gender)}</span>` : ''}${currentLanguage !== 'en' && p.nameJa && p.name ? `<span style="display:block;font-family:'DM Mono',monospace;font-size:11px;color:var(--text-muted);font-weight:normal;margin-top:3px;letter-spacing:0.04em">${p.name}</span>` : ''}</div>
          <div class="detail-meta">${[displayMeta(p), displayYears(p)].filter(Boolean).join(' &nbsp;/&nbsp; ')}</div>
          <div class="detail-keywordline">${keywordLine}</div>
        </div>
        <button class="close-btn" onclick="${closeFn}">✕</button>
      </div>
      <div class="detail-lead">${intro}</div>
      ${tags ? `<div class="detail-tags">${tags}</div>` : ''}
      ${contextHTML}
      ${relatedSection}
      ${booksSection}
      ${linksSection}
      ${sourcesSection}
    </div>
  `;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   DETAIL PANEL TOGGLE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function toggleDetail(pid, card) {
  const era = card.closest('.era');
  const panelContainer = era.querySelector('[id^="panels-"]');
  const existingPanel = document.getElementById(`panel-${pid}`);
  const isOpen = existingPanel && existingPanel.classList.contains('open');

  // Close all open panels in this era
  era.querySelectorAll('.detail-panel.open').forEach(p => p.classList.remove('open'));
  era.querySelectorAll('.photographer-card.active').forEach(c => c.classList.remove('active'));

  if (!isOpen) {
    // Inject panel HTML if not already present
    if (!existingPanel) {
      const p = PHOTOGRAPHER_LOOKUP.get(pid);
      if (p) panelContainer.insertAdjacentHTML('beforeend', renderDetailPanel(p));
    }
    const panel = document.getElementById(`panel-${pid}`);
    panel.classList.add('open');
    card.classList.add('active');
    setLocationHash(`photographer-${pid}`);
    setTimeout(() => panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 50);
  }
}

function closeDetail(pid) {
  const panel = document.getElementById(`panel-${pid}`);
  if (panel) panel.classList.remove('open');
  document.querySelectorAll('.photographer-card.active').forEach(c => c.classList.remove('active'));
  if (window.location.hash === `#photographer-${pid}`) {
    setLocationHash('');
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FILTERS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function populateFilters() {
  populateArchiveNavigation();
}

function applyFilters() {
  const searchInput = document.getElementById('filter-search');
  activeFilters.search = normalizeSearch(searchInput ? searchInput.value : '');
  activeFilters.country = '';
  activeFilters.movement = '';

  let visibleCount = 0;

  // Only filter cards in era-main (not movement tab)
  document.querySelectorAll('#era-main .photographer-card').forEach(card => {
    if (card.dataset.placeholder === 'true') {
      card.classList.toggle('filtered-out', hasActiveFilters());
      return;
    }
    const nat = card.dataset.nationality;
    const movs = card.dataset.movements.split(',');
    const searchText = card.dataset.search || '';
    const matchS = !activeFilters.search || searchText.includes(activeFilters.search);
    const matchC = !activeFilters.country || nat.includes(activeFilters.country);
    const matchM = !activeFilters.movement || movs.includes(activeFilters.movement);
    if (matchS && matchC && matchM) {
      card.classList.remove('filtered-out');
      visibleCount++;
    } else {
      card.classList.add('filtered-out');
    }
  });

  // Hide era sections with no visible cards
  document.querySelectorAll('.era').forEach(era => {
    const visibleCards = era.querySelectorAll('.photographer-card:not(.filtered-out)');
    era.classList.toggle('hidden', visibleCards.length === 0);
  });

  const noResults = document.getElementById('no-results');
  noResults.classList.toggle('visible', visibleCount === 0);

  const countEl = document.getElementById('filter-count');
  const total = realPhotographers().length;
  if (hasActiveFilters()) {
    countEl.textContent = t('filteredCount', visibleCount, total);
  } else {
    countEl.textContent = t('totalCount', total);
  }
}

function resetFilters() {
  const searchInput = document.getElementById('filter-search');
  if (searchInput) searchInput.value = '';
  activeFilters = { search: '', country: '', movement: '' };
  document.querySelectorAll('#era-main .photographer-card').forEach(c => c.classList.remove('filtered-out'));
  document.querySelectorAll('.era').forEach(e => e.classList.remove('hidden'));
  document.getElementById('no-results').classList.remove('visible');
  document.getElementById('filter-count').textContent = t('totalCount', realPhotographers().length);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   RENDER: MOVEMENT TAB
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function renderMovementTab() {
  const main = document.getElementById('movement-main');
  if (!main) return;
  main.innerHTML = '';

  // Gather movements that have at least one photographer
  const movementMap = {};
  realPhotographers().forEach(p => {
    p.movements.forEach(m => {
      if (!movementMap[m]) movementMap[m] = [];
      movementMap[m].push(p);
    });
  });

  Object.entries(movementMap).sort((a, b) => a[0].localeCompare(b[0], 'ja')).forEach(([mvName, photographers]) => {
    const meta = MOVEMENTS_META[mvName] || { en: mvName, desc: '' };
    const mvId = mvName.replace(/[^a-zA-Z\u3000-\u9fff]/g, '');

    const cardsHTML = photographers.map(p => renderCard(p, `data-mv="${mvId}" onclick="toggleMovementDetail('${p.id}','${mvId}',this)"`)).join('');

    const section = document.createElement('section');
    section.className = 'movement-section';
    section.dataset.mv = mvId;
    section.id = `movement-${mvId}`;
    section.innerHTML = `
      <div class="movement-toggle" onclick="toggleMovement('${mvId}')">
        <div>
          <div class="movement-name">${currentLanguage === 'en' ? (meta.en || mvName) : mvName}<em class="movement-name-en">${currentLanguage === 'en' ? mvName : meta.en}</em></div>
          <div class="movement-period">${t('registeredCount', photographers.length)}</div>
        </div>
        <div class="movement-toggle-arrow">▼</div>
      </div>
      <div class="movement-body">
        <div class="movement-body-content">
          <div class="context-block" style="margin-bottom:24px">
            <div class="context-label">${t('movementOverview')}</div>
            <div class="context-text">${renderOptionalText(localizeValue(meta.desc, meta.descEn))}</div>
          </div>
          <div class="photographers-label">${t('movementPhotographers')}</div>
          <div class="movement-grid" id="mvgrid-${mvId}">${cardsHTML}</div>
          <div id="mvpanels-${mvId}"></div>
        </div>
      </div>
    `;
    main.appendChild(section);
  });

  setupObserver('.movement-section');
}

function toggleMovementDetail(pid, mvId, card) {
  const section = card.closest('.movement-section');
  const panelContainer = section.querySelector(`[id^="mvpanels-"]`);
  const panelId = `mvpanel-${mvId}-${pid}`;
  const existingPanel = document.getElementById(panelId);
  const isOpen = existingPanel && existingPanel.classList.contains('open');

  // Close all open panels in this movement section
  section.querySelectorAll('.detail-panel.open').forEach(p => p.classList.remove('open'));
  section.querySelectorAll('.photographer-card.active').forEach(c => c.classList.remove('active'));

  if (!isOpen) {
    if (!existingPanel) {
      const p = PHOTOGRAPHER_LOOKUP.get(pid);
      if (p) panelContainer.insertAdjacentHTML('beforeend', renderDetailPanel(p, `mvpanel-${mvId}-`, `closeMovementDetail('${pid}','${mvId}')`));
    }
    const panel = document.getElementById(panelId);
    panel.classList.add('open');
    card.classList.add('active');
    setTimeout(() => panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 50);
  }
}

function closeMovementDetail(pid, mvId) {
  const panel = document.getElementById(`mvpanel-${mvId}-${pid}`);
  if (panel) panel.classList.remove('open');
  document.querySelectorAll('.photographer-card.active').forEach(c => c.classList.remove('active'));
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TAB SWITCHING
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  const tabContent = document.getElementById(`tab-${tabId}`);
  const tabButton = document.querySelector(`[data-tab="${tabId}"]`);
  if (tabContent) tabContent.classList.add('active');
  if (tabButton) tabButton.classList.add('active');
  updateArchiveLanguageLinks();
}

function toggleMovement(mvId) {
  const section = document.getElementById(`movement-${mvId}`);
  if (!section) return;
  const body = section.querySelector('.movement-body');
  if (section.classList.contains('open')) {
    body.style.height = body.scrollHeight + 'px';
    requestAnimationFrame(() => requestAnimationFrame(() => { body.style.height = '0'; }));
    section.classList.remove('open');
  } else {
    section.classList.add('open');
    body.style.height = body.scrollHeight + 'px';
    body.addEventListener('transitionend', () => {
      if (section.classList.contains('open')) body.style.height = 'auto';
    }, { once: true });
  }
}

function openMovement(mvId) {
  const section = document.getElementById(`movement-${mvId}`);
  if (!section || section.classList.contains('open')) return;
  const body = section.querySelector('.movement-body');
  section.classList.add('open');
  body.style.height = body.scrollHeight + 'px';
  body.addEventListener('transitionend', () => {
    if (section.classList.contains('open')) body.style.height = 'auto';
  }, { once: true });
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ERA ACCORDION
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function toggleEra(eraId) {
  const section = document.getElementById(`era-${eraId}`);
  if (!section) return;
  const body = section.querySelector('.era-body');
  if (section.classList.contains('open')) {
    // closing: fix height first, then animate to 0
    body.style.height = body.scrollHeight + 'px';
    requestAnimationFrame(() => requestAnimationFrame(() => { body.style.height = '0'; }));
    section.classList.remove('open');
  } else {
    section.classList.add('open');
    body.style.height = body.scrollHeight + 'px';
    body.addEventListener('transitionend', () => {
      if (section.classList.contains('open')) body.style.height = 'auto';
    }, { once: true });
  }
}

function openEra(eraId) {
  const section = document.getElementById(`era-${eraId}`);
  if (!section || section.classList.contains('open')) return;
  const body = section.querySelector('.era-body');
  section.classList.add('open');
  body.style.height = body.scrollHeight + 'px';
  body.addEventListener('transitionend', () => {
    if (section.classList.contains('open')) body.style.height = 'auto';
  }, { once: true });
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   RANDOM PHOTOGRAPHER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function initRandom() {
  const randomBox = document.getElementById('random-box');
  if (!randomBox) return;
  const photographers = realPhotographers();
  if (!photographers.length) return;
  // Seed by date so it changes daily
  const dateStr = new Date().toDateString();
  let hash = 0;
  for (let i = 0; i < dateStr.length; i++) {
    hash = ((hash << 5) - hash) + dateStr.charCodeAt(i);
    hash |= 0;
  }
  const idx = Math.abs(hash) % photographers.length;
  const p = photographers[idx];

  document.getElementById('random-name').textContent = displayName(p);
  document.getElementById('random-meta').textContent =
    `${displayMeta(p)}  /  ${p.years}  /  ${p.movements.map(displayMovementName).join(' · ')}`;
  const excerptSrc =
    getPhotographerEssayPayload(p).text ||
    (p.context && localizeValue(p.context.text, p.context.textEn)) ||
    (p.expression && localizeValue(p.expression.text, p.expression.textEn)) ||
    '';
  document.getElementById('random-excerpt').textContent =
    excerptSrc.replace(/\*\d+/g, '').slice(0, 80) + '…';

  randomBox.dataset.pid = p.id;
}

function openRandomCoordinates(event) {
  event.stopPropagation();
  const box = document.getElementById('random-box');
  if (!box) return;
  const pid = box.dataset.pid;
  openCoordinatesForPhotographer(pid);
}

function scrollToPhotographer() {
  const box = document.getElementById('random-box');
  if (!box) return;
  const pid = box.dataset.pid;
  if (!pid) return;
  switchTab('era');
  setTimeout(() => {
    const card = document.querySelector(`#era-main [data-pid="${pid}"]`);
    if (!card) return;
    const era = card.closest('.era');
    if (era) {
      era.classList.add('visible');
      openEra(era.dataset.eraId);
    }
    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    setTimeout(() => toggleDetail(pid, card), 600);
  }, 100);
}

function revealPhotographerFromHash(pid) {
  if (!pid) return;
  switchTab('era');
  setTimeout(() => {
    const card = document.querySelector(`#era-main [data-pid="${pid}"]`);
    if (!card) return;
    const era = card.closest('.era');
    if (era) {
      era.classList.remove('hidden');
      openEra(era.dataset.eraId);
    }
    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    setTimeout(() => {
      const panel = document.getElementById(`panel-${pid}`);
      if (!panel || !panel.classList.contains('open')) {
        toggleDetail(pid, card);
      }
    }, 280);
  }, 80);
}

function revealMovementFromHash(mvId) {
  if (!mvId) return;
  switchTab('movement');
  setTimeout(() => {
    const section = document.getElementById(`movement-${mvId}`);
    if (section) {
      openMovement(mvId);
      section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, 80);
}

function handleDeepLink() {
  const hash = window.location.hash.replace(/^#/, '');
  if (!hash) return;

  if (hash === 'tab-era') {
    switchTab('era');
    return;
  }

  if (hash.startsWith('photographer-')) {
    revealPhotographerFromHash(hash.slice('photographer-'.length));
    return;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   INTERSECTION OBSERVER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function setupObserver(selector = '.era') {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.05 });
  document.querySelectorAll(selector).forEach(el => observer.observe(el));
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   INIT
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
initializeLanguageControls();
renderEraTab();
renderMovementTab();
initRandom();
applyFilters(); // initialize count
handleDeepLink();
window.addEventListener('hashchange', () => {
  handleDeepLink();
  updateArchiveLanguageLinks();
});
