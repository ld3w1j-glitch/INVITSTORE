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
  if (!option.value) return;
  document.querySelector('[data-product-price]').textContent = new Intl.NumberFormat('pt-BR', {style:'currency',currency:'BRL'}).format(Number(option.dataset.price)/100);
  document.querySelector('[data-stock-label]').textContent = `${option.dataset.stock} unidade(s) disponível(is)`;
  const quantity = document.getElementById('quantity');
  quantity.max = option.dataset.stock;
  if (Number(quantity.value) > Number(quantity.max)) quantity.value = quantity.max;
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
