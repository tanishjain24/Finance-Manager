/**
 * Finance Manager — global UI utilities
 */
(function () {
  'use strict';

  const THEME_KEY = 'fm-theme';

  function getStoredTheme() {
    return localStorage.getItem(THEME_KEY);
  }

  function applyTheme(theme) {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else if (theme === 'light') {
      root.classList.remove('dark');
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.toggle('dark', prefersDark);
    }
  }

  function initTheme() {
    const stored = getStoredTheme();
    const serverTheme = document.documentElement.dataset.theme;
    applyTheme(stored || serverTheme || 'dark');
  }

  function toggleTheme() {
    const isDark = document.documentElement.classList.contains('dark');
    const next = isDark ? 'light' : 'dark';
    localStorage.setItem(THEME_KEY, next);
    applyTheme(next);
    updateThemeIcons(next);
  }

  function updateThemeIcons(theme) {
    document.querySelectorAll('[data-theme-icon="sun"]').forEach(el => {
      el.classList.toggle('hidden', theme !== 'dark');
    });
    document.querySelectorAll('[data-theme-icon="moon"]').forEach(el => {
      el.classList.toggle('hidden', theme === 'dark');
    });
  }

  function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const openBtn = document.getElementById('sidebar-open');
    const closeBtn = document.getElementById('sidebar-close');

    function open() {
      sidebar?.classList.remove('-translate-x-full');
      overlay?.classList.remove('hidden');
    }
    function close() {
      sidebar?.classList.add('-translate-x-full');
      overlay?.classList.add('hidden');
    }

    openBtn?.addEventListener('click', open);
    closeBtn?.addEventListener('click', close);
    overlay?.addEventListener('click', close);
  }

  function initFlashToasts() {
    document.querySelectorAll('.flash-toast').forEach(toast => {
      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
      }, 5000);
    });
  }

  function formatCurrency(amount, currency) {
    currency = currency || 'USD';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  }

  window.FinanceManager = {
    toggleTheme,
    formatCurrency,
    applyTheme,
  };

  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    updateThemeIcons(getStoredTheme() || document.documentElement.dataset.theme || 'dark');
    initSidebar();
    initFlashToasts();

    document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
      btn.addEventListener('click', toggleTheme);
    });
  });
})();
