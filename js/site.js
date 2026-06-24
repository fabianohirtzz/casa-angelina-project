/* ============================================================
   CASA ANGELINA — site.js
   Comportamentos compartilhados por todas as páginas:
   nav que comprime ao rolar, gaveta mobile, autoplay de vídeos,
   reveal-and-rise, reveal do rodapé, acordeão de FAQ e lightbox
   da galeria. Cada bloco é autônomo: só roda se os elementos
   existirem na página.
   ============================================================ */
(function () {
  'use strict';

  // ---- Nav: comprime ao rolar ----
  (function () {
    var nav = document.getElementById('nav');
    if (!nav) return;
    var ticking = false;
    function update() {
      nav.dataset.state = window.scrollY > 60 ? 'scrolled' : 'top';
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    update();
  })();

  // ---- Menu mobile: sanduíche abre/fecha a gaveta ----
  (function () {
    var toggle = document.getElementById('navToggle');
    var drawer = document.getElementById('navDrawer');
    if (!toggle || !drawer) return;

    function setOpen(open) {
      document.body.classList.toggle('nav-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
      drawer.setAttribute('aria-hidden', open ? 'false' : 'true');
    }
    toggle.addEventListener('click', function () {
      setOpen(!document.body.classList.contains('nav-open'));
    });
    [].forEach.call(drawer.querySelectorAll('a'), function (a) {
      a.addEventListener('click', function () { setOpen(false); });
    });
    window.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });
    window.matchMedia('(min-width: 1041px)').addEventListener('change', function (e) {
      if (e.matches) setOpen(false);
    });
  })();

  // ---- Vídeos: força o autoplay (iOS/Low Power costuma pausar) ----
  (function () {
    var vids = [].slice.call(document.querySelectorAll('video'));
    if (!vids.length) return;
    function tryPlay() {
      vids.forEach(function (v) {
        v.muted = true;
        var p = v.play();
        if (p && p.catch) p.catch(function () {});
      });
    }
    tryPlay();
    document.addEventListener('touchstart', tryPlay, { once: true, passive: true });
    document.addEventListener('click', tryPlay, { once: true });
    document.addEventListener('visibilitychange', function () { if (!document.hidden) tryPlay(); });
  })();

  // ---- Rodapé: revela o cartão e os adesivos ao entrar na tela ----
  (function () {
    var footer = document.getElementById('rodape');
    if (!footer) return;
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce || !('IntersectionObserver' in window)) { footer.classList.add('is-revealed'); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { footer.classList.add('is-revealed'); io.unobserve(entry.target); }
      });
    }, { threshold: 0.18 });
    io.observe(footer);
  })();

  // ---- Reveal-and-rise genérico ----
  (function () {
    var els = document.querySelectorAll('.reveal, .reveal-group');
    if (!els.length) return;
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce || !('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('is-revealed'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.intersectionRatio > 0.18) { e.target.classList.add('is-revealed'); io.unobserve(e.target); }
      });
    }, { threshold: [0, 0.18, 0.5] });
    els.forEach(function (el) { io.observe(el); });
  })();

  // ---- FAQ: acordeão ----
  (function () {
    var items = document.querySelectorAll('.faq__item');
    if (!items.length) return;
    [].forEach.call(items, function (item) {
      var q = item.querySelector('.faq__q');
      var a = item.querySelector('.faq__a');
      if (!q || !a) return;
      item.setAttribute('aria-expanded', 'false');
      q.addEventListener('click', function () {
        var open = item.getAttribute('aria-expanded') === 'true';
        // fecha os outros (acordeão exclusivo)
        [].forEach.call(items, function (other) {
          if (other !== item) {
            other.setAttribute('aria-expanded', 'false');
            var oa = other.querySelector('.faq__a');
            if (oa) oa.style.maxHeight = null;
          }
        });
        item.setAttribute('aria-expanded', open ? 'false' : 'true');
        a.style.maxHeight = open ? null : a.scrollHeight + 'px';
      });
    });
  })();

  // ---- Lightbox da galeria ----
  (function () {
    var triggers = document.querySelectorAll('[data-lightbox]');
    var box = document.getElementById('lightbox');
    if (!triggers.length || !box) return;
    var imgEl = box.querySelector('.lightbox__img');
    var sources = [].map.call(triggers, function (t) {
      return { src: t.getAttribute('data-full') || t.querySelector('img').getAttribute('src'), alt: t.querySelector('img') ? t.querySelector('img').getAttribute('alt') : '' };
    });
    var i = 0;
    function show(n) {
      i = (n + sources.length) % sources.length;
      imgEl.setAttribute('src', sources[i].src);
      imgEl.setAttribute('alt', sources[i].alt);
    }
    function open(n) { show(n); box.classList.add('is-open'); document.body.classList.add('nav-open'); }
    function close() { box.classList.remove('is-open'); document.body.classList.remove('nav-open'); }
    [].forEach.call(triggers, function (t, n) {
      t.addEventListener('click', function () { open(n); });
    });
    box.querySelector('.lightbox__close').addEventListener('click', close);
    box.querySelector('.lightbox__prev').addEventListener('click', function () { show(i - 1); });
    box.querySelector('.lightbox__next').addEventListener('click', function () { show(i + 1); });
    box.addEventListener('click', function (e) { if (e.target === box) close(); });
    window.addEventListener('keydown', function (e) {
      if (!box.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowLeft') show(i - 1);
      else if (e.key === 'ArrowRight') show(i + 1);
    });
  })();

})();
