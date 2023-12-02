import pandas as pd

def get_top_secret_data():
    data = {
        'Project Code Name': [
            'Apollo Unearthed',
            'Majestic 12 Guests',
            'Operation Atlantis',
            'Nessie\'s Itinerary',
            'Sasquatch Sizing'
        ],
        'Brief': [
            'Lunar set, Studio 51, Nevada Desert. Shutter Speed: 1/250 sec.',
            'Visitor log including Zorg, Chewbacca. RSVP status: Confirmed.',
            'Coordinates: Undisclosed. Status: Active. Seeker Drones: Deployed.',
            'Daily routine: Splash, Greet, Siesta. Tea Time: Confidential.',
            'Footwear logistics. Size: Classified. Preferred Terrain: Undetected.'
        ],
        'Clearance Level': [
            'Ultra',
            'Cosmic Top Secret',
            'Eyes Only',
            'Delta Green',
            'Shadow'
        ]
    }
    df = pd.DataFrame(data)
    return df
