from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, Attraction, Photo, Review, User, AttractionCategory, WeatherSuitability
from geopy.distance import geodesic
import os
import qrcode
import uuid
from datetime import datetime
import photo_processor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attraction.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_unique_filename(filename):
    """Generate a unique filename to prevent overwriting"""
    ext = os.path.splitext(filename)[1]
    unique_filename = str(uuid.uuid4()) + ext
    return unique_filename

def generate_attraction_qr(attraction):
    """Generate QR code for an attraction"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"Attraction: {attraction.name}\nDescription: {attraction.description}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    filename = f"qr_{attraction.id}.png"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img.save(filepath)
    return filename

def rank_attractions(attractions, user_location=None):
    """
    Rank attractions based on multiple factors:
    1. Average rating
    2. Total visits
    3. Distance from user (if location provided)
    """
    def calculate_score(attraction):
        rating_weight = attraction.average_rating * 2 if attraction.average_rating else 0
        visits_weight = attraction.total_visits * 0.5 if attraction.total_visits else 0
        
        distance_weight = 0
        if user_location:
            # Calculate distance penalty/bonus
            distance = geodesic(user_location, (attraction.latitude, attraction.longitude)).kilometers
            distance_weight = max(10 - (distance * 0.1), 0)  # Closer attractions get bonus points
        
        return rating_weight + visits_weight + distance_weight

    return sorted(attractions, key=calculate_score, reverse=True)

@app.route('/')
def index():
    """Home page with featured attractions"""
    #featured_attractions = rank_attractions(Attraction.query.limit(6).all())
    return redirect(url_for('list_attractions'))

@app.route('/attractions')
def list_attractions():
    """List attractions with optional filtering"""
    category = request.args.get('category')
    weather = request.args.get('weather')
    
    query = Attraction.query
    if category:
        query = query.filter(Attraction.category == category)
    if weather:
        query = query.filter(Attraction.weather_suitability == weather)
    
    attractions = rank_attractions(query.all())
    return render_template('attractions.html', attractions=attractions)

@app.route('/attraction/<int:attraction_id>', methods=['GET', 'POST'])
def attraction_detail(attraction_id):
    attraction = Attraction.query.get_or_404(attraction_id)
    
    if request.method == 'POST':
        # Handle photo upload and post creation
        try:
            if 'photo' in request.files:
                photo = request.files['photo']
                
                if photo and allowed_file(photo.filename):
                    try:
                        # Process and save the image
                        filename = photo_processor.process_and_save_image(
                            photo, 
                            app.config['UPLOAD_FOLDER'], 
                            target_size=(1200, 800)
                        )
                        
                        # Create new photo record
                        new_photo = Photo(
                            filename=filename,
                            caption=request.form['caption'],
                            rating=int(request.form['rating']),
                            attraction_id=attraction_id,
                            user_id=1234,
                            upload_date=datetime.utcnow()
                        )
                        
                        # Update attraction's average rating
                        new_rating = int(request.form['rating'])
                        attraction.total_visits += 1
                        attraction.average_rating = (
                            (attraction.average_rating * (attraction.total_visits - 1) + new_rating) / 
                            attraction.total_visits
                        )
                        
                        db.session.add(new_photo)
                        db.session.add(attraction)
                        db.session.commit()
                        
                        flash('Photo posted successfully!', 'success')
                    except Exception as e:
                        db.session.rollback()
                        flash(f'Error uploading photo: {str(e)}', 'error')
                        app.logger.error(f"Photo upload error: {str(e)}")
                
                return redirect(url_for('attraction_detail', attraction_id=attraction_id))
        
        except Exception as e:
            flash('An unexpected error occurred.', 'error')
            app.logger.error(f"Unexpected error in attraction_detail: {str(e)}")
    
    # Fetch photos sorted by upload date, most recent first
    photos = Photo.query.filter_by(attraction_id=attraction_id).order_by(Photo.upload_date.desc()).all()
    
    return render_template('attraction_detail.html', attraction=attraction, photos=photos)

@app.route('/add_attraction', methods=['GET', 'POST'])
def add_attraction():
    """Add a new attraction"""
    if request.method == 'POST':
        try:
            # Extract form data
            name = request.form['name']
            description = request.form['description']
            latitude = float(request.form['latitude'])
            longitude = float(request.form['longitude'])
            category = AttractionCategory(request.form['category'])
            weather = WeatherSuitability(request.form['weather'])
            
            # Create new attraction
            new_attraction = Attraction(
                name=name,
                description=description,
                latitude=latitude,
                longitude=longitude,
                category=category,
                weather_suitability=weather,
                average_rating=0,
                total_visits=0
            )
            
            # Add and commit the attraction first
            db.session.add(new_attraction)
            db.session.commit()

            # Handle photo uploads
            if 'photos' in request.files:
                photos = request.files.getlist('photos')
                photos_added = 0
                
                for photo in photos:
                    if photo and photo.filename:  # Ensure the file is not empty
                        try:
                            filename = photo_processor.process_and_save_image(
                                photo, 
                                app.config['UPLOAD_FOLDER'], 
                                target_size=(800, 600)
                            )
                            
                            # Create photo record
                            new_photo = Photo(
                                filename=filename,
                                attraction_id=new_attraction.id,
                                user_id=1234,
                                upload_date=datetime.utcnow()
                            )
                            db.session.add(new_photo)
                            photos_added += 1
                        
                        except Exception as e:
                            flash(f'Error processing image {photo.filename}: {str(e)}', 'error')
                            app.logger.error(f'Image processing error: {str(e)}')
                
                # Commit photo uploads
                try:
                    db.session.commit()
                    if photos_added > 0:
                        flash(f'Successfully added {photos_added} photo(s) to the attraction.', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash('Error saving photos. Please try again.', 'error')
                    app.logger.error(f'Photo upload commit error: {str(e)}')

            # Flash success message and redirect
            flash('Attraction added successfully!', 'success')
            return redirect(url_for('attraction_detail', attraction_id=new_attraction.id))

        except ValueError as ve:
            # Handle potential value conversion errors
            flash(f'Invalid input: {str(ve)}', 'error')
            db.session.rollback()
        except Exception as e:
            # Catch any other unexpected errors
            flash(f'An error occurred: {str(e)}', 'error')
            db.session.rollback()
            app.logger.error(f'Attraction creation error: {str(e)}')

    # GET request - render the form
    categories = [category.value for category in AttractionCategory]
    weathers = [weather.value for weather in WeatherSuitability]
    return render_template('add_attraction.html', categories=categories, weathers=weathers)

@app.route('/add_photo/<int:attraction_id>', methods=['POST'])
@login_required
def add_photo(attraction_id):
    """Add a photo to an attraction"""
    attraction = Attraction.query.get_or_404(attraction_id)
    
    # Handle photo upload
    if 'photo' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('attraction_detail', attraction_id=attraction_id))
    
    file = request.files['photo']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('attraction_detail', attraction_id=attraction_id))
    
    # Generate unique filename
    filename = generate_unique_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Create photo entry
    new_photo = Photo(
        filename=filename,
        caption=request.form['caption'],
        attraction_id=attraction_id,
        user_id=1234
    )
    db.session.add(new_photo)
    
    # Create review entry
    new_review = Review(
        rating=int(request.form['rating']),
        comment=request.form['caption'],
        attraction_id=attraction_id,
        user_id=1234,
        visit_date=datetime.utcnow()
    )
    db.session.add(new_review)
    
    # Update attraction statistics
    attraction.total_visits += 1
    attraction.average_rating = (attraction.average_rating * (attraction.total_visits - 1) + new_review.rating) / attraction.total_visits
    
    db.session.commit()
    
    flash('Photo and review added successfully!', 'success')
    return redirect(url_for('attraction_detail', attraction_id=attraction_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        # Create new user
        new_user = User(
            username=username, 
            email=email, 
            password=hashed_password
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/delete_photo/<int:photo_id>', methods=['POST'])
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    # Ensure only the owner or an admin can delete the photo
    if photo.user_id != 1234 and not current_user.is_admin:
        flash('You do not have permission to delete this photo.', 'danger')
        return redirect(url_for('attraction_detail', attraction_id=photo.attraction_id))
    
    attraction_id = photo.attraction_id
    db.session.delete(photo)
    db.session.commit()
    flash('Photo deleted successfully!', 'success')
    return redirect(url_for('attraction_detail', attraction_id=attraction_id))


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user_photos = Photo.query.filter_by(user_id=1234).order_by(Photo.upload_date.desc()).all()
    return render_template('profile.html', photos=user_photos)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)