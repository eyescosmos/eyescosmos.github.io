/* UI behavior for the photography history site. */

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   STATE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
let activeFilters = { search: '', country: '', movement: '' };
const EMPTY_BLOCK = '<div class="empty-copy" aria-hidden="true"></div>';
const languageApi = window.PhotoCoordinatesI18n;
let currentLanguage = languageApi ? languageApi.getLanguage() : 'ja';

const UI_TEXT = {
  ja: {
    homeTitle: '写真の座標',
    homeBack: '写真の座標へ戻る',
    wip: '随時更新中',
    archiveHeaderLabel: 'Photo Coordinates / Archive',
    archiveSubtitle: '年代と表現',
    archiveLead: '写真は常にその時代の社会・政治・技術の文脈の中に生まれてきた。年代をたどりながら、世界の動きと写真表現の関係を探る。',
    archiveDisclaimer: '※ 本サイトの情報はAIがウェブ上の公開資料をもとに収集・整理したものです。出典を明記していますが、曖昧さや誤りが含まれる可能性があります。気になった作家・表現・時代については、ぜひご自身でも確認してください。',
    randomLabel: '今日のランダム写真家',
    randomHint: '→ クリックして詳細を見る',
    coordinateButton: '座標で見る',
    coordinateDetail: '解説',
    eraTab: '年代から見る',
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
    registeredCount: count => `登録: ${count}名`,
    explanation: '解説',
    externalLinks: '外部リンク',
    books: '写真集',
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
    archiveSubtitle: 'Era and Movement',
    archiveLead: 'Photography has always emerged within the social, political, and technological conditions of its time. Move through the eras and trace how world events shaped photographic expression.',
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
    registeredCount: count => `${count} registered`,
    explanation: 'Essay',
    externalLinks: 'External Links',
    books: 'Books',
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

const GENDER_TEXT = {
  男性: { ja: '男性', en: 'Male' },
  女性: { ja: '女性', en: 'Female' }
};

function t(key, ...args) {
  const value = UI_TEXT[currentLanguage][key] ?? UI_TEXT.ja[key];
  return typeof value === 'function' ? value(...args) : value;
}

function localizeValue(valueJa, valueEn) {
  return currentLanguage === 'en'
    ? (valueEn || valueJa || '')
    : (valueJa || valueEn || '');
}

function realPhotographers() {
  return PHOTOGRAPHERS.filter(p => !p.isPlaceholder);
}

function renderOptionalText(text) {
  return text && text.trim() ? text : EMPTY_BLOCK;
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
  if (!p.nameJa || !p.name) return '';
  return `<div class="card-name-sub">${currentLanguage === 'en' ? p.nameJa : p.name}</div>`;
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
    return MOVEMENTS_META[movementName]?.en || movementName;
  }
  return movementName;
}

function displayEraTitle(era) {
  return currentLanguage === 'en' ? era.titleEn || era.title : era.title;
}

function displayBlockText(block) {
  return currentLanguage === 'en'
    ? (block.textEn || block.text || '')
    : (block.text || block.textEn || '');
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

function applyStaticTranslations() {
  document.documentElement.lang = currentLanguage;
  document.title = currentLanguage === 'en' ? 'Photo Coordinates | Eras and Movements' : '写真の座標 | 年代と表現';

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
    ['tab-movement-button', 'movementTab'],
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

  const countryDefault = document.getElementById('filter-country-default');
  if (countryDefault) countryDefault.textContent = t('allCountries');

  const movementDefault = document.getElementById('filter-movement-default');
  if (movementDefault) movementDefault.textContent = t('allMovements');

  const searchInput = document.getElementById('filter-search');
  if (searchInput) searchInput.placeholder = t('filterSearchPlaceholder');
}

function rerenderArchive() {
  const activeTab = document.querySelector('.tab-btn.active')?.dataset.tab || 'era';
  renderEraTab();
  renderMovementTab();
  initRandom();
  applyFilters();
  switchTab(activeTab);
  handleDeepLink();
}

function initializeLanguageControls() {
  updateLanguageButtons();
  applyStaticTranslations();
  document.querySelectorAll('.lang-btn').forEach(button => {
    button.addEventListener('click', () => {
      const next = button.dataset.lang;
      if (next === currentLanguage) return;
      currentLanguage = languageApi ? languageApi.setLanguage(next) : next;
      updateLanguageButtons();
      applyStaticTranslations();
      rerenderArchive();
    });
  });
}

function openCoordinatesForPhotographer(pid) {
  if (!pid) return;
  const url = `index.html?focus=${encodeURIComponent(`photographer:${pid}`)}`;
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
    const photographers = PHOTOGRAPHERS.filter(p => p.era === era.id);
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
      <div class="card-years">${p.years}</div>
      <div class="card-tags">${tags}</div>
      ${coordinateButton}
    </div>
  `;
}

/* 脚注マーカー *1 *2 をツールチップ付きの<span>に変換 */
function renderCiteText(text, citations) {
  if (!citations || !citations.length) return text;
  let result = text;
  citations.forEach(c => {
    const tooltip = c.url
      ? `<a class="cite-tooltip" href="${c.url}" target="_blank" rel="noopener" onclick="event.stopPropagation()">${c.name} ↗</a>`
      : `<span class="cite-tooltip">${c.name}</span>`;
    result = result.replace(
      new RegExp('\\*' + c.num + '(?!\\d)', 'g'),
      `<span class="cite-ref">${tooltip}<sup>*${c.num}</sup></span>`
    );
  });
  return result;
}

function renderDetailPanel(p, idPrefix = 'panel-', customCloseFn = '') {
  const isMovement = idPrefix !== 'panel-';
  const panelId = `${idPrefix}${p.id}`;
  const closeFn = customCloseFn || (isMovement ? `closeMovementDetail('${p.id}')` : `closeDetail('${p.id}')`);

  const tags = p.movements.map(m => `<span class="detail-tag">${displayMovementName(m)}</span>`).join('');
  const linksHTML = p.links.map(l =>
    `<a class="detail-link" href="${l.url}" target="_blank" rel="noopener">${l.label} ↗</a>`
  ).join('');
  const amazonHTML = p.amazon
    ? `<a class="detail-link" href="${p.amazon}" target="_blank" rel="noopener sponsored">${t('amazon')}</a>`
    : `<div class="amazon-placeholder">${p.isPlaceholder ? '' : t('amazonPending')}</div>`;

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
  if (p.context && p.context.citations) {
    /* 新フォーマット：context.text に *1 *2 マーカー、context.citations に出典 */
    const ctxText = renderCiteText(localizeValue(p.context.text, p.context.textEn), p.context.citations);
    const citeListHTML = p.context.citations.map(c =>
      `<div class="cite-item"><span class="cite-num">*${c.num}</span><a href="${c.url}" target="_blank" rel="noopener">${c.name}</a></div>`
    ).join('');
    contextHTML = `
      <div class="detail-section">
        <div class="detail-section-title">${t('explanation')}</div>
        <div class="detail-text">${ctxText}</div>
        <div class="cite-list">${citeListHTML}</div>
      </div>`;
  } else {
    /* 旧フォーマット：expression.text + context.text を結合し、全出典を自動番号化 */
    const expText = p.expression ? localizeValue(p.expression.text, p.expression.textEn) : '';
    const ctxText = p.context ? localizeValue(p.context.text, p.context.textEn) : '';
    const combined = expText + (expText && ctxText ? '<br><br>' : '') + ctxText;
    const allSrc = [
      ...((p.expression && p.expression.sources) || []),
      ...((p.context && p.context.sources) || []),
    ];
    /* 重複URLを除去 */
    const seen = new Set();
    const dedupSrc = allSrc.filter(s => { if (seen.has(s.url)) return false; seen.add(s.url); return true; });
    const citeListHTML = dedupSrc.map((s, i) =>
      `<div class="cite-item"><span class="cite-num">*${i+1}</span><a href="${s.url}" target="_blank" rel="noopener">${s.text}</a></div>`
    ).join('');
    contextHTML = `
      <div class="detail-section">
        <div class="detail-section-title">${t('explanation')}</div>
        <div class="detail-text">${combined}</div>
        ${citeListHTML ? `<div class="cite-list">${citeListHTML}</div>` : ''}
          </div>`;
  }

  const linksSection = linksHTML ? `
      <div class="detail-section">
        <div class="detail-section-title">${t('externalLinks')}</div>
        <div class="detail-links">${linksHTML}</div>
      </div>` : '';

  const booksSection = amazonHTML ? `
      <div class="detail-section">
        <div class="detail-section-title">${t('books')}</div>
        ${amazonHTML}
      </div>` : '';

  return `
    <div class="detail-panel" id="${panelId}">
      <div class="detail-header">
        <div>
          <div class="detail-name">${displayName(p)}${p.gender ? `<span style="font-size:12px;color:var(--text-muted);font-weight:normal;margin-left:10px;vertical-align:middle;letter-spacing:0.05em">${displayGender(p.gender)}</span>` : ''}${p.nameJa && p.name ? `<span style="display:block;font-family:'DM Mono',monospace;font-size:11px;color:var(--text-muted);font-weight:normal;margin-top:3px;letter-spacing:0.04em">${currentLanguage === 'en' ? p.nameJa : p.name}</span>` : ''}</div>
          <div class="detail-meta">${[displayMeta(p), p.years].filter(Boolean).join(' &nbsp;/&nbsp; ')}</div>
        </div>
        <button class="close-btn" onclick="${closeFn}">✕</button>
      </div>
      ${tags ? `<div class="detail-tags">${tags}</div>` : ''}
      ${contextHTML}
      ${linksSection}
      ${booksSection}
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
      const p = PHOTOGRAPHERS.find(ph => ph.id === pid);
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
  const photographers = realPhotographers();
  const countries = [...new Set(photographers.map(p => p.nationality).filter(Boolean))].sort();
  const movements = [...new Set(photographers.flatMap(p => p.movements))].sort();

  const cSel = document.getElementById('filter-country');
  cSel.innerHTML = `<option value="">${t('allCountries')}</option>`;
  countries.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c; opt.textContent = COUNTRY_TEXT[c]?.[currentLanguage] || c;
    cSel.appendChild(opt);
  });

  const mSel = document.getElementById('filter-movement-era');
  mSel.innerHTML = `<option value="">${t('allMovements')}</option>`;
  movements.forEach(m => {
    const opt = document.createElement('option');
    opt.value = m; opt.textContent = displayMovementName(m);
    mSel.appendChild(opt);
  });
}

