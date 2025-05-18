import numpy as np
from datetime import datetime, timedelta

def predict_traffic_pattern(hour, day_of_week, is_holiday=False):
    """
    Predict traffic patterns based on time and day
    Returns a traffic multiplier (0.1 to 1.0)
    """
    # Base traffic patterns by hour (24-hour format)
    hourly_patterns = {
        # Morning rush hours
        7: 0.7, 8: 0.9, 9: 0.8, 10: 0.6,
        # Afternoon
        11: 0.4, 12: 0.5, 13: 0.5, 14: 0.4, 15: 0.5, 16: 0.6,
        # Evening rush hours
        17: 0.8, 18: 0.9, 19: 0.8, 20: 0.6,
        # Night/Early morning
        21: 0.4, 22: 0.3, 23: 0.2, 0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.2, 5: 0.3, 6: 0.5
    }

    # Day of week multipliers (0 = Monday, 6 = Sunday)
    day_multipliers = {
        0: 1.0,  # Monday
        1: 1.0,  # Tuesday
        2: 1.0,  # Wednesday
        3: 1.0,  # Thursday
        4: 1.1,  # Friday
        5: 0.7,  # Saturday
        6: 0.6   # Sunday
    }

    # Get base traffic level for the hour
    base_traffic = hourly_patterns.get(hour, 0.5)
    
    # Apply day of week multiplier
    traffic = base_traffic * day_multipliers[day_of_week]
    
    # Reduce traffic if it's a holiday
    if is_holiday:
        traffic *= 0.6
    
    # Add some randomness (±10%)
    traffic *= np.random.uniform(0.9, 1.1)
    
    # Ensure traffic stays within bounds
    return np.clip(traffic, 0.1, 1.0)

def get_future_traffic_predictions(hours_ahead=3):
    """
    Get traffic predictions for the next few hours
    Returns a list of (timestamp, traffic_level) tuples
    """
    predictions = []
    current_time = datetime.now()
    
    for i in range(hours_ahead):
        future_time = current_time + timedelta(hours=i)
        traffic_level = predict_traffic_pattern(
            future_time.hour,
            future_time.weekday(),
            is_holiday=False  # Could be enhanced with actual holiday data
        )
        predictions.append((future_time, traffic_level))
    
    return predictions

def get_road_specific_prediction(road_name, base_traffic):
    """
    Adjust traffic prediction based on road-specific factors
    """
    road_factors = {
        "NH-48": 1.2,  # Major highway, typically busier
        "DND Flyway": 1.1,  # Major connecting route
        "Mathura Road": 1.0,
        "GT Karnal Road": 1.0,
        "NH-9": 0.9,
        "KMP Expressway": 0.8,  # Usually less congested
        "Noida-Greater Noida Expressway": 1.1,
        "Yamuna Expressway": 0.9,
        "Eastern Peripheral Expressway": 0.8
    }
    
    factor = road_factors.get(road_name, 1.0)
    return np.clip(base_traffic * factor, 0.1, 1.0) 