import googlemaps
from dataclasses import dataclass, field
from enum import Enum
from typing import List
# Assuming the existing Attraction and related classes are defined
class AttractionCategory(Enum):
    NATURE = "Nature"
    RECREATION = "Recreation"
    DINING = "Dining"
    HISTORICAL = "Historical"
    ENTERTAINMENT = "Entertainment"

class WeatherSuitability(Enum):
    ALL_WEATHER = "All Weather"
    FAIR_WEATHER = "Fair Weather"

@dataclass
class Attraction:
    name: str
    description: str
    latitude: float
    longitude: float
    category: AttractionCategory
    weather_suitability: WeatherSuitability
    average_rating: float

def geocode_attractions(attractions: List[Attraction], api_key: str) -> List[Attraction]:
    """
    Update attractions with precise geocoding coordinates using Google Maps Geocoding API.
    
    :param attractions: List of Attraction objects
    :param api_key: Google Maps API key
    :return: Updated list of Attraction objects with verified coordinates
    """
    # Initialize Google Maps client
    gmaps = googlemaps.Client(key=api_key)
    
    updated_attractions = []
    
    for attraction in attractions:
        try:
            # Perform geocoding
            geocode_result = gmaps.geocode(attraction.name)
            
            if geocode_result:
                # Get the first result's geometry location
                location = geocode_result[0]['geometry']['location']
                
                # Create an updated attraction with precise coordinates
                updated_attraction = Attraction(
                    name=attraction.name,
                    description=attraction.description,
                    latitude=location['lat'],
                    longitude=location['lng'],
                    category=attraction.category,
                    weather_suitability=attraction.weather_suitability,
                    average_rating=attraction.average_rating
                )
                
                print(f"Updated {attraction.name}:")
                print(f"  Old coordinates: {attraction.latitude}, {attraction.longitude}")
                print(f"  New coordinates: {location['lat']}, {location['lng']}")
                
                updated_attractions.append(updated_attraction)
            else:
                print(f"No geocoding results found for {attraction.name}")
                updated_attractions.append(attraction)
        
        except Exception as e:
            print(f"Error geocoding {attraction.name}: {e}")
            updated_attractions.append(attraction)
    
    return updated_attractions

# Example usage
def main():
    # Replace with your actual Google Maps API key
    API_KEY = 'AIzaSyCBlI94ILrAMym6umwIpjKCYytGnljbGFo'
    
    # Attractions to geocode
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
        # Add other attractions from the original list
    ]
    
    # Geocode attractions
    updated_attractions = geocode_attractions(attractions, API_KEY)
    print(updated_attractions)
    
    # You can further process or store the updated attractions as needed

if __name__ == "__main__":
    main()
