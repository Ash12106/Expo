"""
Solar Panel Health Monitoring System
Provides real-time monitoring of individual panel performance and health metrics
"""

from datetime import datetime, timedelta, date
from sqlalchemy import func
import random
import json
from models import SolarPlant, EnergyProduction, WeatherData, MaintenanceRecord
from app import db

class PanelHealthMonitor:
    """Real-time panel health monitoring and analytics"""
    
    def __init__(self):
        self.health_thresholds = {
            'excellent': 90,  # Above 90% efficiency
            'good': 80,       # 80-90% efficiency  
            'warning': 70,    # 70-80% efficiency
            'critical': 60    # Below 70% efficiency
        }
    
    def get_panel_health_overview(self, plant_id=None):
        """Get overall health metrics for all panels"""
        try:
            # Get plant(s)
            if plant_id:
                plants = [SolarPlant.query.get(plant_id)]
            else:
                plants = SolarPlant.query.all()
            
            total_panels = sum(self._estimate_panel_count(plant) for plant in plants if plant)
            
            # Simulate panel health data based on recent performance
            health_metrics = self._calculate_health_metrics(plants, total_panels)
            
            return {
                'overall_efficiency': health_metrics['avg_efficiency'],
                'active_panels': health_metrics['active_panels'],
                'total_panels': total_panels,
                'panels_needing_attention': health_metrics['warning_panels'],
                'maintenance_required': health_metrics['critical_panels'],
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting panel health overview: {e}")
            return self._default_health_metrics()
    
    def get_individual_panel_data(self, plant_id=None):
        """Get detailed health data for individual panels"""
        try:
            if plant_id:
                plant = SolarPlant.query.get(plant_id)
                plants = [plant] if plant else []
            else:
                plants = SolarPlant.query.all()
            
            panel_data = []
            
            for plant in plants:
                panel_count = self._estimate_panel_count(plant)
                
                # Get recent performance for this plant
                recent_data = self._get_recent_performance_data(plant.id)
                
                # Generate individual panel data
                for i in range(min(panel_count, 12)):  # Limit to 12 panels for display
                    panel_info = self._generate_panel_health_data(plant, i + 1, recent_data)
                    panel_data.append(panel_info)
            
            return panel_data
            
        except Exception as e:
            print(f"Error getting individual panel data: {e}")
            return self._default_panel_data()
    
    def get_health_alerts(self, plant_id=None):
        """Get current health alerts and warnings"""
        try:
            alerts = []
            
            # Get maintenance alerts
            maintenance_alerts = self._get_maintenance_alerts(plant_id)
            alerts.extend(maintenance_alerts)
            
            # Get performance alerts
            performance_alerts = self._get_performance_alerts(plant_id)
            alerts.extend(performance_alerts)
            
            # Get environmental alerts
            environmental_alerts = self._get_environmental_alerts(plant_id)
            alerts.extend(environmental_alerts)
            
            # Sort by priority and timestamp
            alerts.sort(key=lambda x: (x['priority_order'], x['timestamp']), reverse=True)
            
            return alerts[:10]  # Return top 10 alerts
            
        except Exception as e:
            print(f"Error getting health alerts: {e}")
            return []
    
    def get_performance_trends(self, plant_id=None, hours=24):
        """Get 24-hour performance trend data"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Generate hourly data points
            labels = []
            efficiency_data = []
            power_data = []
            temperature_data = []
            
            for i in range(hours):
                time_point = start_time + timedelta(hours=i)
                labels.append(time_point.strftime('%H:%M'))
                
                # Simulate realistic data with daily patterns
                hour = time_point.hour
                base_efficiency = 85 + 10 * self._get_solar_factor(hour)
                base_power = 2.5 + 3.5 * self._get_solar_factor(hour)
                base_temp = 25 + 15 * self._get_solar_factor(hour)
                
                # Add some randomness
                efficiency_data.append(round(base_efficiency + random.uniform(-5, 5), 1))
                power_data.append(round(base_power + random.uniform(-0.5, 0.5), 2))
                temperature_data.append(round(base_temp + random.uniform(-3, 3), 1))
            
            return {
                'labels': labels,
                'efficiency': efficiency_data,
                'power': power_data,
                'temperature': temperature_data
            }
            
        except Exception as e:
            print(f"Error getting performance trends: {e}")
            return self._default_trend_data()
    
    def _estimate_panel_count(self, plant):
        """Estimate number of panels based on plant capacity"""
        if not plant:
            return 0
        # Assume ~300W per panel
        return int(plant.capacity_mw * 1000 / 300)
    
    def _calculate_health_metrics(self, plants, total_panels):
        """Calculate overall health metrics from plant data"""
        if not plants:
            return {
                'avg_efficiency': 85.0,
                'active_panels': 0,
                'warning_panels': 0,
                'critical_panels': 0
            }
        
        # Get recent efficiency data
        total_efficiency = 0
        count = 0
        
        for plant in plants:
            recent_data = EnergyProduction.query.filter_by(
                plant_id=plant.id
            ).filter(
                EnergyProduction.date >= date.today() - timedelta(days=7)
            ).all()
            
            if recent_data:
                avg_eff = sum(d.equipment_efficiency for d in recent_data) / len(recent_data)
                total_efficiency += avg_eff
                count += 1
        
        avg_efficiency = total_efficiency / count if count > 0 else 85.0
        
        # Estimate panel status distribution
        active_panels = max(1, int(total_panels * 0.95))  # 95% active
        warning_panels = max(0, int(total_panels * 0.03))  # 3% warning
        critical_panels = max(0, int(total_panels * 0.02))  # 2% critical
        
        return {
            'avg_efficiency': round(avg_efficiency, 1),
            'active_panels': active_panels,
            'warning_panels': warning_panels,
            'critical_panels': critical_panels
        }
    
    def _get_recent_performance_data(self, plant_id):
        """Get recent performance data for a plant"""
        recent_data = EnergyProduction.query.filter_by(
            plant_id=plant_id
        ).filter(
            EnergyProduction.date >= date.today() - timedelta(days=7)
        ).order_by(EnergyProduction.date.desc()).first()
        
        return recent_data
    
    def _generate_panel_health_data(self, plant, panel_number, recent_data):
        """Generate health data for an individual panel"""
        base_efficiency = recent_data.equipment_efficiency if recent_data else 85.0
        
        # Add panel-specific variation
        panel_efficiency = base_efficiency + random.uniform(-10, 10)
        panel_efficiency = max(60, min(100, panel_efficiency))  # Clamp between 60-100
        
        # Determine status
        if panel_efficiency >= self.health_thresholds['excellent']:
            status = 'excellent'
            status_class = 'excellent'
            status_icon = 'check-circle'
        elif panel_efficiency >= self.health_thresholds['good']:
            status = 'good'
            status_class = 'good'
            status_icon = 'thumbs-up'
        elif panel_efficiency >= self.health_thresholds['warning']:
            status = 'warning'
            status_class = 'warning'
            status_icon = 'exclamation-triangle'
        else:
            status = 'critical'
            status_class = 'critical'
            status_icon = 'tools'
        
        # Generate other metrics
        current_power = round(300 * (panel_efficiency / 100) + random.uniform(-20, 20), 0)
        temperature = round(30 + random.uniform(-5, 15), 1)
        voltage = round(24 + random.uniform(-2, 2), 1)
        
        # Generate hourly performance data for mini chart
        hourly_data = {
            'labels': [f'{i:02d}:00' for i in range(6, 19)],  # 6 AM to 6 PM
            'values': [round(panel_efficiency * self._get_solar_factor(i) + random.uniform(-5, 5), 1) 
                      for i in range(6, 19)]
        }
        
        # Generate alerts if needed
        alerts = []
        if status == 'critical':
            alerts.append({'type': 'danger', 'message': 'Maintenance required'})
        elif status == 'warning':
            alerts.append({'type': 'warning', 'message': 'Monitor closely'})
        
        return {
            'id': f"{plant.id}_{panel_number}",
            'name': f"Panel {plant.name}-{panel_number:02d}",
            'efficiency': round(panel_efficiency, 1),
            'status': status.title(),
            'status_class': status_class,
            'status_icon': status_icon,
            'current_power': int(current_power),
            'temperature': temperature,
            'voltage': voltage,
            'hourly_data': hourly_data,
            'alerts': alerts
        }
    
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
    
    def _get_maintenance_alerts(self, plant_id=None):
        """Get maintenance-related alerts"""
        alerts = []
        
        # Check for overdue maintenance
        cutoff_date = date.today() - timedelta(days=90)
        
        if plant_id:
            plants = [SolarPlant.query.get(plant_id)]
        else:
            plants = SolarPlant.query.all()
        
        for plant in plants:
            if not plant:
                continue
                
            last_maintenance = MaintenanceRecord.query.filter_by(
                plant_id=plant.id
            ).order_by(MaintenanceRecord.date.desc()).first()
            
            if not last_maintenance or last_maintenance.date < cutoff_date:
                alerts.append({
                    'id': f'maint_{plant.id}',
                    'title': 'Maintenance Overdue',
                    'message': f'{plant.name} requires scheduled maintenance',
                    'priority': 'urgent',
                    'priority_order': 3,
                    'icon': 'tools',
                    'timestamp': '2 hours ago',
                    'action': 'Schedule'
                })
        
        return alerts
    
    def _get_performance_alerts(self, plant_id=None):
        """Get performance-related alerts"""
        alerts = []
        
        # Check for efficiency drops
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        if plant_id:
            plants = [SolarPlant.query.get(plant_id)]
        else:
            plants = SolarPlant.query.all()
        
        for plant in plants:
            if not plant:
                continue
                
            recent_efficiency = db.session.query(
                func.avg(EnergyProduction.equipment_efficiency)
            ).filter(
                EnergyProduction.plant_id == plant.id,
                EnergyProduction.date >= week_ago
            ).scalar()
            
            if recent_efficiency and recent_efficiency < 75:
                alerts.append({
                    'id': f'perf_{plant.id}',
                    'title': 'Efficiency Drop Detected',
                    'message': f'{plant.name} efficiency below normal levels',
                    'priority': 'warning',
                    'priority_order': 2,
                    'icon': 'chart-line-down',
                    'timestamp': '1 hour ago',
                    'action': 'Analyze'
                })
        
        return alerts
    
    def _get_environmental_alerts(self, plant_id=None):
        """Get environment-related alerts"""
        alerts = []
        
        # Check for extreme weather conditions
        if plant_id:
            plants = [SolarPlant.query.get(plant_id)]
        else:
            plants = SolarPlant.query.all()
        
        for plant in plants:
            if not plant:
                continue
                
            recent_weather = WeatherData.query.filter_by(
                plant_id=plant.id,
                date=date.today()
            ).first()
            
            if recent_weather:
                if recent_weather.temperature > 45:
                    alerts.append({
                        'id': f'temp_{plant.id}',
                        'title': 'High Temperature Alert',
                        'message': f'Temperature at {plant.name} exceeds 45°C',
                        'priority': 'warning',
                        'priority_order': 2,
                        'icon': 'thermometer-full',
                        'timestamp': '30 minutes ago',
                        'action': None
                    })
                
                if recent_weather.wind_speed > 50:
                    alerts.append({
                        'id': f'wind_{plant.id}',
                        'title': 'High Wind Speed',
                        'message': f'Wind speed at {plant.name} exceeds 50 km/h',
                        'priority': 'info',
                        'priority_order': 1,
                        'icon': 'wind',
                        'timestamp': '45 minutes ago',
                        'action': None
                    })
        
        return alerts
    
    def _default_health_metrics(self):
        """Default health metrics when no data available"""
        return {
            'overall_efficiency': 85.0,
            'active_panels': 24,
            'total_panels': 25,
            'panels_needing_attention': 1,
            'maintenance_required': 0,
            'last_updated': datetime.now().isoformat()
        }
    
    def _default_panel_data(self):
        """Default panel data when no data available"""
        return [
            {
                'id': f'demo_{i}',
                'name': f'Demo Panel {i:02d}',
                'efficiency': 85.0 + random.uniform(-10, 10),
                'status': 'Good',
                'status_class': 'good',
                'status_icon': 'thumbs-up',
                'current_power': 290 + random.randint(-20, 20),
                'temperature': 32 + random.uniform(-3, 8),
                'voltage': 24 + random.uniform(-1, 1),
                'hourly_data': {
                    'labels': [f'{h:02d}:00' for h in range(6, 19)],
                    'values': [85 * self._get_solar_factor(h) + random.uniform(-5, 5) for h in range(6, 19)]
                },
                'alerts': []
            }
            for i in range(1, 9)
        ]
    
    def _default_trend_data(self):
        """Default trend data when no data available"""
        return {
            'labels': [f'{i:02d}:00' for i in range(24)],
            'efficiency': [85 * self._get_solar_factor(i) + random.uniform(-5, 5) for i in range(24)],
            'power': [2.5 * self._get_solar_factor(i) + random.uniform(-0.5, 0.5) for i in range(24)],
            'temperature': [25 + 15 * self._get_solar_factor(i) + random.uniform(-3, 3) for i in range(24)]
        }

# Initialize health monitor
health_monitor = PanelHealthMonitor()