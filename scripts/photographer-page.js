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
  const entry = registry[photographerId] || {};
  const featured = entry.featured || {};
  const books = Array.isArray(entry.books) ? entry.books : [];

  const hero = document.querySelector('[data-amazon-hero]');
  const section = document.querySelector('[data-affiliate-section]');
  const list = document.querySelector('[data-affiliate-list]');

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
