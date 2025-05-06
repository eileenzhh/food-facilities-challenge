import sqlite3
import pandas as pd
from geopy.distance import geodesic
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from typing import Optional, List
from pydantic import BaseModel
from io import StringIO
import logging
import googlemaps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Google Maps client
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
if not GOOGLE_MAPS_API_KEY:
    logger.warning("Google Maps API key not found. Using fallback distance calculation.")
    gmaps = None
else:
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# Initialize FASTAPI app
app = FastAPI(
    title="Mobile Food Facilities Distance API",
    description="API to search for the nearest mobile food facilities in San Francisco.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

# Create SQLite database connection and load data if needed
DATABASE_PATH = "mobile_food_facilities.db"
SF_DATA_URL = "https://data.sfgov.org/resource/rqzj-sfat.csv"

def create_database():
    if os.path.exists(DATABASE_PATH):
        logger.info("Database already exists, skipping creation")
        return
    
    try:
        # Fetch data from SF OpenData API
        logger.info("Fetching data from SF OpenData API...")
        response = requests.get(SF_DATA_URL)
        response.raise_for_status()
        
        # Load CSV data from response
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        
        # Debug: Log column names and first few rows
        logger.info("Available columns in CSV:")
        logger.info(df.columns.tolist())
        logger.info("\nHead of data:")
        logger.info(df.head().to_string())
        
        # Clean and select relevant columns
        logger.info("Processing data...")
        df = df[['applicant', 'address', 'status', 'latitude', 'longitude']].copy()
        df['applicant'] = df['applicant'].str.lower().str.strip()
        df['address'] = df['address'].str.upper().str.strip()
        df['status'] = df['status'].str.upper().str.strip()
        df = df.dropna(subset=['latitude', 'longitude', 'status'])
        
        # Debug: Log final processed data
        logger.info("Processed data columns:")
        logger.info(df.columns.tolist())
        logger.info("\nHead of processed data:")
        logger.info(df.head().to_string())
        
        # Connect to SQLite and store data
        logger.info("Storing data in SQLite database...")
        conn = sqlite3.connect(DATABASE_PATH)
        df.to_sql("food_trucks", conn, if_exists="replace", index=False)
        conn.close()
        logger.info("Database creation completed successfully")
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize database: {str(e)}")

# Create database on startup
@app.on_event("startup")
async def startup_event():
    create_database()

# Pydantic models for request/response
class FoodTruck(BaseModel):
    applicant: str
    address: str
    status: str
    latitude: float
    longitude: float
    distance: Optional[float] = None

class NearestFoodTrucksRequest(BaseModel):
    latitude: float
    longitude: float
    include_all_statuses: bool = False

def get_db_connection():
    return sqlite3.connect(DATABASE_PATH)

@app.get("/search/name/{applicant_name}", response_model=List[FoodTruck])
async def search_by_name(applicant_name: str, status: Optional[str] = None):
    """
    Search for food trucks by applicant name with optional status filter.
    """
    conn = get_db_connection()
    try:
        query = """
            SELECT *
            FROM food_trucks
            WHERE applicant LIKE ?
        """
        params = [f"%{applicant_name.lower()}%"]
        
        if status:
            query += " AND status = ?"
            params.append(status.upper())
            
        df = pd.read_sql_query(query, conn, params=params)
        return df.to_dict('records')
    finally:
        conn.close()

@app.get("/search/address/{street_name}", response_model=List[FoodTruck])
async def search_by_address(street_name: str):
    """
    Search for food trucks by street name (partial match).
    """
    conn = get_db_connection()
    try:
        query = """
            SELECT *
            FROM food_trucks
            WHERE address LIKE ?
        """
        df = pd.read_sql_query(query, conn, params=[f"%{street_name.upper()}%"])
        return df.to_dict('records')
    finally:
        conn.close()

def calculate_distance(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> float:
    """
    Calculate distance between two points using Google Maps API if available,
    otherwise fall back to geopy's geodesic distance.
    """
    if gmaps:
        try:
            # Use Google Maps Distance Matrix API
            result = gmaps.distance_matrix(
                origins=[(origin_lat, origin_lng)],
                destinations=[(dest_lat, dest_lng)],
                units="imperial",
                mode="walking"
            )
            
            if result['status'] == 'OK':
                distance = result['rows'][0]['elements'][0]['distance']['value'] 
                return distance
            else:
                logger.warning(f"Google Maps API error: {result['status']}. Falling back to geodesic distance.")
        except Exception as e:
            logger.warning(f"Google Maps API error: {str(e)}. Falling back to geodesic distance.")
    
    # Fallback to geodesic distance
    return geodesic((origin_lat, origin_lng), (dest_lat, dest_lng)).miles

@app.post("/search/nearest", response_model=List[FoodTruck])
async def find_nearest_food_trucks(request: NearestFoodTrucksRequest):
    """
    Find the 5 nearest food trucks to the given coordinates.
    By default, only returns APPROVED status trucks unless include_all_statuses is True.
    Use Google Maps API for accurate distance calculations if available.
    """
    conn = get_db_connection()
    try:
        query = """
            SELECT *
            FROM food_trucks
        """
        if not request.include_all_statuses:
            query += " WHERE status = 'APPROVED'"
            
        df = pd.read_sql_query(query, conn)
        
        # Calculate distances using Google Maps API or fallback
        df['distance'] = df.apply(
            lambda row: calculate_distance(
                request.latitude,
                request.longitude,
                row['latitude'],
                row['longitude']
            ),
            axis=1
        )
        
        # Sort by distance and get top 5
        df = df.sort_values('distance').head(5)
        return df.to_dict('records')
    finally:
        conn.close()

