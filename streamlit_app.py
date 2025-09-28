#!/usr/bin/env python3
"""
Streamlit UI for the Weather MCP Server.
Provides an intuitive interface for weather alerts and forecasts.
"""

import streamlit as st
import asyncio
import time
from datetime import datetime
import re

# Load environment variables
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
    /* Main layout improvements */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f0f2f6;
    }
    
    /* Sidebar text visibility */
    .css-1d391kg .stMarkdown h2 {
        color: #2c3e50 !important;
    }
    
    .css-1d391kg .stMarkdown h3 {
        color: #2c3e50 !important;
    }
    
    .css-1d391kg .stMarkdown p {
        color: #2c3e50 !important;
    }
    
    /* Selectbox label styling */
    .css-1d391kg .stSelectbox label {
        color: white !important;
        font-weight: 600;
        background-color: #2c3e50;
        padding: 0.5rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
        display: inline-block;
    }
    
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .weather-card {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 16px rgba(44,62,80,0.3);
        border: none;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .weather-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(44,62,80,0.4);
    }
    
    .weather-card h4 {
        color: white;
        font-size: 1.4rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid rgba(255,255,255,0.3);
        padding-bottom: 0.5rem;
    }
    
    .alert-card {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 16px rgba(231,76,60,0.3);
        border: none;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .alert-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(231,76,60,0.4);
    }
    
    .alert-card h4 {
        color: white;
        font-size: 1.4rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid rgba(255,255,255,0.3);
        padding-bottom: 0.5rem;
    }
    
    .success-card {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 16px rgba(39,174,96,0.3);
        border: none;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .success-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(39,174,96,0.4);
    }
    
    .success-card h3 {
        color: white;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .error-card {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 16px rgba(231,76,60,0.3);
        border: none;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .error-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(231,76,60,0.4);
    }
    
    .error-card h3 {
        color: white;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(44,62,80,0.3);
        margin: 1rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-container:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(44,62,80,0.4);
    }
    
    .metric-container h4 {
        color: white;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
        text-align: center;
    }
    
    .metric-container p {
        color: rgba(255,255,255,0.9);
        margin: 0;
        font-size: 0.9rem;
        text-align: center;
        line-height: 1.4;
    }
    
    /* Weather details styling */
    .weather-details {
        background: rgba(255,255,255,0.2);
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .weather-details p {
        margin: 0.8rem 0;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    .weather-details strong {
        color: #fff;
        font-weight: 600;
    }
    
    /* Sidebar input styling */
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 8px;
    }
    
    .stSelectbox > div > div > div {
        background-color: white !important;
        color: #2c3e50 !important;
    }
    
    .stSelectbox option {
        background-color: white !important;
        color: #2c3e50 !important;
    }
    
    .stTextInput > div > div > input {
        background-color: white !important;
        color: #2c3e50 !important;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #95a5a6 !important;
    }
    
    .stNumberInput > div > div > input {
        background-color: white !important;
        color: #2c3e50 !important;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    
    /* Selectbox dropdown styling */
    div[data-testid="stSelectbox"] > div > div {
        background-color: white !important;
        color: #2c3e50 !important;
    }
    
    div[data-testid="stSelectbox"] > div > div > div {
        color: #2c3e50 !important;
    }
    
    /* Additional input field fixes */
    .stSelectbox [data-testid="stMarkdownContainer"] {
        color: #2c3e50 !important;
    }
    
    /* Ensure all sidebar text is visible */
    .css-1d391kg .stMarkdown {
        color: #2c3e50;
    }
    
    .css-1d391kg label {
        color: #2c3e50 !important;
        font-weight: 600;
    }
    
    /* Fix for selectbox options */
    div[role="listbox"] {
        background-color: white !important;
    }
    
    div[role="option"] {
        background-color: white !important;
        color: #2c3e50 !important;
    }
    
    div[role="option"]:hover {
        background-color: #f8f9fa !important;
        color: #2c3e50 !important;
    }
    
    /* Results header */
    .results-header {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .results-header h2 {
        margin: 0;
        font-size: 1.8rem;
    }
    
    /* Cache info styling */
    .cache-info {
        background: rgba(79,172,254,0.1);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4facfe;
        margin-top: 2rem;
        color: #2c3e50;
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

def get_weather_emoji(period_name: str, forecast: str) -> str:
    """Get appropriate weather emoji based on period name and forecast."""
    period_lower = period_name.lower()
    forecast_lower = forecast.lower()
    
    # Night periods
    if 'night' in period_lower or 'tonight' in period_lower:
        if any(word in forecast_lower for word in ['rain', 'shower', 'storm']):
            return '🌧️'
        elif any(word in forecast_lower for word in ['snow', 'blizzard']):
            return '❄️'
        elif 'cloud' in forecast_lower:
            return '☁️'
        else:
            return '🌙'
    
    # Day periods
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
        <div class="success-card">
            <h3>✅ No Active Alerts</h3>
            <p>Great news! There are currently no active weather alerts for this state.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown(f"<h3>🚨 {len(alerts)} Active Weather Alert(s)</h3>", unsafe_allow_html=True)
    
    for i, alert in enumerate(alerts, 1):
        severity = alert.get('Severity', 'Unknown').lower()
        icon = "🔴" if severity in ['extreme', 'severe'] else "🟡" if severity == 'moderate' else "🟠"
        
        st.markdown(f"""
        <div class="alert-card">
            <h4>{icon} Alert #{i}: {alert.get('Event', 'Unknown Event')}</h4>
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
        <div class="error-card">
            <h3>❌ Forecast Unavailable</h3>
            <p>Unable to fetch forecast data for this location. Please try again or check your coordinates.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Display location info if available
    if location_info:
        if 'city' in location_info:
            st.markdown(f"""<div style="background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%); padding: 1.5rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="margin: 0; color: white;">🌍 Weather Forecast for {location_info['city']}</h2>
                <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.9);">📍 Coordinates: {location_info['coordinates'][0]:.4f}, {location_info['coordinates'][1]:.4f}</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div style="background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%); padding: 1.5rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="margin: 0; color: white;">🌍 Weather Forecast</h2>
                <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.9);">📍 Coordinates: {location_info['coordinates'][0]:.4f}, {location_info['coordinates'][1]:.4f}</p>
            </div>""", unsafe_allow_html=True)
    
    # Create forecast periods in 2-column layout
    for i in range(0, len(periods), 2):
        cols = st.columns(2)
        
        # Left column
        with cols[0]:
            period = periods[i]
            # Add weather emoji based on period name or forecast content
            weather_emoji = get_weather_emoji(period.get('name', ''), period.get('Forecast', ''))
            st.markdown(f"""
            <div class="weather-card">
                <h4>{weather_emoji} {period.get('name', f'Period {i+1}')}</h4>
                <div class="weather-details">
                    <p><strong>🌡️ Temperature:</strong> {period.get('Temperature', 'N/A')}</p>
                    <p><strong>💨 Wind:</strong> {period.get('Wind', 'N/A')}</p>
                    <p><strong>📋 Forecast:</strong> {period.get('Forecast', 'No details available')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Right column (if there's a second period)
        with cols[1]:
            if i + 1 < len(periods):
                period = periods[i + 1]
                weather_emoji = get_weather_emoji(period.get('name', ''), period.get('Forecast', ''))
                st.markdown(f"""
                <div class="weather-card">
                    <h4>{weather_emoji} {period.get('name', f'Period {i+2}')}</h4>
                    <div class="weather-details">
                        <p><strong>🌡️ Temperature:</strong> {period.get('Temperature', 'N/A')}</p>
                        <p><strong>💨 Wind:</strong> {period.get('Wind', 'N/A')}</p>
                        <p><strong>📋 Forecast:</strong> {period.get('Forecast', 'No details available')}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def main():
    """Main Streamlit application."""
    
    # Header in main area
    st.markdown("""
    <div class="main-header">
        <h1>🌤️ Weather Dashboard</h1>
        <p>Get real-time weather alerts and forecasts for any location</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for inputs only
    with st.sidebar:
        st.markdown("## 🔧 Weather Options")
        
        weather_type = st.selectbox(
            "What would you like to check?",
            [
                "🚨 Weather Alerts (US State)",
                "🌤️ Weather Forecast (Coordinates)",
                "🏙️ Weather Forecast (City Name)"
            ],
            key="weather_type"
        )
        
        st.markdown("---")
        
        # Input fields based on selection
        if weather_type == "🚨 Weather Alerts (US State)":
            st.markdown("### 📍 Enter US State")
            state_code = st.text_input(
                "State Code (2 letters)",
                placeholder="CA, NY, TX...",
                help="Enter a valid 2-letter US state code",
                key="state_input"
            ).upper()
            
            location_data = state_code
            request_type = "alerts"
            is_valid = len(state_code) == 2 and state_code.isalpha()
            
        elif weather_type == "🌤️ Weather Forecast (Coordinates)":
            st.markdown("### 🗺️ Enter Coordinates")
            
            latitude = st.number_input(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                step=0.0001,
                format="%.4f",
                help="Latitude between -90 and 90",
                key="lat_input"
            )
            
            longitude = st.number_input(
                "Longitude",
                min_value=-180.0,
                max_value=180.0,
                step=0.0001,
                format="%.4f",
                help="Longitude between -180 and 180",
                key="lon_input"
            )
            
            location_data = f"{latitude},{longitude}"
            request_type = "forecast"
            is_valid = latitude != 0.0 or longitude != 0.0
            
        else:  # City name
            st.markdown("### 🏙️ Enter City Name")
            city_name = st.text_input(
                "City Name",
                placeholder="New York City, Los Angeles...",
                help="Enter any city name worldwide",
                key="city_input"
            )
            
            location_data = city_name
            request_type = "forecast_by_city"
            is_valid = bool(city_name.strip())
        
        st.markdown("---")
        
        # Submit button
        submit_button = st.button(
            "🔍 Get Weather Data",
            type="primary",
            disabled=not is_valid,
            use_container_width=True
        )
        
        if not is_valid:
            st.warning("⚠️ Please enter valid location data")
        
        # Add help section in sidebar
        st.markdown("---")
        st.markdown("### 💡 Quick Help")
        if weather_type == "🚨 Weather Alerts (US State)":
            st.info("Enter 2-letter state codes like CA, NY, TX, FL")
        elif weather_type == "🌤️ Weather Forecast (Coordinates)":
            st.info("You can find coordinates by searching '[City Name] coordinates' on Google")
        else:
            st.info("Enter any city name worldwide. AI will find the coordinates automatically!")
    
    # Main content area - Results only
    if submit_button and is_valid:
        # Show what we're searching for
        st.markdown("""
        <div class="results-header">
            <h2>🔍 Weather Results</h2>
        </div>
        """, unsafe_allow_html=True)
        
        with st.spinner("🔄 Fetching weather data..."):
            # Use cached request
            result = cached_weather_request(request_type, location_data)
            
            if result["success"]:
                if result["type"] == "alerts":
                    display_alerts(result["data"])
                else:  # forecast
                    location_info = None
                    if "city" in result:
                        location_info = {"city": result["city"], "coordinates": result["coordinates"]}
                    elif "coordinates" in result:
                        location_info = {"coordinates": result["coordinates"]}
                    
                    display_forecast(result["data"], location_info)
                
                # Show cache info
                st.markdown("""
                <div class="cache-info">
                    <p><strong>✨ Performance Info:</strong> Data cached for 5 minutes for faster subsequent requests</p>
                    <p><strong>🕒 Last updated:</strong> {}</p>
                </div>
                """.format(datetime.now().strftime('%H:%M:%S')), unsafe_allow_html=True)
                
            else:
                st.markdown(f"""
                <div class="error-card">
                    <h3>❌ Error</h3>
                    <p>{result['error']}</p>
                    <p>Please check your input and try again.</p>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        # Landing page content in main area
        st.markdown("""
        ## 👋 Welcome to the Weather Dashboard!
        
        This powerful tool provides comprehensive weather information with lightning-fast performance.
        
        ### 🚨 Weather Alerts
        - **Real-time alerts** for any US state
        - **Severity indicators** with color coding
        - **Detailed descriptions** and safety instructions
        - **Emergency notifications** for severe weather
        
        ### 🌤️ Weather Forecasts
        - **5-day detailed forecasts** for any location worldwide
        - **Precise coordinates** or **city name** input
        - **Temperature, wind, and atmospheric conditions**
        - **Professional weather descriptions**
        
        ### ⚡ Performance Features
        - **⚡ Lightning Fast**: Smart caching provides instant responses
        - **🎨 Beautiful Display**: Clean, easy-to-read weather information
        - **🌍 Global Coverage**: AI-powered city lookup works worldwide
        - **📊 Real-time Data**: Fresh data from the National Weather Service
        
        ---
        
        👈 **Get started by selecting an option from the sidebar and entering your location!**
        """)
        
        # Add feature showcase
        st.markdown("### 🎯 Feature Showcase")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="metric-container">
                <h4>🚨 Emergency Alerts</h4>
                <p>Monitor severe weather conditions across all 50 US states with real-time emergency notifications</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-container">
                <h4>📍 Pinpoint Accuracy</h4>
                <p>Use exact GPS coordinates for precise weather data or let AI find coordinates from city names</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Second row
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("""
            <div class="metric-container">
                <h4>🌍 Global Coverage</h4>
                <p>Search weather for any city worldwide with intelligent location detection and validation</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-container">
                <h4>⚡ Lightning Fast</h4>
                <p>Smart caching provides instant responses for repeated requests with 5-minute data freshness</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()