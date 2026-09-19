/* Shared helpers: nav toggle, flash dismissal, fetch wrapper, modals. */

const Safar = {
  /* --- fetch wrapper: always returns {ok, data|error} --- */
  async request(url, options = {}) {
    try {
      const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        ...options,
      });
      const body = await res.json();
      if (!res.ok) return { ok: false, error: body.error || 'Something went wrong.' };
      return body;
    } catch (err) {
      return { ok: false, error: 'Network unavailable. Check your connection.' };
    }
  },

  /* --- toast, matching the server-rendered flash style --- */
  toast(message, kind = 'info') {
    let box = document.querySelector('.flashes');
    if (!box) {
      box = document.createElement('div');
      box.className = 'flashes';
      document.body.appendChild(box);
    }
    const el = document.createElement('div');
    el.className = `flash flash-${kind}`;
    el.innerHTML = `<span></span><button aria-label="Dismiss">&times;</button>`;
    el.querySelector('span').textContent = message;
    el.querySelector('button').onclick = () => el.remove();
    box.appendChild(el);
    setTimeout(() => el.remove(), 5000);
  },

  money(value) {
    return '₹' + Number(value || 0).toLocaleString('en-IN');
  },

  openModal(id) { document.getElementById(id)?.classList.add('open'); },
  closeModal(id) { document.getElementById(id)?.classList.remove('open'); },
};

document.addEventListener('DOMContentLoaded', () => {
  /* mobile navigation */
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav');
  toggle?.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });

  /* dismiss server flashes */
  document.querySelectorAll('.flash button').forEach((btn) => {
    btn.onclick = () => btn.closest('.flash').remove();
  });
  setTimeout(() => document.querySelectorAll('.flash').forEach((f) => f.remove()), 6000);

  /* close modals on backdrop click or Escape */
  document.querySelectorAll('.modal-backdrop').forEach((back) => {
    back.addEventListener('click', (e) => {
      if (e.target === back) back.classList.remove('open');
    });
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-backdrop.open').forEach((m) => m.classList.remove('open'));
    }
  });

  /* confirm before any destructive form */
  document.querySelectorAll('form[data-confirm]').forEach((form) => {
    form.addEventListener('submit', (e) => {
      if (!window.confirm(form.dataset.confirm)) e.preventDefault();
    });
  });
});
