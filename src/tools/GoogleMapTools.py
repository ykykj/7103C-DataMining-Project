"""
Google Maps API Tools Integration
Provides location search, geocoding, directions, and places functionality
Uses Google Routes API v2 for advanced routing with real-time traffic
"""
from typing import List, Optional, Dict, Any
from langchain.tools import tool
import googlemaps
import requests
from datetime import datetime
from src.config import settings


# Lazy initialization of Google Maps client
_gmaps_client = None


def _get_gmaps_client():
    """Lazy initialization of Google Maps client"""
    global _gmaps_client
    if _gmaps_client is None and settings.google_maps_api_key:
        _gmaps_client = googlemaps.Client(key=settings.google_maps_api_key)
    return _gmaps_client


@tool
def searchPlace(query: str, language: str = "zh-CN") -> str:
    """
    Search for places using Google Maps Places API.
    
    Parameters:
    ----------
    query : str
        Search query (e.g., "restaurants near me", "Starbucks in Beijing", "hotels")
    language : str, optional
        Language for results (default: "zh-CN" for Chinese, use "en" for English)
    
    Returns:
    -------
    str
        Formatted list of places with name, address, rating, and location
    
    Notes:
    -----
    - Supports both Chinese and English queries
    - Returns top results with detailed information
    - Use for finding restaurants, hotels, shops, attractions, etc.
    """
    client = _get_gmaps_client()
    if not client:
        return "Error: Google Maps API not configured. Please set GOOGLE_MAPS_API_KEY."
    
    try:
        # Use Text Search API
        results = client.places(query=query, language=language)
        
        if not results.get('results'):
            return f"No places found for '{query}'."
        
        # Format results
        formatted_results = []
        formatted_results.append(f"Found {len(results['results'])} places:\n")
        
        for idx, place in enumerate(results['results'][:10], 1):  # Limit to top 10
            name = place.get('name', 'Unknown')
            address = place.get('formatted_address', 'Address unknown')
            rating = place.get('rating', 'N/A')
            user_ratings = place.get('user_ratings_total', 0)
            location = place.get('geometry', {}).get('location', {})
            lat = location.get('lat', 'N/A')
            lng = location.get('lng', 'N/A')
            
            formatted_results.append(f"{idx}. {name}")
            formatted_results.append(f"   Address: {address}")
            formatted_results.append(f"   Rating: {rating} ({user_ratings} reviews)")
            formatted_results.append(f"   Coordinates: {lat}, {lng}")
            
            # Add place types if available
            if place.get('types'):
                types = ', '.join(place['types'][:3])
                formatted_results.append(f"   Types: {types}")
            
            formatted_results.append("")
        
        return "\n".join(formatted_results)
    
    except Exception as e:
        return f"Search failed: {str(e)}"


@tool
def geocodeAddress(address: str, language: str = "zh-CN") -> str:
    """
    Convert an address to geographic coordinates (latitude, longitude).
    
    Parameters:
    ----------
    address : str
        Address to geocode (e.g., "北京市朝阳区", "1600 Amphitheatre Parkway, Mountain View, CA")
    language : str, optional
        Language for results (default: "zh-CN")
    
    Returns:
    -------
    str
        Formatted address with coordinates and location details
    
    Notes:
    -----
    - Supports both Chinese and English addresses
    - Returns precise coordinates for navigation
    - Use for address validation and location lookup
    """
    client = _get_gmaps_client()
    if not client:
        return "Error: Google Maps API not configured. Please set GOOGLE_MAPS_API_KEY."
    
    try:
        results = client.geocode(address, language=language)
        
        if not results:
            return f"Unable to geocode address: {address}"
        
        # Get the first (best) result
        result = results[0]
        location = result['geometry']['location']
        formatted_address = result['formatted_address']
        
        output = []
        output.append(f"Address: {formatted_address}")
        output.append(f"Coordinates: {location['lat']}, {location['lng']}")
        
        # Add address components
        components = result.get('address_components', [])
        if components:
            output.append("\nDetails:")
            for component in components:
                types = ', '.join(component['types'])
                output.append(f"  {component['long_name']} ({types})")
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Geocoding failed: {str(e)}"


@tool
def reverseGeocode(latitude: float, longitude: float, language: str = "zh-CN") -> str:
    """
    Convert coordinates to a human-readable address.
    
    Parameters:
    ----------
    latitude : float
        Latitude coordinate
    longitude : float
        Longitude coordinate
    language : str, optional
        Language for results (default: "zh-CN")
    
    Returns:
    -------
    str
        Formatted address for the given coordinates
    
    Notes:
    -----
    - Converts GPS coordinates to readable addresses
    - Useful for location sharing and navigation
    """
    client = _get_gmaps_client()
    if not client:
        return "Error: Google Maps API not configured. Please set GOOGLE_MAPS_API_KEY."
    
    try:
        results = client.reverse_geocode((latitude, longitude), language=language)
        
        if not results:
            return f"Unable to find address for coordinates ({latitude}, {longitude})"
        
        # Return the most specific address (first result)
        return f"Address: {results[0]['formatted_address']}"
    
    except Exception as e:
        return f"Reverse geocoding failed: {str(e)}"


