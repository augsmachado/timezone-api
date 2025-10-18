from utils.timezones import (
    load_all_timezones,
    TZ_LOCATIONS,
)
from utils.geo import haversine


ALL_TIMEZONES = load_all_timezones()
def tz_region(latitude: float, longitude: float):
    regions = []
    regions.extend(
        name
        for name, bounds in TZ_LOCATIONS.items()
        if (
            bounds["min_latitude"] <= latitude <= bounds["max_latitude"]
            and bounds["min_longitude"] <= longitude <= bounds["max_longitude"]
        )
    )
    return {"regions": regions}

def tz_regions():
    return [
        {"name": name, **bounds}
        for name, bounds in TZ_LOCATIONS.items()
    ]

def tz_region_nearest(latitude: float, longitude: float):
    min_dist = None
    nearest_region = None
    for name, bounds in TZ_LOCATIONS.items():
        center_lat = (bounds["min_latitude"] + bounds["max_latitude"]) / 2
        center_lon = (bounds["min_longitude"] + bounds["max_longitude"]) / 2
        dist = haversine(latitude, longitude, center_lat, center_lon)
        if min_dist is None or dist < min_dist:
            min_dist = dist
            nearest_region = name
    return {"region": nearest_region, "distance_km": round(min_dist, 2) if min_dist is not None else None}

def tz_region_cities(region: str):
    region = region.lower()
    if region not in TZ_LOCATIONS:
        return {"error": "Region not found"}
    bounds = TZ_LOCATIONS[region]
    cities = [
        tz for tz in ALL_TIMEZONES
        if (
            bounds["min_latitude"] <= tz["latitude"] <= bounds["max_latitude"]
            and bounds["min_longitude"] <= tz["longitude"] <= bounds["max_longitude"]
        )
    ]
    return {"region": region, "cities": cities}

def cities_nearest(latitude: float, longitude: float):
    distances = []
    for tz in ALL_TIMEZONES:
        dist = haversine(latitude, longitude, tz["latitude"], tz["longitude"])
        distances.append((dist, tz))
    distances.sort(key=lambda x: x[0])
    nearest = [
        {
            "name": tz["name"],
            "latitude": tz["latitude"],
            "longitude": tz["longitude"],
            "distance_km": round(dist, 2),
            "utc_offset": tz["utc_offset"],
            "dst": tz["dst"],
            "region": tz["region"],
        }
        for dist, tz in distances[:4]
    ]
    tz_location = nearest[0]["name"] if nearest else None
    return {
        "tz_location": tz_location,
        "nearest_cities": nearest,
    }

def cities_in_radius(latitude: float, longitude: float, radius_km: float):
    result = []
    for city in ALL_TIMEZONES:
        dist = haversine(latitude, longitude, city["latitude"], city["longitude"])
        if dist <= radius_km:
            city_copy = city.copy()
            city_copy["distance_km"] = round(dist, 2)
            result.append(city_copy)
    result.sort(key=lambda c: c["distance_km"])
    return {"cities": result}

def cities_by_utc_offset(offset: float):
    result = []
    for city in ALL_TIMEZONES:
        if float(city.get("utc_offset", 0)) == offset:
            city_copy = city.copy()
            result.append(city_copy)
    return {"cities": result}

def cities_with_dst(dst: bool = True, region: str = None):
    result = []
    for city in ALL_TIMEZONES:
        if bool(city.get("dst", False)) == dst:
            if region and city["region"] != region:
                continue
            city_copy = city.copy()
            result.append(city_copy)
    return {"cities": result}

def city_extremes(offset: float):
    cities = [
        city
        for city in ALL_TIMEZONES
        if float(city.get("utc_offset", 0)) == offset
    ]
    if not cities:
        return {"error": "No cities found for this UTC offset."}
    north = max(cities, key=lambda c: c["latitude"])
    south = min(cities, key=lambda c: c["latitude"])
    east = max(cities, key=lambda c: c["longitude"])
    west = min(cities, key=lambda c: c["longitude"])
    return {
        "north": north,
        "south": south,
        "east": east,
        "west": west,
    }
