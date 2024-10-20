from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

db = SQLAlchemy()

# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    
    # Relationships
    reviews = db.relationship('Review', back_populates='user', cascade='all, delete-orphan')
    orders = db.relationship('Order', back_populates='user', cascade='all, delete-orphan')

# Vendor Model
class Vendor(db.Model):
    __tablename__ = 'vendors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    # Add any other necessary fields

# Product Model
class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    price = db.Column(db.Float, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))

    # Relationships
    reviews = db.relationship('Review', back_populates='product', cascade='all, delete-orphan')

# Order Model
class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)  # Total amount of the order

    # Relationships
    user = db.relationship('User', back_populates='orders')
    order_items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

# Order Item Model
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # Keeping this required for clarity

    # Relationships
    order = db.relationship('Order', back_populates='order_items')
    product = db.relationship('Product')

# Review Model
class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Consider validation for rating (1-5)
    comment = db.Column(db.String, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='reviews')
    product = db.relationship('Product', back_populates='reviews')


# Schemas for serialization
class UserSchema(Schema):
    id = fields.Int()
    email = fields.Str()

class VendorSchema(Schema):
    id = fields.Int()
    name = fields.Str()

class ProductSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    price = fields.Float()
    vendor_id = fields.Int()

class OrderSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    total_amount = fields.Float()  # Include total amount
    order_items = fields.List(fields.Nested('OrderItemSchema'))  # Include order items

class OrderItemSchema(Schema):
    id = fields.Int()
    order_id = fields.Int()
    product_id = fields.Int()
    quantity = fields.Int()

class ReviewSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    product_id = fields.Int()
    rating = fields.Int()  # You might want to restrict values between 1-5
    comment = fields.Str()
