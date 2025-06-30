# VVCE Solar Plant ML Prediction System

A comprehensive machine learning-powered web application for monitoring, predicting, and optimizing solar power plants at Vidhyavardhaka College of Engineering (VVCE) in Mysuru, Karnataka.

## Features

- **6-Month Forecasting**: Advanced ML models for energy production predictions
- **Real-time Monitoring**: Live dashboard with weather data integration
- **Panel Health Monitoring**: Individual panel performance tracking
- **Maintenance Advisor**: Intelligent cleaning and maintenance recommendations
- **Weather Impact Analysis**: Comprehensive weather correlation analytics
- **Financial Tracking**: Revenue calculations in Indian Rupees (INR)

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   ```bash
   export SESSION_SECRET="your-secret-key-here"
   export DATABASE_URL="sqlite:///instance/solar_ml.db"
   export OPENWEATHER_API_KEY="your-api-key-here"  # Optional
   ```

3. **Run the Application**
   ```bash
   python main.py
   ```

4. **Access the Dashboard**
   Open your browser to `http://localhost:5000`

## Project Structure

- `main.py` - Application entry point
- `app.py` - Flask application configuration
- `models.py` - Database models and schema
- `routes.py` - API endpoints and web routes
- `ml_models.py` - Machine learning prediction engine
- `weather_api.py` - Weather data integration
- `maintenance_advisor.py` - Intelligent maintenance system
- `panel_health_monitor.py` - Real-time panel monitoring
- `templates/` - HTML templates
- `static/` - CSS and JavaScript assets

## Machine Learning Models

The system uses ensemble methods combining:
- Random Forest Regressor
- XGBoost Regressor
- Advanced LSTM architecture (prepared for future integration)

## Database Schema

- **SolarPlant**: Plant specifications and configuration
- **WeatherData**: Daily weather metrics
- **EnergyProduction**: Energy output and financial data
- **MaintenanceRecord**: Maintenance logs and costs
- **MLPrediction**: Model predictions with confidence scores

## API Endpoints

- `/api/train/<plant_id>` - Train ML models
- `/api/predictions/<plant_id>` - Generate predictions
- `/api/weather/<plant_id>` - Get weather data
- `/api/panel-health/<plant_id>` - Panel health metrics
- `/api/maintenance/<plant_id>` - Maintenance recommendations

## Development

The application is designed for Indian solar installations with:
- INR currency calculations
- Mysuru, Karnataka weather patterns
- Academic calendar integration for VVCE
- Local climate considerations

## License

This project is developed for educational purposes at VVCE.