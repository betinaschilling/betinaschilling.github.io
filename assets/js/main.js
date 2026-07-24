(() => {
  const button = document.querySelector('.menu-button');
  const nav = document.querySelector('.site-header nav');
  if (!button || !nav) return;

  const closeMenu = () => {
    button.setAttribute('aria-expanded', 'false');
    nav.classList.remove('open');
  };

  button.addEventListener('click', () => {
    const open = button.getAttribute('aria-expanded') === 'true';
    button.setAttribute('aria-expanded', String(!open));
    nav.classList.toggle('open', !open);
  });

  nav.addEventListener('click', (event) => {
    if (event.target.closest('a')) closeMenu();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && nav.classList.contains('open')) {
      closeMenu();
      button.focus();
    }
  });

  document.addEventListener('click', (event) => {
    if (!nav.classList.contains('open')) return;
    if (!nav.contains(event.target) && !button.contains(event.target)) closeMenu();
  });
})();
