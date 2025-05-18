import random
from datetime import datetime

class WeatherImpact:
    def __init__(self):
        self.weather_conditions = {
            'Clear': {'impact': 1.0, 'icon': '☀️', 'description': 'Normal traffic conditions'},
            'Rain': {'impact': 1.3, 'icon': '🌧️', 'description': 'Slower speeds, increased congestion'},
            'Heavy Rain': {'impact': 1.5, 'icon': '⛈️', 'description': 'Significant delays, careful driving required'},
            'Fog': {'impact': 1.4, 'icon': '🌫️', 'description': 'Reduced visibility, slower traffic'},
            'Snow': {'impact': 1.6, 'icon': '❄️', 'description': 'Severe delays, hazardous conditions'}
        }
        
        # Seasonal weather probabilities (simplified)
        self.seasonal_weights = {
            'winter': {'Clear': 0.4, 'Rain': 0.2, 'Heavy Rain': 0.1, 'Fog': 0.2, 'Snow': 0.1},
            'summer': {'Clear': 0.6, 'Rain': 0.2, 'Heavy Rain': 0.1, 'Fog': 0.1, 'Snow': 0},
            'monsoon': {'Clear': 0.2, 'Rain': 0.4, 'Heavy Rain': 0.3, 'Fog': 0.1, 'Snow': 0}
        }
    
    def get_current_season(self):
        """Determine current season based on month"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5, 6]:
            return 'summer'
        else:
            return 'monsoon'
    
    def get_current_weather(self):
        """Get current weather condition based on seasonal probabilities"""
        season = self.get_current_season()
        weights = self.seasonal_weights[season]
        conditions = list(weights.keys())
        probabilities = list(weights.values())
        
        weather = random.choices(conditions, probabilities)[0]
        return {
            'condition': weather,
            'impact': self.weather_conditions[weather]['impact'],
            'icon': self.weather_conditions[weather]['icon'],
            'description': self.weather_conditions[weather]['description']
        }
    
    def apply_weather_impact(self, base_traffic):
        """Apply weather impact to base traffic level"""
        weather = self.get_current_weather()
        return min(0.95, base_traffic * weather['impact']), weather 