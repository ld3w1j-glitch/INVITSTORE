import re
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, current_app, send_from_directory
from sqlalchemy import select, or_, func
from app.extensions import db
from app.models import Product, Category, User, Variant
from app.services.cart import selection, add_item, resolve_cart, whatsapp_url
from app.services.validation import integer, text

site_bp = Blueprint('site', __name__)

@site_bp.get('/')
def home():
    q = request.args.get('q', '').strip()[:100]
    category_id = request.args.get('categoria', type=int)
    order = request.args.get('ordem', 'recentes')
    query = select(Product).join(Product.owner).join(Product.category).where(Product.active.is_(True), User.active.is_(True), Category.active.is_(True))
    if q:
        escaped = q.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        query = query.where(or_(Product.name.ilike(f'%{escaped}%', escape='\\'), Product.description.ilike(f'%{escaped}%', escape='\\')))
    if category_id: query = query.where(Product.category_id == category_id)
    variant_price = select(func.min(func.coalesce(Variant.price_cents, Product.price_cents))).where(Variant.product_id == Product.id).correlate(Product).scalar_subquery()
    display_price = func.coalesce(variant_price, Product.price_cents)
    ordering = {'menor-preco': display_price.asc(), 'maior-preco': display_price.desc(), 'nome': Product.name.asc()}
    query = query.order_by(ordering.get(order, Product.created_at.desc()), Product.id.desc())
    page = db.paginate(query, page=request.args.get('pagina', 1, type=int), per_page=12, error_out=False)
    categories = db.session.scalars(select(Category).where(Category.active.is_(True)).order_by(Category.name)).all()
    return render_template('site/home.html', page=page, categories=categories, q=q, category_id=category_id, order=order)

@site_bp.get('/produto/<int:product_id>')
def product(product_id):
    p = db.get_or_404(Product, product_id)
    if not p.public: abort(404)
    return render_template('site/product.html', product=p)

@site_bp.post('/produto/<int:product_id>/whatsapp')
def direct_whatsapp(product_id):
    p = db.get_or_404(Product, product_id)
    try:
        item = selection(p, request.form.get('variant_id'), request.form.get('quantity', '1'))
        return redirect(whatsapp_url(p.owner, [item]), 303)
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('site.product', product_id=p.id), 303)

@site_bp.post('/carrinho/adicionar/<int:product_id>')
def add(product_id):
    p = db.get_or_404(Product, product_id)
    try:
        add_item(p, request.form.get('variant_id'), request.form.get('quantity', '1'))
        flash('Produto adicionado ao seu pedido.', 'success')
        return redirect(url_for('site.cart'), 303)
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('site.product', product_id=p.id), 303)

@site_bp.get('/carrinho')
def cart():
    groups, errors = resolve_cart()
    return render_template('site/cart.html', groups=groups, errors=errors, total=sum(g['total'] for g in groups))

@site_bp.post('/carrinho/atualizar')
def update_cart():
    key = request.form.get('key', '')
    cart = dict(session.get('cart', {}))
    if key not in cart: abort(400)
    try:
        qty = integer(request.form.get('quantity'), maximum=999)
        if qty == 0: cart.pop(key)
        else:
            pid, vid = map(int, key.split(':'))
            selection(db.session.get(Product, pid), vid, qty)
            cart[key] = qty
        session['cart'] = cart
    except ValueError as e: flash(str(e), 'error')
    return redirect(url_for('site.cart'), 303)

@site_bp.post('/carrinho/whatsapp/<int:seller_id>')
def checkout(seller_id):
    groups, errors = resolve_cart()
    # Invalid lines must be reviewed instead of silently omitted from the request.
    if errors:
        flash('Revise ou remova os itens indisponíveis antes de continuar.', 'error')
        return redirect(url_for('site.cart'), 303)
    group = next((g for g in groups if g['seller'].id == seller_id), None)
    if not group: abort(400)
    try:
        name = text(request.form.get('name'), 'Nome', 80, 0)
        notes = text(request.form.get('notes'), 'Observações', 500, 0)
        return redirect(whatsapp_url(group['seller'], group['items'], name, notes), 303)
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('site.cart'), 303)

@site_bp.get('/midia/<filename>')
def media(filename):
    if not re.fullmatch(r'[a-f0-9]{32}\.webp', filename): abort(404)
    p = db.session.scalar(select(Product).where(Product.image == filename))
    if not p: abort(404)
    if not p.public:
        from flask_login import current_user
        if not current_user.is_authenticated or not (current_user.is_superadmin or p.owner_id == current_user.id): abort(404)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, max_age=3600)

@site_bp.get('/health')
def health():
    db.session.execute(select(1))
    return {'status':'ok', 'app':'InvitStore', 'version':'2.0.2'}
