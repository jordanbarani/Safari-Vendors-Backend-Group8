from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import logging
from models import db, User, Vendor, Product, Order, OrderItem, Review, UserSchema, OrderSchema, ReviewSchema

app = Flask(__name__)

# First Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safarivendors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'my_super_secret_key'  # Use a strong, unique secret key for production
app.json.compact = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)

# Home route or root page
@app.route("/")
def home():
    return "Welcome To Safari Vendors API"

# Login route
@app.route('/login', methods=['POST'])
def login():
    """Log in a user and return a JWT."""
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return make_response(jsonify(access_token=access_token), 200)
    else:
        return make_response(jsonify({"msg": "Bad email or password"}), 401)

# Create a new review
@app.route('/products/<int:product_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(product_id):
    """Submit a review for a specific product."""
    current_user_id = get_jwt_identity()  # Get the ID of the current user
    data = request.json

    # Validate input
    rating = data.get('rating')
    comment = data.get('comment')

    if rating is None or comment is None:
        return make_response(jsonify({"error": "Rating and comment are required."}), 400)

    try:
        new_review = Review(user_id=current_user_id, product_id=product_id, rating=rating, comment=comment)
        db.session.add(new_review)
        db.session.commit()
        return make_response(jsonify({"message": "Review created successfully!"}), 201)
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}")
        return make_response(jsonify({"error": "An error occurred while creating the review."}), 500)

# Create a new order (checkout)
@app.route('/checkout', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new order for the current user."""
    current_user_id = get_jwt_identity()  # Get the ID of the current user
    data = request.json

    product_ids = data.get('product_ids')

    if not product_ids:
        return make_response(jsonify({"error": "Product IDs are required."}), 400)

    try:
        # Create the order
        order = Order(user_id=current_user_id)
        db.session.add(order)
        db.session.commit()  # Commit to get the order ID

        # Add order items
        for product_id in product_ids:
            order_item = OrderItem(order_id=order.id, product_id=product_id)
            db.session.add(order_item)

        db.session.commit()  # Commit the order items
        return make_response(jsonify({"message": "Order created successfully!"}), 201)
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        return make_response(jsonify({"error": "An error occurred while creating the order."}), 500)

# Get all orders for the current user
@app.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """Fetch and return a list of orders for the current user."""
    current_user_id = get_jwt_identity()  # Get the ID of the current user

    try:
        orders = Order.query.filter_by(user_id=current_user_id).all()
        order_schema = OrderSchema(many=True)  # Use your schema for serialization
        return make_response(order_schema.dump(orders), 200)
    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        return make_response(jsonify({"error": "An error occurred while fetching orders."}), 500)

if __name__ == "__main__":
    app.run(port=5500, debug=True)
