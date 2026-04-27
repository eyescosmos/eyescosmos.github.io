(function () {
  const SCRIPT_VERSION = '20260421b';
  const DATA_FILES = [
    'data/movements.js?v=20260403d',
    'data/eras.js?v=20260403c',
    'data/photographers.js?v=20260405j',
    'data/photographers-supplement.js?v=20260409c',
    'data/photographers-manual-additions.js?v=20260409c',
    'data/content-helpers.js?v=20260418e',
    'data/future/era-1990s.js?v=20260418d',
    'data/future/era-2000s.js?v=20260403c',
    'data/future/era-2010s.js?v=20260403c',
    'data/future/photographers-1990s.js?v=20260403c',
    'data/future/photographers-2000s.js?v=20260403c',
    'data/future/photographers-2010s.js?v=20260403c',
    'data/photographer-enrichments.js?v=20260406a',
    'data/photographer-essay-overrides.js?v=20260418d',
  ];
  const NON_PHOTOGRAPHER_IDS = new Set([
    'charles-wirgman',
    'fabian-marti',
    'gabriel-orozco',
  ]);
  const COUNTRY_META = {
    FR: { ja: 'フランス', en: 'France', slug: 'france', flag: '🇫🇷' },
    GB: { ja: 'イギリス', en: 'United Kingdom', slug: 'united-kingdom', flag: '🇬🇧' },
    US: { ja: 'アメリカ', en: 'United States', slug: 'united-states', flag: '🇺🇸' },
    JP: { ja: '日本', en: 'Japan', slug: 'japan', flag: '🇯🇵' },
    DE: { ja: 'ドイツ', en: 'Germany', slug: 'germany', flag: '🇩🇪' },
    BR: { ja: 'ブラジル', en: 'Brazil', slug: 'brazil', flag: '🇧🇷' },
    CA: { ja: 'カナダ', en: 'Canada', slug: 'canada', flag: '🇨🇦' },
    CH: { ja: 'スイス', en: 'Switzerland', slug: 'switzerland', flag: '🇨🇭' },
    HU: { ja: 'ハンガリー', en: 'Hungary', slug: 'hungary', flag: '🇭🇺' },
    RU: { ja: 'ロシア', en: 'Russia', slug: 'russia', flag: '🇷🇺' },
    'IT / GB': { ja: 'イタリア / イギリス', en: 'Italy / United Kingdom', slug: 'italy-united-kingdom', flag: '🇮🇹 🇬🇧' },
    'GB / US': { ja: 'イギリス / アメリカ', en: 'United Kingdom / United States', slug: 'united-kingdom-united-states', flag: '🇬🇧 🇺🇸' },
    'DK / US': { ja: 'デンマーク / アメリカ', en: 'Denmark / United States', slug: 'denmark-united-states', flag: '🇩🇰 🇺🇸' },
    'LU / US': { ja: 'ルクセンブルク / アメリカ', en: 'Luxembourg / United States', slug: 'luxembourg-united-states', flag: '🇱🇺 🇺🇸' },
    'US / GB': { ja: 'アメリカ / イギリス', en: 'United States / United Kingdom', slug: 'united-states-united-kingdom', flag: '🇺🇸 🇬🇧' },
    'US / FR': { ja: 'アメリカ / フランス', en: 'United States / France', slug: 'united-states-france', flag: '🇺🇸 🇫🇷' },
    'HU / DE': { ja: 'ハンガリー / ドイツ', en: 'Hungary / Germany', slug: 'hungary-germany', flag: '🇭🇺 🇩🇪' },
  };
  const READING_OVERRIDES = {
    domon: 'どもんけん',
    araki: 'あらきのぶよし',
    tomatsu: 'とまつしょうめい',
    moriyama: 'もりやまだいどう',
    'takeji-iwamiya': 'いわみやたけじ',
    'jp-横山松三郎': 'よこやままつさぶろう',
    'jp-冨重利平': 'とみしげりへい',
    'jp-冨重徳次': 'とみしげとくじ',
    'jp-鹿島清兵衛': 'かしませいべえ',
    'jp-亀井茲明': 'かめいこれあき',
    'jp-屋須弘平': 'やすこうへい',
    'jp-鳥居龍蔵': 'とりいりゅうぞう',
    'jp-福原信三': 'ふくはらしんぞう',
    'jp-野島康三': 'のじまやすぞう',
    'jp-中山岩太': 'なかやまいわた',
    'jp-安井仲治': 'やすいなかじ',
    'jp-植田正治': 'うえだしょうじ',
    'jp-金丸重嶺': 'かなまるしげね',
    'jp-鈴木八郎': 'すずきはちろう',
    'jp-長谷川伝次郎': 'はせがわでんじろう',
    'jp-影山光洋': 'かげやまこうよう',
    'takeyoshi-tanuma': 'たぬまたけよし',
    'hideo-haga': 'はがひでお',
    'eikoh-hosoe': 'ほそええいこう',
    'kishin-shinoyama': 'しのやまきしん',
    'takuma-nakahira': 'なかひらたくま',
    'hiroshi-sugimoto': 'すぎもとひろし',
    'issei-suda': 'すだいっせい',
    'kazuyoshi-nomachi': 'のまちかずよし',
    'mitsuaki-iwago': 'いわごうみつあき',
    'miyako-ishiuchi': 'いしうちみやこ',
    'yoshino-oishi': 'おおいしよしの',
    'keizo-kitajima': 'きたじまけいぞう',
    'hiromi-tsuchida': 'つちだひろみ',
    'yasumasa-morimura': 'もりむらやすまさ',
    'rinko-kawauchi': 'かわうちりんこ',
    'takashi-yasumura': 'やすむらたかし',
    'naoya-hatakeyama': 'はたけやまなおや',
    'jikei-sato': 'さとうじけい',
    'norihiko-matsumoto': 'まつもとのりひこ',
    'yurie-nagashima': 'ながしまゆりえ',
    'mika-ninagawa': 'にながわみか',
    'taiji-matsue': 'まつえたいじ',
    'lieko-shiga': 'しがりえこ',
    'noriko-hayashi': 'はやしのりこ',
    'daisuke-yokota': 'よこただいすけ',
  };
  const SUGGESTIONS_JA = ['アメリカ写真', 'ピクトリアリズム', '1890'];
  const SUGGESTIONS_EN = ['American Photography', 'Pictorialism', '1890'];
  const BASE_URL = (() => {
    const src = document.currentScript?.src || '';
    if (src) return src.replace(/scripts\/global-search\.js(?:\?.*)?$/, '');
    return location.pathname.includes('/en/') || /\/(photographers|countries|movements|eras)\//.test(location.pathname) ? '../' : './';
  })();

  let items = [];
  let dataReady = false;
  let activeRoot = null;

  function currentLanguage() {
    const htmlLang = document.documentElement.lang || '';
    return htmlLang.toLowerCase().startsWith('en') || location.pathname.includes('/en/') ? 'en' : 'ja';
  }

  function rootUrl() {
    return BASE_URL;
  }

  function asciiSlug(value) {
    return String(value || '')
      .normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .replace(/&/g, ' and ')
      .replace(/\+/g, ' plus ')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '') || 'movement';
  }

  function movementSlug(name, label, lang) {
    if (lang === 'en') return asciiSlug(label || name);
    return String(name || '').replace(/[^A-Za-z\u3000-\u9fff]/g, '');
  }

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      if (document.querySelector(`script[data-global-search-src="${src}"]`)) {
        resolve();
        return;
      }
      const script = document.createElement('script');
      script.src = rootUrl() + src;
      script.dataset.globalSearchSrc = src;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  async function ensureData() {
    if (dataReady) return;
    if (typeof PHOTOGRAPHERS === 'undefined' || typeof MOVEMENTS_META === 'undefined' || typeof ERAS === 'undefined') {
      for (const file of DATA_FILES) {
        const needsFile = file.includes('photographers-supplement') || file.includes('photographers-manual') || file.includes('/future/') || file.includes('photographer-');
        if (!needsFile && file.includes('movements') && typeof MOVEMENTS_META !== 'undefined') continue;
        if (!needsFile && file.includes('eras.js') && typeof ERAS !== 'undefined') continue;
        if (!needsFile && file.includes('photographers.js') && typeof PHOTOGRAPHERS !== 'undefined') continue;
        try {
          await loadScript(file);
        } catch (error) {
          console.warn('[global-search] failed to load', file, error);
        }
      }
    }
    items = buildItems();
    dataReady = true;
  }

  function katakanaToHiragana(value) {
    return String(value || '').replace(/[\u30a1-\u30f6]/g, (char) => String.fromCharCode(char.charCodeAt(0) - 0x60));
  }

  function normalize(value) {
    return katakanaToHiragana(String(value || '')
      .normalize('NFKC')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, ''))
      .replace(/[・･\s\u3000|｜/／\\()[\]{}「」『』.,，、。:：;；'’"“”\-‐‑‒–—―=＝+＋_＿]/g, '');
  }

  function movementLabel(name, lang = currentLanguage()) {
    const meta = typeof MOVEMENTS_META !== 'undefined' ? MOVEMENTS_META[name] : null;
    return lang === 'en' ? (meta?.en || name) : name;
  }

  function eraLabel(era, lang = currentLanguage()) {
    if (!era) return '';
    const period = String(era.period || era.id || '').replace(/\s*—\s*/g, '–');
    const title = lang === 'en' ? (era.titleEn || era.title || '') : (era.title || era.titleEn || '');
    return title ? `${period} ${title}` : period;
  }

  function countryMeta(code) {
    return COUNTRY_META[code] || { ja: code || '', en: code || '', slug: '', flag: '' };
  }

  function photographerCountry(photographer, lang = currentLanguage()) {
    const enrichment = typeof PHOTOGRAPHER_ENRICHMENTS !== 'undefined'
      ? (PHOTOGRAPHER_ENRICHMENTS[photographer.id] || {})
      : {};
    const code = enrichment.countryCode || enrichment.nationality || photographer.nationality || '';
    const meta = countryMeta(code);
    return {
      code,
      label: lang === 'en' ? (meta.en || code) : (meta.ja || code),
      flag: enrichment.flag || photographer.flag || meta.flag || '',
      slug: meta.slug || '',
    };
  }

  function photographerReading(photographer) {
    if (READING_OVERRIDES[photographer.id]) return READING_OVERRIDES[photographer.id];
    const name = photographer.nameJa || photographer.name || '';
    return normalize(name);
  }

  function stripRefs(text) {
    return String(text || '').replace(/\*\d+/g, '').replace(/\s+/g, ' ').trim();
  }

  function shortLead(photographer, lang = currentLanguage()) {
    const overrides = typeof window.PHOTOGRAPHER_ESSAY_OVERRIDES !== 'undefined' ? window.PHOTOGRAPHER_ESSAY_OVERRIDES : {};
    const override = overrides[photographer.id] || {};
    const context = photographer.context || {};
    const text = lang === 'en'
      ? (override.leadEn || context.textEn || override.leadJa || context.text || '')
      : (override.leadJa || context.text || override.leadEn || context.textEn || '');
    const clean = stripRefs(text);
    if (!clean) {
      const movements = (photographer.movements || []).map((movement) => movementLabel(movement, lang)).filter(Boolean).slice(0, 2).join(lang === 'en' ? ', ' : '、');
      return lang === 'en'
        ? `A photographer connected to ${movements || 'photography history'}.`
        : `${movements || '写真史'}に関わる写真家です。`;
    }
    return clean.length > 120 ? clean.slice(0, 118).replace(/[、,.\s]+$/g, '') + '…' : clean;
  }

  function buildItems() {
    const lang = currentLanguage();
    const photographers = (typeof PHOTOGRAPHERS !== 'undefined' ? PHOTOGRAPHERS : [])
      .filter((photographer) => photographer && !photographer.isPlaceholder && !NON_PHOTOGRAPHER_IDS.has(photographer.id))
      .map((photographer) => {
        const country = photographerCountry(photographer, lang);
        const era = (typeof ERAS !== 'undefined' ? ERAS : []).find((entry) => entry.id === photographer.era);
        const movementLabels = (photographer.movements || []).map((movement) => movementLabel(movement, lang));
        const name = lang === 'en' ? (photographer.name || photographer.nameJa || '') : (photographer.nameJa || photographer.name || '');
        const alt = lang === 'en' ? (photographer.nameJa || '') : (photographer.name || '');
        const reading = photographerReading(photographer);
        const searchParts = [
          name,
          alt,
          reading,
          photographer.id,
          photographer.years,
          photographer.era,
          eraLabel(era, lang),
          country.code,
          country.label,
          ...movementLabels,
          ...(photographer.movements || []),
        ];
        return {
          type: 'photographer',
          id: photographer.id,
          title: name,
          alt,
          url: `${rootUrl()}${lang === 'en' ? 'en/' : ''}photographers/${photographer.id}.html`,
          meta: [country.flag, country.code, photographer.years].filter(Boolean).join(' / '),
          tags: movementLabels.slice(0, 3),
          text: shortLead(photographer, lang),
          searchText: normalize(searchParts.join(' ')),
          nameText: normalize(`${name} ${alt}`),
          kanaText: normalize(reading),
          movementText: normalize([...movementLabels, ...(photographer.movements || [])].join(' ')),
          countryText: normalize(`${country.code} ${country.label}`),
          yearText: normalize(`${photographer.years || ''} ${photographer.era || ''} ${eraLabel(era, lang)}`),
        };
      });

    const movements = Object.entries(typeof MOVEMENTS_META !== 'undefined' ? MOVEMENTS_META : {}).map(([name, meta]) => {
      const label = lang === 'en' ? (meta.en || name) : name;
      const related = photographers.filter((item) => item.movementText.includes(normalize(label)) || item.movementText.includes(normalize(name)));
      return {
        type: 'movement',
        id: name,
        title: label,
        alt: lang === 'en' ? name : (meta.en || ''),
        url: `${rootUrl()}${lang === 'en' ? 'en/' : ''}movements/${movementSlug(name, label, lang)}.html`,
        meta: lang === 'en' ? 'Movement' : '表現',
        tags: related.slice(0, 3).map((item) => item.title),
        text: lang === 'en' ? (meta.descEn || meta.desc || '') : (meta.desc || meta.descEn || ''),
        searchText: normalize([label, name, meta.en, meta.desc, meta.descEn, ...related.map((item) => item.title)].join(' ')),
        nameText: normalize(`${label} ${name} ${meta.en || ''}`),
        movementText: normalize(`${label} ${name} ${meta.en || ''}`),
        countryText: '',
        yearText: '',
      };
    });

    const eras = (typeof ERAS !== 'undefined' ? ERAS : []).map((era) => ({
      type: 'era',
      id: era.id,
      title: String(era.period || era.id || '').replace(/\s*—\s*/g, '–'),
      alt: lang === 'en' ? (era.titleEn || era.title || '') : (era.title || era.titleEn || ''),
      url: `${rootUrl()}${lang === 'en' ? 'en/' : ''}eras/${era.id}.html`,
      meta: lang === 'en' ? 'Era' : '年代',
      tags: [],
      text: lang === 'en'
        ? ((era.worldEvents || {}).textEn || (era.photoContext || {}).textEn || '')
        : ((era.worldEvents || {}).text || (era.photoContext || {}).text || ''),
      searchText: normalize([era.id, era.period, era.title, era.titleEn].join(' ')),
      nameText: normalize([era.id, era.period, era.title, era.titleEn].join(' ')),
      movementText: '',
      countryText: '',
      yearText: normalize([era.id, era.period].join(' ')),
    }));

    const countryCounts = new Map();
    photographers.forEach((item) => {
      const parts = item.meta.split(' / ');
      const code = parts.find((part) => COUNTRY_META[part]);
      if (code) countryCounts.set(code, (countryCounts.get(code) || 0) + 1);
    });
    const countries = Object.entries(COUNTRY_META).map(([code, meta]) => {
      const label = lang === 'en' ? meta.en : meta.ja;
      return {
        type: 'country',
        id: code,
        title: label,
        alt: code,
        url: `${rootUrl()}${lang === 'en' ? 'en/' : ''}countries/${meta.slug}.html`,
        meta: lang === 'en' ? 'Country' : '国',
        tags: countryCounts.get(code) ? [String(countryCounts.get(code))] : [],
        text: lang === 'en' ? `Photographers connected to ${label}.` : `${label}に関わる写真家をたどります。`,
        searchText: normalize(`${code} ${label} ${meta.en} ${meta.ja}`),
        nameText: normalize(`${code} ${label} ${meta.en} ${meta.ja}`),
        movementText: '',
        countryText: normalize(`${code} ${label} ${meta.en} ${meta.ja}`),
        yearText: '',
      };
    });

    return [...photographers, ...movements, ...eras, ...countries];
  }

  function scoreItem(item, queryRaw) {
    const query = normalize(queryRaw);
    if (!query) return 0;
    const isSingleChar = query.length === 1;
    let score = 0;
    if (item.nameText === query || item.searchText === query) score += 1200;
    if (item.kanaText && item.kanaText.startsWith(query)) score += 1050;
    if (item.nameText.startsWith(query)) score += 1000;
    if (item.type === 'movement' && item.nameText.startsWith(query)) score += isSingleChar ? 760 : 980;
    if (item.type === 'era' && item.yearText.startsWith(query)) score += 960;
    if (item.nameText.includes(query)) score += 850;
    if (item.type === 'movement' && item.nameText.includes(query)) score += isSingleChar ? 560 : 820;
    if (item.movementText && item.movementText.includes(query)) score += item.type === 'photographer' ? 680 : 760;
    if (item.countryText && item.countryText.includes(query)) score += 520;
    if (item.yearText && item.yearText.includes(query)) score += item.type === 'era' ? 700 : 420;
    if (item.searchText.includes(query)) score += 260;
    if (query.length === 1 && score > 0) score += item.nameText.startsWith(query) || (item.kanaText && item.kanaText.startsWith(query)) ? 120 : 0;
    if (item.type === 'movement') score += 24;
    if (item.type === 'photographer') score += 16;
    return score;
  }

  function searchItems(query) {
    const normalized = normalize(query);
    if (!normalized) return [];
    return items
      .map((item) => ({ item, score: scoreItem(item, query) }))
      .filter((entry) => entry.score > 0)
      .sort((a, b) => b.score - a.score || a.item.title.localeCompare(b.item.title, 'ja'))
      .slice(0, 36)
      .map((entry) => entry.item);
  }

  function injectStyles() {
    if (document.getElementById('global-search-style')) return;
    const style = document.createElement('style');
    style.id = 'global-search-style';
    style.textContent = `
      .global-search-nav {
        position: relative;
        min-width: 168px;
        width: clamp(168px, 17vw, 230px);
        flex: 0 1 clamp(168px, 17vw, 230px);
        margin-left: 12px;
      }
      .global-search-field-wrap {
        position: relative;
        display: flex;
        align-items: center;
      }
      .global-search-input {
        width: 100%;
        min-height: 34px;
        padding: 8px 34px 8px 12px;
        border: 1px solid var(--border, rgba(198, 170, 130, 0.18));
        background: rgba(10, 12, 18, 0.68);
        color: var(--text, #eee6d8);
        font: 400 11px/1.2 'DM Mono', 'Noto Sans JP', monospace;
        letter-spacing: 0.08em;
        border-radius: 0;
        outline: none;
      }
      .global-search-input::placeholder {
        color: var(--text-muted, rgba(238, 230, 216, 0.42));
      }
      .global-search-icon {
        position: absolute;
        right: 12px;
        width: 15px;
        height: 15px;
        border: 1px solid currentColor;
        border-radius: 50%;
        color: var(--text-muted, rgba(238, 230, 216, 0.42));
        pointer-events: none;
      }
      .global-search-icon::after {
        content: '';
        position: absolute;
        width: 6px;
        height: 1px;
        right: -4px;
        bottom: -2px;
        background: currentColor;
        transform: rotate(45deg);
        transform-origin: left center;
      }
      .global-search-panel {
        position: fixed;
        z-index: 140;
        width: auto;
        max-height: min(78vh, 720px);
        overflow-y: auto;
        overscroll-behavior: contain;
        border: 1px solid var(--border, rgba(198, 170, 130, 0.18));
        background: rgba(5, 6, 8, 0.94);
        color: var(--text, #eee6d8);
        box-shadow: 0 22px 58px rgba(0,0,0,0.38);
        backdrop-filter: blur(18px);
      }
      .global-search-panel[hidden] {
        display: none;
      }
      .global-search-inner {
        display: grid;
        gap: 10px;
        padding: 12px;
      }
      .global-search-panel-header {
        position: sticky;
        top: -12px;
        z-index: 3;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        margin: -12px -12px 0;
        padding: 12px;
        border-bottom: 1px solid rgba(198, 170, 130, 0.12);
        background: rgba(5, 6, 8, 0.96);
        backdrop-filter: blur(18px);
      }
      .global-search-hint {
        color: var(--text-muted, rgba(238, 230, 216, 0.42));
        font: 400 10px/1.5 'DM Mono', 'Noto Sans JP', monospace;
        letter-spacing: 0.08em;
      }
      .global-search-close {
        flex: 0 0 auto;
        width: 26px;
        height: 26px;
        border: 1px solid rgba(198, 170, 130, 0.18);
        border-radius: 999px;
        background: rgba(255,255,255,0.02);
        color: var(--text-muted, rgba(238, 230, 216, 0.52));
        font: 400 16px/1 'DM Mono', monospace;
        cursor: pointer;
      }
      .global-search-close:hover {
        border-color: rgba(198, 170, 130, 0.35);
        color: var(--accent, #c6aa82);
      }
      .global-search-suggestions {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
      }
      .global-search-chip {
        border: 1px solid rgba(198, 170, 130, 0.18);
        background: rgba(198, 170, 130, 0.06);
        color: var(--accent, #c6aa82);
        font: 400 10px/1 'DM Mono', 'Noto Sans JP', monospace;
        letter-spacing: 0.08em;
        padding: 8px 9px;
        cursor: pointer;
      }
      .global-search-results {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 8px;
      }
      .global-search-card {
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 5px;
        padding: 12px 12px 11px;
        border: 1px solid rgba(198, 170, 130, 0.12);
        background: rgba(255,255,255,0.018);
        text-decoration: none;
        color: inherit;
        min-width: 0;
        writing-mode: horizontal-tb !important;
        text-orientation: mixed !important;
      }
      .global-search-card:hover {
        border-color: rgba(198, 170, 130, 0.32);
        background: rgba(198, 170, 130, 0.07);
      }
      .global-search-card-top {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between;
        gap: 12px;
        align-items: baseline;
        width: 100%;
        min-width: 0;
        writing-mode: horizontal-tb !important;
      }
      .global-search-title {
        color: var(--text, #eee6d8);
        font: 700 14px/1.35 'Noto Sans JP', sans-serif;
        letter-spacing: 0.03em;
        min-width: 0;
        flex: 1 1 auto;
        word-break: normal;
        overflow-wrap: break-word;
        white-space: normal;
        writing-mode: horizontal-tb !important;
      }
      .global-search-kind {
        flex: 0 0 auto;
        color: var(--accent, #c6aa82);
        font: 400 10px/1 'DM Mono', monospace;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        white-space: nowrap;
        writing-mode: horizontal-tb !important;
      }
      .global-search-meta,
      .global-search-text,
      .global-search-tags {
        color: var(--text-muted, rgba(238, 230, 216, 0.52));
        font: 400 11px/1.55 'DM Mono', 'Noto Sans JP', monospace;
        letter-spacing: 0.04em;
        min-width: 0;
        width: 100%;
        word-break: normal;
        overflow-wrap: break-word;
        white-space: normal;
        writing-mode: horizontal-tb !important;
      }
      .global-search-tags {
        color: var(--accent, #c6aa82);
      }
      .global-search-mobile-button {
        display: none;
      }
      body.global-search-ready .filter-bar {
        display: none;
      }
      body.global-search-desktop-open,
      body.global-search-open {
        overflow: hidden;
      }
      @media (min-width: 769px) and (max-width: 1280px) {
        .global-search-nav {
          min-width: 142px;
          width: clamp(142px, 13vw, 176px);
          flex-basis: clamp(142px, 13vw, 176px);
        }
        .global-search-input {
          font-size: 10px;
          letter-spacing: 0.05em;
        }
        .global-search-results {
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }
      }
      @media (min-width: 769px) and (max-width: 920px) {
        .global-search-results {
          grid-template-columns: 1fr;
        }
      }
      @media (max-width: 768px) {
        .global-search-nav {
          display: none;
        }
        .global-search-mobile-button {
          display: flex;
          align-items: center;
          justify-content: center;
          position: fixed;
          right: 16px;
          bottom: calc(18px + env(safe-area-inset-bottom));
          z-index: 920;
          width: 42px;
          height: 42px;
          border: 1px solid var(--border, rgba(198, 170, 130, 0.18));
          border-radius: 999px;
          background: rgba(10, 12, 18, 0.58);
          color: var(--accent, #c6aa82);
          backdrop-filter: blur(14px);
          cursor: pointer;
        }
        .global-search-mobile-button .global-search-lens {
          position: relative;
          width: 16px;
          height: 16px;
          border: 1.3px solid currentColor;
          border-radius: 50%;
        }
        .global-search-mobile-button .global-search-lens::after {
          content: '';
          position: absolute;
          width: 7px;
          height: 1.3px;
          right: -5px;
          bottom: -3px;
          background: currentColor;
          transform: rotate(45deg);
          transform-origin: left center;
        }
        .global-search-mobile-button.global-search-top-button {
          position: absolute;
          top: calc(100% + 8px);
          right: 0;
          width: 40px;
          height: 40px;
          margin-left: auto;
          background: rgba(10, 12, 18, 0.44);
        }
        .global-search-mobile-shell {
          position: fixed;
          left: 16px;
          right: 16px;
          top: calc(76px + env(safe-area-inset-top));
          z-index: 1000;
          display: none;
          gap: 8px;
        }
        body.global-search-open .global-search-mobile-shell {
          display: grid;
        }
        .global-search-mobile-shell .global-search-input {
          min-height: 44px;
          font-size: 16px;
          line-height: 1.25;
          letter-spacing: 0.02em;
          background: rgba(5, 6, 8, 0.92);
        }
        .global-search-panel {
          left: 16px !important;
          right: 16px !important;
          top: calc(128px + env(safe-area-inset-top)) !important;
          bottom: calc(16px + env(safe-area-inset-bottom));
          z-index: 1001;
          width: auto;
          max-height: none;
          overscroll-behavior: contain;
          -webkit-overflow-scrolling: touch;
        }
        .global-search-inner {
          padding: 10px;
        }
        .global-search-panel-header {
          top: -10px;
          margin: -10px -10px 0;
          padding: 10px;
        }
        .global-search-results {
          grid-template-columns: 1fr;
          gap: 1px;
        }
        .global-search-card {
          padding: 11px 12px 10px;
        }
        .global-search-title {
          font-size: 15px;
          line-height: 1.35;
        }
        .global-search-text {
          max-height: 4.8em;
          overflow: hidden;
        }
      }
    `;
    document.head.appendChild(style);
  }

  function itemKindLabel(type) {
    const lang = currentLanguage();
    const labels = {
      photographer: { ja: '写真家', en: 'Photographer' },
      movement: { ja: '表現', en: 'Movement' },
      era: { ja: '年代', en: 'Era' },
      country: { ja: '国', en: 'Country' },
    };
    return labels[type]?.[lang] || type;
  }

  function renderCard(item) {
    const tags = (item.tags || []).filter(Boolean).slice(0, 3).join(' / ');
    return `
      <a class="global-search-card global-search-card-${item.type}" href="${item.url}">
        <div class="global-search-card-top">
          <div class="global-search-title">${escapeHtml(item.title)}</div>
          <div class="global-search-kind">${escapeHtml(itemKindLabel(item.type))}</div>
        </div>
        ${item.alt ? `<div class="global-search-meta">${escapeHtml(item.alt)}</div>` : ''}
        ${item.meta ? `<div class="global-search-meta">${escapeHtml(item.meta)}</div>` : ''}
        ${tags ? `<div class="global-search-tags">${escapeHtml(tags)}</div>` : ''}
        ${item.text ? `<div class="global-search-text">${escapeHtml(item.text)}</div>` : ''}
      </a>
    `;
  }

  function escapeHtml(value) {
    return String(value || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function renderPanel(root, query = '') {
    const panel = root.querySelector('.global-search-panel');
    if (!panel) return;
    const lang = currentLanguage();
    const results = searchItems(query);
    const suggestions = lang === 'en' ? SUGGESTIONS_EN : SUGGESTIONS_JA;
    const showSuggestions = !normalize(query);
    panel.innerHTML = `
      <div class="global-search-inner">
        <div class="global-search-panel-header">
          <div class="global-search-hint">${lang === 'en' ? 'Search photographers, countries, movements, and eras.' : '写真家名・国・運動・年代で検索できます。'}</div>
          <button class="global-search-close" type="button" aria-label="${lang === 'en' ? 'Close search' : '検索を閉じる'}">×</button>
        </div>
        ${showSuggestions ? `<div class="global-search-suggestions">${suggestions.map((label) => `<button class="global-search-chip" type="button" data-global-search-suggestion="${escapeHtml(label)}">${escapeHtml(label)}</button>`).join('')}</div>` : ''}
        <div class="global-search-results">
          ${results.length ? results.map(renderCard).join('') : `<div class="global-search-hint">${lang === 'en' ? 'No matching results.' : '一致する候補がありません。'}</div>`}
        </div>
      </div>
    `;
    panel.hidden = false;
  }

  function positionDesktopPanel(root) {
    const panel = root.querySelector('.global-search-panel');
    const input = root.querySelector('.global-search-input');
    if (!panel || !input || window.innerWidth <= 768) return;
    const rect = input.getBoundingClientRect();
    const nav = root.closest('.tab-nav') || document.querySelector('.tab-nav');
    const navBottom = nav ? nav.getBoundingClientRect().bottom : rect.bottom;
    const top = Math.max(8, Math.round(navBottom + 8));
    panel.style.top = `${top}px`;
    panel.style.left = '16px';
    panel.style.right = '16px';
    panel.style.maxHeight = `${Math.max(240, window.innerHeight - top - 16)}px`;
  }

  function bindRoot(root) {
    const input = root.querySelector('.global-search-input');
    const panel = root.querySelector('.global-search-panel');
    if (!input || !panel) return;
    const open = async () => {
      activeRoot = root;
      await ensureData();
      renderPanel(root, input.value);
      positionDesktopPanel(root);
      if (window.innerWidth > 768) {
        document.body.classList.add('global-search-desktop-open');
      }
    };
    input.addEventListener('focus', open);
    input.addEventListener('input', open);
    panel.addEventListener('click', (event) => {
      if (event.target.closest('.global-search-close')) {
        closeSearch();
        return;
      }
      const suggestion = event.target.closest('[data-global-search-suggestion]');
      if (!suggestion) return;
      input.value = suggestion.dataset.globalSearchSuggestion || '';
      input.focus();
      renderPanel(root, input.value);
      positionDesktopPanel(root);
    });
    window.addEventListener('resize', () => {
      if (window.innerWidth <= 768) {
        document.body.classList.remove('global-search-desktop-open');
      }
      positionDesktopPanel(root);
    });
  }

  function createSearchRoot({ mobileOnly = false } = {}) {
    const root = document.createElement('div');
    root.className = mobileOnly ? 'global-search-mobile-shell' : 'global-search-nav';
    root.innerHTML = `
      <div class="global-search-field-wrap">
        <input class="global-search-input" type="search" placeholder="${currentLanguage() === 'en' ? 'Search photographers, countries, movements' : '写真家名・国・運動で検索'}" autocomplete="off">
        <span class="global-search-icon" aria-hidden="true"></span>
      </div>
      <div class="global-search-panel" hidden></div>
    `;
    bindRoot(root);
    return root;
  }

  function createMobileButton(isTop = false) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `global-search-mobile-button${isTop ? ' global-search-top-button' : ''}`;
    button.setAttribute('aria-label', currentLanguage() === 'en' ? 'Open search' : '検索を開く');
    button.innerHTML = '<span class="global-search-lens" aria-hidden="true"></span>';
    button.addEventListener('click', async () => {
      document.body.classList.toggle('global-search-open');
      const shell = document.querySelector('.global-search-mobile-shell');
      const input = shell?.querySelector('.global-search-input');
      if (document.body.classList.contains('global-search-open') && input) {
        await ensureData();
        input.focus();
        renderPanel(shell, input.value);
      }
    });
    return button;
  }

  function closeSearch() {
    document.body.classList.remove('global-search-open');
    document.body.classList.remove('global-search-desktop-open');
    document.querySelectorAll('.global-search-panel').forEach((panel) => {
      panel.hidden = true;
    });
  }

  function initMobileNavLayout() {
    const hero = document.querySelector('.page-shell > .hero');
    if (!hero) return;
    const mq = window.matchMedia('(max-width: 768px)');
    function doLayout() {
      const nav = document.querySelector('.tab-nav');
      const title = hero.querySelector('.title');
      if (!nav || !title) return;
      if (mq.matches) {
        if (nav.parentNode !== hero) title.after(nav);
      } else {
        if (nav.parentNode === hero) hero.after(nav);
      }
    }
    doLayout();
    mq.addEventListener('change', doLayout);
  }

  function install() {
    injectStyles();
    document.body.classList.add('global-search-ready');
    const isTopPage = /\/(?:index\.html)?$/.test(location.pathname) || /\/en\/(?:index\.html)?$/.test(location.pathname);
    const navInner = document.querySelector('.tab-nav .tab-nav-inner');
    if (navInner && !navInner.querySelector('.global-search-nav')) {
      const root = createSearchRoot();
      const langToggle = navInner.querySelector('.lang-toggle');
      const nestedControlRow = langToggle?.closest('.tab-nav-mobile-grid');
      if (nestedControlRow && navInner.contains(nestedControlRow)) {
        nestedControlRow.insertBefore(root, langToggle);
      } else {
        const directAnchor = langToggle
          ? Array.from(navInner.children).find((child) => child === langToggle || child.contains(langToggle))
          : null;
        navInner.insertBefore(root, directAnchor || null);
      }
    }
    if (!document.querySelector('.global-search-mobile-shell')) {
      document.body.appendChild(createSearchRoot({ mobileOnly: true }));
    }
    if (!document.querySelector('.global-search-mobile-button')) {
      if (isTopPage) {
        const pageLinks = document.querySelector('.page-links');
        if (pageLinks) pageLinks.appendChild(createMobileButton(true));
      } else {
        document.body.appendChild(createMobileButton(false));
      }
    }
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeSearch();
    });
    document.addEventListener('click', (event) => {
      if (!activeRoot) return;
      if (event.target.closest('.global-search-nav, .global-search-mobile-shell, .global-search-mobile-button')) return;
      if (window.innerWidth > 768) closeSearch();
    });
    initMobileNavLayout();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', install);
  } else {
    install();
  }
  window.globalPhotoSearch = { normalize, searchItems, ensureData, version: SCRIPT_VERSION };
})();
