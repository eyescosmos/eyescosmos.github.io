(function () {
  const body = document.body;
  if (!body) return;

  const photographerId = body.dataset.photographerId;
  const lang = body.dataset.pageLang === 'en' ? 'en' : 'ja';
  if (!photographerId) return;

  const essayRegistry = window.PHOTOGRAPHER_ESSAY_OVERRIDES || {};
  const essayEntry = essayRegistry[photographerId] || null;
  const mobileNavDrawer = document.querySelector('.mobile-nav-drawer');
  const mobileNavContent = document.querySelector('.mobile-nav-content');
  const heroTopLinks = document.querySelector('.page-top-links, .hero > .top-links');

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

})();
