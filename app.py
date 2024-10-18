from flask import Flask, make_response,jsonify
from flask_migrate import Migrate
from models import db

app = Flask(__name__)

# First Configurations and are provided so don't stress
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safarivendors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

#Home route or root page
@app.route("/")
def home():
    return "Welcome To this API generation"


if __name__ == "__main__":
    app.run(port=5500, debug=True)