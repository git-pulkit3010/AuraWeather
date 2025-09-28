# AuraWeather 🌤️

A modern, feature-rich weather dashboard that provides real-time weather alerts and forecasts. AuraWeather offers two distinct user interfaces: a sleek, dynamic web application powered by FastAPI and a comprehensive, data-centric dashboard built with Streamlit.

## ✨ Key Features

- **Dual Interfaces**: Choose between a modern, interactive web UI or a powerful Streamlit dashboard.
- **Real-time Weather Alerts**: Get up-to-the-minute weather alerts for any US state from the National Weather Service (NWS).
- **Detailed Forecasts**: Access detailed 5-day weather forecasts for any location worldwide.
- **AI-Powered Geocoding**: Simply enter a city name, and AuraWeather automatically retrieves the precise coordinates using the OpenRouter API.
- **Interactive Experience**: The web UI is built with modern JavaScript, providing a smooth and responsive user experience.
- **Data-Rich Analysis**: The Streamlit app offers a more analytical view of the weather data, perfect for detailed inspection.
- **Efficient & Fast**: The FastAPI backend is asynchronous and includes a caching mechanism for rapid responses.

## 🏛️ Architecture Overview

AuraWeather is composed of several key components:

- **FastAPI Backend (`backend_server.py`)**: A robust Python backend that serves the main web application, provides a RESTful API for weather data, and handles caching.
- **Vanilla JS Frontend (`frontend/`)**: A lightweight, modern frontend built with HTML, Tailwind CSS, and plain JavaScript that communicates with the FastAPI backend.
- **Streamlit UI (`streamlit_app.py`)**: A separate, self-contained Python application that offers an alternative, data-focused user interface.
- **Weather Logic (`weather.py`)**: The core module responsible for fetching and parsing data from the National Weather Service (NWS) and handling geocoding via the OpenRouter API.
- **MCP Integration**: The project utilizes the `mcp` library to define and expose its core weather-fetching capabilities as tools.

## 🚀 Getting Started

Follow these steps to set up and run AuraWeather on your local machine.

### 1. Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js](https://nodejs.org/) (for package management scripts)
- An API key from [OpenRouter](https://openrouter.ai/)

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd weather-server
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Create an environment file:**
    Create a file named `.env` in the root of the project and add your OpenRouter API key:
    ```
    OPENROUTER_API_KEY="your_openrouter_api_key"
    ```

### 3. Running the Application

AuraWeather offers two ways to experience the dashboard. You can run either one or both simultaneously.

#### Option 1: Run the FastAPI Backend & Web UI

This is the primary, recommended way to use AuraWeather.

```bash
uvicorn backend_server:app --host 0.0.0.0 --port 8000 --reload
```

Once the server is running, open your web browser and navigate to [http://localhost:8000](http://localhost:8000).

#### Option 2: Run the Streamlit Application

For a more data-oriented view, you can run the Streamlit app.

```bash
streamlit run streamlit_app.py
```

Once the server is running, open your web browser and navigate to the URL provided in your terminal (usually [http://localhost:8501](http://localhost:8501)).

## 📖 Usage

### Web Application

-   **Switch Tabs**: Navigate between "Alerts", "Forecast by City", and "Forecast by Coordinates".
-   **Get Alerts**: Enter a 2-letter US state code (e.g., CA, NY) to see active weather alerts.
-   **Get Forecasts**:
    -   Enter a city name (e.g., "London", "Tokyo") to get a forecast.
    -   Alternatively, provide precise latitude and longitude for a specific point.

### Streamlit Dashboard

-   **Select Option**: Use the sidebar to choose between fetching alerts or forecasts.
-   **Enter Location**: Input the required information (state code, city, or coordinates).
-   **View Results**: The main panel will display the detailed weather data in a clean, card-based layout.