function applyFilters() {
  activeFilters.search = normalizeSearch(document.getElementById('filter-search').value);
  activeFilters.country = document.getElementById('filter-country').value;
  activeFilters.movement = document.getElementById('filter-movement-era').value;

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
  document.getElementById('filter-search').value = '';
  document.getElementById('filter-country').value = '';
  document.getElementById('filter-movement-era').value = '';
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
            <div class="context-text">${localizeValue(meta.desc, meta.descEn) || EMPTY_BLOCK}</div>
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
      const p = PHOTOGRAPHERS.find(ph => ph.id === pid);
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
  document.getElementById(`tab-${tabId}`).classList.add('active');
  document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');

  if (tabId === 'movement') {
    setupObserver('.movement-section');
  }
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
    (p.context && localizeValue(p.context.text, p.context.textEn)) ||
    (p.expression && localizeValue(p.expression.text, p.expression.textEn)) ||
    '';
  document.getElementById('random-excerpt').textContent =
    excerptSrc.replace(/\*\d+/g, '').slice(0, 80) + '…';

  document.getElementById('random-box').dataset.pid = p.id;
}

function openRandomCoordinates(event) {
  event.stopPropagation();
  const pid = document.getElementById('random-box').dataset.pid;
  openCoordinatesForPhotographer(pid);
}

function scrollToPhotographer() {
  const pid = document.getElementById('random-box').dataset.pid;
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

  if (hash === 'tab-movement') {
    switchTab('movement');
    return;
  }

  if (hash.startsWith('photographer-')) {
    revealPhotographerFromHash(hash.slice('photographer-'.length));
    return;
  }

  if (hash.startsWith('movement-')) {
    revealMovementFromHash(hash.slice('movement-'.length));
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
window.addEventListener('hashchange', handleDeepLink);
