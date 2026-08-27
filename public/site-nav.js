function toggleMob() {
  const nav = document.getElementById('mob-nav');
  const button = document.querySelector('.mob-toggle');
  if (!nav) return;
  const isOpen = nav.classList.toggle('open');
  if (button) button.setAttribute('aria-expanded', String(isOpen));
}

document.addEventListener('keydown', (event) => {
  if (event.key !== 'Escape') return;
  const nav = document.getElementById('mob-nav');
  const button = document.querySelector('.mob-toggle');
  if (!nav || !nav.classList.contains('open')) return;
  nav.classList.remove('open');
  if (button) {
    button.setAttribute('aria-expanded', 'false');
    button.focus();
  }
});
