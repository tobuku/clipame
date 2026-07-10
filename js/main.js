// ===== HEADER SCROLL EFFECT =====
const header = document.querySelector('.header');
if (header) {
  window.addEventListener('scroll', () => {
    header.classList.toggle('scrolled', window.scrollY > 10);
  });
}

// ===== MOBILE MENU =====
const hamburger = document.querySelector('.hamburger');
const nav = document.querySelector('.nav');
if (hamburger && nav) {
  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    nav.classList.toggle('open');
  });
  nav.querySelectorAll('.nav__link').forEach(link => {
    link.addEventListener('click', () => {
      hamburger.classList.remove('active');
      nav.classList.remove('open');
    });
  });
}

// ===== FILTER BUTTONS =====
document.querySelectorAll('.filter-bar').forEach(bar => {
  bar.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      bar.querySelector('.filter-btn.active')?.classList.remove('active');
      btn.classList.add('active');
      const filter = btn.dataset.filter;
      const grid = bar.nextElementSibling;
      if (!grid) return;
      grid.querySelectorAll('[data-category]').forEach(card => {
        if (filter === 'all' || card.dataset.category === filter) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
});

// ===== SEARCH FUNCTIONALITY =====
document.querySelectorAll('.search-bar').forEach(bar => {
  const input = bar.querySelector('input');
  const btn = bar.querySelector('.btn');
  if (!input) return;

  function doSearch() {
    const q = input.value.trim().toLowerCase();
    if (!q) return;
    // On index page, redirect to clippers page with search query
    const page = window.location.pathname;
    if (page === '/' || page.endsWith('index.html')) {
      window.location.href = 'clippers.html?q=' + encodeURIComponent(q);
    } else {
      // Filter cards on current page
      const cards = document.querySelectorAll('.listing-card, .job-card, .tool-card, .community-card');
      cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(q) ? '' : 'none';
      });
    }
  }

  if (btn) btn.addEventListener('click', doSearch);
  input.addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });
});

// Apply search query from URL
(function() {
  const params = new URLSearchParams(window.location.search);
  const q = params.get('q');
  if (q) {
    const input = document.querySelector('.search-bar input, .page-search input');
    if (input) input.value = q;
    const cards = document.querySelectorAll('.listing-card, .job-card, .tool-card, .community-card');
    cards.forEach(card => {
      const text = card.textContent.toLowerCase();
      card.style.display = text.includes(q.toLowerCase()) ? '' : 'none';
    });
  }
})();

// ===== MODAL HANDLING =====
document.querySelectorAll('[data-modal]').forEach(trigger => {
  trigger.addEventListener('click', () => {
    const modal = document.querySelector(trigger.dataset.modal);
    if (modal) modal.classList.add('active');
  });
});
document.querySelectorAll('.modal__close, .modal-overlay').forEach(el => {
  el.addEventListener('click', e => {
    if (e.target === el) {
      el.closest('.modal-overlay')?.classList.remove('active');
    }
  });
});

// ===== SMOOTH SCROLL FOR ANCHOR LINKS =====
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
