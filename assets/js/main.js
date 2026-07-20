(() => {
  const button = document.querySelector('.menu-button');
  const nav = document.querySelector('.site-header nav');
  if (!button || !nav) return;
  button.addEventListener('click', () => {
    const open = button.getAttribute('aria-expanded') === 'true';
    button.setAttribute('aria-expanded', String(!open));
    nav.classList.toggle('open', !open);
  });
})();
