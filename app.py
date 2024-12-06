from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
import os

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

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        location_data = request.form.get('location_data')
        if location_data:
            try:
                name, gps, description = location_data.split('|')
                location = Location.query.filter_by(name=name).first()
                if not location:
                    location = Location(name=name, gps=gps, description=description)
                    db.session.add(location)
                    db.session.commit()

                return redirect(url_for('location', location_id=location.id))
            except ValueError:
                return "Invalid QR Code data format.", 400
    return render_template('scan.html')

def ensure_upload_folder_exists():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

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
            filename = f"{location.name.replace(' ', '_')}_{photo.filename.replace(' ', '_')}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(filepath)
            new_photo = Photo(filename=filename, caption=caption, rating=rating, location_id=location_id, session_id=session_id, expiry_time=expiry_time)
            db.session.add(new_photo)
            db.session.commit()

        return redirect(url_for('location', location_id=location_id))
        
    photos = Photo.query.filter_by(location_id=location_id).all()
    experiences = Experience.query.filter_by(location_id=location_id).all()
    return render_template('location.html', location=location, photos=photos, experiences=experiences)

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
    current_time = datetime.utcnow()
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
