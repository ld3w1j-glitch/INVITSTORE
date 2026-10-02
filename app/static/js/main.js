'use strict';
document.querySelectorAll('[data-auto-submit]').forEach(el => el.addEventListener('change', () => el.form.requestSubmit()));
document.querySelectorAll('[data-confirm]').forEach(form => form.addEventListener('submit', event => {
  if (!window.confirm(form.dataset.confirm)) event.preventDefault();
}));
const menu = document.querySelector('[data-toggle-menu]');
if (menu) menu.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  document.getElementById('admin-nav').classList.toggle('open', open);
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && menu) {menu.setAttribute('aria-expanded','false');document.getElementById('admin-nav').classList.remove('open');}
});
document.querySelectorAll('[data-qty]').forEach(button => button.addEventListener('click', () => {
  const input = button.closest('.quantity-control').querySelector('input');
  const next = Number(input.value || 1) + Number(button.dataset.qty);
  input.value = Math.max(Number(input.min || 1), Math.min(Number(input.max || 999), next));
}));
const variants = document.querySelector('[data-variant-select]');
if (variants) variants.addEventListener('change', () => {
  const option = variants.selectedOptions[0];
  const gallery = document.querySelector('[data-product-gallery]');
  const mainImage = document.querySelector('[data-gallery-main]');
  if (!option.value) {
    if (gallery?.dataset.defaultImage && mainImage) mainImage.src = gallery.dataset.defaultImage;
    return;
  }
  document.querySelector('[data-product-price]').textContent = new Intl.NumberFormat('pt-BR', {style:'currency',currency:'BRL'}).format(Number(option.dataset.price)/100);
  document.querySelector('[data-stock-label]').textContent = `${option.dataset.stock} unidade(s) disponível(is)`;
  const quantity = document.getElementById('quantity');
  quantity.max = option.dataset.stock;
  if (Number(quantity.value) > Number(quantity.max)) quantity.value = quantity.max;
  if (option.dataset.image && mainImage) {
    mainImage.src = option.dataset.image;
    document.querySelectorAll('[data-gallery-image]').forEach(button => button.classList.toggle('selected', button.dataset.galleryImage === option.dataset.image));
  }
});
document.querySelectorAll('[data-gallery-image]').forEach(button => button.addEventListener('click', () => {
  const mainImage = document.querySelector('[data-gallery-main]');
  if (!mainImage) return;
  mainImage.src = button.dataset.galleryImage;
  document.querySelectorAll('[data-gallery-image]').forEach(item => item.classList.toggle('selected', item === button));
}));
const zoomArea = document.querySelector('[data-zoom-area]');
if (zoomArea) zoomArea.addEventListener('mousemove', event => {
  const bounds = zoomArea.getBoundingClientRect();
  zoomArea.style.setProperty('--zoom-x', `${(event.clientX - bounds.left) / bounds.width * 100}%`);
  zoomArea.style.setProperty('--zoom-y', `${(event.clientY - bounds.top) / bounds.height * 100}%`);
});
const addVariant = document.querySelector('[data-add-variant]');
if (addVariant) addVariant.addEventListener('click', () => {
  const list = document.getElementById('variant-list');
  if (list.children.length >= 50) {window.alert('Use no máximo 50 variações.');return;}
  list.appendChild(document.getElementById('variant-template').content.cloneNode(true));
  list.lastElementChild.querySelector('[name=variant_label]').focus();
});
document.addEventListener('click', event => {
  const button = event.target.closest('[data-remove-variant]');
  if (button) button.closest('.variant-row').remove();
});
const imageInput = document.querySelector('[data-image-input]');
let imageObjectURL;
if (imageInput) imageInput.addEventListener('change', () => {
  const file = imageInput.files[0];
  if (!file) return;
  if (file.size > 8 * 1024 * 1024) {window.alert('Use uma imagem com até 8 MB.');imageInput.value='';return;}
  if (!['image/jpeg','image/png','image/webp'].includes(file.type)) {window.alert('Use JPG, PNG ou WebP.');imageInput.value='';return;}
  if (imageObjectURL) URL.revokeObjectURL(imageObjectURL);
  imageObjectURL = URL.createObjectURL(file);
  const img = new Image();img.src=imageObjectURL;img.alt='Prévia da imagem selecionada';
  document.querySelector('[data-image-preview]').replaceChildren(img);
});
const validImage = file => {
  if (file.size > 8 * 1024 * 1024) {window.alert('Cada imagem deve ter até 8 MB.');return false;}
  if (!['image/jpeg','image/png','image/webp'].includes(file.type)) {window.alert('Use imagens JPG, PNG ou WebP.');return false;}
  return true;
};
const galleryInput = document.querySelector('[data-gallery-input]');
if (galleryInput) galleryInput.addEventListener('change', () => {
  const files = [...galleryInput.files];
  if (files.length > 8 || files.some(file => !validImage(file))) {galleryInput.value='';return;}
  const preview = document.querySelector('[data-gallery-preview]');
  preview.replaceChildren(...files.map(file => {
    const img = new Image();img.src=URL.createObjectURL(file);img.alt=`Prévia de ${file.name}`;
    const item=document.createElement('div');item.className='admin-gallery-item';item.appendChild(img);return item;
  }));
});
document.addEventListener('change', event => {
  const input = event.target.closest('[data-variant-image-input]');
  if (!input || !input.files[0]) return;
  const file=input.files[0];
  if (!validImage(file)) {input.value='';return;}
  let img=input.closest('.variant-image-field').querySelector('img');
  if (!img) {img=new Image();input.closest('.variant-image-field').prepend(img);}
  img.src=URL.createObjectURL(file);img.alt='Prévia da imagem da variação';
});

