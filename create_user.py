from flask import Flask
from flask_bcrypt import Bcrypt
from models import db, User

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configure the app with your settings (database URI, etc.)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safarivendors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.cli.command("create-user")
def create_user():
    """Command to create a new user."""
    with app.app_context():
        email = input("Enter the email for the new user: ")
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            print(f"User with email {email} already exists.")
            return
        
        name = input("Enter the name for the new user: ")
        password = input("Enter the password for the new user: ")
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        print("User created successfully!")

if __name__ == "__main__":
    app.run()
