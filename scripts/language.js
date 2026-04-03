(function () {
  const STORAGE_KEY = 'photo-coordinates-language';
  const fixedLanguage = document.documentElement.dataset.fixedLang === 'true';

  function normalizeLanguage(value) {
    return value === 'en' ? 'en' : 'ja';
  }

  function getLanguage() {
    const documentLanguage = normalizeLanguage(document.documentElement.lang || 'ja');
    if (fixedLanguage) return documentLanguage;
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (stored) return normalizeLanguage(stored);
    } catch (error) {
      // Ignore storage failures and fall back to document state.
    }
    return documentLanguage;
  }

  function setLanguage(value) {
    const next = normalizeLanguage(value);
    document.documentElement.lang = next;
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch (error) {
      // Ignore storage failures.
    }
    return next;
  }

  function localizeText(jaText, enText, language) {
    const current = normalizeLanguage(language || getLanguage());
    if (current === 'en') return enText || jaText || '';
    return jaText || enText || '';
  }

  window.PhotoCoordinatesI18n = {
    getLanguage,
    setLanguage,
    localizeText,
    normalizeLanguage
  };
})();
