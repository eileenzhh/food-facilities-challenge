import pytest
from fastapi.testclient import TestClient
from main import app, DATABASE_PATH
import sqlite3
import pandas as pd
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = TestClient(app)

@pytest.fixture(autouse=True)
def test_db():
    # Store original database path
    original_db_path = DATABASE_PATH
    
    # Create a test database with some sample data
    test_db_path = "test_mobile_food_facilities.db"
    
    # Temporarily modify the database path
    import main
    main.DATABASE_PATH = test_db_path
    
    # Create test database
    conn = sqlite3.connect(test_db_path)
    df = pd.DataFrame({
        'applicant': [
            'test truck 1', 
            'test truck 2', 
            'test truck 3', 
            'food truck 4', 
            'foodies 5', 
            'tacos 6'
            ],
        'address': [
            '123 TEST ST', 
            '456 TEST AVE', 
            '789 TEST BLVD', 
            '101 UNIT CT', 
            '202 FOOD DR', 
            '303 TEST LN'
            ],
        'status': ['APPROVED', 'APPROVED', 'EXPIRED', "REQUESTED", "APPROVED", "EXPIRED"],
        'latitude': [37.7749, 37.7848, 37.7947, 37.8046, 37.8145, 37.8244],
        'longitude': [-122.4194, -122.4294, -122.4394, -122.4494, -122.4594, -122.4694]
    })
    df.to_sql("food_trucks", conn, if_exists="replace", index=False)
    conn.close()
    
    yield test_db_path
    
    # Cleanup: restore original database path and remove test database
    main.DATABASE_PATH = original_db_path
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

def test_search_by_name():
    logger.info("Testing search by name...")
    response = client.get("/search/name/test")
    logger.info(f"Status code: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    logger.info(f"Data: {data}")
    assert len(data) == 3
    assert all("test" in item["applicant"].lower() for item in data)

def test_search_by_name_with_status():
    logger.info("Testing search by name with status...")
    response = client.get("/search/name/test?status=APPROVED")
    logger.info(f"Status code: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    logger.info(f"Data: {data}")
    assert len(data) > 0
    assert all(item["status"] == "APPROVED" for item in data)

def test_search_by_address():
    logger.info("Testing search by address...")
    response = client.get("/search/address/TEST")
    logger.info(f"Status code: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    logger.info(f"Data: {data}")
    assert len(data) > 0
    assert all("TEST" in item["address"].upper() for item in data)

def test_find_nearest():
    logger.info("Testing find nearest...")
    response = client.post(
        "/search/nearest",
        json={"latitude": 37.7749, "longitude": -122.4194, "include_all_statuses": False}
    )
    logger.info(f"Status code: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    logger.info(f"Data: {data}")
    assert len(data) <= 5
    assert all("distance" in item for item in data)

def test_find_nearest_food_trucks_all_statuses():
    logger.info("Testing find nearest food trucks with all statuses...")
    response = client.post(
        "/search/nearest",
        json={
            "latitude": 37.7749,
            "longitude": -122.4194,
            "include_all_statuses": True
        }
    )
    logger.info(f"Status code: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    logger.info(f"Data: {data}")
    assert len(data) == 5
    # Should include both APPROVED and EXPIRED statuses
    assert any(item["status"] == "EXPIRED" for item in data) 
    assert any(item["status"] == "REQUESTED" for item in data)