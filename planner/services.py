# In planner/services.py
from .models import Destination
from users.models import UserProfile
import requests
from django.conf import settings
from .models import Itinerary

def get_ai_recommendations(user_profile: UserProfile):
    """
    A simple "AI" service to recommend destinations based on user profile.

    This is a "dummy" service. The logic here can be replaced with a real
    machine learning model in the future without changing the API.
    """
    
    # 1. Get user preferences
    style = user_profile.travel_style
    budget = user_profile.budget or 99999.99 # Use a high number if budget is not set

    # 2. Define a simple mapping from travel style to destination type
    style_to_destination_map = {
        UserProfile.TravelStyle.ADVENTURE: [Destination.DestinationType.HIKING_TRAIL, Destination.DestinationType.PARK],
        UserProfile.TravelStyle.RELAXATION: [Destination.DestinationType.PARK, Destination.DestinationType.BEACH, Destination.DestinationType.LANDMARK],
        UserProfile.TravelStyle.CULTURAL: [Destination.DestinationType.MUSEUM, Destination.DestinationType.LANDMARK],
        # Define mappings for other styles as you add them
        UserProfile.TravelStyle.FAMILY: [Destination.DestinationType.PARK, Destination.DestinationType.MUSEUM],
        UserProfile.TravelStyle.BUDGET: [Destination.DestinationType.PARK, Destination.DestinationType.MUSEUM],
    }

    # 3. Filter destinations based on the mapping and budget
    preferred_types = style_to_destination_map.get(style, [])
    
    if not preferred_types:
        # If the style has no mapping, return a generic list of affordable places
        recommendations = Destination.objects.filter(average_cost__lte=budget).order_by('?')[:5]
    else:
        # Find destinations that match the preferred types and are within budget
        recommendations = Destination.objects.filter(
            destination_type__in=preferred_types,
            average_cost__lte=budget
        ).order_by('?') # '?' orders them randomly
    
    # Limit to 5 suggestions for a clean response
    return recommendations[:5]

def get_weather_alerts_for_itinerary(itinerary: Itinerary):
    """
    Fetches weather forecasts for the unique cities in an itinerary.
    """
    # 1. Get unique cities from the itinerary to avoid duplicate API calls
    destinations = itinerary.items.select_related('destination').all()
    unique_cities = {item.destination.city for item in destinations}

    if not unique_cities:
        return {"message": "No destinations in this itinerary to fetch weather for."}

    # 2. Prepare to call the weather API for each city
    api_key = settings.OPENWEATHER_API_KEY
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    weather_data = []

    for city in unique_cities:
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'  # Get temperature in Celsius
        }
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()

            # 3. Format the data cleanly for our response
            weather_data.append({
                "city": city,
                "temperature": data['main']['temp'],
                "feels_like": data['main']['feels_like'],
                "description": data['weather'][0]['description'].title(),
                "icon_code": data['weather'][0]['icon'],
                # You can build the full icon URL on the frontend like this:
                # `http://openweathermap.org/img/wn/{icon_code}@2x.png`
            })
        except requests.exceptions.HTTPError as e:
            # Handle cases where city is not found (404) or other API errors
            weather_data.append({"city": city, "error": f"Could not retrieve weather data. {e}"})
        except Exception as e:
            weather_data.append({"city": city, "error": f"An unexpected error occurred. {e}"})
    
    return weather_data

def get_optimized_route_for_itinerary(itinerary: Itinerary):
    """
    Fetches an optimized route connecting all destinations in an itinerary
    for a specific day (or the whole trip).
    """
    # 1. Get the coordinates of all destinations in the itinerary
    # We order them by day number to make the route logical
    items = itinerary.items.order_by('day_number', 'start_time').select_related('destination')
    
    if items.count() < 2:
        return {"error": "At least two destinations are required to calculate a route."}

    # Format coordinates for the ORS API: [[lon, lat], [lon, lat], ...]
    coordinates = [
        [item.destination.longitude, item.destination.latitude] for item in items
    ]

    # 2. Call the OpenRouteService API
    api_key = settings.OPENROUTESERVICE_API_KEY
    # ORS requires a POST request with the coordinates in the body
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json',
    }
    # We use the 'directions' endpoint with the 'driving-car' profile
    body = {
        "coordinates": coordinates,
        # 'radiuses' helps ORS snap points to the nearest road. -1 means infinite radius.
        "radiuses": [-1] * len(coordinates)
    }
    
    try:
        response = requests.post(
            'https://api.openrouteservice.org/v2/directions/driving-car/geojson',
            json=body,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

        # 3. Extract the key information: the route geometry, distance, and duration
        route = data['features'][0]
        summary = route['properties']['summary']

        return {
            # The geometry is a GeoJSON LineString, perfect for mapping libraries like Leaflet
            "route_geometry": route['geometry']['coordinates'],
            # Distance is in meters, Duration is in seconds
            "total_distance_km": round(summary['distance'] / 1000, 2),
            "total_duration_hours": round(summary['duration'] / 3600, 2),
        }
    except requests.exceptions.HTTPError as e:
        return {"error": f"Failed to get route from ORS. {e.response.text}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred. {e}"}
