from models import User, db
from app import app  # Ensure 'app' matches your application module name
from werkzeug.security import generate_password_hash

with app.app_context():
    existing_user = db.session.query(User).filter_by(email='jordanbarani@example.com').first()
    if existing_user:
        print(f"User with email {existing_user.email} already exists.")
    else:
        name = input("Enter the name for the new user: ")
        email = input("Enter the email for the new user: ")
        
        # Check if the email already exists
        existing_user = db.session.query(User).filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists.")
        else:
            password = input("Enter the password for the new user: ")
            hashed_password = generate_password_hash(password)  # Hash the password

            new_user = User(name=name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            print("User created successfully!")
