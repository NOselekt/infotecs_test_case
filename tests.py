from fastapi.testclient import TestClient
from script import app


client = TestClient(app)


def test_get_current_weather():
    response = client.get("/57.002&12.004")
    assert response.status_code == 200
    assert "temperature" in response.json()
    assert "pressure" in response.json()
    assert "wind_speed" in response.json()

def test_add_city():
    response = client.get("/Moscow/56&38")
    assert response.status_code == 200
    assert "temperature" in response.json()
    assert "pressure" in response.json()
    assert "wind_speed" in response.json()
    assert "last_update_time" in response.json()
    assert "city_name" in response.json()

def test_get_cities():
    response = client.get("/cities")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_city_weather():
    response = client.get("/Moscow/12:30")
    assert response.status_code == 200
    assert "temperature" in response.json()
    assert "pressure" in response.json()
    assert "wind_speed" in response.json()
    assert response.json()["city_name"] == "Moscow"

