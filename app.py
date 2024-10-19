from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import logging  # Import logging
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

# Utility function for pagination
def paginate_query(query, page, per_page):
    return query.paginate(page=page, per_page=per_page, error_out=False)

# Allowed sorting fields
ALLOWED_SORT_FIELDS = ['id', 'name', 'email']  # Add other fields as necessary

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"An error occurred: {str(e)}")
    return make_response(jsonify({"error": "An internal error occurred"}), 500)

# Get all users (with pagination, sorting, and filtering)
@app.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """Fetch and return a paginated list of users with sorting and filtering."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'id', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str)

    # Validate sort_by field
    if sort_by not in ALLOWED_SORT_FIELDS:
        return make_response(jsonify({"error": f"Invalid sort_by field: {sort_by}"}), 400)

    try:
        # Apply sorting
        sort_column = getattr(User, sort_by)
        sort_column = sort_column.desc() if sort_order == 'desc' else sort_column

        # Filter by name if provided
        name_filter = request.args.get('name')
        query = User.query
        if name_filter:
            query = query.filter(User.name.ilike(f'%{name_filter}%'))

        # Apply sorting and pagination
        query = query.order_by(sort_column)
        paginated_users = paginate_query(query, page, per_page)

        users_data = [{"id": user.id, "name": user.name, "email": user.email} for user in paginated_users.items]
        return make_response(jsonify({
            "users": users_data,
            "page": paginated_users.page,
            "total_pages": paginated_users.pages,
            "total_users": paginated_users.total
        }), 200)
    except Exception as e:
        logger.error(f"Error fetching users from {request.path}: {str(e)}")
        return make_response(jsonify({"error": "An error occurred while fetching users"}), 500)

# Get all orders (with pagination, sorting, and filtering)
@app.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """Fetch and return a paginated list of orders for the current user with sorting and filtering."""
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'id', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str)

    try:
        # Apply sorting
        sort_column = getattr(Order, sort_by)
        sort_column = sort_column.desc() if sort_order == 'desc' else sort_column

        # Filter by status if provided
        status_filter = request.args.get('status')
        query = Order.query.filter_by(user_id=current_user_id)
        if status_filter:
            query = query.filter(Order.status.ilike(f'%{status_filter}%'))

        # Apply sorting and pagination
        query = query.order_by(sort_column)
        paginated_orders = paginate_query(query, page, per_page)

        orders_data = [order.to_dict() for order in paginated_orders.items]
        return make_response(jsonify({
            "orders": orders_data,
            "page": paginated_orders.page,
            "total_pages": paginated_orders.pages,
            "total_orders": paginated_orders.total
        }), 200)
    except Exception as e:
        logger.error(f"Error fetching orders from {request.path}: {str(e)}")
        return make_response(jsonify({"error": "An error occurred while fetching orders"}), 500)

# Get all reviews for a specific product (with pagination)
@app.route('/products/<int:product_id>/reviews', methods=['GET'])
@jwt_required()  # Protect this endpoint if reviews are user-specific
def get_reviews(product_id):
    """Fetch and return a paginated list of reviews for a specific product."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        query = Review.query.filter_by(product_id=product_id)
        paginated_reviews = paginate_query(query, page, per_page)

        reviews_data = [review.to_dict() for review in paginated_reviews.items]
        return make_response(jsonify({
            "reviews": reviews_data,
            "page": paginated_reviews.page,
            "total_pages": paginated_reviews.pages,
            "total_reviews": paginated_reviews.total
        }), 200)
    except Exception as e:
        logger.error(f"Error fetching reviews for product {product_id}: {str(e)}")
        return make_response(jsonify({"error": "An error occurred while fetching reviews"}), 500)

if __name__ == "__main__":
    app.run(port=5500, debug=True)
