from typing import Dict, List, Tuple
import math
import json
from pathlib import Path
from src.config import settings


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth
    
    Args:
        lat1, lon1: Latitude and longitude of point 1
        lat2, lon2: Latitude and longitude of point 2
    
    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r


def find_nearby_locations(
    user_lat: float, 
    user_lon: float, 
    max_distance_km: float = None
) -> List[Dict]:
    """
    Find stores near the user's location
    
    Args:
        user_lat: User's latitude
        user_lon: User's longitude
        max_distance_km: Maximum distance in km (default from settings)
    
    Returns:
        List of nearby stores sorted by distance
    """
    if max_distance_km is None:
        max_distance_km = settings.MAX_SEARCH_RADIUS_KM
    
    # Load locations
    locations_file = settings.LOCATIONS_FILE
    if not locations_file.exists():
        return []
    
    with open(locations_file, 'r') as f:
        locations = json.load(f)
    
    # Calculate distances and filter
    nearby = []
    for location in locations:
        loc_data = location['location']
        distance = haversine_distance(
            user_lat, user_lon,
            loc_data['latitude'], loc_data['longitude']
        )
        
        if distance <= max_distance_km:
            location_copy = location.copy()
            location_copy['distance_km'] = round(distance, 2)
            nearby.append(location_copy)
    
    # Sort by distance
    nearby.sort(key=lambda x: x['distance_km'])
    
    return nearby


def get_closest_location(user_lat: float, user_lon: float) -> Dict:
    """
    Get the single closest location to the user
    
    Args:
        user_lat: User's latitude
        user_lon: User's longitude
    
    Returns:
        Closest store or None
    """
    nearby = find_nearby_locations(user_lat, user_lon, max_distance_km=50)
    return nearby[0] if nearby else None


def format_location_info(location: Dict) -> str:
    """
    Format location information for display
    
    Args:
        location: Location dictionary
    
    Returns:
        Formatted string
    """
    distance = location.get('distance_km', 'N/A')
    wait_time = location.get('current_wait_time_min', 'N/A')
    
    info = f"""
📍 {location['name']}
📏 Distance: {distance} km
⏱️ Wait time: ~{wait_time} minutes
📫 Address: {location['location']['address']}
🕐 Hours: {location['business_hours']}
"""
    
    if location.get('amenities'):
        amenities = ', '.join(location['amenities'])
        info += f"✨ Amenities: {amenities}\n"
    
    return info.strip()


def is_weather_relevant(temperature_celsius: float, condition: str) -> Dict[str, bool]:
    """
    Determine weather-based recommendations
    
    Args:
        temperature_celsius: Current temperature
        condition: Weather condition (e.g., 'cold', 'hot', 'rainy')
    
    Returns:
        Dictionary of boolean flags for recommendations
    """
    return {
        'suggest_hot_drinks': temperature_celsius < 20 or condition == 'cold',
        'suggest_cold_drinks': temperature_celsius > 28 or condition == 'hot',
        'suggest_indoor': condition in ['rainy', 'stormy'],
        'suggest_seasonal': True  # Always show seasonal items
    }


def parse_user_location(location_str: str) -> Tuple[float, float]:
    """
    Parse location from user input (placeholder for future geocoding)
    
    Args:
        location_str: Location string (e.g., "Connaught Place, Delhi")
    
    Returns:
        (latitude, longitude) tuple, defaults to Delhi center if not found
    """
    # For MVP, return default Delhi location
    # In production, this would use a geocoding API
    default = settings.DEFAULT_LOCATION
    return default['latitude'], default['longitude']