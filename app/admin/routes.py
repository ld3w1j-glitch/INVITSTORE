from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, session
from flask_login import current_user, login_required
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import Product, Category, Variant, User, PendingOrderItem
from app.core.security import require_owner, superadmin_required
from app.services import validation as v
from app.services.uploads import save_image, remove_image

admin_bp = Blueprint('admin', __name__)

def scope(query):
    return query if current_user.is_superadmin else query.where(Product.owner_id == current_user.id)

@admin_bp.get('/')
@login_required
def dashboard():
    products = db.session.scalars(scope(select(Product)).order_by(Product.created_at.desc())).all()
    return render_template('admin/dashboard.html', products=products[:6], count=len(products),
        active=sum(p.active for p in products), stock=sum(p.available_stock for p in products),
        low=sum(p.available_stock <= 3 for p in products))

@admin_bp.get('/produtos')
@login_required
def products():
    q = request.args.get('q', '').strip()[:100]
    query = scope(select(Product))
    if q: query = query.where(Product.name.icontains(q, autoescape=True))
    page = db.paginate(query.order_by(Product.created_at.desc()), page=request.args.get('pagina', 1, type=int), per_page=20, error_out=False)
    return render_template('admin/products.html', page=page, q=q)

def product_form(product=None):
    categories = db.session.scalars(select(Category).where(Category.active.is_(True)).order_by(Category.name)).all()
    if product and product.category not in categories: categories.append(product.category)
    if request.method == 'POST':
        new_image = None
        try:
            name = v.text(request.form.get('name'), 'Nome', 140)
            description = v.text(request.form.get('description'), 'Descrição', 5000, 5)
            price = v.money(request.form.get('price'))
            stock = v.integer(request.form.get('stock', '0'), 'Estoque')
            cat = db.session.get(Category, v.integer(request.form.get('category_id'), 'Categoria', 1))
            if not cat or (not cat.active and (not product or product.category_id != cat.id)):
                raise ValueError('Escolha uma categoria ativa.')
            labels = request.form.getlist('variant_label')
            ids = request.form.getlist('variant_id')
            prices = request.form.getlist('variant_price')
            stocks = request.form.getlist('variant_stock')
            if not (len(labels) == len(ids) == len(prices) == len(stocks)) or len(labels) > 50:
                raise ValueError('Lista de variações inválida. Use até 50 opções.')
            variants = []
            seen_labels, seen_ids = set(), set()
            for label, vid, amount, qty in zip(labels, ids, prices, stocks):
                label = v.text(label, 'Variação', 100)
                if label.casefold() in seen_labels: raise ValueError('Não repita o nome das variações.')
                seen_labels.add(label.casefold())
                variant = None
                if vid:
                    variant = db.session.get(Variant, v.integer(vid, 'Variação', 1))
                    if not product or not variant or variant.product_id != product.id or variant.id in seen_ids:
                        raise ValueError('A variação não pertence a este produto.')
                    seen_ids.add(variant.id)
                variants.append((variant, label, v.money(amount, True), v.integer(qty, 'Estoque da variação')))
            new_image = save_image(request.files.get('image'))
            if product is None:
                product = Product(owner_id=current_user.id)
                db.session.add(product)
            old_image = product.image
            product.name, product.description, product.price_cents = name, description, price
            product.stock, product.category = (0 if variants else stock), cat
            product.active = request.form.get('active') == 'on'
            product.featured = request.form.get('featured') == 'on'
            if new_image: product.image = new_image
            elif request.form.get('remove_image') == 'on': product.image = None
            keep = []
            for variant, label, amount, qty in variants:
                variant = variant or Variant()
                variant.label, variant.price_cents, variant.stock = label, amount, qty
                keep.append(variant)
            product.variants = keep
            db.session.commit()
            if old_image and old_image != product.image: remove_image(old_image)
            flash('Produto salvo. O responsável e o WhatsApp estão vinculados ao cadastro.', 'success')
            return redirect(url_for('admin.products'), 303)
        except (ValueError, IntegrityError) as e:
            db.session.rollback()
            if new_image: remove_image(new_image)
            flash(str(e) if isinstance(e, ValueError) else 'Não foi possível salvar. Confira os dados.', 'error')
            return render_template('admin/product_form.html', product=product if product and product.id else None, categories=categories), 400
    return render_template('admin/product_form.html', product=product, categories=categories)

@admin_bp.route('/produtos/novo', methods=['GET', 'POST'])
@login_required
def new_product(): return product_form()

