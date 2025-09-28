#!/usr/bin/env python3
"""
FastAPI backend server for the Weather Dashboard with Dark Mode Support
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
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
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
    description="Modern weather dashboard backend with dark mode support",
    version="2.0.0"
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
    """Get appropriate weather emoji with enhanced detection."""
    period_lower = period_name.lower()
    forecast_lower = forecast.lower()

    # Night detection
    if 'night' in period_lower or 'tonight' in period_lower:
        if any(word in forecast_lower for word in ['rain', 'shower', 'storm', 'drizzle']):
            return '🌧️'
        elif any(word in forecast_lower for word in ['snow', 'blizzard', 'flurries']):
            return '❄️'
        elif any(word in forecast_lower for word in ['cloud', 'overcast', 'partly']):
            return '☁️'
        else:
            return '🌙'
    else:
        # Day detection
        if any(word in forecast_lower for word in ['thunderstorm', 'severe']):
            return '⛈️'
        elif any(word in forecast_lower for word in ['rain', 'shower', 'drizzle']):
            return '🌧️'
        elif any(word in forecast_lower for word in ['snow', 'blizzard', 'flurries']):
            return '🌨️'
        elif any(word in forecast_lower for word in ['fog', 'mist']):
            return '🌫️'
        elif any(word in forecast_lower for word in ['cloud', 'overcast']):
            return '☁️'
        elif any(word in forecast_lower for word in ['partly', 'scattered', 'few clouds']):
            return '⛅'
        elif any(word in forecast_lower for word in ['clear', 'sunny', 'fair']):
            return '☀️'
        elif any(word in forecast_lower for word in ['hot', 'heat']):
            return '🌡️'
        elif any(word in forecast_lower for word in ['cold', 'freeze', 'frost']):
            return '❄️'
        else:
            return '🌤️'

# Static file serving
@app.get("/", response_class=HTMLResponse)
async def read_index():
    """Serve the main HTML page with dark mode support."""
    try:
        with open("frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>Weather Dashboard</title></head>
            <body style="background: #1a1a1a; color: white; font-family: Arial;">
                <div style="text-align: center; padding: 50px;">
                    <h1>🌤️ Weather Dashboard</h1>
                    <p>Frontend not found. Please ensure the frontend files are in the 'frontend' directory.</p>
                    <p>Expected files: frontend/index.html, frontend/app.js</p>
                </div>
            </body>
        </html>
        """)

@app.get("/app.js")
async def get_app_js():
    """Serve the JavaScript file."""
    try:
        return FileResponse("frontend/app.js", media_type="application/javascript")
    except FileNotFoundError:
        return JSONResponse(
            content={"error": "app.js not found"},
            status_code=404
        )

# API Routes
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
        error_result = WeatherResponse(
            success=False,
            error=str(e),
            timestamp=datetime.now().isoformat()
        )
        return error_result

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

@app.get("/api/health")
async def health_check():
    """Health check endpoint with theme support info."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "openrouter_configured": bool(os.environ.get("OPENROUTER_API_KEY")),
        "features": {
            "dark_mode": True,
            "theme_toggle": True,
            "caching": True,
            "responsive_design": True
        },
        "cache_stats": {
            "cached_items": len(cache),
            "cache_duration_minutes": CACHE_DURATION / 60
        }
    }

@app.get("/api/cache/clear")
async def clear_cache():
    """Clear the weather data cache."""
    global cache
    cache_count = len(cache)
    cache.clear()
    return {
        "message": f"Cache cleared. Removed {cache_count} cached items.",
        "timestamp": datetime.now().isoformat()
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn

    print("🌤️ Starting Weather Dashboard Server...")
    print("🌙 Dark mode enabled by default")
    print("🎨 Theme toggle functionality included")
    print("⚡ Enhanced caching and error handling")
    print("📱 Responsive design optimized")
    print("")
    print("🚀 Server will be available at: http://localhost:8000")
    print("📋 API documentation at: http://localhost:8000/docs")
    print("")

    uvicorn.run("run_server:app", host="0.0.0.0", port=8000, reload=True)
