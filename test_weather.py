#!/usr/bin/env python3
"""
Test script for the weather MCP server functions.
This will test the weather functions directly without using the MCP protocol.
"""

import asyncio
import sys
from weather import get_alerts, get_forecast

async def test_weather_functions():
    """Test the weather functions directly."""
    print("=" * 50)
    print("Testing Weather Server Functions")
    print("=" * 50)
    
    # Test 1: Get alerts for California
    print("\n1. Testing weather alerts for California (CA):")
    print("-" * 40)
    try:
        alerts = await get_alerts("CA")
        print(alerts)
    except Exception as e:
        print(f"Error getting alerts: {e}")
    
    # Test 2: Get forecast for San Francisco
    print("\n2. Testing forecast for San Francisco (37.7749, -122.4194):")
    print("-" * 60)
    try:
        forecast = await get_forecast(37.7749, -122.4194)
        print(forecast)
    except Exception as e:
        print(f"Error getting forecast: {e}")
    
    # Test 3: Get forecast for New York City
    print("\n3. Testing forecast for New York City (40.7128, -74.0060):")
    print("-" * 58)
    try:
        forecast = await get_forecast(40.7128, -74.0060)
        print(forecast)
    except Exception as e:
        print(f"Error getting forecast: {e}")
    
    print("\n" + "=" * 50)
    print("Testing completed!")
    print("=" * 50)

if __name__ == "__main__":
    print("Starting weather function tests...")
    asyncio.run(test_weather_functions())
