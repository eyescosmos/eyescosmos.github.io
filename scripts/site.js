/* UI behavior for the photography history site. */

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   STATE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
let activeFilters = { search: '', country: '', movement: '' };
const EMPTY_BLOCK = '<div class="empty-copy" aria-hidden="true"></div>';

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
  return `<div class="context-source">出典：${links}</div>`;
}

function renderEmptyPhotographerState() {
  return '<div class="empty-photographers">この時代の写真家はこれから追加予定です。</div>';
}

function displayName(p) {
  return p.nameJa || p.name || '追加予定';
}

function displaySubName(p) {
  if (!p.nameJa || !p.name) return '';
  return `<div class="card-name-sub">${p.name}</div>`;
}

function displayMeta(p) {
  return [p.flag, p.nationality].filter(Boolean).join(' ').trim();
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
  ].filter(Boolean).join(' '));
}

function setLocationHash(hashValue) {
  const next = hashValue ? `#${hashValue}` : '';
  if (window.location.hash === next) return;
  const url = new URL(window.location.href);
  url.hash = hashValue || '';
  history.replaceState(null, '', url.toString());
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
        <div class="era-title" style="margin:0">${era.title}</div>
        <div class="era-toggle-arrow">▼</div>
      </div>
      <div class="era-body">
        <div class="era-body-content">
            <div class="era-info">
              <div class="context-block">
                <div class="context-label">世界情勢</div>
                <div class="context-text">${renderOptionalText(era.worldEvents.text)}</div>
                ${renderSources(era.worldEvents.sources)}
              </div>
              <div class="context-block">
                <div class="context-label">写真と時代</div>
                <div class="context-text">${renderOptionalText(era.photoContext.text)}</div>
                ${renderSources(era.photoContext.sources)}
              </div>
            </div>
            <div class="photographers-label">この時代の写真家</div>
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
    ? p.movements.map(m => `<span class="card-tag">${m}</span>`).join('')
    : '';
  const searchIndex = buildSearchIndex(p);
  const coordinateButton = p.isPlaceholder
    ? ''
    : `<button class="coordinate-link" type="button" onclick="event.stopPropagation(); openCoordinatesForPhotographer('${p.id}')">座標で見る</button>`;
  return `
    <div class="photographer-card${p.isPlaceholder ? ' placeholder' : ''}" data-pid="${p.id}" data-nationality="${p.nationality}" data-movements="${p.movements.join(',')}" data-search="${searchIndex}" data-placeholder="${p.isPlaceholder ? 'true' : 'false'}" ${extraAttrs}>
      <div class="card-action">
        <div class="card-action-label">解説</div>
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

  const tags = p.movements.map(m => `<span class="detail-tag">${m}</span>`).join('');
  const linksHTML = p.links.map(l =>
    `<a class="detail-link" href="${l.url}" target="_blank" rel="noopener">${l.label} ↗</a>`
  ).join('');
  const amazonHTML = p.amazon
    ? `<a class="detail-link" href="${p.amazon}" target="_blank" rel="noopener sponsored">写真集を Amazon で見る ↗</a>`
    : `<div class="amazon-placeholder">${p.isPlaceholder ? '' : '写真集へのリンク（準備中）'}</div>`;

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
          <div class="detail-section-title">解説</div>
          <div class="detail-text">${EMPTY_BLOCK}</div>
        </div>
      </div>
    `;
  }

  /* ── 解説セクション：新旧フォーマット両対応 ── */
  let contextHTML;
  if (p.context && p.context.citations) {
    /* 新フォーマット：context.text に *1 *2 マーカー、context.citations に出典 */
    const ctxText = renderCiteText(p.context.text, p.context.citations);
    const citeListHTML = p.context.citations.map(c =>
      `<div class="cite-item"><span class="cite-num">*${c.num}</span><a href="${c.url}" target="_blank" rel="noopener">${c.name}</a></div>`
    ).join('');
    contextHTML = `
      <div class="detail-section">
        <div class="detail-section-title">解説</div>
        <div class="detail-text">${ctxText}</div>
        <div class="cite-list">${citeListHTML}</div>
      </div>`;
  } else {
    /* 旧フォーマット：expression.text + context.text を結合し、全出典を自動番号化 */
    const expText = (p.expression && p.expression.text) || '';
    const ctxText = (p.context && p.context.text) || '';
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
        <div class="detail-section-title">解説</div>
        <div class="detail-text">${combined}</div>
        ${citeListHTML ? `<div class="cite-list">${citeListHTML}</div>` : ''}
          </div>`;
  }

  const linksSection = linksHTML ? `
      <div class="detail-section">
        <div class="detail-section-title">外部リンク</div>
        <div class="detail-links">${linksHTML}</div>
      </div>` : '';

  const booksSection = amazonHTML ? `
      <div class="detail-section">
        <div class="detail-section-title">写真集</div>
        ${amazonHTML}
      </div>` : '';

  return `
    <div class="detail-panel" id="${panelId}">
      <div class="detail-header">
        <div>
          <div class="detail-name">${displayName(p)}${p.gender ? `<span style="font-size:12px;color:var(--text-muted);font-weight:normal;margin-left:10px;vertical-align:middle;letter-spacing:0.05em">${p.gender}</span>` : ''}${p.nameJa && p.name ? `<span style="display:block;font-family:'DM Mono',monospace;font-size:11px;color:var(--text-muted);font-weight:normal;margin-top:3px;letter-spacing:0.04em">${p.name}</span>` : ''}</div>
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
  countries.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c; opt.textContent = c;
    cSel.appendChild(opt);
  });

  const mSel = document.getElementById('filter-movement-era');
  movements.forEach(m => {
    const opt = document.createElement('option');
    opt.value = m; opt.textContent = m;
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
    countEl.textContent = `${visibleCount} / ${total}人`;
  } else {
    countEl.textContent = `${total}人`;
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
  document.getElementById('filter-count').textContent = `${realPhotographers().length}人`;
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
          <div class="movement-name">${mvName}<em class="movement-name-en">${meta.en}</em></div>
          <div class="movement-period">登録: ${photographers.length}名</div>
        </div>
        <div class="movement-toggle-arrow">▼</div>
      </div>
      <div class="movement-body">
        <div class="movement-body-content">
          <div class="context-block" style="margin-bottom:24px">
            <div class="context-label">概要</div>
            <div class="context-text">${meta.desc || EMPTY_BLOCK}</div>
          </div>
          <div class="photographers-label">この表現の写真家</div>
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

  document.getElementById('random-name').textContent = p.nameJa || p.name;
  document.getElementById('random-meta').textContent =
    `${p.flag} ${p.nationality}  /  ${p.years}  /  ${p.movements.join(' · ')}`;
  const excerptSrc = (p.context && p.context.text) || (p.expression && p.expression.text) || '';
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
renderEraTab();
renderMovementTab();
initRandom();
applyFilters(); // initialize count
handleDeepLink();
window.addEventListener('hashchange', handleDeepLink);
