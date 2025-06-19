import numpy as np
from datetime import datetime, timedelta

def get_base_traffic_pattern():
    """Get base traffic patterns for different times and seasons in Uttarakhand"""
    
    # Hour-based patterns (24-hour format)
    hourly_patterns = {
        'weekday': {
            'morning_peak': {
                'hours': [8, 9, 10],
                'factor': 1.5,
                'description': 'Morning commute and tourist movement'
            },
            'afternoon_lull': {
                'hours': [13, 14],
                'factor': 0.8,
                'description': 'Post-lunch quiet period'
            },
            'evening_peak': {
                'hours': [16, 17, 18],
                'factor': 1.4,
                'description': 'Evening rush and tourist return'
            },
            'pilgrimage_hours': {
                'hours': [4, 5, 6, 7],
                'factor': 1.6,
                'description': 'Early morning pilgrimage movement'
            },
            'night_quiet': {
                'hours': [23, 0, 1, 2, 3],
                'factor': 0.4,
                'description': 'Night time low traffic'
            }
        },
        'weekend': {
            'early_pilgrimage': {
                'hours': [4, 5, 6, 7],
                'factor': 1.8,
                'description': 'Weekend pilgrimage rush'
            },
            'tourist_peak': {
                'hours': [9, 10, 11, 12, 13, 14],
                'factor': 1.7,
                'description': 'Peak tourist movement hours'
            },
            'evening_leisure': {
                'hours': [15, 16, 17, 18, 19],
                'factor': 1.5,
                'description': 'Evening tourist activities'
            },
            'night_movement': {
                'hours': [20, 21, 22],
                'factor': 0.9,
                'description': 'Evening return traffic'
            },
            'night_quiet': {
                'hours': [23, 0, 1, 2, 3],
                'factor': 0.5,
                'description': 'Night time low traffic'
            }
        }
    }
    
    # Seasonal patterns with Uttarakhand-specific events
    seasonal_patterns = {
        'winter_tourism': {
            'months': [12, 1],
            'factor': 1.3,
            'description': 'Winter sports and snow tourism',
            'affected_areas': ['Auli', 'Munsiyari', 'Mussoorie']
        },
        'spring_season': {
            'months': [2, 3, 4],
            'factor': 1.2,
            'description': 'Pleasant weather tourism',
            'affected_areas': ['Nainital', 'Mussoorie', 'Ranikhet']
        },
        'summer_peak': {
            'months': [5, 6],
            'factor': 1.8,
            'description': 'Peak tourist season',
            'affected_areas': ['All tourist destinations']
        },
        'monsoon': {
            'months': [7, 8, 9],
            'factor': 0.6,
            'description': 'Reduced traffic due to rain',
            'affected_areas': ['Mountain roads', 'Char Dham routes']
        },
        'autumn_tourism': {
            'months': [10, 11],
            'factor': 1.4,
            'description': 'Post-monsoon tourism',
            'affected_areas': ['Valley regions', 'Wildlife sanctuaries']
        }
    }
    
    # Religious and cultural events
    special_events = {
        'Char_Dham_Yatra': {
            'months': [5, 6, 7, 8, 9, 10],
            'factor': 1.8,
            'affected_routes': ['Yamunotri', 'Gangotri', 'Kedarnath', 'Badrinath'],
            'description': 'Major pilgrimage season'
        },
        'Kanwar_Yatra': {
            'month': 7,
            'factor': 2.0,
            'affected_routes': ['Haridwar', 'Rishikesh'],
            'description': 'Major religious foot traffic'
        },
        'Nanda_Devi_Raj_Jat': {
            'month': 8,
            'factor': 1.5,
            'affected_routes': ['Nainital', 'Almora'],
            'description': 'Traditional pilgrimage'
        },
        'Kumbh_Mela': {
            'month': 1,
            'factor': 2.5,
            'affected_routes': ['Haridwar', 'Rishikesh'],
            'description': 'Major religious gathering'
        },
        'Winter_Sports': {
            'months': [12, 1],
            'factor': 1.6,
            'affected_routes': ['Auli', 'Dayara Bugyal'],
            'description': 'Winter sports season'
        },
        'Valley_of_Flowers': {
            'months': [7, 8, 9],
            'factor': 1.4,
            'affected_routes': ['Valley of Flowers', 'Hemkund Sahib'],
            'description': 'Peak flowering season'
        }
    }
    
    return hourly_patterns, seasonal_patterns, special_events

