(function () {
  const body = document.body;
  if (!body) return;

  const photographerId = body.dataset.photographerId;
  const lang = body.dataset.pageLang === 'en' ? 'en' : 'ja';
  if (!photographerId) return;

  const copy = {
    ja: {
      fallbackButton: '写真集を Amazon で見る ↗',
      fallbackNote: '写真集は準備中です。',
      kicker: 'Available at',
      brand: 'Amazon',
      heroNote: '写真史の流れとあわせて読める写真集'
    },
    en: {
      fallbackButton: 'View on Amazon ↗',
      fallbackNote: 'Photobooks coming soon.',
      kicker: 'Available at',
      brand: 'Amazon',
      heroNote: 'Photobooks to read alongside this photographer'
    }
  };

  const locale = copy[lang];
  const registry = window.PHOTOGRAPHER_AFFILIATE_BOOKS || {};
  const essayRegistry = window.PHOTOGRAPHER_ESSAY_OVERRIDES || {};
  const entry = registry[photographerId] || {};
  const essayEntry = essayRegistry[photographerId] || null;
  const featured = entry.featured || {};
  const books = Array.isArray(entry.books) ? entry.books : [];

  const hero = document.querySelector('[data-amazon-hero]');
  const section = document.querySelector('[data-affiliate-section]');
  const list = document.querySelector('[data-affiliate-list]');
  const mobileNavDrawer = document.querySelector('.mobile-nav-drawer');
  const mobileNavContent = document.querySelector('.mobile-nav-content');
  const heroTopLinks = document.querySelector('.hero > .top-links');

  if (mobileNavDrawer && mobileNavContent && heroTopLinks) {
    const linksPlaceholder = document.createComment('mobile-top-links-placeholder');
    heroTopLinks.parentNode.insertBefore(linksPlaceholder, heroTopLinks);

    const mobileQuery = window.matchMedia('(max-width: 768px)');

    const syncMobileNav = () => {
      if (mobileQuery.matches) {
        if (heroTopLinks.parentNode !== mobileNavContent) {
          mobileNavContent.appendChild(heroTopLinks);
        }
      } else {
        if (linksPlaceholder.parentNode && heroTopLinks.parentNode !== linksPlaceholder.parentNode) {
          linksPlaceholder.parentNode.insertBefore(heroTopLinks, linksPlaceholder.nextSibling);
        }
        mobileNavDrawer.open = false;
      }
    };

    syncMobileNav();
    if (typeof mobileQuery.addEventListener === 'function') {
      mobileQuery.addEventListener('change', syncMobileNav);
    } else if (typeof mobileQuery.addListener === 'function') {
      mobileQuery.addListener(syncMobileNav);
    }
  }

  function resolveByLanguage(record, jaKey, enKey, fallbackKey) {
    if (!record || typeof record !== 'object') return '';
    if (lang === 'en') {
      return record[enKey] || record[jaKey] || record[fallbackKey] || '';
    }
    return record[jaKey] || record[enKey] || record[fallbackKey] || '';
  }

  function createAction(url, label, className) {
    const anchor = document.createElement('a');
    anchor.className = className;
    anchor.href = url;
    anchor.target = '_blank';
    anchor.rel = 'noopener sponsored';
    anchor.setAttribute('aria-label', label);

    const copyWrap = document.createElement('span');
    copyWrap.className = 'amazon-cta-copy';

    const kicker = document.createElement('span');
    kicker.className = 'amazon-cta-kicker';
    kicker.textContent = locale.kicker;

    const brand = document.createElement('span');
    brand.className = 'amazon-cta-brand';
    brand.innerHTML = `<span class="amazon-word">${locale.brand}</span> ↗`;

    copyWrap.appendChild(kicker);
    copyWrap.appendChild(brand);
    anchor.appendChild(copyWrap);
    return anchor;
  }

  function renderEssayRefs(text, citations) {
    return String(text || '')
      .replace(/[&<>"]/g, (char) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;'
      }[char]))
      .replace(/(\*\d+)/g, (match) => {
        const num = match.replace('*', '');
        const citation = (citations || []).find((item) => String(item.num) === num);
        if (!citation) return match;
        return `<sup class="sup-ref"><a href="#cite-${num}">*${num}</a></sup>`;
      });
  }

  function localizeEssayValue(record, jaKey, enKey) {
    if (!record) return '';
    return lang === 'en'
      ? (record[enKey] || record[jaKey] || '')
      : (record[jaKey] || record[enKey] || '');
  }

  function renderEssaySections(sections, citations) {
    return (sections || []).map((section) => {
      const heading = localizeEssayValue(section, 'headingJa', 'headingEn');
      const paragraphs = lang === 'en'
        ? (section.paragraphsEn || section.paragraphsJa || [])
        : (section.paragraphsJa || section.paragraphsEn || []);
      const body = paragraphs.map((paragraph) => `<p>${renderEssayRefs(paragraph, citations)}</p>`).join('');
      return `<h3>${heading}</h3>${body}`;
    }).join('');
  }

  function renderEssayFromPlainText(text, citations) {
    const headingSet = new Set([
      '経歴',
      '表現解説',
      '批評と受容',
      'Biography',
      'Expression / method',
      'Criticism and reception'
    ]);
    const blocks = String(text || '')
      .split(/\n\s*\n/)
      .map((block) => block.trim())
      .filter(Boolean);
    let html = '';
    let currentHeading = '';

    blocks.forEach((block) => {
      if (headingSet.has(block)) {
        currentHeading = block;
        html += `<h3>${block}</h3>`;
        return;
      }
      if (!currentHeading) return;
      html += `<p>${renderEssayRefs(block, citations)}</p>`;
    });

    return html;
  }

  function renderSourceList(citations) {
    return (citations || []).map((citation) => (
      `<div class="cite-item" id="cite-${citation.num}"><div class="cite-num">*${citation.num}</div><a href="${citation.url}" target="_blank" rel="noopener">${citation.name}</a></div>`
    )).join('');
  }

  function renderExternalLinks(links) {
    return (links || []).map((link) => (
      `<a class="chip-link" href="${link.url}" target="_blank" rel="noopener">${link.label} ↗</a>`
    )).join('');
  }

  if (essayEntry && lang === 'en') {
    const lead = document.querySelector('.lead');
    if (lead && essayEntry.leadEn) {
      lead.innerHTML = renderEssayRefs(essayEntry.leadEn, essayEntry.citations || []);
    }

    const essay = document.querySelector('.essay');
    if (essay) {
      if (Array.isArray(essayEntry.sections) && essayEntry.sections.length) {
        essay.innerHTML = renderEssaySections(essayEntry.sections, essayEntry.citations || []);
      } else if (essayEntry.textEn || essayEntry.textJa) {
        essay.innerHTML = renderEssayFromPlainText(localizeEssayValue(essayEntry, 'textJa', 'textEn'), essayEntry.citations || []);
      }
    }

    const links = document.querySelector('.links');
    if (links && Array.isArray(essayEntry.links) && essayEntry.links.length) {
      links.innerHTML = renderExternalLinks(essayEntry.links);
    }

    const sources = document.querySelector('.sources');
    if (sources && Array.isArray(essayEntry.citations) && essayEntry.citations.length) {
      sources.innerHTML = renderSourceList(essayEntry.citations);
    }
  }

  if (hero) {
    hero.textContent = '';
    const featuredRecord = lang === 'en' ? (featured.en || featured.ja || featured) : (featured.ja || featured.en || featured);
    const featuredUrl = featuredRecord && featuredRecord.url;
    if (featuredUrl) {
      const featuredLabel = featuredRecord.label || locale.fallbackButton;
      hero.appendChild(createAction(featuredUrl, featuredLabel, 'chip-link amazon-cta'));
      const note = document.createElement('div');
      note.className = 'amazon-note';
      note.textContent = locale.heroNote;
      hero.appendChild(note);
    }
  }

  if (!section || !list) return;

  const validBooks = books
    .map((book) => {
      const title = resolveByLanguage(book, 'titleJa', 'titleEn', 'title');
      const note = resolveByLanguage(book, 'noteJa', 'noteEn', 'note');
      const url = resolveByLanguage(book, 'urlJa', 'urlEn', 'url');
      const imageUrl = resolveByLanguage(book, 'imageUrlJa', 'imageUrlEn', 'imageUrl');
      const imageAlt = resolveByLanguage(book, 'imageAltJa', 'imageAltEn', 'imageAlt') || title;
      return { title, note, url, imageUrl, imageAlt };
    })
    .filter((book) => book.title && book.url)
    .slice(0, 3);

  if (!validBooks.length) {
    section.hidden = true;
    list.innerHTML = `<div class="note">${locale.fallbackNote}</div>`;
    return;
  }

  section.hidden = false;
  list.textContent = '';

  validBooks.forEach((book) => {
    const card = document.createElement('div');
    card.className = 'book-card';

    const media = document.createElement('div');
    media.className = 'book-media';

    if (book.imageUrl) {
      const image = document.createElement('img');
      image.className = 'book-thumb';
      image.src = book.imageUrl;
      image.alt = book.imageAlt;
      image.loading = 'lazy';
      media.appendChild(image);
    }

    const copy = document.createElement('div');
    copy.className = 'book-copy';

    const title = document.createElement('div');
    title.className = 'book-title';
    title.textContent = book.title;
    copy.appendChild(title);

    if (book.note) {
      const note = document.createElement('div');
      note.className = 'book-note';
      note.textContent = book.note;
      copy.appendChild(note);
    }

    media.appendChild(copy);
    card.appendChild(media);

    const actions = document.createElement('div');
    actions.className = 'book-actions';
    actions.appendChild(createAction(book.url, locale.fallbackButton, 'chip-link amazon-cta'));
    card.appendChild(actions);

    list.appendChild(card);
  });
})();
