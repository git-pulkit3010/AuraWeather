#!/usr/bin/env python3
"""
FastAPI backend server for the Weather Dashboard
Integrates with existing weather.py functions
"""

import os
import sys
import json
import time
import asyncio
from typing import Dict, List, Optional, Union
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import your existing weather functions
from weather import get_alerts, get_forecast, get_coordinates_from_city

# Initialize FastAPI
app = FastAPI(
    title="Weather Dashboard API",
    description="Modern weather dashboard backend",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class AlertsRequest(BaseModel):
    state: str = Field(..., min_length=2, max_length=2, description="Two-letter US state code")

class ForecastRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")

class CityForecastRequest(BaseModel):
    city: str = Field(..., min_length=1, description="City name for coordinate lookup")

class WeatherResponse(BaseModel):
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    timestamp: str
    cached: bool = False

# Simple in-memory cache
cache = {}
CACHE_DURATION = 300  # 5 minutes

def get_cache_key(request_type: str, location_data: str) -> str:
    """Generate cache key for requests."""
    return f"{request_type}_{location_data}_{int(time.time() / CACHE_DURATION)}"

def parse_alerts(alerts_text: str) -> List[Dict]:
    """Parse alert text into structured data."""
    if "No active alerts" in alerts_text or "Unable to fetch alerts" in alerts_text:
        return []

    alerts = alerts_text.strip().split("---")
    parsed_alerts = []

    for alert in alerts:
        if alert.strip():
            lines = alert.strip().split('\n')
            alert_data = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    alert_data[key.strip()] = value.strip()
            if alert_data:
                parsed_alerts.append(alert_data)

    return parsed_alerts

def parse_forecast(forecast_text: str) -> List[Dict]:
    """Parse forecast text into structured data."""
    if "Unable to fetch" in forecast_text:
        return []

    periods = forecast_text.strip().split("---")
    parsed_periods = []

    for period in periods:
        if period.strip():
            lines = period.strip().split('\n')
            period_data = {"name": lines[0].replace(':', '') if lines else "Unknown"}

            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    period_data[key.strip()] = value.strip()

            if len(period_data) > 1:
                # Add weather emoji based on forecast
                emoji = get_weather_emoji(period_data.get('name', ''), period_data.get('Forecast', ''))
                period_data['emoji'] = emoji
                parsed_periods.append(period_data)

    return parsed_periods

def get_weather_emoji(period_name: str, forecast: str) -> str:
    """Get appropriate weather emoji."""
    period_lower = period_name.lower()
    forecast_lower = forecast.lower()

    if 'night' in period_lower or 'tonight' in period_lower:
        if any(word in forecast_lower for word in ['rain', 'shower', 'storm']):
            return '🌧️'
        elif any(word in forecast_lower for word in ['snow', 'blizzard']):
            return '❄️'
        elif 'cloud' in forecast_lower:
            return '☁️'
        else:
            return '🌙'
    else:
        if any(word in forecast_lower for word in ['rain', 'shower', 'storm', 'thunderstorm']):
            return '⛈️' if 'thunder' in forecast_lower or 'storm' in forecast_lower else '🌧️'
        elif any(word in forecast_lower for word in ['snow', 'blizzard']):
            return '🌨️'
        elif any(word in forecast_lower for word in ['cloud', 'overcast']):
            return '☁️'
        elif any(word in forecast_lower for word in ['partly', 'scattered']):
            return '⛅'
        elif any(word in forecast_lower for word in ['clear', 'sunny']):
            return '☀️'
        else:
            return '🌤️'

# API Routes
@app.get("/", response_class=HTMLResponse)
async def read_index():
    """Serve the main HTML page."""
    try:
        with open("frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Weather Dashboard</h1><p>Frontend not found. Please build the frontend.</p>")

@app.post("/api/alerts", response_model=WeatherResponse)
async def get_weather_alerts(request: AlertsRequest):
    """Get weather alerts for a US state."""
    state = request.state.upper()
    cache_key = get_cache_key("alerts", state)

    # Check cache
    if cache_key in cache:
        cached_result = cache[cache_key]
        cached_result["cached"] = True
        return cached_result

    try:
        # Call your existing weather function
        alerts_text = await get_alerts(state)
        parsed_alerts = parse_alerts(alerts_text)

        result = WeatherResponse(
            success=True,
            data={
                "state": state,
                "alerts": parsed_alerts,
                "count": len(parsed_alerts)
            },
            timestamp=datetime.now().isoformat(),
            cached=False
        )

        # Cache the result
        cache[cache_key] = result.dict()
        return result

    except Exception as e:
        return WeatherResponse(
            success=False,
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

@app.post("/api/forecast", response_model=WeatherResponse)
async def get_weather_forecast(request: ForecastRequest):
    """Get weather forecast for coordinates."""
    cache_key = get_cache_key("forecast", f"{request.latitude},{request.longitude}")

    # Check cache
    if cache_key in cache:
        cached_result = cache[cache_key]
        cached_result["cached"] = True
        return cached_result

    try:
        # Call your existing weather function
        forecast_text = await get_forecast(request.latitude, request.longitude)
        parsed_forecast = parse_forecast(forecast_text)

        result = WeatherResponse(
            success=True,
            data={
                "coordinates": [request.latitude, request.longitude],
                "forecast": parsed_forecast,
                "location": f"Lat: {request.latitude:.4f}, Lon: {request.longitude:.4f}"
            },
            timestamp=datetime.now().isoformat(),
            cached=False
        )

        # Cache the result
        cache[cache_key] = result.dict()
        return result

    except Exception as e:
        return WeatherResponse(
            success=False,
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

@app.post("/api/forecast/city", response_model=WeatherResponse)
async def get_city_forecast(request: CityForecastRequest):
    """Get weather forecast for a city (uses OpenRouter for coordinate lookup)."""
    cache_key = get_cache_key("city_forecast", request.city)

    # Check cache
    if cache_key in cache:
        cached_result = cache[cache_key]
        cached_result["cached"] = True
        return cached_result

    try:
        # Check if OpenRouter API key is available
        if not os.environ.get("OPENROUTER_API_KEY"):
            return WeatherResponse(
                success=False,
                error="OpenRouter API key not configured. Please add OPENROUTER_API_KEY to your environment variables.",
                timestamp=datetime.now().isoformat()
            )

        # Get coordinates from city name
        coordinates = await get_coordinates_from_city(request.city)

        if not coordinates:
            return WeatherResponse(
                success=False,
                error=f"Could not find coordinates for '{request.city}'. Please try a different city name or use coordinates directly.",
                timestamp=datetime.now().isoformat()
            )

        latitude, longitude = coordinates

        # Get forecast for the coordinates
        forecast_text = await get_forecast(latitude, longitude)
        parsed_forecast = parse_forecast(forecast_text)

        result = WeatherResponse(
            success=True,
            data={
                "city": request.city,
                "coordinates": [latitude, longitude],
                "forecast": parsed_forecast,
                "location": f"{request.city} ({latitude:.4f}, {longitude:.4f})"
            },
            timestamp=datetime.now().isoformat(),
            cached=False
        )

        # Cache the result
        cache[cache_key] = result.dict()
        return result

    except Exception as e:
        return WeatherResponse(
            success=False,
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

@app.get("/debug")
async def debug_info():
    """Debug endpoint to check server status."""
    import os
    return {
        "status": "Server is running",
        "frontend_dir_exists": os.path.exists("frontend"),
        "app_js_exists": os.path.exists("frontend/app.js"),
        "index_html_exists": os.path.exists("frontend/index.html"),
        "current_dir": os.getcwd(),
        "frontend_files": os.listdir("frontend") if os.path.exists("frontend") else []
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "openrouter_configured": bool(os.environ.get("OPENROUTER_API_KEY"))
    }

# Serve static files (your frontend)
# Mount static files before the catch-all route
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Also serve JavaScript and CSS files directly from root for easier access
@app.get("/app.js")
async def get_app_js():
    """Serve the main JavaScript file."""
    try:
        with open("frontend/app.js", "r") as f:
            return Response(content=f.read(), media_type="application/javascript")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="JavaScript file not found")

@app.get("/favicon.ico")
async def get_favicon():
    """Return a simple favicon response."""
    return Response(status_code=204)  # No content

def create_app():
    """Application factory for proper ASGI deployment."""
    return app

if __name__ == "__main__":
    import uvicorn
    # Use the import string format to avoid the warning
    uvicorn.run("backend_server:app", host="0.0.0.0", port=8000, reload=True)
