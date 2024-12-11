from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import AttractionCategory, WeatherSuitability, Attraction, Photo, User
from datetime import datetime
import enum
import os
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attraction.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def add_photos_to_attraction(attraction, user, photo_folder):
    """
    Add photos to an attraction from the specified folder
    Looks for exact filename match with .jpg or .jpeg extension
    """
    photo_extensions = ['.jpg', '.jpeg']
    for ext in photo_extensions:
        filename = f"{attraction.name}{ext}"
        filepath = os.path.join(photo_folder, filename)
        
        if os.path.exists(filepath):
            # Ensure the uploads directory exists
            os.makedirs(os.path.dirname(os.path.join(app.config['UPLOAD_FOLDER'], filename)), exist_ok=True)
            
            # Copy the file to the uploads folder
            destination = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            shutil.copy(filepath, destination)
            
            # Create a Photo instance
            photo = Photo(
                filename=filename,
                caption=f"Photo of {attraction.name}",
                attraction_id=attraction.id,
                user_id=1234
            )
            db.session.add(photo)
            break  # Stop after finding the first matching photo
    
    return None

def populate_db():

    # Specify the photo folder
    photo_folder = '/Users/AF52569/Downloads/palm_coast_attraction'

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

    # Combine all attractions
    all_attractions = attractions + restaurants + nearby_attractions

    db.session.query(Attraction).delete()

    # Add attractions to the session
    for attraction in all_attractions:
        db.session.add(attraction)
    
    # Commit to get IDs
    db.session.flush()
    default_user=1234
    # Add photos for each attraction
    for attraction in all_attractions:
        add_photos_to_attraction(attraction, default_user, photo_folder)
    
    # Final commit
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        populate_db()
        print("Database populated with dummy data and photos.")