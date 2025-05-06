import pytest
from fastapi.testclient import TestClient
from main import app
import sqlite3
import pandas as pd

client = TestClient(app)

@pytest.fixture
def test_db():
    # Create a test database with some sample data
    conn = sqlite3.connect("test_mobile_food_facilities.db")
    df = pd.DataFrame({
        'Applicant': [
            'test truck 1', 
            'test truck 2', 
            'test truck 3', 
            'food truck 4', 
            'foodies 5', 
            'tacos 6'
            ],
        'Address': [
            '123 TEST ST', 
            '456 TEST AVE', 
            '789 TEST BLVD', 
            '101 UNIT CT', 
            '202 FOOD DR', 
            '303 TEST LN'
            ],
        'Status': ['APPROVED', 'APPROVED', 'EXPIRED', "REQUESTED", "APPROVED", "EXPIRED"],
        'Latitude': [37.7749, 37.7848, 37.7947, 37.8046, 37.8145, 37.8244],
        'Longitude': [-122.4194, -122.4294, -122.4394, -122.4494, -122.4594, -122.4694, -122.4794],
    })
    df.to_sql("food_trucks", conn, if_exists="replace", index=False)
    conn.close()
    return "test_mobile_food_facilities.db"

def test_search_by_name():
    response = client.get("/search/name/test")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all("test" in item["applicant"].lower() for item in data)

def test_search_by_name_with_status():
    response = client.get("/search/name/test?status=APPROVED")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(item["status"] == "APPROVED" for item in data)

def test_search_by_address():
    response = client.get("/search/address/UNIT")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["applicant"] == "food truck 4"
    assert all("UNIT" in item["address"] for item in data)

def test_find_nearest_food_trucks():
    response = client.post(
        "/search/nearest",
        json={
            "latitude": 37.7749,
            "longitude": -122.4194,
            "include_all_statuses": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5
    assert all(item["status"] == "APPROVED" for item in data)

def test_find_nearest_food_trucks_all_statuses():
    response = client.post(
        "/search/nearest",
        json={
            "latitude": 37.7749,
            "longitude": -122.4194,
            "include_all_statuses": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    # Should include both APPROVED and EXPIRED statuses
    assert any(item["status"] == "EXPIRED" for item in data) 
    assert any(item["status"] == "REQUESTED" for item in data)