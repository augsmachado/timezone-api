import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils import (
    load_all_timezones,
    ALL_TIMEZONES,
    TZ_LOCATIONS,
    haversine,
)

app = FastAPI(
	title="Timestamp Utility API",
	version="1.0.0",
	description="API for status and timestamp conversion"
)

start_time = time.time()

# Allow CORS for all origins (optional, for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status")
def status():
	uptime = int(time.time() - start_time)
	return {
		"msg": "API status 🚀",
		"name": "timestamp-api",
		"version": app.version,
		"uptime": uptime,
	}

@app.get("/tz_region")
def tz_region(latitude: float, longitude: float):
    # Retorna as regiões que englobam o ponto (pode ser mais de uma)
    regions = []
    for name, bounds in TZ_LOCATIONS.items():
        if (
            bounds["min_latitude"] <= latitude <= bounds["max_latitude"]
            and bounds["min_longitude"] <= longitude <= bounds["max_longitude"]
        ):
            regions.append(name)
    return {"regions": regions}

@app.get("/tz_regions")
def tz_regions():
    # Retorna todas as regiões e seus limites
    return [
        {"name": name, **bounds}
        for name, bounds in TZ_LOCATIONS.items()
    ]

@app.get("/tz_region_nearest")
def tz_region_nearest(latitude: float, longitude: float):
    # Retorna a região mais próxima do ponto (menor distância até o centro do
    # retângulo) em km usando a fórmula de Haversine
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

@app.get("/tz_region_cities")
def tz_region_cities(region: str):
    # Retorna todas as cidades/timezones dentro da região informada.
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

@app.get("/cities_nearest")
def cities_nearest(latitude: float, longitude: float):
    # Calcula a distância das 4 cidades mais próximas do ponto
    distances = []
    for tz in ALL_TIMEZONES:
        dist = haversine(latitude, longitude, tz["latitude"], tz["longitude"])
        distances.append((dist, tz))

    # Ordena pelas menores distâncias
    distances.sort(key=lambda x: x[0])

    # Pega as 8 cidades mais próximas
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
    # Considera o timezone da cidade mais próxima como o do ponto
    tz_location = nearest[0]["name"] if nearest else None
    return {
        "tz_location": tz_location,
        "nearest_cities": nearest,
    }

@app.get("/cities_in_radius")
def cities_in_radius(latitude: float, longitude: float, radius_km: float):
    # Todas as cidades num raio em km do ponto.
    result = []
    for city in ALL_TIMEZONES:
        dist = haversine(latitude, longitude, city["latitude"], city["longitude"])
        if dist <= radius_km:
            city_copy = city.copy()
            city_copy["distance_km"] = round(dist, 2)
            result.append(city_copy)
    result.sort(key=lambda c: c["distance_km"])
    return {"cities": result}

@app.get("/cities_by_utc_offset")
def cities_by_utc_offset(offset: float):
    # Todas as cidades com UTC offset X.
    # Aceita tanto float quanto string (ex: -3, 5.5, "3.5")
    result = []
    for city in ALL_TIMEZONES:
        if float(city.get("utc_offset", 0)) == float(offset):
            city_copy = city.copy()
            result.append(city_copy)
    return {"cities": result}

@app.get("/cities_with_dst")
def cities_with_dst(dst: bool = True, region: str = None):
    # Todas as cidades que estão com DST (horário de verão) ativo ou não.
    # dst pode ser true ou false
    # region é opcional e filtra apenas cidades daquela região
    result = []
    for city in ALL_TIMEZONES:
        if bool(city.get("dst", False)) == dst:
            if region and city["region"] != region:
                continue
            city_copy = city.copy()
            result.append(city_copy)
    return {"cities": result}

@app.get("/city_extremes")
def city_extremes(offset: float):
    # Cidades mais ao norte, sul, leste, oeste de uma timezone utc offset
    # Filtra cidades pelo UTC offset
    cities = [
        city for city in ALL_TIMEZONES
        if float(city.get("utc_offset", 0)) == float(offset)
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
