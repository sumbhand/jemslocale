from app import db, Location

def add_location(name, gps, description):
    location = Location(name=name, gps=gps, description=description)
    db.session.add(location)
    db.session.commit()
    generate_qr(location.id, 'http://192.168.86.21:5000')  # Replace with the actual base URL

def prestore_locations():
    locations = [
        {"name": "Statue of Liberty", "gps": "40.6892,-74.0445", "description": "An iconic symbol of freedom."},
        {"name": "Eiffel Tower", "gps": "48.8584,2.2945", "description": "A wrought-iron lattice tower in Paris, France."},
        # Add more predefined locations here
    ]

    for location in locations:
        add_location(location["name"], location["gps"], location["description"])

if __name__ == "__main__":
    with app.app_context():
        prestore_locations()
        db.session.commit()
