# Русский
Для старта сервера просто запустите файл script.py. Он автоматически установит необходимые библиотеки и модули и запустит приложение. 
Так как в ТЗ было указано, что решение должно содержать только файл script.py, в проекте отсутствуют HTML-шаблоны и стили. По этой причине при открытии главной страницы 
(http://127.0.0.1:8000/ в случае локального запуска) вас перенаправит на страницу встроенной документации FastAPI для полноценного пользования методами.
## Methods
#### get_weather()
	:param latitude: широта места для получения данных о погоде
	:param longitude: долгота места для получения данных о погоде
	:param start_time: начало заданного периода времени в формате ISO 8601
	:param end_time: окончание заданного периода времени в формате ISO 8601
	:return: словарь с данными о погоде
Вспомогательный метод, отправляющий запрос к Open-Meteo API и возвращающий словарь с заданными координатами места, погодой в заданный период времени в этом месте и текущее время.
#### city_update()
	:param city: город, для которого необходимо обновить данные
	:return: None
Обновляет данные о погоде в данном городе на текущее время.
#### setup()
	no params
	:return: None
Запускает цикл бесконечного обновления данных о погоде в городах с некоторым интервалом (по умолчанию 15 минут).
#### lifespan()
	:param app: сущность FastAPI
	:return: None
Запускает setup() и сервер.
#### home()
	no params
	:return: сущность RedirectResponse
Redirects user from home page to the documentation page for better experience.
#### get_current_weather() "/{latitude}&{longitude}"
	:param latitude: широта места, где нужно посмотреть погоду
	:param longitude: долгота места, где нужно посмотреть погоду
	:return: словарь текущих данных о погоде в данном месте
Перенаправляет пользователя с домашней страницы на страницу документации для удобства.
#### add_city() "/{city_name}/{latitude}&{longitude}"
	:param city_name: название города, который нужно добавить
	:param latitude: широта города
	:param longitude: долгота города
	:return: словарь текущих погодных данных в добавленном городе с указанием названия города и текущей погоды на данный момент
Добавляет данный город в базу данных и возвращает словарь с текущими данными о погоде, времени, названии города и его координатах.
#### get_cities() "/cities"
	no params
	:return: список названий городов
Возвращает список названий городов, содержащихся в базе данных.
#### get_city_weather
	:param city_name: название города, где нужно посмотреть погоду
	:param scan_time: текущее время для просмотра погоды в формате ISO8601
	:return: словарь данных о погоде в данном месте в указанное время
Возвращает словарь с данными о погоде в заданном городе на указанное время, если этот город есть в базе данных.

# English
Server may be set up with just launching "script.py". It will automatically install all required frameworks and modules and set up the server.
## Methods
#### get_weather()
	:param latitude: latitude of the place to get weather data for
	:param longitude: longitude of the place to get weather data for
	:param start_time: start of the given time period in ISO 8601 format
	:param end_time: end of the given time period in ISO 8601 format
	:return: dictionary with weather data.
A supportive method holding the requesting to Open-Meteo API logic. Returns a dictionary containing the given place's coordinates, weather data and current time.
#### city_update()
	:param city: city to update weather data for
	:return: None
Updates weather data of the given city for the current time.
#### setup()
	no params
	:return: None
Sets ups a cycle of endless updating cities' weather data with some interval (15 mins by default).
#### lifespan()
	:param app: FastAPI instance.
	:return: None
Starts setup() function and server.
#### home()
	no params
	:return: RedirectResponse instance
Redirects user from home page to the documentation page for better experience.
#### get_current_weather() "/{latitude}&{longitude}"
	:param latitude: latitude of the place to see weather in
	:param longitude: longitude of the place to see weather in
	:return: dictionary of current weather data in the given place
Returns dictionary with current weather in the given with coordinates place and time.
#### add_city() "/{city_name}/{latitude}&{longitude}"
	:param city_name: name of the city to add
	:param latitude: latitude of the city
	:param longitude: longitude of the city
	:return: dictionary of current weather data in the added city with city name
	and current time
Adds given city to the database and returns dictionary with its current weather data, time, city's name and its coordinates.
#### get_cities() "/cities"
	no params
	:return: list of city names
Returns list of cities' names contained in the database.
#### get_city_weather
	:param city_name: name of the city to see weather in
	:param scan_time: time of the weather to see in ISO8601 format
	:return: dictionary of the weather data in the given place at the specified now
Returns dictionary with the given city's weather data in the specified time, if this city is in the database.
