from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import AttractionCategory, WeatherSuitability, Attraction, Photo, User
from datetime import datetime
import enum


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attraction.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



def populate_db():
    attractions = [
        Attraction(
            name="Washington Oaks Gardens State Park",
            description="Beautiful state park featuring historic gardens, coastal landscapes, and unique coquina rock beaches.",
            latitude=29.6396,
            longitude=-81.2310,
            category=AttractionCategory.NATURE,
            weather_suitability=WeatherSuitability.ALL_WEATHER,
            average_rating=4.7
        ),
        Attraction(
            name="Flagler Beach Pier",
            description="Iconic fishing pier offering stunning ocean views and recreational fishing opportunities.",
            latitude=29.5133,
            longitude=-81.1576,
            category=AttractionCategory.RECREATION,
            weather_suitability=WeatherSuitability.FAIR_WEATHER,
            average_rating=4.5
        ),
        Attraction(
            name="Princess Place Preserve",
            description="Historic 1800s lodge with 1,500 acres of natural beauty, hiking trails, and kayaking opportunities.",
            latitude=29.5746,
            longitude=-81.2254,
            category=AttractionCategory.NATURE,
            weather_suitability=WeatherSuitability.ALL_WEATHER,
            average_rating=4.6
        ),
        Attraction(
            name="Palm Coast Linear Park",
            description="Scenic 2-mile walking and biking trail connecting various parks and natural areas.",
            latitude=29.5833,
            longitude=-81.2416,
            category=AttractionCategory.RECREATION,
            weather_suitability=WeatherSuitability.ALL_WEATHER,
            average_rating=4.4
        ),
        Attraction(
            name="Graham Swamp Preserve",
            description="Wildlife preserve offering hiking trails and opportunities for nature photography and bird watching.",
            latitude=29.5944,
            longitude=-81.2167,
            category=AttractionCategory.NATURE,
            weather_suitability=WeatherSuitability.ALL_WEATHER,
            average_rating=4.3
        )
    ]

    restaurants = [
        Attraction(
            name="European Village",
            description="Unique dining and entertainment complex with multiple restaurants and cuisines.",
            latitude=29.5828,
            longitude=-81.2461,
            category=AttractionCategory.DINING,
            weather_suitability=WeatherSuitability.ALL_WEATHER,
            average_rating=4.5
        ),
        Attraction(
            name="Hammock Beach Resort Dining",
            description="Multiple upscale dining options with ocean views, including Ocean Course Grille and Atlantic Grille.",
            latitude=29.5419,
            longitude=-81.1987,
            category=AttractionCategory.DINING,
            weather_suitability=WeatherSuitability.ALL_WEATHER,
            average_rating=4.6
        ),
        Attraction(
            name="Dominic's on the Lakes",
            description="Local favorite offering Italian and American cuisine with a scenic lake view.",
            latitude=29.5833,
            longitude=-81.2416,
            category=AttractionCategory.DINING,
            weather_suitability=WeatherSuitability.ALL_WEATHER,
            average_rating=4.4
        ),
        Attraction(
            name="Sunset Harbor Restaurant",
            description="Waterfront dining with fresh seafood and spectacular sunset views.",
            latitude=29.5133,
            longitude=-81.1576,
            category=AttractionCategory.DINING,
            weather_suitability=WeatherSuitability.FAIR_WEATHER,
            average_rating=4.5
        )
    ]

    nearby_attractions = [
        Attraction(
            name="St. Augustine Historic District",
            description="Oldest continuously inhabited European-established settlement in the United States, featuring historic sites and museums.",
            latitude=29.8948,
            longitude=-81.3130,
            category=AttractionCategory.HISTORICAL,
            weather_suitability=WeatherSuitability.ALL_WEATHER,
            average_rating=4.8
        ),
        Attraction(
            name="Castillo de San Marcos National Monument",
            description="Historic Spanish stone fortress offering tours and stunning views of Matanzas Bay.",
            latitude=29.8958,
            longitude=-81.3120,
            category=AttractionCategory.HISTORICAL,
            weather_suitability=WeatherSuitability.ALL_WEATHER,
            average_rating=4.7
        ),
        Attraction(
            name="Daytona Beach",
            description="Famous beach destination known for its wide, hard-packed sandy beaches and motorsports history.",
            latitude=29.2108,
            longitude=-81.0228,
            category=AttractionCategory.RECREATION,
            weather_suitability=WeatherSuitability.FAIR_WEATHER,
            average_rating=4.5
        ),
        Attraction(
            name="Walt Disney World Resort",
            description="Iconic theme park complex featuring four main parks: Magic Kingdom, Epcot, Disney's Hollywood Studios, and Disney's Animal Kingdom.",
            latitude=28.3852,
            longitude=-81.5639,
            category=AttractionCategory.ENTERTAINMENT,
            weather_suitability=WeatherSuitability.ALL_WEATHER,
            average_rating=4.9
        ),
        Attraction(
            name="Universal Orlando Resort",
            description="Massive entertainment complex featuring Universal Studios, Islands of Adventure, and the Wizarding World of Harry Potter.",
            latitude=28.4752,
            longitude=-81.4664,
            category=AttractionCategory.ENTERTAINMENT,
            weather_suitability=WeatherSuitability.ALL_WEATHER,
            average_rating=4.8
        )
    ]

    for attraction in attractions + restaurants + nearby_attractions:
        db.session.add(attraction)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        populate_db()
        print("Database populated with dummy data.")