def get_future_traffic_predictions(hours_ahead=3):
    """Predict traffic conditions for the next few hours in Uttarakhand"""
    current_time = datetime.now()
    predictions = []
    
    hourly_patterns, seasonal_patterns, special_events = get_base_traffic_pattern()
    
    for hour in range(hours_ahead):
        future_time = current_time + timedelta(hours=hour)
        
        # Base traffic level (adjusted for Uttarakhand's general traffic patterns)
        base_traffic = 0.4  # Lower base traffic due to mountainous terrain
        
        # Apply hourly patterns
        current_hour = future_time.hour
        is_weekend = future_time.weekday() >= 5
        pattern_key = 'weekend' if is_weekend else 'weekday'
        
        for period, data in hourly_patterns[pattern_key].items():
            if current_hour in data['hours']:
                base_traffic *= data['factor']
                break
        
        # Apply seasonal factors
        current_month = future_time.month
        for season, data in seasonal_patterns.items():
            if current_month in data.get('months', [data.get('month')]):
                base_traffic *= data['factor']
        
        # Check for special events
        for event, data in special_events.items():
            if isinstance(data.get('months', data.get('month')), list):
                if current_month in data['months']:
                    base_traffic *= data['factor']
            elif current_month == data.get('month'):
                base_traffic *= data['factor']
        
        # Add weather-based randomness
        # More variation in monsoon months
        if current_month in [7, 8, 9]:
            noise = np.random.normal(0, 0.2)  # More variation during monsoon
        else:
            noise = np.random.normal(0, 0.1)
        
        traffic_level = min(1.0, max(0.1, base_traffic + noise))
        predictions.append((future_time, traffic_level))
    
    return predictions

def get_road_specific_prediction(road_name, base_prediction, elevation=None, road_type=None):
    """Adjust predictions based on specific road characteristics in Uttarakhand"""
    
    # Road type factors based on Uttarakhand's road network
    road_factors = {
        'NH-7': 1.2,    # Dehradun-Haridwar highway
        'NH-58': 1.3,   # Badrinath route
        'NH-94': 1.2,   # Uttarkashi route
        'NH-109': 1.1,  # Kedarnath route
        'NH-121': 1.0,  # Standard national highway
        'NH-309A': 0.9, # Less trafficked route
        'NH-119': 0.9,  # Secondary route
        'SH-': 0.8,     # State highways
        'MDR': 0.7      # Major district roads
    }
    
    # Special route characteristics
    route_characteristics = {
        'char_dham': {
            'factor': 1.6,
            'description': 'Major pilgrimage route'
        },
        'tourist': {
            'factor': 1.4,
            'description': 'Popular tourist route'
        },
        'pilgrimage': {
            'factor': 1.3,
            'description': 'Religious significance'
        },
        'local': {
            'factor': 0.9,
            'description': 'Local traffic route'
        }
    }
    
    # Elevation-based adjustments
    elevation_factors = {
        (0, 1000): 1.0,      # Plains and valleys
        (1000, 2000): 0.9,   # Lower hills
        (2000, 3000): 0.8,   # Higher hills
        (3000, float('inf')): 0.7  # Alpine zones
    }
    
    # Find applicable road factor
    factor = 1.0
    for road_type, road_factor in road_factors.items():
        if road_type in road_name:
            factor = road_factor
            break
    
    # Apply route type factor
    if road_type in route_characteristics:
        factor *= route_characteristics[road_type]['factor']
    
    # Apply elevation factor if available
    if elevation is not None:
        for (min_elev, max_elev), elev_factor in elevation_factors.items():
            if min_elev <= elevation < max_elev:
                factor *= elev_factor
                break
    
    # Calculate final prediction
    adjusted_prediction = min(1.0, base_prediction * factor)
    
    return adjusted_prediction 