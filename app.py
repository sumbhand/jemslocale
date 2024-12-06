from flask import Flask, request, render_template, redirect, url_for, send_file, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
import os
import qrcode
from io import BytesIO
from werkzeug.utils import secure_filename  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///locations.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

ADMIN_SESSION_ID = 'admin_session'

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    gps = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    photo_filename = db.Column(db.String(100), nullable=True)
    url = db.Column(db.String(200), nullable=False, default="")
    photos = db.relationship('Photo', backref='location', lazy=True)
    experiences = db.relationship('Experience', backref='location', lazy=True)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    expiry_time = db.Column(db.DateTime, nullable=False)

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)

with app.app_context():
    db.create_all()

@app.template_filter('to_datetime')
def to_datetime_filter(value):
    if isinstance(value, datetime):
        return value
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/location/<int:location_id>', methods=['GET', 'POST'])
def location(location_id):
    location = Location.query.get_or_404(location_id)
    if request.method == 'POST':
        if 'photo' in request.files and 'caption' in request.form and 'rating' in request.form:
            photo = request.files['photo']
            caption = request.form['caption']
            rating = int(request.form['rating'])
            session_id = session.get('session_id')
            expiry_time = datetime.utcnow() + timedelta(minutes=5)

            if not session_id:
                session_id = os.urandom(16).hex()
                session['session_id'] = session_id

            ensure_upload_folder_exists()
            filename = secure_filename(f"{location.name.replace(' ', '_')}_{photo.filename.replace(' ', '_')}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(filepath)
            new_photo = Photo(filename=filename, caption=caption, rating=rating, location_id=location_id, session_id=session_id, expiry_time=expiry_time)
            db.session.add(new_photo)
            db.session.commit()
            
            # Update Location with the latest photo
            location.photo_filename = filename
            db.session.commit()

        if 'name' in request.form and 'description' in request.form:
            location.name = request.form['name']
            location.description = request.form['description']
            if 'cover_photo' in request.files:
                cover_photo = request.files['cover_photo']
                filename = secure_filename(f"{location.name.replace(' ', '_')}_{cover_photo.filename.replace(' ', '_')}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                cover_photo.save(filepath)
                location.photo_filename = filename
            db.session.commit()

        return redirect(url_for('location', location_id=location_id))
        
    photos = Photo.query.filter_by(location_id=location_id).all()
    experiences = Experience.query.filter_by(location_id=location_id).all()
    return render_template('location.html', location=location, photos=photos, experiences=experiences)


@app.route('/generate_qr', methods=['GET', 'POST'])  
def generate_qr():  
    if session.get('session_id') != ADMIN_SESSION_ID:  
        flash("You are not authorized to generate a QR code.")  
        return redirect(url_for('index'))
      
    if request.method == 'POST':  
        location_id = request.form.get('location_id')  
        name = request.form.get('name')  
        description = request.form.get('description')  
        photo = request.files.get('photo')  
  
        if location_id:  
            location = Location.query.get_or_404(location_id)  
        else:  
            # Handle new location creation  
            if not name or not description or not photo:  
                flash("Name, description, and photo are required for creating a new location.")  
                return redirect(url_for('generate_qr'))  
  
            ensure_upload_folder_exists()  
            filename = f"{name.replace(' ', '_')}_{photo.filename.replace(' ', '_')}"  
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)  
            photo.save(filepath)  
  
            location = Location(  
                name=name,   
                description=description,   
                gps="0.0",   
                photo_filename=filename  
            )  
            db.session.add(location)  
            db.session.commit()  
  
        # Construct the URL of the location's detail page  
        location_url = url_for('location', location_id=location.id, _external=True)  
          
        # Update the location with the generated URL and save it to the database  
        location.url = location_url  
        db.session.commit()  
  
        # Print the URL in the console  
        print(f"Location URL: {location_url}")  
  
        qr = qrcode.QRCode(  
            version=1,  
            error_correction=qrcode.constants.ERROR_CORRECT_L,  
            box_size=10,  
            border=4,  
        )  
        qr.add_data(location_url)  
        qr.make(fit=True)  
          
        img = qr.make_image(fill_color="black", back_color="white")  
        buf = BytesIO()  
        img.save(buf)  
        buf.seek(0)  
          
        return send_file(buf, mimetype='image/png', as_attachment=True, download_name=f'{location.name}_qr.png')  
      
    locations = Location.query.all()  
    return render_template('generate_qr.html', locations=locations)


def ensure_upload_folder_exists():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'adminpass':
            session['session_id'] = ADMIN_SESSION_ID
            flash("Logged in as admin.")
        else:
            flash("Invalid credentials.")
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('session_id', None)
    flash("Logged out.")
    return redirect(url_for('index'))

@app.route('/delete_photo/<int:photo_id>', methods=['POST'])
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    session_id = session.get('session_id')
    now = datetime.utcnow()

    if session_id == ADMIN_SESSION_ID or (session_id == photo.session_id and now < photo.expiry_time):
        db.session.delete(photo)
        db.session.commit()
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], photo.filename))
        flash("Photo deleted.")
    else:
        flash("You are not authorized to delete this photo.")
    return redirect(request.referrer)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
