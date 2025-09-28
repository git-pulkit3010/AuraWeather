#!/usr/bin/env python3
"""
Interactive test script for the weather MCP server functions.
This will test the weather functions with user-provided locations.
"""

import asyncio
import sys
from weather import get_alerts, get_forecast

def get_user_input():
    """Get location input from the user."""
    print("=" * 50)
    print("Interactive Weather Information Tool")
    print("=" * 50)
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Get weather alerts for a US state")
        print("2. Get weather forecast for a location (coordinates)")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            return "alerts", get_state_input()
        elif choice == "2":
            return "forecast", get_coordinates_input()
        elif choice == "3":
            return "exit", None
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def get_state_input():
    """Get US state code from user."""
    while True:
        state = input("\nEnter a US state code (e.g., CA, NY, TX): ").strip().upper()
        if len(state) == 2 and state.isalpha():
            return state
        else:
            print("Please enter a valid 2-letter state code.")

def get_coordinates_input():
    """Get latitude and longitude from user."""
    print("\nEnter coordinates for the location:")
    print("(You can find coordinates by searching '[City Name] coordinates' on Google)")
    
    while True:
        try:
            lat_input = input("Latitude (e.g., 37.7749): ").strip()
            lon_input = input("Longitude (e.g., -122.4194): ").strip()
            
            latitude = float(lat_input)
            longitude = float(lon_input)
            
            # Basic validation for US coordinates
            if -180 <= longitude <= 180 and -90 <= latitude <= 90:
                return latitude, longitude
            else:
                print("Please enter valid coordinates (latitude: -90 to 90, longitude: -180 to 180)")
        except ValueError:
            print("Please enter valid numeric coordinates.")

async def run_weather_request(action_type, location_data):
    """Execute the weather request based on user input."""
    try:
        if action_type == "alerts":
            state = location_data
            print(f"\n🌩️  Getting weather alerts for {state}...")
            print("-" * 40)
            result = await get_alerts(state)
            print(result)
            
        elif action_type == "forecast":
            latitude, longitude = location_data
            print(f"\n🌤️  Getting weather forecast for coordinates ({latitude}, {longitude})...")
            print("-" * 60)
            result = await get_forecast(latitude, longitude)
            print(result)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your input and try again.")

async def main():
    """Main interactive loop."""
    while True:
        action_type, location_data = get_user_input()
        
        if action_type == "exit":
            print("\n👋 Thanks for using the weather tool! Goodbye!")
            break
            
        await run_weather_request(action_type, location_data)
        
        # Ask if user wants to continue
        while True:
            continue_choice = input("\n\nWould you like to check another location? (y/n): ").strip().lower()
            if continue_choice in ['y', 'yes']:
                break
            elif continue_choice in ['n', 'no']:
                print("\n👋 Thanks for using the weather tool! Goodbye!")
                return
            else:
                print("Please enter 'y' for yes or 'n' for no.")

if __name__ == "__main__":
    print("Welcome to the Interactive Weather Tool!")
    print("This tool allows you to get weather alerts and forecasts.")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
