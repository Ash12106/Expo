"""
Contextual Weather Impact Prediction for Solar Output
Advanced prediction system that analyzes weather patterns and forecasts their impact on solar generation
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from sqlalchemy import func
from models import SolarPlant, WeatherData, EnergyProduction
from weather_api import weather_api
from app import db
import logging

class WeatherImpactPredictor:
    """
    Advanced weather impact prediction system for solar energy output
    Analyzes correlations between weather conditions and energy production
    """
    
    def __init__(self):
        self.weather_factors = {
            'solar_irradiance': {'weight': 0.4, 'optimal': 7.0, 'threshold': 2.0},
            'cloud_cover': {'weight': 0.3, 'optimal': 0.0, 'threshold': 80.0},
            'temperature': {'weight': 0.15, 'optimal': 25.0, 'threshold': 45.0},
            'humidity': {'weight': 0.1, 'optimal': 50.0, 'threshold': 90.0},
            'wind_speed': {'weight': 0.05, 'optimal': 15.0, 'threshold': 50.0}
        }
        
        # Weather impact categories
        self.impact_categories = {
            'excellent': {'min': 0.9, 'color': '#22c55e', 'description': 'Optimal conditions for maximum output'},
            'very_good': {'min': 0.8, 'color': '#16a34a', 'description': 'Very favorable conditions'},
            'good': {'min': 0.65, 'color': '#84cc16', 'description': 'Good conditions with minor impact'},
            'moderate': {'min': 0.5, 'color': '#eab308', 'description': 'Moderate impact on output'},
            'poor': {'min': 0.35, 'color': '#f97316', 'description': 'Significant reduction expected'},
            'very_poor': {'min': 0.0, 'color': '#ef4444', 'description': 'Severe weather impact'}
        }
    
    def get_current_weather_impact(self, plant_id):
        """Get current weather impact analysis for a plant"""
        try:
            plant = SolarPlant.query.get(plant_id)
            if not plant:
                return self._default_weather_impact()
            
            # Get current weather
            coords = weather_api.get_location_coordinates(plant.location.split(',')[0])
            current_weather = weather_api.get_current_weather(coords[0], coords[1])
            
            # Calculate impact score
            impact_score = self._calculate_weather_impact_score(current_weather)
            
            # Determine impact category
            impact_category = self._get_impact_category(impact_score)
            
            # Get historical baseline for comparison
            baseline_output = self._get_baseline_output(plant_id)
            predicted_output = baseline_output * impact_score
            
            # Calculate specific factor impacts
            factor_impacts = self._analyze_individual_factors(current_weather)
            
            return {
                'plant_id': plant_id,
                'current_weather': current_weather,
                'impact_score': round(impact_score, 3),
                'impact_category': impact_category,
                'predicted_output_kwh': round(predicted_output, 1),
                'baseline_output_kwh': round(baseline_output, 1),
                'output_change_percent': round((impact_score - 1) * 100, 1),
                'factor_impacts': factor_impacts,
                'recommendations': self._generate_recommendations(current_weather, impact_category),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error getting current weather impact: {e}")
            return self._default_weather_impact()
    
    def get_hourly_forecast_impact(self, plant_id, hours=24):
        """Get hourly weather impact forecast for next 24 hours"""
        try:
            plant = SolarPlant.query.get(plant_id)
            if not plant:
                return self._default_forecast_impact()
            
            # Get weather forecast
            coords = weather_api.get_location_coordinates(plant.location.split(',')[0])
            forecast_data = weather_api.get_forecast(coords[0], coords[1], days=2)
            
            hourly_impacts = []
            baseline_output = self._get_baseline_output(plant_id)
            
            for hour in range(hours):
                forecast_time = datetime.now() + timedelta(hours=hour)
                
                # Get weather for this hour (simplified from daily forecast)
                day_index = min(hour // 24, len(forecast_data) - 1)
                day_weather = forecast_data[day_index] if forecast_data else {}
                
                # Apply hourly solar pattern
                hourly_weather = self._apply_hourly_pattern(day_weather, forecast_time.hour)
                
                # Calculate impact
                impact_score = self._calculate_weather_impact_score(hourly_weather)
                impact_category = self._get_impact_category(impact_score)
                
                hourly_impacts.append({
                    'hour': forecast_time.strftime('%H:%M'),
                    'datetime': forecast_time.isoformat(),
                    'weather': hourly_weather,
                    'impact_score': round(impact_score, 3),
                    'impact_category': impact_category,
                    'predicted_output': round(baseline_output * impact_score * self._get_solar_factor(forecast_time.hour), 1),
                    'solar_factor': self._get_solar_factor(forecast_time.hour)
                })
            
            return {
                'plant_id': plant_id,
                'forecast_period': f'{hours} hours',
                'hourly_impacts': hourly_impacts,
                'summary': self._generate_forecast_summary(hourly_impacts),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error getting forecast impact: {e}")
            return self._default_forecast_impact()
    
    def get_weather_correlation_analysis(self, plant_id, days=30):
        """Analyze correlation between weather factors and actual production"""
        try:
            # Get historical data
            cutoff_date = date.today() - timedelta(days=days)
            
            production_data = db.session.query(
                EnergyProduction.date,
                EnergyProduction.energy_produced,
                EnergyProduction.equipment_efficiency,
                WeatherData.temperature,
                WeatherData.humidity,
                WeatherData.cloud_cover,
                WeatherData.wind_speed,
                WeatherData.solar_irradiance
            ).join(
                WeatherData,
                (EnergyProduction.plant_id == WeatherData.plant_id) &
                (EnergyProduction.date == WeatherData.date)
            ).filter(
                EnergyProduction.plant_id == plant_id,
                EnergyProduction.date >= cutoff_date
            ).all()
            
            if not production_data:
                return self._default_correlation_analysis()
            
            # Convert to arrays for analysis
            energy_data = [row.energy_produced for row in production_data]
            weather_metrics = {
                'temperature': [row.temperature for row in production_data],
                'humidity': [row.humidity for row in production_data],
                'cloud_cover': [row.cloud_cover for row in production_data],
                'wind_speed': [row.wind_speed for row in production_data],
                'solar_irradiance': [row.solar_irradiance for row in production_data]
            }
            
            # Calculate correlations
            correlations = {}
            for factor, values in weather_metrics.items():
                correlation = np.corrcoef(energy_data, values)[0, 1]
                correlations[factor] = {
                    'correlation': round(correlation, 3),
                    'strength': self._interpret_correlation_strength(correlation),
                    'impact_direction': 'positive' if correlation > 0 else 'negative'
                }
            
            # Find optimal conditions
            optimal_conditions = self._find_optimal_conditions(production_data)
            
            # Performance insights
            insights = self._generate_performance_insights(production_data, correlations)
            
            return {
                'plant_id': plant_id,
                'analysis_period': f'{days} days',
                'data_points': len(production_data),
                'correlations': correlations,
                'optimal_conditions': optimal_conditions,
                'insights': insights,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error in correlation analysis: {e}")
            return self._default_correlation_analysis()
    
    def get_seasonal_weather_patterns(self, plant_id):
        """Analyze seasonal weather patterns and their impact"""
        try:
            # Get data for different seasons
            seasons = {
                'winter': {'months': [12, 1, 2], 'data': []},
                'spring': {'months': [3, 4, 5], 'data': []},
                'summer': {'months': [6, 7, 8], 'data': []},
                'autumn': {'months': [9, 10, 11], 'data': []}
            }
            
            # Get historical data for past year
            cutoff_date = date.today() - timedelta(days=365)
            
            historical_data = db.session.query(
                EnergyProduction.date,
                EnergyProduction.energy_produced,
                WeatherData.temperature,
                WeatherData.humidity,
                WeatherData.cloud_cover,
                WeatherData.solar_irradiance
            ).join(
                WeatherData,
                (EnergyProduction.plant_id == WeatherData.plant_id) &
                (EnergyProduction.date == WeatherData.date)
            ).filter(
                EnergyProduction.plant_id == plant_id,
                EnergyProduction.date >= cutoff_date
            ).all()
            
            # Group data by seasons
            for row in historical_data:
                month = row.date.month
                for season, info in seasons.items():
                    if month in info['months']:
                        info['data'].append(row)
                        break
            
            # Analyze each season
            seasonal_analysis = {}
            for season, info in seasons.items():
                if info['data']:
                    seasonal_analysis[season] = self._analyze_seasonal_data(info['data'])
                else:
                    seasonal_analysis[season] = self._default_seasonal_data()
            
            return {
                'plant_id': plant_id,
                'seasonal_patterns': seasonal_analysis,
                'current_season': self._get_current_season(),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error in seasonal analysis: {e}")
            return self._default_seasonal_patterns()
    
    def _calculate_weather_impact_score(self, weather_data):
        """Calculate overall weather impact score (0-1)"""
        if not weather_data:
            return 0.7  # Default moderate impact
        
        total_score = 0
        total_weight = 0
        
        for factor, config in self.weather_factors.items():
            if factor in weather_data:
                value = weather_data[factor]
                factor_score = self._calculate_factor_score(factor, value, config)
                total_score += factor_score * config['weight']
                total_weight += config['weight']
        
        return total_score / total_weight if total_weight > 0 else 0.7
    
    def _calculate_factor_score(self, factor, value, config):
        """Calculate score for individual weather factor"""
        optimal = config['optimal']
        threshold = config['threshold']
        
        if factor == 'cloud_cover':
            # Lower cloud cover is better
            if value <= optimal:
                return 1.0
            elif value >= threshold:
                return 0.2
            else:
                return 1.0 - (value - optimal) / (threshold - optimal) * 0.8
        
        elif factor == 'solar_irradiance':
            # Higher irradiance is better
            if value >= optimal:
                return 1.0
            elif value <= threshold:
                return 0.3
            else:
                return 0.3 + (value - threshold) / (optimal - threshold) * 0.7
        
        elif factor == 'temperature':
            # Optimal around 25°C, decreases at extremes
            if abs(value - optimal) <= 5:
                return 1.0
            elif value >= threshold:
                return 0.4  # Very hot reduces efficiency
            elif value <= 0:
                return 0.3  # Very cold reduces efficiency
            else:
                distance = abs(value - optimal)
                return max(0.3, 1.0 - distance / 30)
        
        elif factor == 'humidity':
            # Lower humidity generally better
            if value <= optimal:
                return 1.0
            elif value >= threshold:
                return 0.6
            else:
                return 1.0 - (value - optimal) / (threshold - optimal) * 0.4
        
        elif factor == 'wind_speed':
            # Moderate wind is good for cooling
            if 5 <= value <= optimal:
                return 1.0
            elif value >= threshold:
                return 0.3  # Very high wind is problematic
            else:
                return 0.8 + value / optimal * 0.2
        
        return 0.7  # Default for unknown factors
    
    def _get_impact_category(self, impact_score):
        """Get impact category based on score"""
        for category, config in self.impact_categories.items():
            if impact_score >= config['min']:
                return {
                    'name': category,
                    'score': impact_score,
                    'color': config['color'],
                    'description': config['description']
                }
        
        return {
            'name': 'very_poor',
            'score': impact_score,
            'color': self.impact_categories['very_poor']['color'],
            'description': self.impact_categories['very_poor']['description']
        }
    
    def _get_baseline_output(self, plant_id):
        """Get baseline energy output for the plant"""
        try:
            # Get average production for similar conditions
            recent_avg = db.session.query(
                func.avg(EnergyProduction.energy_produced)
            ).filter(
                EnergyProduction.plant_id == plant_id,
                EnergyProduction.date >= date.today() - timedelta(days=30)
            ).scalar()
            
            if recent_avg:
                return recent_avg
            
            # Fallback to plant capacity estimation
            plant = SolarPlant.query.get(plant_id)
            if plant:
                # Assume 6-8 hours of effective sunlight
                return plant.capacity_mw * 1000 * 7  # 7 hours average
            
            return 5000  # Default fallback
            
        except Exception:
            return 5000
    
    def _analyze_individual_factors(self, weather_data):
        """Analyze impact of individual weather factors"""
        factor_impacts = {}
        
        for factor, config in self.weather_factors.items():
            if factor in weather_data:
                value = weather_data[factor]
                score = self._calculate_factor_score(factor, value, config)
                
                factor_impacts[factor] = {
                    'current_value': value,
                    'optimal_value': config['optimal'],
                    'impact_score': round(score, 3),
                    'impact_level': self._get_factor_impact_level(score),
                    'recommendation': self._get_factor_recommendation(factor, value, config)
                }
        
        return factor_impacts
    
    def _get_factor_impact_level(self, score):
        """Get impact level description for factor score"""
        if score >= 0.9:
            return 'optimal'
        elif score >= 0.7:
            return 'good'
        elif score >= 0.5:
            return 'moderate'
        else:
            return 'poor'
    
    def _get_factor_recommendation(self, factor, value, config):
        """Get recommendation for specific weather factor"""
        optimal = config['optimal']
        
        if factor == 'cloud_cover':
            if value > 70:
                return "Heavy cloud cover expected - monitor for reduced output"
            elif value > 40:
                return "Partly cloudy conditions - moderate impact expected"
            else:
                return "Clear skies - optimal conditions for solar generation"
        
        elif factor == 'temperature':
            if value > 40:
                return "High temperature may reduce panel efficiency - ensure adequate ventilation"
            elif value < 5:
                return "Low temperature - monitor for potential frost or ice formation"
            else:
                return "Temperature within optimal range for solar generation"
        
        elif factor == 'wind_speed':
            if value > 40:
                return "High wind speeds - check panel security and safety protocols"
            elif value < 5:
                return "Low wind - panels may run warmer, potentially reducing efficiency"
            else:
                return "Good wind conditions for panel cooling"
        
        return f"Monitor {factor} levels - current value: {value}"
    
    def _generate_recommendations(self, weather_data, impact_category):
        """Generate actionable recommendations based on weather impact"""
        recommendations = []
        
        # Temperature-based recommendations
        if 'temperature' in weather_data:
            temp = weather_data['temperature']
            if temp > 40:
                recommendations.append({
                    'priority': 'high',
                    'category': 'temperature',
                    'message': 'High temperature alert - ensure panel cooling systems are operational',
                    'action': 'Check ventilation and cooling systems'
                })
            elif temp < 0:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'temperature',
                    'message': 'Freezing conditions - monitor for ice formation on panels',
                    'action': 'Inspect panels for ice or frost buildup'
                })
        
        # Cloud cover recommendations
        if 'cloud_cover' in weather_data:
            clouds = weather_data['cloud_cover']
            if clouds > 80:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'clouds',
                    'message': 'Heavy cloud cover - significant output reduction expected',
                    'action': 'Adjust energy consumption plans accordingly'
                })
        
        # Wind speed recommendations
        if 'wind_speed' in weather_data:
            wind = weather_data['wind_speed']
            if wind > 50:
                recommendations.append({
                    'priority': 'high',
                    'category': 'wind',
                    'message': 'High wind speeds - potential safety concern',
                    'action': 'Secure loose equipment and check panel mountings'
                })
        
        # Overall impact recommendations
        impact_name = impact_category['name']
        if impact_name in ['poor', 'very_poor']:
            recommendations.append({
                'priority': 'medium',
                'category': 'general',
                'message': 'Poor weather conditions expected - reduced energy output',
                'action': 'Consider backup power sources if critical loads are present'
            })
        
        return recommendations
    
    def _apply_hourly_pattern(self, daily_weather, hour):
        """Apply hourly patterns to daily weather forecast"""
        if not daily_weather:
            return {}
        
        # Copy base weather
        hourly_weather = daily_weather.copy()
        
        # Adjust temperature for time of day
        if 'temperature' in hourly_weather:
            base_temp = hourly_weather['temperature']
            if 6 <= hour <= 18:  # Daylight hours
                temp_factor = 0.7 + 0.6 * self._get_solar_factor(hour)
            else:  # Night hours
                temp_factor = 0.6
            hourly_weather['temperature'] = base_temp * temp_factor
        
        # Adjust solar irradiance for time of day
        if 'solar_irradiance' in hourly_weather:
            base_irradiance = hourly_weather['solar_irradiance']
            solar_factor = self._get_solar_factor(hour)
            hourly_weather['solar_irradiance'] = base_irradiance * solar_factor
        
        return hourly_weather
    
    def _get_solar_factor(self, hour):
        """Get solar intensity factor based on hour (0-1)"""
        if hour < 6 or hour > 18:
            return 0
        elif 6 <= hour < 8 or 16 < hour <= 18:
            return 0.3
        elif 8 <= hour < 10 or 14 < hour <= 16:
            return 0.7
        else:  # 10 AM to 2 PM
            return 1.0
    
    def _generate_forecast_summary(self, hourly_impacts):
        """Generate summary of hourly forecast impacts"""
        if not hourly_impacts:
            return {}
        
        # Calculate averages
        avg_impact = np.mean([h['impact_score'] for h in hourly_impacts])
        avg_output = np.mean([h['predicted_output'] for h in hourly_impacts])
        
        # Find peak and low periods
        peak_hour = max(hourly_impacts, key=lambda x: x['predicted_output'])
        low_hour = min(hourly_impacts, key=lambda x: x['predicted_output'])
        
        # Count impact categories
        category_counts = {}
        for impact in hourly_impacts:
            category = impact['impact_category']['name']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            'average_impact_score': round(avg_impact, 3),
            'average_predicted_output': round(avg_output, 1),
            'peak_output_hour': peak_hour['hour'],
            'peak_output_value': peak_hour['predicted_output'],
            'lowest_output_hour': low_hour['hour'],
            'lowest_output_value': low_hour['predicted_output'],
            'impact_distribution': category_counts,
            'overall_outlook': self._get_overall_outlook(avg_impact)
        }
    
    def _get_overall_outlook(self, avg_impact):
        """Get overall outlook description"""
        if avg_impact >= 0.8:
            return "Excellent weather conditions expected"
        elif avg_impact >= 0.65:
            return "Good conditions with minimal impact"
        elif avg_impact >= 0.5:
            return "Moderate weather impact expected"
        else:
            return "Challenging weather conditions ahead"
    
    def _interpret_correlation_strength(self, correlation):
        """Interpret correlation coefficient strength"""
        abs_corr = abs(correlation)
        if abs_corr >= 0.7:
            return 'strong'
        elif abs_corr >= 0.5:
            return 'moderate'
        elif abs_corr >= 0.3:
            return 'weak'
        else:
            return 'very_weak'
    
    def _find_optimal_conditions(self, production_data):
        """Find optimal weather conditions from historical data"""
        if not production_data:
            return {}
        
        # Find the day with highest production
        best_day = max(production_data, key=lambda x: x.energy_produced)
        
        return {
            'best_production_date': best_day.date.isoformat(),
            'best_production_value': best_day.energy_produced,
            'optimal_temperature': best_day.temperature,
            'optimal_humidity': best_day.humidity,
            'optimal_cloud_cover': best_day.cloud_cover,
            'optimal_solar_irradiance': best_day.solar_irradiance
        }
    
    def _generate_performance_insights(self, production_data, correlations):
        """Generate insights from correlation analysis"""
        insights = []
        
        # Temperature insights
        if 'temperature' in correlations:
            temp_corr = correlations['temperature']['correlation']
            if temp_corr < -0.3:
                insights.append({
                    'type': 'temperature',
                    'message': 'Higher temperatures show negative correlation with output',
                    'recommendation': 'Consider panel cooling solutions for hot days'
                })
        
        # Cloud cover insights
        if 'cloud_cover' in correlations:
            cloud_corr = correlations['cloud_cover']['correlation']
            if cloud_corr < -0.5:
                insights.append({
                    'type': 'clouds',
                    'message': 'Cloud cover significantly impacts energy production',
                    'recommendation': 'Monitor weather forecasts for cloudy periods'
                })
        
        # Solar irradiance insights
        if 'solar_irradiance' in correlations:
            irr_corr = correlations['solar_irradiance']['correlation']
            if irr_corr > 0.6:
                insights.append({
                    'type': 'irradiance',
                    'message': 'Solar irradiance shows strong positive correlation',
                    'recommendation': 'Optimize panel positioning for maximum sun exposure'
                })
        
        return insights
    
    def _analyze_seasonal_data(self, seasonal_data):
        """Analyze data for a specific season"""
        if not seasonal_data:
            return self._default_seasonal_data()
        
        avg_production = np.mean([row.energy_produced for row in seasonal_data])
        avg_temp = np.mean([row.temperature for row in seasonal_data])
        avg_humidity = np.mean([row.humidity for row in seasonal_data])
        avg_clouds = np.mean([row.cloud_cover for row in seasonal_data])
        avg_irradiance = np.mean([row.solar_irradiance for row in seasonal_data])
        
        return {
            'average_production': round(avg_production, 1),
            'average_temperature': round(avg_temp, 1),
            'average_humidity': round(avg_humidity, 1),
            'average_cloud_cover': round(avg_clouds, 1),
            'average_solar_irradiance': round(avg_irradiance, 2),
            'data_points': len(seasonal_data),
            'peak_production': max(row.energy_produced for row in seasonal_data),
            'lowest_production': min(row.energy_produced for row in seasonal_data)
        }
    
    def _get_current_season(self):
        """Get current season"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'
    
    def _default_weather_impact(self):
        """Default weather impact data"""
        return {
            'plant_id': None,
            'current_weather': {'temperature': 25, 'humidity': 60, 'cloud_cover': 30, 'solar_irradiance': 5.5},
            'impact_score': 0.75,
            'impact_category': {'name': 'good', 'score': 0.75, 'color': '#84cc16', 'description': 'Good conditions'},
            'predicted_output_kwh': 5250,
            'baseline_output_kwh': 7000,
            'output_change_percent': -25.0,
            'factor_impacts': {},
            'recommendations': [],
            'last_updated': datetime.now().isoformat()
        }
    
    def _default_forecast_impact(self):
        """Default forecast impact data"""
        return {
            'plant_id': None,
            'forecast_period': '24 hours',
            'hourly_impacts': [],
            'summary': {},
            'generated_at': datetime.now().isoformat()
        }
    
    def _default_correlation_analysis(self):
        """Default correlation analysis data"""
        return {
            'plant_id': None,
            'analysis_period': '30 days',
            'data_points': 0,
            'correlations': {},
            'optimal_conditions': {},
            'insights': [],
            'generated_at': datetime.now().isoformat()
        }
    
    def _default_seasonal_patterns(self):
        """Default seasonal patterns data"""
        return {
            'plant_id': None,
            'seasonal_patterns': {},
            'current_season': self._get_current_season(),
            'generated_at': datetime.now().isoformat()
        }
    
    def _default_seasonal_data(self):
        """Default seasonal data"""
        return {
            'average_production': 0,
            'average_temperature': 25,
            'average_humidity': 60,
            'average_cloud_cover': 40,
            'average_solar_irradiance': 5.0,
            'data_points': 0,
            'peak_production': 0,
            'lowest_production': 0
        }

# Initialize weather impact predictor
weather_impact_predictor = WeatherImpactPredictor()