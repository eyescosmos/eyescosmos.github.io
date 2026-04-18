(function () {
  function closeAllEraContext() {
    document.querySelectorAll('.hero.is-context-open').forEach(hero => {
      hero.classList.remove('is-context-open');
      const trigger = hero.querySelector('[data-era-context-toggle]');
      if (trigger) trigger.setAttribute('aria-expanded', 'false');
    });
    document.body.classList.remove('era-context-modal-open');
  }

  document.addEventListener('click', event => {
    const closeButton = event.target.closest('[data-era-context-close]');
    if (closeButton) {
      event.preventDefault();
      closeAllEraContext();
      return;
    }

    const trigger = event.target.closest('[data-era-context-toggle]');
    if (!trigger) return;
    event.preventDefault();
    const hero = trigger.closest('.hero');
    if (!hero) return;
    const shouldOpen = !hero.classList.contains('is-context-open');
    closeAllEraContext();
    if (shouldOpen) {
      hero.classList.add('is-context-open');
      trigger.setAttribute('aria-expanded', 'true');
      document.body.classList.add('era-context-modal-open');
    }
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeAllEraContext();
  });
}());
