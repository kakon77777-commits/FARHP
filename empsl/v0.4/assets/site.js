(() => {
  document.documentElement.classList.add('js');

  const header = document.querySelector('.site-header');
  const toggle = document.querySelector('#siteNavToggle');
  const links = document.querySelector('#siteNavLinks');
  const year = document.querySelector('#siteYear');

  toggle?.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!open));
    links?.toggleAttribute('data-open', !open);
  });

  document.querySelectorAll('#siteNavLinks a').forEach(link => {
    link.addEventListener('click', () => {
      toggle?.setAttribute('aria-expanded', 'false');
      links?.removeAttribute('data-open');
    });
  });

  window.addEventListener('scroll', () => {
    header?.toggleAttribute('data-scrolled', window.scrollY > 12);
  }, { passive: true });

  if (year) year.textContent = String(new Date().getFullYear());

  const nodes = [...document.querySelectorAll('[data-reveal]')];
  if (!('IntersectionObserver' in window)) {
    nodes.forEach(node => node.setAttribute('data-visible', ''));
    return;
  }

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.setAttribute('data-visible', '');
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.12 });

  nodes.forEach(node => observer.observe(node));
})();
