#!/usr/bin/env python3
"""
Streamlit UI for the Weather MCP Server.
Provides an intuitive interface for weather alerts and forecasts.
"""
import streamlit as st
import asyncio
import time
import os
from datetime import datetime
import re

# Load environment variables from .env file FIRST
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from weather import get_alerts, get_forecast, get_coordinates_from_city

# Page configuration
st.set_page_config(
    page_title="🌤️ Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .alert-card {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .forecast-card {
        background-color: #e3f2fd;
        border: 1px solid #90caf9;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'weather_cache' not in st.session_state:
    st.session_state.weather_cache = {}

def get_cache_key(request_type: str, location_data: str) -> str:
    """Generate a cache key for weather requests."""
    return f"{request_type}_{location_data}_{int(time.time() / 300)}"  # 5-minute cache

@st.cache_data(ttl=300)  # Cache for 5 minutes
def cached_weather_request(request_type: str, location_data: str):
    """Cached wrapper for weather requests."""
    return asyncio.run(execute_weather_request(request_type, location_data))

async def execute_weather_request(request_type: str, location_data: str):
    """Execute weather request based on type and location."""
    try:
        if request_type == "alerts":
            result = await get_alerts(location_data)
            return {"success": True, "data": result, "type": "alerts"}
        elif request_type == "forecast":
            # location_data is "lat,lon"
            lat, lon = map(float, location_data.split(','))
            result = await get_forecast(lat, lon)
            return {"success": True, "data": result, "type": "forecast", "coordinates": (lat, lon)}
        elif request_type == "forecast_by_city":
            coordinates = await get_coordinates_from_city(location_data)
            if coordinates:
                lat, lon = coordinates
                result = await get_forecast(lat, lon)
                return {
                    "success": True, 
                    "data": result, 
                    "type": "forecast",
                    "city": location_data,
                    "coordinates": (lat, lon)
                }
            else:
                return {
                    "success": False,
                    "error": f"Could not find coordinates for '{location_data}'. Please try a different city name."
                }
    except Exception as e:
        return {"success": False, "error": str(e)}

def parse_alerts(alerts_text: str):
    """Parse alerts text into structured data."""
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

def parse_forecast(forecast_text: str):
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

            if len(period_data) > 1:  # More than just name
                parsed_periods.append(period_data)

    return parsed_periods

def display_alerts(alerts_data):
    """Display weather alerts in a beautiful format."""
    alerts = parse_alerts(alerts_data)

    if not alerts:
        st.markdown("""
        <div class="success-message">
            <h4>🌤️ Good News!</h4>
            <p>Great news! There are currently no active weather alerts for this state.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"<h3>⚠️ Active Weather Alerts ({len(alerts)} found)</h3>", unsafe_allow_html=True)

    for i, alert in enumerate(alerts, 1):
        st.markdown(f"""
        <div class="alert-card">
            <h4>Alert #{i}: {alert.get('Event', 'Unknown Event')}</h4>
            <p><strong>📍 Area:</strong> {alert.get('Area', 'Unknown')}</p>
            <p><strong>⚠️ Severity:</strong> {alert.get('Severity', 'Unknown')}</p>
            <p><strong>📝 Description:</strong> {alert.get('Description', 'No description available')}</p>
            <p><strong>💡 Instructions:</strong> {alert.get('Instructions', 'No specific instructions provided')}</p>
        </div>
        """, unsafe_allow_html=True)

def display_forecast(forecast_data, location_info=None):
    """Display weather forecast in a beautiful format."""
    periods = parse_forecast(forecast_data)

    if not periods:
        st.markdown("""
        <div class="error-message">
            <h4>❌ Forecast Unavailable</h4>
            <p>Unable to fetch forecast data for this location. Please try again or check your coordinates.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Display location info if provided
    if location_info:
        if 'city' in location_info:
            st.markdown(f"<h3>🌤️ Weather Forecast for {location_info['city']}</h3>", unsafe_allow_html=True)
            st.markdown(f"📍 Coordinates: {location_info['coordinates'][0]:.4f}, {location_info['coordinates'][1]:.4f}", unsafe_allow_html=True)
        else:
            st.markdown("<h3>🌤️ Weather Forecast</h3>", unsafe_allow_html=True)
            st.markdown(f"📍 Coordinates: {location_info['coordinates'][0]:.4f}, {location_info['coordinates'][1]:.4f}", unsafe_allow_html=True)

    # Create columns for the forecast periods
    for i, period in enumerate(periods):
        with st.container():
            st.markdown(f"""
            <div class="forecast-card">
                <h4>{period.get('name', f'Period {i+1}')}</h4>
                <p><strong>🌡️ Temperature:</strong> {period.get('Temperature', 'N/A')}</p>
                <p><strong>💨 Wind:</strong> {period.get('Wind', 'N/A')}</p>
                <p><strong>📋 Forecast:</strong> {period.get('Forecast', 'No details available')}</p>
            </div>
            """, unsafe_allow_html=True)

# Main App Layout
st.markdown("""
<div class="main-header">
    <h1>🌤️ Weather Dashboard</h1>
    <p>Get real-time weather alerts and forecasts for any location</p>
</div>
""", unsafe_allow_html=True)

# Check if OpenRouter API key is available
openrouter_key = os.environ.get("OPENROUTER_API_KEY")
if not openrouter_key:
    st.error("⚠️ OpenRouter API key not found. Please add OPENROUTER_API_KEY to your .env file.")
    st.info("💡 This is required for city name to coordinate conversion functionality.")

# Sidebar for input
with st.sidebar:
    st.header("📍 Location Input")

    input_method = st.radio(
        "Choose input method:",
        ["🏙️ City Search", "🎯 Coordinates", "🚨 State Alerts"],
        help="Select how you want to specify the location"
    )

    if input_method == "🚨 State Alerts":
        st.subheader("Monitor weather emergencies across all 50 US states")
        state_code = st.text_input(
            "Enter US State Code",
            placeholder="CA, NY, TX, FL...",
            help="Enter the 2-letter state code (e.g., CA for California)"
        ).upper().strip()

        if st.button("🚨 Get Alerts", type="primary") and state_code:
            if len(state_code) == 2 and state_code.isalpha():
                with st.spinner(f"Fetching weather alerts for {state_code}..."):
                    result = cached_weather_request("alerts", state_code)

                    if result["success"]:
                        display_alerts(result["data"])
                    else:
                        st.error(f"❌ Error: {result['error']}")
                        st.info("Please check your input and try again.")
            else:
                st.error("Please enter a valid 2-letter US state code.")

    elif input_method == "🎯 Coordinates":
        st.subheader("Use exact coordinates for pinpoint accuracy")

        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=37.7749, step=0.0001)
        with col2:
            longitude = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=-122.4194, step=0.0001)

        if st.button("🌤️ Get Forecast", type="primary"):
            location_data = f"{latitude},{longitude}"
            with st.spinner(f"Fetching forecast for coordinates ({latitude}, {longitude})..."):
                result = cached_weather_request("forecast", location_data)

                if result["success"]:
                    display_forecast(result["data"], result)
                else:
                    st.error(f"❌ Error: {result['error']}")
                    st.info("Please check your input and try again.")

    elif input_method == "🏙️ City Search":
        st.subheader("Search by city name anywhere in the world")

        if not openrouter_key:
            st.warning("🔑 OpenRouter API key required for city search functionality")
            st.info("Please add your OpenRouter API key to the .env file to use this feature.")

        city_name = st.text_input(
            "Enter City Name",
            placeholder="New York City, Los Angeles, Tokyo...",
            help="Enter any city name worldwide"
        ).strip()

        if st.button("🌍 Get City Forecast", type="primary", disabled=not openrouter_key) and city_name:
            with st.spinner(f"Looking up coordinates for {city_name} and fetching forecast..."):
                result = cached_weather_request("forecast_by_city", city_name)

                if result["success"]:
                    display_forecast(result["data"], result)
                else:
                    st.error(f"❌ Error: {result['error']}")
                    st.info("Please check your input and try again.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🌤️ Weather data provided by the National Weather Service</p>
    <p>🤖 City geocoding powered by OpenRouter AI</p>
    <p><small>Weather alerts are updated in real-time. Forecasts are cached for 5 minutes.</small></p>
</div>
""", unsafe_allow_html=True)
