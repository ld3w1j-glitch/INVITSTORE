from collections import OrderedDict
from flask import session, current_app
from app.extensions import db
from app.models import Product, Variant
from app.services.validation import integer, brl
from urllib.parse import urlencode

MAX_LINES = 30

def selection(product, variant_id, quantity):
    if not product or not product.public: raise ValueError('Este produto não está mais disponível.')
    qty = integer(quantity, minimum=1, maximum=999)
    variant = None
    if product.variants:
        vid = integer(variant_id, 'Variação', 1)
        variant = db.session.get(Variant, vid)
        if not variant or variant.product_id != product.id: raise ValueError('Escolha uma variação válida para este produto.')
    elif variant_id not in (None, '', '0', 0):
        raise ValueError('Este produto não possui essa variação.')
    stock = variant.stock if variant else product.stock
    if qty > stock: raise ValueError(f'{product.name}: há apenas {stock} unidade(s) disponível(is).')
    cents = variant.price_cents if variant and variant.price_cents else product.price_cents
    return dict(product=product, variant=variant, quantity=qty, price=cents, total=cents * qty, stock=stock,
                key=f'{product.id}:{variant.id if variant else 0}')

def add_item(product, variant_id, quantity):
    item = selection(product, variant_id, quantity)
    cart = dict(session.get('cart', {}))
    old = cart.get(item['key'], 0)
    item = selection(product, variant_id, old + item['quantity'])
    if item['key'] not in cart and len(cart) >= MAX_LINES: raise ValueError('Seu pedido pode ter até 30 itens diferentes.')
    cart[item['key']] = item['quantity']
    session['cart'] = cart

def resolve_cart():
    groups = OrderedDict()
    errors = []
    for key, quantity in session.get('cart', {}).items():
        product = None
        try:
            pid, vid = map(int, key.split(':'))
            product = db.session.get(Product, pid)
            item = selection(product, vid, quantity)
            seller = product.owner
            group = groups.setdefault(seller.id, dict(seller=seller, items=[], total=0))
            group['items'].append(item)
            group['total'] += item['total']
        except (ValueError, TypeError):
            errors.append(dict(key=key, name=product.name if product else 'Produto removido'))
    return list(groups.values()), errors

def whatsapp_url(seller, items, name='', notes='', order_id=None):
    lines = [f'Olá, {seller.name}! Gostaria de fazer este pedido na InvitStore' + (f' #{order_id}' if order_id else '') + ':', '']
    for item in items:
        p = item['product']
        lines.extend([f'• {p.name} [IV-{p.id:05}]'])
        if item['variant']: lines.append(f"  Variação: {item['variant'].label}")
        lines.extend([f"  Quantidade: {item['quantity']}", f"  Valor unitário: {brl(item['price'])}", f"  Subtotal: {brl(item['total'])}"])
    lines.extend(['', f"Total dos itens: {brl(sum(i['total'] for i in items))}"])
    if name: lines.append(f'Nome: {name}')
    if notes: lines.append(f'Observações: {notes}')
    lines.extend(['', 'Pedido aguardando sua aprovação. Disponibilidade, entrega e pagamento a confirmar. Frete não incluído.'])
    base = current_app.config.get('PUBLIC_BASE_URL')
    if base and len(items) == 1: lines.append(f"Produto: {base}/produto/{items[0]['product'].id}")
    return 'https://wa.me/' + seller.whatsapp + '?' + urlencode({'text': '\n'.join(lines)})