@admin_bp.route('/produtos/<int:product_id>/editar', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    p = db.get_or_404(Product, product_id)
    require_owner(p)
    return product_form(p)

@admin_bp.post('/produtos/<int:product_id>/excluir')
@login_required
def delete_product(product_id):
    p = db.get_or_404(Product, product_id)
    require_owner(p)
    if db.session.scalar(select(PendingOrderItem.id).where(PendingOrderItem.product_id == p.id).limit(1)):
        p.active = False; db.session.commit()
        flash('Produto com histórico de pedidos: foi ocultado da vitrine para preservar os registros.', 'success')
        return redirect(url_for('admin.products'), 303)
    image = p.image
    db.session.delete(p)
    db.session.commit()
    remove_image(image)
    flash('Produto excluído.', 'success')
    return redirect(url_for('admin.products'), 303)

@admin_bp.route('/categorias', methods=['GET', 'POST'])
@login_required
def categories():
    if request.method == 'POST':
        try:
            cat_id = request.form.get('category_id')
            cat = db.get_or_404(Category, v.integer(cat_id, 'Categoria', 1)) if cat_id else Category(creator_id=current_user.id)
            if cat_id and cat.creator_id != current_user.id and not current_user.is_superadmin: abort(403)
            cat.name = v.text(request.form.get('name'), 'Categoria', 70)
            cat.active = request.form.get('active') == 'on'
            db.session.add(cat)
            db.session.commit()
            flash('Categoria salva.', 'success')
        except (ValueError, IntegrityError) as e:
            db.session.rollback()
            flash(str(e) if isinstance(e, ValueError) else 'Já existe uma categoria com esse nome.', 'error')
        return redirect(url_for('admin.categories'), 303)
    cats = db.session.scalars(select(Category).order_by(Category.name)).all()
    return render_template('admin/categories.html', categories=cats)

@admin_bp.post('/categorias/<int:category_id>/excluir')
@login_required
def delete_category(category_id):
    cat = db.get_or_404(Category, category_id)
    if cat.creator_id != current_user.id and not current_user.is_superadmin: abort(403)
    if cat.products: flash('Esta categoria tem produtos. Mova os produtos ou desative a categoria.', 'error')
    else:
        db.session.delete(cat); db.session.commit(); flash('Categoria excluída.', 'success')
    return redirect(url_for('admin.categories'), 303)

@admin_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            name, email, phone = v.text(request.form.get('name'), 'Nome', 90), v.email(request.form.get('email')), v.phone(request.form.get('whatsapp'))
            pwd = request.form.get('new_password', '')
            if pwd:
                v.password(pwd)
                if not current_user.check_password(request.form.get('current_password', '')): raise ValueError('A senha atual está incorreta.')
            current_user.name, current_user.email, current_user.whatsapp = name, email, phone
            if pwd:
                current_user.set_password(pwd)
                current_user.session_version += 1
            db.session.commit()
            session['session_version'] = current_user.session_version
            flash('Perfil atualizado. Seus produtos já usam essas informações.', 'success')
            return redirect(url_for('admin.profile'), 303)
        except (ValueError, IntegrityError) as e:
            db.session.rollback()
            flash(str(e) if isinstance(e, ValueError) else 'Esse e-mail já está em uso.', 'error')
    return render_template('admin/profile.html')

@admin_bp.route('/administradores', methods=['GET', 'POST'])
@superadmin_required
def users():
    if request.method == 'POST':
        try:
            u = User(name=v.text(request.form.get('name'), 'Nome', 90), email=v.email(request.form.get('email')), whatsapp=v.phone(request.form.get('whatsapp')), role='admin', active=True)
            u.set_password(v.password(request.form.get('password')))
            db.session.add(u); db.session.commit()
            flash('Administrador criado. Ele pode entrar e cadastrar os próprios produtos.', 'success')
            return redirect(url_for('admin.users'), 303)
        except (ValueError, IntegrityError) as e:
            db.session.rollback()
            flash(str(e) if isinstance(e, ValueError) else 'Esse e-mail já está em uso.', 'error')
    users = db.session.scalars(select(User).order_by(User.created_at)).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/administradores/<int:user_id>/editar', methods=['GET', 'POST'])
@superadmin_required
def edit_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id: return redirect(url_for('admin.profile'))
    if user.is_superadmin: abort(403)
    if request.method == 'POST':
        try:
            user.name = v.text(request.form.get('name'), 'Nome', 90)
            user.email = v.email(request.form.get('email'))
            user.whatsapp = v.phone(request.form.get('whatsapp'))
            user.active = request.form.get('active') == 'on'
            pwd = request.form.get('password', '')
            if pwd: user.set_password(v.password(pwd))
            user.session_version += 1
            db.session.commit()
            flash('Administrador atualizado.', 'success')
            return redirect(url_for('admin.users'), 303)
        except (ValueError, IntegrityError) as e:
            db.session.rollback()
            flash(str(e) if isinstance(e, ValueError) else 'Esse e-mail já está em uso.', 'error')
    return render_template('admin/user_edit.html', user=user)
