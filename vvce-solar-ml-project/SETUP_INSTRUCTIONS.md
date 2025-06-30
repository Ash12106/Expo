# VS Code Setup Instructions

## Quick Setup for Development

1. **Extract the Project**
   - Extract the `vvce-solar-ml-project.zip` file to your desired location
   - Open the extracted folder in VS Code

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   python run.py
   ```

4. **Access the Dashboard**
   - Open your browser to `http://localhost:5000`
   - The application will automatically create sample VVCE solar plant data

## Environment Variables (Optional)

For production or custom configuration, set these environment variables:

```bash
export SESSION_SECRET="your-secure-secret-key"
export DATABASE_URL="sqlite:///instance/solar_ml.db"
export OPENWEATHER_API_KEY="your-openweather-api-key"
```

## Project Features

- **Dashboard**: Real-time solar plant monitoring
- **ML Predictions**: 6-month energy forecasting
- **Panel Health**: Individual panel performance tracking
- **Maintenance Advisor**: Smart cleaning recommendations
- **Weather Analysis**: Weather impact on solar production

## File Structure

- `run.py` - Start the development server
- `main.py` - Production entry point
- `app.py` - Flask configuration
- `models.py` - Database models
- `routes.py` - Web routes and API endpoints
- `ml_models.py` - Machine learning engine
- `templates/` - HTML templates
- `static/` - CSS and JavaScript files

## Development Tips

- The application uses SQLite by default (no additional setup needed)
- Sample data is automatically generated for VVCE plants
- All currency calculations are in Indian Rupees (INR)
- Weather data uses fallback patterns when no API key is provided