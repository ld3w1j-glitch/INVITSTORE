from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90), nullable=False)
    email = db.Column(db.String(180), nullable=False, unique=True)
    whatsapp = db.Column(db.String(15), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='admin')
    active = db.Column(db.Boolean, nullable=False, default=True)
    session_version = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=now, nullable=False)
    products = db.relationship('Product', back_populates='owner')

    @property
    def is_active(self): return self.active

    @property
    def is_superadmin(self): return self.role == 'superadmin'

    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), nullable=False, unique=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    products = db.relationship('Product', back_populates='category')

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price_cents = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    image = db.Column(db.String(80))
    active = db.Column(db.Boolean, nullable=False, default=True)
    featured = db.Column(db.Boolean, nullable=False, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)
    owner = db.relationship('User', back_populates='products')
    category = db.relationship('Category', back_populates='products')
    variants = db.relationship('Variant', back_populates='product', cascade='all, delete-orphan', order_by='Variant.id')
    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(db.DateTime, default=now, onupdate=now, nullable=False)
    __table_args__ = (db.CheckConstraint('price_cents > 0'), db.CheckConstraint('stock >= 0'))

    @property
    def available_stock(self): return sum(v.stock for v in self.variants) if self.variants else self.stock

    @property
    def display_price(self): return min((v.price_cents or self.price_cents) for v in self.variants) if self.variants else self.price_cents

    @property
    def public(self): return self.active and self.owner.active and self.category.active

class Variant(db.Model):
    __tablename__ = 'variants'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    price_cents = db.Column(db.Integer)
    stock = db.Column(db.Integer, nullable=False, default=0)
    product = db.relationship('Product', back_populates='variants')
    __table_args__ = (db.CheckConstraint('stock >= 0'), db.CheckConstraint('price_cents IS NULL OR price_cents > 0'))

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=now, nullable=False, index=True)

class Supply(db.Model):
    __tablename__ = 'supplies'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    kind = db.Column(db.String(20), nullable=False, default='insumo')
    unit = db.Column(db.String(20), nullable=False, default='un')
    stock = db.Column(db.Float, nullable=False, default=0)
    minimum = db.Column(db.Float, nullable=False, default=0)
    cost_cents = db.Column(db.Integer, nullable=False, default=0)
    waste_percent = db.Column(db.Float, nullable=False, default=0)

class ProductSupply(db.Model):
    __tablename__ = 'product_supplies'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    supply_id = db.Column(db.Integer, db.ForeignKey('supplies.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    supply = db.relationship('Supply')
    __table_args__ = (db.UniqueConstraint('product_id', 'supply_id'),)

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    description = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(60), nullable=False)
    amount_cents = db.Column(db.Integer, nullable=False)
    incurred_at = db.Column(db.DateTime, default=now, nullable=False)

class PendingOrder(db.Model):
    __tablename__ = 'pending_orders'
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    customer_name = db.Column(db.String(80), nullable=False, default='Cliente não informado')
    customer_phone = db.Column(db.String(15))
    notes = db.Column(db.String(500))
    status = db.Column(db.String(20), nullable=False, default='pendente', index=True)
    total_cents = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=now, nullable=False)
    decided_at = db.Column(db.DateTime)
    seller = db.relationship('User')
    items = db.relationship('PendingOrderItem', back_populates='order', cascade='all, delete-orphan')

class PendingOrderItem(db.Model):
    __tablename__ = 'pending_order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('pending_orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('variants.id', ondelete='SET NULL'))
    product_name = db.Column(db.String(140), nullable=False)
    variant_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price_cents = db.Column(db.Integer, nullable=False)
    unit_cost_cents = db.Column(db.Integer, nullable=False, default=0)
    order = db.relationship('PendingOrder', back_populates='items')

    @property
    def subtotal_cost_cents(self): return self.unit_cost_cents * self.quantity