// Movimento editorial: apenas na loja pública, sem dependências externas.
(() => {
  if (!document.querySelector('.site-header')) return;
  document.body.classList.add('storefront');
  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');

  // O conteúdo nunca fica escondido esperando JavaScript ou uma observação.
  // Cada entrada é executada uma única vez, somente ao chegar à tela.
  const motionGroups = [
    '.brand-intro > .eyebrow, .brand-intro > h1, .brand-intro > p, .brand-intro > .text-link',
    '.catalog > .section-heading, .catalog > .catalog-tools',
    '.product-grid > .product-card',
    '.brand-categories > .brand-category',
    '.store-promise > div',
    '.ornamental-divider, .editorial-cta, .footer-ornament, .brand-intro > img'
  ];
  const motionTargets = [];
  motionGroups.forEach(selector => {
    document.querySelectorAll(selector).forEach((element, index) => {
      element.classList.add('motion-item', `motion-step-${index % 4}`);
      motionTargets.push(element);
    });
  });
  let revealObserver;
  if (!motionPreference.matches && 'IntersectionObserver' in window) {
    revealObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        revealObserver.unobserve(entry.target);
        if (!motionPreference.matches && !entry.target.matches(':focus-within')) {
          entry.target.classList.add('is-revealing');
        }
      });
    }, {threshold: 0, rootMargin: '0px 0px -24px 0px'});
    motionTargets.forEach(element => revealObserver.observe(element));
  }
  motionPreference.addEventListener('change', () => {
    if (!motionPreference.matches) return;
    revealObserver?.disconnect();
    motionTargets.forEach(element => element.classList.remove('is-revealing'));
  });

  const carousel = document.querySelector('[data-campaign-carousel]');
  if (!carousel) return;
  const slides = [...carousel.querySelectorAll('[data-carousel-slide]')];
  if (slides.length < 2) return;
  const dots = [...carousel.querySelectorAll('[data-carousel-dot]')];
  const status = carousel.querySelector('[data-carousel-status]');
  const toggle = carousel.querySelector('[data-carousel-toggle]');
  const progress = carousel.querySelector('[data-carousel-progress]');
  const cssDuration = parseFloat(getComputedStyle(carousel).getPropertyValue('--campaign-duration'));
  const duration = Number.isFinite(cssDuration) ? Math.max(1000, cssDuration) : 6500;
  let current = Math.max(0, slides.findIndex(slide => slide.classList.contains('is-active')));
  let timer = null;
  let remaining = duration;
  let startedAt = 0;
  let userPaused = motionPreference.matches;
  let hovered = window.matchMedia('(hover: hover)').matches && carousel.matches(':hover');
  let focused = carousel.contains(document.activeElement);
  let touching = false;
  let pageActive = true;
  const bounds = carousel.getBoundingClientRect();
  let inViewport = bounds.bottom > 0 && bounds.top < window.innerHeight;
  let touchStart = null;
  let suppressClickUntil = 0;

  const updateToggle = () => {
    if (!toggle) return;
    const reduced = motionPreference.matches;
    toggle.disabled = reduced;
    toggle.setAttribute('aria-pressed', String(userPaused || reduced));
    const label = reduced ? 'Movimento reduzido: rotação automática desativada' :
      (userPaused ? 'Continuar rotação automática' : 'Pausar rotação automática');
    toggle.setAttribute('aria-label', label);
    toggle.title = `${label}. O carrossel também pausa durante a interação.`;
    toggle.querySelector('span').textContent = userPaused || reduced ? '▶' : 'Ⅱ';
  };
  const stop = () => {
    if (timer !== null) {
      window.clearTimeout(timer);
      remaining = Math.max(0, remaining - (performance.now() - startedAt));
      timer = null;
    }
    carousel.classList.remove('is-playing');
  };
  const syncPlayback = () => {
    const canPlay = !userPaused && !motionPreference.matches && !hovered && !focused &&
      !touching && inViewport && !document.hidden && pageActive;
    if (!canPlay) {stop(); return;}
    if (timer !== null) return;
    startedAt = performance.now();
    carousel.classList.add('is-playing');
    timer = window.setTimeout(() => {
      timer = null;
      show(current + 1, false);
    }, Math.max(16, remaining));
  };
  const resetProgress = () => {
    if (!progress) return;
    progress.classList.remove('is-running');
    void progress.offsetWidth;
    progress.classList.add('is-running');
  };
  const show = (next, announce = true) => {
    const nextIndex = (next + slides.length) % slides.length;
    if (nextIndex === current) return;
    const moveFocus = slides[current].contains(document.activeElement);
    stop();
    current = nextIndex;
    remaining = duration;
    slides.forEach((slide, index) => {
      const active = index === current;
      slide.classList.toggle('is-active', active);
      slide.setAttribute('aria-hidden', String(!active));
      slide.tabIndex = active ? 0 : -1;
    });
    dots.forEach((dot, index) => {
      const active = index === current;
      dot.classList.toggle('is-active', active);
      dot.setAttribute('aria-current', String(active));
    });
    if (announce && status) status.textContent = `Imagem ${current + 1} de ${slides.length}`;
    if (moveFocus) slides[current].focus({preventScroll: true});
    resetProgress();
    syncPlayback();
  };

  carousel.querySelector('[data-carousel-prev]')?.addEventListener('click', () => show(current - 1));
  carousel.querySelector('[data-carousel-next]')?.addEventListener('click', () => show(current + 1));
  dots.forEach(dot => dot.addEventListener('click', () => show(Number(dot.dataset.carouselDot))));
  carousel.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const keys = {ArrowLeft: current - 1, ArrowRight: current + 1, Home: 0, End: slides.length - 1};
    if (!(event.key in keys)) return;
    event.preventDefault();
    show(keys[event.key]);
  });
  carousel.addEventListener('mouseenter', () => {
    hovered = window.matchMedia('(hover: hover)').matches;
    syncPlayback();
  });
  carousel.addEventListener('mouseleave', () => {hovered = false; syncPlayback();});
  carousel.addEventListener('focusin', () => {focused = true; syncPlayback();});
  carousel.addEventListener('focusout', event => {
    focused = carousel.contains(event.relatedTarget);
    syncPlayback();
  });
  carousel.addEventListener('touchstart', event => {
    if (event.touches.length !== 1) {touchStart = null; return;}
    touchStart = {x: event.touches[0].clientX, y: event.touches[0].clientY};
    touching = true;
    syncPlayback();
  }, {passive: true});
  carousel.addEventListener('touchend', event => {
    const touch = event.changedTouches[0];
    if (touchStart && touch) {
      const dx = touch.clientX - touchStart.x;
      const dy = touch.clientY - touchStart.y;
      // Rolagem vertical não muda a foto nem captura a navegação da página.
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.3) {
        show(current + (dx < 0 ? 1 : -1));
        suppressClickUntil = performance.now() + 600;
      }
    }
    touchStart = null;
    touching = false;
    syncPlayback();
  }, {passive: true});
  carousel.addEventListener('touchcancel', () => {
    touchStart = null;
    touching = false;
    syncPlayback();
  }, {passive: true});
  carousel.addEventListener('click', event => {
    if (performance.now() < suppressClickUntil && event.target.closest('[data-carousel-slide]')) {
      event.preventDefault();
    }
  }, true);
  toggle?.addEventListener('click', () => {
    userPaused = !userPaused;
    updateToggle();
    syncPlayback();
  });
  motionPreference.addEventListener('change', () => {
    stop();
    // Não retoma sozinho depois de uma mudança na preferência do dispositivo.
    if (motionPreference.matches) userPaused = true;
    remaining = duration;
    resetProgress();
    updateToggle();
    syncPlayback();
  });
  document.addEventListener('visibilitychange', syncPlayback);
  window.addEventListener('pagehide', () => {pageActive = false; stop();});
  window.addEventListener('pageshow', () => {
    pageActive = true;
    focused = carousel.contains(document.activeElement);
    hovered = window.matchMedia('(hover: hover)').matches && carousel.matches(':hover');
    syncPlayback();
  });
  if ('IntersectionObserver' in window) {
    const carouselObserver = new IntersectionObserver(entries => {
      inViewport = entries[0].isIntersecting && entries[0].intersectionRatio >= 0.15;
      syncPlayback();
    }, {threshold: [0, 0.15]});
    carouselObserver.observe(carousel);
  } else {
    // Sem observador, mantém navegação manual e evita rotação fora da tela.
    userPaused = true;
  }

  carousel.classList.add('is-enhanced');
  carousel.querySelectorAll('[data-carousel-control]').forEach(control => {control.hidden = false;});
  updateToggle();
  resetProgress();
  syncPlayback();
})();

const siteHeader = document.querySelector('.site-header');
const backToTop = document.querySelector('[data-back-to-top]');
const updateScrollUI = () => {
  const scrolled = window.scrollY > 24;
  siteHeader?.classList.toggle('is-scrolled', scrolled);
  backToTop?.classList.toggle('is-visible', window.scrollY > 650);
};
window.addEventListener('scroll', updateScrollUI, {passive:true});
updateScrollUI();
backToTop?.addEventListener('click', () => window.scrollTo({top:0,behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'}));
