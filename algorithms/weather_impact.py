import random
from datetime import datetime

class WeatherImpact:
    def __init__(self):
        self.weather_conditions = {
            'Clear': {
                'icon': '☀️',
                'impact': 1.0,
                'description': 'Normal traffic conditions',
                'elevation_sensitivity': 1.0
            },
            'Cloudy': {
                'icon': '☁️',
                'impact': 1.1,
                'description': 'Slightly reduced visibility',
                'elevation_sensitivity': 1.1
            },
            'Light Rain': {
                'icon': '🌦️',
                'impact': 1.2,
                'description': 'Wet roads, moderate visibility',
                'elevation_sensitivity': 1.2
            },
            'Heavy Rain': {
                'icon': '🌧️',
                'impact': 1.4,
                'description': 'Poor visibility, risk of waterlogging',
                'elevation_sensitivity': 1.5
            },
            'Thunderstorm': {
                'icon': '⛈️',
                'impact': 1.6,
                'description': 'Dangerous driving conditions',
                'elevation_sensitivity': 1.7
            },
            'Light Snow': {
                'icon': '🌨️',
                'impact': 1.5,
                'description': 'Slippery roads, chains recommended',
                'elevation_sensitivity': 1.6
            },
            'Heavy Snow': {
                'icon': '❄️',
                'impact': 2.0,
                'description': 'Extremely dangerous conditions',
                'elevation_sensitivity': 2.2
            },
            'Mountain Fog': {
                'icon': '🌫️',
                'impact': 1.7,
                'description': 'Near-zero visibility in mountains',
                'elevation_sensitivity': 1.8
            },
            'Landslide Risk': {
                'icon': '⚠️',
                'impact': 2.0,
                'description': 'High risk in mountain areas',
                'elevation_sensitivity': 2.5
            },
            'Road Blockage': {
                'icon': '🚫',
                'impact': 2.5,
                'description': 'Mountain passes may be closed',
                'elevation_sensitivity': 3.0
            }
        }
        
        # Uttarakhand-specific seasons
        self.seasons = {
            'Winter': {
                'months': [12, 1, 2],
                'conditions': {
                    'low': ['Clear', 'Cloudy', 'Mountain Fog'],
                    'medium': ['Light Snow', 'Mountain Fog', 'Clear', 'Cloudy'],
                    'high': ['Heavy Snow', 'Mountain Fog', 'Light Snow'],
                    'very_high': ['Heavy Snow', 'Road Blockage']
                },
                'description': 'Snow in higher elevations, fog in valleys'
            },
            'Spring': {
                'months': [3, 4],
                'conditions': {
                    'low': ['Clear', 'Light Rain', 'Cloudy'],
                    'medium': ['Light Rain', 'Cloudy', 'Mountain Fog'],
                    'high': ['Light Snow', 'Mountain Fog', 'Light Rain'],
                    'very_high': ['Heavy Snow', 'Light Snow', 'Mountain Fog']
                },
                'description': 'Moderate weather, occasional rain'
            },
            'Summer': {
                'months': [5, 6],
                'conditions': {
                    'low': ['Clear', 'Light Rain', 'Thunderstorm'],
                    'medium': ['Light Rain', 'Thunderstorm', 'Mountain Fog'],
                    'high': ['Thunderstorm', 'Mountain Fog', 'Light Rain'],
                    'very_high': ['Thunderstorm', 'Mountain Fog', 'Light Snow']
                },
                'description': 'Pleasant in hills, hot in plains'
            },
            'Monsoon': {
                'months': [7, 8, 9],
                'conditions': {
                    'low': ['Heavy Rain', 'Thunderstorm', 'Light Rain'],
                    'medium': ['Heavy Rain', 'Landslide Risk', 'Thunderstorm'],
                    'high': ['Landslide Risk', 'Heavy Rain', 'Road Blockage'],
                    'very_high': ['Road Blockage', 'Landslide Risk', 'Heavy Rain']
                },
                'description': 'Heavy rainfall, high landslide risk'
            },
            'Post-Monsoon': {
                'months': [10, 11],
                'conditions': {
                    'low': ['Clear', 'Cloudy', 'Light Rain'],
                    'medium': ['Cloudy', 'Mountain Fog', 'Light Rain'],
                    'high': ['Mountain Fog', 'Light Snow', 'Cloudy'],
                    'very_high': ['Light Snow', 'Mountain Fog', 'Road Blockage']
                },
                'description': 'Clearing weather, early winter in high areas'
            }
        }
        
        # Elevation zones for Uttarakhand
        self.elevation_zones = {
            'low': (0, 1000),       # Terai and Doon Valley
            'medium': (1000, 2000),  # Lesser Himalayan Zone
            'high': (2000, 3000),    # Greater Himalayan Zone
            'very_high': (3000, float('inf'))  # Tethys Himalayan Zone
        }
        
        # Special route conditions
        self.special_routes = {
            'char_dham': {
                'risk_factor': 1.5,
                'seasonal_closure': ['Winter'],
                'monsoon_risk': 2.0
            },
            'pilgrimage': {
                'risk_factor': 1.3,
                'seasonal_closure': [],
                'monsoon_risk': 1.5
            },
            'tourist': {
                'risk_factor': 1.2,
                'seasonal_closure': [],
                'monsoon_risk': 1.3
            }
        }

    def get_elevation_zone(self, elevation):
        """Determine elevation zone based on actual elevation"""
        for zone, (min_elev, max_elev) in self.elevation_zones.items():
            if min_elev <= elevation < max_elev:
                return zone
        return 'very_high'

    def get_current_season(self):
        """Get current season based on month"""
        current_month = datetime.now().month
        for season, data in self.seasons.items():
            if current_month in data['months']:
                return season
        return 'Summer'  # Default season

    def get_current_weather(self, elevation_zone):
        """Get weather based on season, time, and elevation zone"""
        season = self.get_current_season()
        hour = datetime.now().hour
        
        # Get conditions for the specific elevation zone
        possible_conditions = self.seasons[season]['conditions'][elevation_zone]
        
        # Time-based modifications
        if 6 <= hour <= 9:  # Morning
            if elevation_zone in ['medium', 'high', 'very_high']:
                possible_conditions = ['Mountain Fog'] * 2 + possible_conditions
        elif 14 <= hour <= 17:  # Afternoon (monsoon thunderstorms)
            if season == 'Monsoon':
                possible_conditions = ['Thunderstorm', 'Heavy Rain'] * 2 + possible_conditions
        elif 18 <= hour <= 23 or 0 <= hour <= 5:  # Night
            if elevation_zone in ['medium', 'high', 'very_high']:
                possible_conditions = ['Mountain Fog'] * 3 + possible_conditions
        
        weather = random.choice(possible_conditions)
        return {
            'condition': weather,
            'icon': self.weather_conditions[weather]['icon'],
            'impact': self.weather_conditions[weather]['impact'],
            'description': self.weather_conditions[weather]['description'],
            'elevation_sensitivity': self.weather_conditions[weather]['elevation_sensitivity'],
            'season': season
        }

    def apply_weather_impact(self, base_traffic, elevation, route_type=None):
        """
        Apply weather impact to traffic considering elevation and route type
        
        Parameters:
        - base_traffic: Base traffic value
        - elevation: Actual elevation in meters
        - route_type: Type of route ('char_dham', 'pilgrimage', 'tourist', None)
        """
        elevation_zone = self.get_elevation_zone(elevation)
        weather = self.get_current_weather(elevation_zone)
        season = self.get_current_season()
        
        # Base weather impact
        impact = weather['impact']
        
        # Elevation sensitivity
        elevation_factor = weather['elevation_sensitivity']
        if elevation_zone == 'high':
            elevation_factor *= 1.2
        elif elevation_zone == 'very_high':
            elevation_factor *= 1.5
        
        # Route type impact
        route_factor = 1.0
        if route_type in self.special_routes:
            route_data = self.special_routes[route_type]
            route_factor = route_data['risk_factor']
            
            # Check seasonal closure
            if season in route_data['seasonal_closure']:
                return 0.0, {**weather, 'description': 'Route closed for season'}
            
            # Apply monsoon risk for special routes
            if season == 'Monsoon':
                route_factor *= route_data['monsoon_risk']
        
        # Calculate final impact
        total_impact = impact * elevation_factor * route_factor
        
        # Calculate final traffic value (capped at 1.0)
        final_traffic = min(base_traffic * total_impact, 1.0)
        
        return final_traffic, weather 