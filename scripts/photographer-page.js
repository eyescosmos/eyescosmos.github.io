(function () {
  const body = document.body;
  if (!body) return;

  const photographerId = body.dataset.photographerId;
  const lang = body.dataset.pageLang === 'en' ? 'en' : 'ja';
  if (!photographerId) return;

  const copy = {
    ja: {
      fallbackButton: '写真集を Amazon で見る ↗',
      fallbackNote: '関連書籍は準備中です。'
    },
    en: {
      fallbackButton: 'View on Amazon ↗',
      fallbackNote: 'Related books coming soon.'
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
    anchor.textContent = label;
    return anchor;
  }

  if (hero) {
    hero.textContent = '';
    const featuredRecord = lang === 'en' ? (featured.en || featured.ja || featured) : (featured.ja || featured.en || featured);
    const featuredUrl = featuredRecord && featuredRecord.url;
    if (featuredUrl) {
      const featuredLabel = featuredRecord.label || locale.fallbackButton;
      hero.appendChild(createAction(featuredUrl, featuredLabel, 'chip-link'));
    }
  }

  if (!section || !list) return;

  const validBooks = books
    .map((book) => {
      const title = resolveByLanguage(book, 'titleJa', 'titleEn', 'title');
      const note = resolveByLanguage(book, 'noteJa', 'noteEn', 'note');
      const url = resolveByLanguage(book, 'urlJa', 'urlEn', 'url');
      return { title, note, url };
    })
    .filter((book) => book.title && book.url);

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

    const title = document.createElement('div');
    title.className = 'book-title';
    title.textContent = book.title;
    card.appendChild(title);

    if (book.note) {
      const note = document.createElement('div');
      note.className = 'book-note';
      note.textContent = book.note;
      card.appendChild(note);
    }

    const actions = document.createElement('div');
    actions.className = 'book-actions';
    actions.appendChild(createAction(book.url, locale.fallbackButton, 'chip-link'));
    card.appendChild(actions);

    list.appendChild(card);
  });
})();
