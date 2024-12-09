from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import enum

db = SQLAlchemy()

class AttractionCategory(enum.Enum):
    FOOD = "Food"
    HIKE = "Hiking"
    CULTURE = "Cultural"
    NATURE = "Nature"
    ENTERTAINMENT = "Entertainment"
    HISTORICAL = "Historical"

class WeatherSuitability(enum.Enum):
    SUNNY = "Sunny"
    RAINY = "Rainy"
    CLOUDY = "Cloudy"
    ALL_WEATHER = "All Weather"

class Attraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    category = db.Column(db.Enum(AttractionCategory), nullable=False)
    weather_suitability = db.Column(db.Enum(WeatherSuitability), nullable=False)
    average_rating = db.Column(db.Float, default=0)
    total_visits = db.Column(db.Integer, default=0)
    barcode = db.Column(db.String(100), unique=True)

    photos = db.relationship('Photo', backref='attraction', lazy=True)
    reviews = db.relationship('Review', backref='attraction', lazy=True)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255), nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    attraction_id = db.Column(db.Integer, db.ForeignKey('attraction.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False, default=0.0)

    # No need for explicit relationship mappings here as they are defined in Attraction and User models

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    visit_date = db.Column(db.DateTime, nullable=False)
    attraction_id = db.Column(db.Integer, db.ForeignKey('attraction.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_photo = db.Column(db.String(300))
    is_admin = db.Column(db.Boolean, default=False)

    photos = db.relationship('Photo', backref='owner', lazy=True)  # Renamed backref to 'owner' for clarity
    reviews = db.relationship('Review', backref='user', lazy=True)
