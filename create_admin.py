# create_admin.py
from flask import Flask
from models import db, User
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attraction.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'

db.init_app(app)

with app.app_context():
    db.create_all()  # Ensure the tables are created

    # Create admin user
    admin_username = 'guest'
    admin_email = 'admin@example.com'
    admin_password = 'guest'  # Change this to a secure password
    hashed_password = generate_password_hash(admin_password)

    admin_user = User(username=admin_username, email=admin_email, password=hashed_password, is_admin=True)
    db.session.add(admin_user)
    db.session.commit()

    print('Admin user created successfully!')
