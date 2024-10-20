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
    # Query for the first user in the database
    user = User.query.first()
    if user:
        logger.info(f"Existing user found: {user.email}")
    else:
        # If no users are found, create a new user
        email = "newuser@example.com"
        plain_password = "password123"
        hashed_password = bcrypt.generate_password_hash(plain_password).decode('utf-8')

        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        logger.info(f"New user created: {email} with password: {plain_password}")

# Home route or root page
@app.route("/")
def home():
    return "Welcome To Safari Vendors API"

# Login route to authenticate user and generate JWT
@app.route('/login', methods=['POST'])
def login():
    """Authenticate user and return a JWT token."""
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return make_response(jsonify({"error": "Email and password are required"}), 400)

    try:
        # Find user by email
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            # Generate JWT token
            access_token = create_access_token(identity=user.id)
            return make_response(jsonify({"access_token": access_token}), 200)
        else:
            return make_response(jsonify({"error": "Invalid email or password"}), 401)
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return make_response(jsonify({"error": "An error occurred during login"}), 500)

# Utility function for pagination
def paginate_query(query, page, per_page):
    return query.paginate(page=page, per_page=per_page, error_out=False)

# Allowed sorting fields
ALLOWED_SORT_FIELDS = ['id', 'name', 'email']

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"An error occurred: {str(e)}")
    return make_response(jsonify({"error": "An internal error occurred"}), 500)

# Get all users (with pagination, sorting, and filtering)
@app.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """Fetch and return a paginated list of users with sorting and filtering."""
    # Existing code for listing users...

# Get all orders (with pagination, sorting, and filtering)
@app.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """Fetch and return a paginated list of orders for the current user."""
    # Existing code for getting orders...

# Create a new order (checkout)
@app.route('/checkout', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new order for the current user."""
    # Existing code for creating an order...

# Create a new review
@app.route('/products/<int:product_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(product_id):
    """Submit a review for a specific product."""
    # Existing code for creating a review...

if __name__ == "__main__":
    app.run(port=5500, debug=True)
