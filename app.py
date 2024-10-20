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

# Set up the application context for querying and creating a user
with app.app_context():
    user = User.query.first()
    if user:
        logger.info(f"Existing user found: {user.email}")
    else:
        email = "newuser@example.com"
        plain_password = "password123"
        hashed_password = bcrypt.generate_password_hash(plain_password).decode('utf-8')

        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        logger.info(f"New user created: {email} with password: {plain_password}")

# Home route
@app.route("/")
def home():
    return "Welcome To Safari Vendors API"

# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return make_response(jsonify({"error": "Email and password are required"}), 400)

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return make_response(jsonify({"access_token": access_token}), 200)
    else:
        return make_response(jsonify({"error": "Invalid email or password"}), 401)

# Utility function for pagination
def paginate_query(query, page, per_page):
    return query.paginate(page=page, per_page=per_page, error_out=False)

# Allowed sorting fields
ALLOWED_SORT_FIELDS = ['id', 'name', 'email']

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"An error occurred: {str(e)}")
    return make_response(jsonify({"error": "An internal error occurred"}), 500)

# Get all users
@app.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    users = User.query.all()  # Modify as needed to include pagination/sorting
    user_schema = UserSchema(many=True)
    return user_schema.jsonify(users)

# Get all orders
@app.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    current_user_id = get_jwt_identity()
    orders = Order.query.filter_by(user_id=current_user_id).all()  # Modify as needed
    order_schema = OrderSchema(many=True)
    return order_schema.jsonify(orders)

# Create a new order (checkout)
@app.route('/checkout', methods=['POST'])
@jwt_required()
def create_order():
    current_user_id = get_jwt_identity()
    data = request.json
    product_ids = data.get('product_ids')  # Assuming a list of product IDs to create the order

    if not product_ids:
        return make_response(jsonify({"error": "Product IDs are required"}), 400)

    order = Order(user_id=current_user_id)
    db.session.add(order)
    
    for product_id in product_ids:
        order_item = OrderItem(order_id=order.id, product_id=product_id)
        db.session.add(order_item)

    db.session.commit()
    return make_response(jsonify({"message": "Order created successfully!", "order_id": order.id}), 201)

# Create a new review
@app.route('/products/<int:product_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(product_id):
    current_user_id = get_jwt_identity()
    data = request.json
    rating = data.get('rating')
    comment = data.get('comment')

    if not rating or not comment:
        return make_response(jsonify({"error": "Rating and comment are required"}), 400)

    review = Review(user_id=current_user_id, product_id=product_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    
    return make_response(jsonify({"message": "Review created successfully!"}), 201)

if __name__ == "__main__":
    app.run(port=5500, debug=True)