@tool
def getDirections(
    origin: str,
    destination: str,
    mode: str = "DRIVE",
    language: str = "zh-CN",
    route_preference: str = "TRAFFIC_AWARE"
) -> str:
    """
    Get directions between two locations using Google Routes API v2.
    
    Parameters:
    ----------
    origin : str
        Starting location (address or place name)
    destination : str
        Destination location (address or place name)
    mode : str, optional
        Travel mode: "DRIVE", "WALK", "BICYCLE", or "TRANSIT" (default: "DRIVE")
        TRANSIT includes bus, MTR, train, and other public transportation
    language : str, optional
        Language for results (default: "zh-CN")
    route_preference : str, optional
        Route preference: "TRAFFIC_AWARE" (fastest with traffic), "TRAFFIC_AWARE_OPTIMAL" (balanced),
        "TRAFFIC_UNAWARE" (ignore traffic), "FUEL_EFFICIENT" (save fuel) (default: "TRAFFIC_AWARE")
        Note: Only applies to DRIVE, WALK, BICYCLE modes
    
    Returns:
    -------
    str
        Formatted directions with distance, duration, and step-by-step instructions
    
    Notes:
    -----
    - Uses Google Routes API v2 for all travel modes with real-time data
    - For TRANSIT: includes specific bus/train lines, stops, departure/arrival times
    - For DRIVE/WALK/BICYCLE: includes turn-by-turn navigation with traffic-aware ETAs
    - Includes toll information, warnings, and route quality indicators
    """
    import requests
    import re
    
    if not settings.google_maps_api_key:
        return "Error: Google Maps API not configured. Please set GOOGLE_MAPS_API_KEY."
    
    try:
        # Map old mode names to new API format
        mode_mapping = {
            "driving": "DRIVE",
            "walking": "WALK",
            "bicycling": "BICYCLE",
            "transit": "TRANSIT"
        }
        mode = mode_mapping.get(mode.lower(), mode.upper())
        
        # Routes API v2 endpoint
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": settings.google_maps_api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline,routes.legs.steps,routes.legs.localizedValues,routes.description,routes.warnings,routes.travelAdvisory"
        }
        
        payload = {
            "origin": {
                "address": origin
            },
            "destination": {
                "address": destination
            },
            "travelMode": mode,
            "languageCode": language,
            "units": "METRIC",
            "computeAlternativeRoutes": False
        }
        
        # Only add routing preference for non-TRANSIT modes
        if mode != "TRANSIT":
            payload["routingPreference"] = route_preference
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('routes'):
            return f"Unable to find route from {origin} to {destination}"
        
        # Get the first (best) route
        route = data['routes'][0]
        leg = route['legs'][0]
        
        output = []
        
        # Basic route information
        output.append(f"Route: {origin} → {destination}")
        
        # Distance and duration
        distance_km = route.get('distanceMeters', 0) / 1000
        duration_text = leg.get('localizedValues', {}).get('duration', {}).get('text', 'N/A')
        output.append(f"Distance: {distance_km:.1f} km")
        output.append(f"Duration: {duration_text}")
        output.append(f"Travel mode: {mode}")
        
        # Route description (if available)
        if route.get('description'):
            output.append(f"Route: {route['description']}")
        
        # Traffic and warnings
        if route.get('travelAdvisory'):
            advisory = route['travelAdvisory']
            if advisory.get('tollInfo'):
                output.append("⚠️  This route includes tolls")
            if advisory.get('speedReadingIntervals'):
                output.append("🚦 Real-time traffic data available")
        
        if route.get('warnings'):
            for warning in route['warnings']:
                output.append(f"⚠️  {warning}")
        
        output.append("")
        
        # Step-by-step directions
        output.append("Directions:")
        steps = leg.get('steps', [])
        
        for idx, step in enumerate(steps, 1):
            travel_mode = step.get('travelMode', 'WALK')
            
            # Handle TRANSIT steps (bus, train, subway, etc.)
            if travel_mode == 'TRANSIT':
                transit_details = step.get('transitDetails', {})
                stop_details = transit_details.get('stopDetails', {})
                transit_line = transit_details.get('transitLine', {})
                
                # Get transit line information
                line_name = transit_line.get('name', 'Unknown Line')
                vehicle = transit_line.get('vehicle', {})
                vehicle_type = vehicle.get('name', {}).get('text', 'Transit')
                
                # Get stop information
                departure_stop = stop_details.get('departureStop', {}).get('name', 'Unknown')
                arrival_stop = stop_details.get('arrivalStop', {}).get('name', 'Unknown')
                stop_count = transit_details.get('stopCount', 0)
                
                # Get time information
                departure_time = stop_details.get('localizedValues', {}).get('departureTime', {}).get('time', {}).get('text', '')
                arrival_time = stop_details.get('localizedValues', {}).get('arrivalTime', {}).get('time', {}).get('text', '')
                
                # Get duration
                duration_text = step.get('localizedValues', {}).get('staticDuration', {}).get('text', '')
                distance_text = step.get('localizedValues', {}).get('distance', {}).get('text', '')
                
                output.append(f"\n{idx}. Take {vehicle_type}: {line_name}")
                output.append(f"   Board at: {departure_stop}")
                if departure_time:
                    output.append(f"   Departure: {departure_time}")
                output.append(f"   Get off at: {arrival_stop}")
                if arrival_time:
                    output.append(f"   Arrival: {arrival_time}")
                output.append(f"   Stops: {stop_count}")
                output.append(f"   Duration: {duration_text}")
                if distance_text:
                    output.append(f"   Distance: {distance_text}")
                
            else:
                # Handle WALK, DRIVE, BICYCLE steps
                instruction = step.get('navigationInstruction', {}).get('instructions', '')
                
                if not instruction:
                    # Fallback to maneuver type
                    maneuver = step.get('navigationInstruction', {}).get('maneuver', '')
                    if maneuver:
                        instruction = maneuver.replace('_', ' ').title()
                    else:
                        instruction = f"{travel_mode.title()}"
                
                # Clean HTML tags if present
                instruction = re.sub(r'<[^>]+>', '', instruction)
                
                # Get localized values
                distance_text = step.get('localizedValues', {}).get('distance', {}).get('text', '')
                duration_text = step.get('localizedValues', {}).get('staticDuration', {}).get('text', '')
                
                output.append(f"\n{idx}. {instruction}")
                if distance_text:
                    output.append(f"   Distance: {distance_text}")
                if duration_text:
                    output.append(f"   Duration: {duration_text}")
        
        return "\n".join(output)
    
    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_data = e.response.json()
            error_detail = error_data.get('error', {}).get('message', str(e))
        except:
            error_detail = str(e)
        return f"Routes API error: {error_detail}"
    except Exception as e:
        return f"Directions query failed: {str(e)}"


