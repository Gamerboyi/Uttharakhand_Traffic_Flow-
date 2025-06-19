import json
import random

# Real Uttarakhand place names organized by type
UTTARAKHAND_PLACES = {
    'cities': [
        'Dehradun', 'Haridwar', 'Rishikesh', 'Mussoorie', 'Tehri', 'Uttarkashi', 
        'Pauri', 'Srinagar', 'Kotdwar', 'Almora', 'Nainital', 'Ranikhet', 'Kausani',
        'Bhimtal', 'Haldwani', 'Rudrapur', 'Kashipur', 'Roorkee', 'Manglaur'
    ],
    'towns': [
        'Chamba', 'Dhanaulti', 'Lansdowne', 'Chakrata', 'Mukteshwar', 'Bageshwar',
        'Pithoragarh', 'Champawat', 'Uttarkashi', 'Joshimath', 'Karnaprayag',
        'Devprayag', 'Rudraprayag', 'Gopeshwar', 'Chamoli', 'Badrinath',
        'Kedarnath', 'Gangotri', 'Yamunotri', 'Hemkund Sahib'
    ],
    'villages': [
        'Maletha', 'Saur', 'Kirtinagar', 'Ghansali', 'Jakholi', 'Guptkashi',
        'Sonprayag', 'Gaurikund', 'Phata', 'Sitapur', 'Kalimath', 'Chopta',
        'Tungnath', 'Chandrashila', 'Auli', 'Gwaldam', 'Kausani', 'Bageshwar',
        'Kapkot', 'Munsyari', 'Dharchula', 'Pithoragarh', 'Gangolihat',
        'Lohaghat', 'Champawat', 'Tanakpur', 'Banbasa', 'Khatima'
    ],
    'passes': [
        'Mana Pass', 'Niti Pass', 'Lipulekh Pass', 'Kungri Bingri Pass',
        'Traill\'s Pass', 'Pindari Pass', 'Kafni Pass', 'Sunderdhunga Pass',
        'Khatling Pass', 'Dayara Pass', 'Dodital Pass', 'Har Ki Doon Pass',
        'Valley of Flowers', 'Hemkund Pass', 'Kedar Tal Pass', 'Gangotri Pass'
    ],
    'temples': [
        'Badrinath Temple', 'Kedarnath Temple', 'Gangotri Temple', 'Yamunotri Temple',
        'Hemkund Sahib', 'Tungnath Temple', 'Rudranath Temple', 'Kalpeshwar Temple',
        'Madhyamaheshwar Temple', 'Kartik Swami Temple', 'Adi Badri Temple',
        'Yogdhyan Badri Temple', 'Vriddha Badri Temple', 'Bhavishya Badri Temple'
    ]
}

def update_place_names():
    """Update the realistic data with proper Uttarakhand place names"""
    
    # Load the current data
    with open('data/uttarakhand_realistic_data.json', 'r') as f:
        data = json.load(f)
    
    # Track used names to avoid duplicates
    used_names = set()
    
    # Update intersections with proper names
    for node_id, node_data in data['intersections'].items():
        current_name = node_data['name']
        
        # Skip if it's already a proper name (not Village/Pass)
        if not current_name.startswith('Village/Pass'):
            used_names.add(current_name)
            continue
        
        # Determine the type of place based on existing type
        place_type = node_data.get('type', 'village')
        
        # Get appropriate name list
        if place_type == 'char_dham':
            name_list = UTTARAKHAND_PLACES['temples']
        elif place_type == 'pilgrimage':
            name_list = UTTARAKHAND_PLACES['temples'] + UTTARAKHAND_PLACES['towns']
        elif place_type == 'tourist':
            name_list = UTTARAKHAND_PLACES['towns'] + UTTARAKHAND_PLACES['villages']
        elif place_type == 'town':
            name_list = UTTARAKHAND_PLACES['towns'] + UTTARAKHAND_PLACES['villages']
        else:
            name_list = UTTARAKHAND_PLACES['villages'] + UTTARAKHAND_PLACES['passes']
        
        # Find an unused name
        new_name = None
        for name in name_list:
            if name not in used_names:
                new_name = name
                used_names.add(name)
                break
        
        # If all names are used, create a unique name
        if new_name is None:
            base_names = UTTARAKHAND_PLACES['villages'] + UTTARAKHAND_PLACES['passes']
            counter = 1
            while new_name is None:
                for base_name in base_names:
                    candidate = f"{base_name} {counter}"
                    if candidate not in used_names:
                        new_name = candidate
                        used_names.add(candidate)
                        break
                counter += 1
        
        # Update the name
        node_data['name'] = new_name
        print(f"Updated {node_id}: {current_name} → {new_name}")
    
    # Update road names to reflect the new place names
    for road in data['roads']:
        from_node = road['from']
        to_node = road['to']
        
        if from_node in data['intersections'] and to_node in data['intersections']:
            from_name = data['intersections'][from_node]['name']
            to_name = data['intersections'][to_node]['name']
            road_type = road.get('type', 'highway')
            
            # Create a proper road name
            road['name'] = f"{from_name} to {to_name} ({road_type.title()})"
    
    # Save the updated data
    with open('data/uttarakhand_realistic_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Updated {len(data['intersections'])} intersections with proper Uttarakhand place names")
    print(f"✅ Updated {len(data['roads'])} roads with proper names")

if __name__ == "__main__":
    update_place_names() 