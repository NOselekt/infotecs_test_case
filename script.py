
if __name__ == "__main__":
	import os
	os.system("pip install -r requirements.txt")
	os.system("python -m uvicorn script:app")


from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import RedirectResponse
import requests
import sqlite3
import datetime
import asyncio
from typing import Iterable


# Constants
URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_PARAMS = {
	"latitude": 0.0,
	"longitude": 0.0,
	"current": ["temperature_2m", "surface_pressure", "wind_speed_10m"]
}
UPDATE_INTERVAL = 60*15  # 15 minutes

# Connecting to the SQLite database
connection = sqlite3.connect("cities_weather.db", check_same_thread=False)
cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS Cities(
id INTEGER PRIMARY KEY,
name STRING NOT NULL,
latitude DOUBLE NOT NULL,
longitude DOUBLE NOT NULL,
temperature FLOAT NOT NULL,
pressure FLOAT NOT NULL,
wind_speed FLOAT NOT NULL,
last_update_time DOUBLE NOT NULL
)
''')
connection.commit()

async def get_weather(latitude: float, longitude: float,
					  start_time: str = str(datetime.datetime.now().replace(microsecond=0).isoformat()),
					  end_time: str = str(datetime.datetime.now().replace(microsecond=0).isoformat())):
	'''
	Gets weather data for a given location and time period.
	:param latitude: latitude of the place to get weather data for
	:param longitude: longitude of the place to get weather data for
	:param start_time: start of the given time period in ISO 8601 format
	:param end_time: end of the given time period in ISO 8601 format
	:return: dictionary with weather data.
	'''
	params = DEFAULT_PARAMS.copy()
	params["latitude"] = latitude
	params["longitude"] = longitude
	params["start_minutely"] = start_time
	params["end_minutely"] = end_time
	try:
		response = requests.get(URL, params=params).json()
	except requests.exceptions.ConnectionError:
		raise HTTPException(status_code=503, detail="Failed to get response from open-meteo.")
	temp = response["current"]["temperature_2m"]
	pressure = response["current"]["surface_pressure"]
	wind_speed = response["current"]["wind_speed_10m"]
	current_time = str(datetime.datetime.now().replace(microsecond=0).isoformat())
	result = {
		"latitude": latitude,
		"longitude": longitude,
		"temperature": temp,
		"pressure": pressure,
		"wind_speed": wind_speed,
		"last_update_time": current_time,
	}
	return result

async def city_update(city: Iterable = None):
	'''
	Updates the weather data for a given city.
	:param city: city to update weather data for
	:return: None
	'''
	if city:
		last_update_time = str(datetime.datetime.now().replace(microsecond=0).isoformat())
		result = await get_weather(city[2], city[3], last_update_time, last_update_time)
		try:
			cursor.execute("UPDATE Cities SET temperature=?, pressure=?, wind_speed=?, last_update_time=? WHERE id=?",
						   (result["temperature"], result["pressure"],
							result["wind_speed"], last_update_time, city[0]))
			connection.commit()
		except sqlite3.Error as e:
			print(f"Error updating city {city[1]}: {e}")


async def setup():
	'''
	Sets up the weather update loop.
	:return: None
	'''
	while True:
		try:
			cities = cursor.execute("SELECT * FROM Cities").fetchall()
		except sqlite3.Error as e:
			print(f"Error fetching cities: {e}")
			continue
		for city in cities:
			await city_update(city)
		await asyncio.sleep(UPDATE_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
	'''
	Starts functions that must run on setup.
	:param app: FastAPI instance.
	:return:
	'''
	asyncio.create_task(setup())
	yield
app = FastAPI(lifespan=lifespan)


@app.get("/")
async def home() -> RedirectResponse:
	'''
    Redirects to the documentation page for better experience.
    :return: RedirectResponse to the FastAPI documentation page
    '''
	return RedirectResponse("/docs")

@app.get("/{latitude}&{longitude}")
async def get_current_weather(latitude: float = Path(ge=-90, le=90, examples=[57.002]),
                      		  longitude: float= Path(ge=-180, le=180, examples=[12.004])) -> dict:
	'''
	Returns the weather in the place with given latitude and longitude.
	:param latitude: latitude of the place to see weather in
	:param longitude: longitude of the place to see weather in
	:return: dictionary of current weather data in the given place
	'''
	result = await get_weather(latitude, longitude)
	return result

@app.get("/{city_name}/{latitude}&{longitude}")
async def add_city(city_name: str = Path(min_length=1, max_length=30, examples=["Saint-Petersburg"]),
				   latitude: float = Path(ge=-90, le=90, examples=[57.3842]),
				   longitude: float = Path(ge=-180, le=180, examples=[12.004])) -> dict:
	'''
    Adds city to the database and returns its current weather.
    :param city_name: name of the city to add
    :param latitude: latitude of the city
    :param longitude: longitude of the city
    :return: dictionary of current weather data in the added city with city name and current now
    '''
	result = await get_weather(latitude, longitude)
	try:
		cursor.execute("INSERT INTO Cities VALUES (NULL,?,?,?,?,?,?,?)",
						(city_name, *result.values(),))
		connection.commit()
	except sqlite3.Error as e:
		raise HTTPException(status_code=500, detail="Failed to add city to the database.")
	result["city_name"] = city_name
	return result

@app.get("/cities")
async def get_cities() -> list:
	'''
    Returns list of all cities in the database.
    :return: list of city names
    '''
	try:
		cursor.execute("SELECT name FROM Cities")
	except sqlite3.Error as e:
		raise HTTPException(status_code=500, detail="Failed to fetch cities from the database.")
	result = [city[0] for city in cursor.fetchall()]
	return result

@app.get("/{city_name}/{scan_time}")
async def get_city_weather(city_name: str = Path(min_length=1, max_length=30, examples=("Saint-Petersburg",)),
						   scan_time: str = Path(min_length=5, max_length=5,
											description="Write date and time specified as in example.",
											examples=["12:00"])) -> dict:
	'''
	Returns weather in the place with given city name and time.
	:param city_name: name of the city to see weather in
	:param scan_time: time of the weather to see in ISO8601 format
	:return: dictionary of the weather data in the given place at the specified now
	'''
	try:
		latitude, longitude = cursor.execute("SELECT latitude, longitude FROM Cities WHERE name = ?",
									 (city_name,)).fetchone()
	except TypeError as e:
		raise HTTPException(status_code=404, detail=f"City {city_name} not found.")
	scan_time = str(datetime.datetime.now().replace(microsecond=0).isoformat())[:11] + scan_time
	result = await get_weather(latitude, longitude, scan_time, scan_time)
	result["city_name"] = city_name
	result["last_update_time"] = scan_time
	return result


# Program setup