@tool
def findNearbyPlaces(
    location: str,
    place_type: str = "restaurant",
    radius: int = 1000,
    language: str = "zh-CN"
) -> str:
    """
    Find nearby places of a specific type around a location.
    
    Parameters:
    ----------
    location : str
        Center location (address or place name)
    place_type : str, optional
        Type of place to search for (e.g., "restaurant", "cafe", "hotel", "gas_station", "hospital")
        Full list: https://developers.google.com/maps/documentation/places/web-service/supported_types
    radius : int, optional
        Search radius in meters (default: 1000, max: 50000)
    language : str, optional
        Language for results (default: "zh-CN")
    
    Returns:
    -------
    str
        Formatted list of nearby places with details
    
    Notes:
    -----
    - Search for specific types of places nearby
    - Useful for finding restaurants, gas stations, hotels, etc.
    - Results sorted by prominence
    """
    client = _get_gmaps_client()
    if not client:
        return "Error: Google Maps API not configured. Please set GOOGLE_MAPS_API_KEY."
    
    try:
        # First geocode the location to get coordinates
        geocode_result = client.geocode(location, language=language)
        if not geocode_result:
            return f"Unable to recognize location: {location}"
        
        coords = geocode_result[0]['geometry']['location']
        
        # Search for nearby places
        results = client.places_nearby(
            location=(coords['lat'], coords['lng']),
            radius=radius,
            type=place_type,
            language=language
        )
        
        if not results.get('results'):
            return f"No {place_type} found within {radius} meters of {location}"
        
        # Format results
        output = []
        output.append(f"Found {len(results['results'])} {place_type} near {location}:\n")
        
        for idx, place in enumerate(results['results'][:10], 1):
            name = place.get('name', 'Unknown')
            vicinity = place.get('vicinity', 'Address unknown')
            rating = place.get('rating', 'N/A')
            
            output.append(f"{idx}. {name}")
            output.append(f"   Address: {vicinity}")
            output.append(f"   Rating: {rating}")
            
            # Calculate distance if available
            if place.get('geometry', {}).get('location'):
                place_loc = place['geometry']['location']
                # Simple distance calculation (not precise, just for reference)
                output.append(f"   Coordinates: {place_loc['lat']}, {place_loc['lng']}")
            
            if place.get('opening_hours'):
                is_open = place['opening_hours'].get('open_now', False)
                status = "Open" if is_open else "Closed"
                output.append(f"   Status: {status}")
            
            output.append("")
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Nearby search failed: {str(e)}"


def get_google_maps_tools() -> List:
    """
    Get all available Google Maps tools.
    
    Returns:
    -------
    List
        List of Google Maps tools for LangChain agents
    """
    if not settings.google_maps_api_key:
        print("Warning: Google Maps API key not configured")
        return []
    
    return [
        searchPlace,
        geocodeAddress,
        reverseGeocode,
        getDirections,
        findNearbyPlaces
    ]
