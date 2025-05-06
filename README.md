# San Francisco Mobile Food Facilities API

## Description
This project provides a RESTful API for searching and finding mobile food facilities (food trucks) in San Francisco. The API allows users to search for food trucks by name, address, and find the nearest food trucks to a given location. The implementation uses real-time data from the San Francisco OpenData API and provides accurate distance calculations using the Google Maps Distance Matrix API.

## Technical Decisions

### Backend Framework: FastAPI
- Chose FastAPI for its high performance, automatic API documentation, and built-in request validation
- Provides async support for better scalability
- Automatic OpenAPI (Swagger) documentation at `/docs` endpoint

### Database: SQLite
- Used SQLite for simplicity and ease of deployment
- Data is loaded from SF OpenData API on startup
- Provides fast read operations for search queries
- No complex write operations needed, making SQLite a suitable choice

### Distance Calculation
- Primary: Google Maps Distance Matrix API
  - Provides accurate walking distances
  - Handles traffic patterns and real-time road conditions
- Fallback: Geopy's geodesic distance
  - Used when Google Maps API is unavailable
  - Provides straight-line distance as a backup

### Data Source
- SF OpenData API (https://data.sfgov.org/resource/rqzj-sfat.csv)
- Data is cached in SQLite database
- Regular updates possible through API refresh

## API Endpoints

1. `GET /search/name/{applicant_name}`
   - Search food trucks by name
   - Optional status filter
   - Case-insensitive partial matching

2. `GET /search/address/{street_name}`
   - Search food trucks by street address
   - Case-insensitive partial matching
   - Returns all matching locations

3. `POST /search/nearest`
   - Find 5 nearest food trucks to given coordinates
   - Optional status filter, default APPROVED
   - Returns sorted results by distance

## Critique and Future Improvements

### What Would I Have Done Differently?
If I had more time, I would add these features to create a more user-friendly and robust application:
1. **Database Choice**
   - For production, would switch to PostgreSQL instead of SQLite
   - Add spatial indexing for faster location-based queries
   - Implement proper database migrations

2. **Caching Strategy**
   - Implement Redis for caching frequent queries
   - Cache Google Maps API responses, reducing costs
   - Add rate limiting for API endpoints

3. **Data Updates**
   - Implement scheduled data updates from SF OpenData
   - Add data validation and cleaning pipeline

4. **Frontend**
   - Incorporate a map element using GoogleMaps API
   - Provide descriptions of food 

### Trade-offs Made
1. **SQLite vs. PostgreSQL**
   - Chose SQLite for simplicity and given the tasks, SQLite was sufficient, also zero-configuration needed
   - Trade-off: Limited concurrency, not scalable for more users
   - Trade-off: No built-in spatial queries
   - Trade-off: Less advanced JSON support if queries become more complex

2. **Distance Calculation**
   - Google Maps API provides accuracy but has cost per call
   - Fallback to geodesic distance when API fails
   - Trade-off: Less accurate but free fallback option

3. **Data Freshness**
   - Data is loaded on start up for simplicity
   - Trade-off: No real-time updates
   - Trade-off: Outdated data between restarts, notably affecting the query of 'status' checks when it is updated from "REQUESTED" to "APPROVED" and the app does not know.

### Features Left Out
1. **User Features**
   - User authentication
   - Favorite food trucks
   - User reviews and ratings

2. **Search Features**
   - Advanced search filters
   - Search by food type, operating hours, price range etc.
   - Search within nearest XX miles
   - Food Truck information after searching 

3. **Data Features**
   - Historical data tracking and popularity metrics
   - Operating hours validation during search times

4. **User Location Detection**
   - Instead of inputting coordinates (very unintuitive for users), automatically detect user location
   - Merge find nearest search to the other two search methods
   - Order results by nearest, including distance for all search results
   - Implement user permission for location access

### Things to consider after scaling
1. **Database**
   - Implement connection pooling to reduce latency
   - Implement proper indexing strategy to speed up query execution

2. **API Performance**
   - Add request caching to return identical requests without re-calling
   - Implement rate limiting to prevent server overload
   - Add request queuing for high-load scenarios to maintain constant service during peak usage
   - Add input validation to ensure proper usage for each requests (e.g. latitude + longitude between a specific range, double-checking datatypes etc.)

3. **Monitoring and Logging**
   - Add structured logging to keep track of bugs or failed requests or rate limit hits
   - Implement metrics collection to assess performance and better troubleshooting
   - Add performance monitoring for system resources


## Setup and Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd food-facilities-challenge
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate 
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. *If want to use Google maps API during distance search:* 
Create a `.env` file in the project root with the following content:
```
GOOGLE_MAPS_API_KEY=your_api_key_here
```

5. Run the application:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation is available at `http://localhost:8000/docs`

6. BONUS: Run the frontend:
```bash
cd frontend
npm install # install dependencies
npm run dev # run the frontend
```
Frontend is available at `http://localhost:3000`

## Running Tests (Backend only)
```bash
pytest
```