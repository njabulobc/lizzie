# data_generator.py
import json
import random
import time
import requests
from faker import Faker
from datetime import datetime
import math

# Initialize Faker
fake = Faker()

# Configuration
WEB_APP_URL = "http://localhost:8000/api/predict/"  # Replace with your web app's URL
NUM_TRANSACTIONS = 150                               # Number of transactions to generate and send
DELAY_BETWEEN_REQUESTS = 1                         # Seconds between requests

# Define possible values for categorical fields
MERCHANTS = [
    'Amazon', 'Pick n Pay', 'N Richards', 'Choppies', 'Savemore',
    'eBay', 'Trade Center', 'Spar', '7 Rings', 'Museyamwa',
    'KFC', 'Chicken Inn', 'QV Pharmacy', 'Total', 'Zuva',
    'Indrive', 'Uber', 'Nike', 'Adidas', 'Under Armour',
    'Push Athletics', 'Pfeka', 'Greenwood Pharmacy', 
    'Chicken Slice', 'Foodbox', 'Thuli', 'Engen', 'Kombi',
    'MedOrange'
]

CATEGORIES = [
    'Food', 'Fuel', 'Clothing', 'Utilities', 'Medical',
    'Toys', 'Appliances', 'Electronics', 'Entertainment',
    'Retail', 'Other'
]

GENDERS = ['M', 'F']

CITIES = [
    'Harare', 'Bulawayo', 'Mutare', 'Gweru', 'Masvingo',
    'Chinhoyi', 'Kwekwe', 'Marondera', 'Chivhu', 'Zvishavane'
]

PROVINCES = [
    'Harare', 'Bulawayo', 'Manicaland', 'Mashonaland',
    'Matabeleland', 'Masvingo', 'Midlands',
    'Mashonaland West', 'Mashonaland East',
    'Matabeleland North', 'Matabeleland South'
]

JOBS = [
    'Engineer', 'Doctor', 'Teacher', 'Lawyer', 'Nurse',
    'Pilot', 'Farmer', 'Artist', 'Musician', 'Athlete', 
    'IT Support', 'Actuary', 'Politician', 'Soldier',
    'Mechanic', 'Hwindi', 'Driver', 'Lecturer', "Accountant", "Architect", 
    "Pharmacist", "Veterinarian", "Data Scientist", "Environmental Consultant", 
    "Research Scientist", "Social Worker", "Chef", "Tour Guide", "Mining Geologist", 
    "Customs Officer", "Banker", "Statistician", "Auditor", "Physiotherapist", "Radiographer", 
    "Forensic Analyst", "Insurance Broker", "Microbiologist", "Human Resource Manager",
    "Marketing Specialist", "Graphic Designer", "Event Planner", 
    "Real Estate Agent", "Plumber", "Electrician", "Interior Designer", "Civil Servant",'Other'
]

FRAUD_TYPES = ['Card Not Present', 'Card Present', 'Account Takeover', 'Merchant Fraud']

def random_lat_long():
    latitude = round(random.uniform(-22.0, -14.5), 6)
    longitude = round(random.uniform(25.5, 33.0), 6)
    return latitude, longitude

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def create_merchant_category_mapping(merchants, categories):
    
    merchant_category_map = {
    # E-commerce
        'Amazon': 'Electronics',
        'eBay': 'Other',
        
        # Grocery Stores
        'Pick n Pay': 'Food',
        'Choppies': 'Food',
        'Savemore': 'Food',
        'Spar': 'Food',
        
        # Pharmacies
        'QV Pharmacy': 'Medical',
        'Greenwood Pharmacy': 'Medical',
        'MedOrange': 'Medical',
        
        # Fast Food
        'KFC': 'Food',
        'Chicken Inn': 'Food',
        'Chicken Slice': 'Food',
        'Foodbox': 'Food',
        
        # Fuel Stations
        'Total': 'Fuel',
        'Zuva': 'Fuel',
        'Thuli': 'Fuel',
        'Engen': 'Fuel',
        
        # Transportation
        'Indrive': 'Other',
        'Uber': 'Other',
        'Kombi': 'Other',
        
        # Clothing Stores
        'Nike': 'Clothing',
        'Adidas': 'Clothing',
        'Under Armour': 'Clothing',
        'Push Athletics': 'Clothing',
        'Pfeka': 'Clothing',
        
        # Other/Misc
        'N Richards': 'Other',
        '7 Rings': 'Other',
        'Museyamwa': 'Other',
        'Trade Center': 'Other'
    }

      # For any merchants not explicitly mapped, randomly assign a category
    for merchant in merchants:
        if merchant not in merchant_category_map:
            merchant_category_map[merchant] = random.choice(categories)
    
    return merchant_category_map

def create_city_province_mapping(cities, provinces):
    city_province_map = {
        'Harare': 'Harare',
        'Bulawayo': 'Bulawayo',
        'Mutare': 'Manicaland',
        'Gweru': 'Midlands',
        'Masvingo': 'Masvingo',
        'Chinhoyi': 'Mashonaland West',
        'Kwekwe': 'Midlands',
        'Marondera': 'Mashonaland East',
        'Chivhu': 'Mashonaland East',
        'Zvishavane': 'Midlands',
        'Kariba': 'Mashonaland West',
        'Shurugwi': 'Midlands',
        'Karoi': 'Mashonaland West',
        'Beit Bridge': 'Matabeleland South',
        'Mhangura': 'Mashonaland West',
        'Hwange': 'Matabeleland North',
        'Vic Falls': 'Matabeleland North',
        'Lupane': 'Matabeleland North'
    }
    
    # For any cities not explicitly mapped, randomly assign a province
    for city in cities:
        if city not in city_province_map:
            city_province_map[city] = random.choice(provinces)
    
    return city_province_map

# Create mappings before generating data
MERCHANT_CATEGORIES = create_merchant_category_mapping(MERCHANTS, CATEGORIES)
CITY_PROVINCES = create_city_province_mapping(CITIES, PROVINCES)

def generate_fake_data():
    merchant = random.choice(MERCHANTS)
    category = random.choice(CATEGORIES)
    gender = random.choice(GENDERS)
    city = random.choice(CITIES)
    province = random.choice(PROVINCES)
    latitude, longitude = random_lat_long()
    merch_latitude, merch_longitude = random_lat_long()
    distance = calculate_distance(latitude, longitude, merch_latitude, merch_longitude)
    base_fraud_prob = 0.01
    category_fraud_multiplier = 1.5 if category in ['Electronics', 'Appliances'] else 1.0
    distance_fraud_multiplier = 1.2 if distance > 5 else 1.0
    adjusted_fraud_prob = base_fraud_prob * category_fraud_multiplier * distance_fraud_multiplier
    adjusted_fraud_prob = min(adjusted_fraud_prob, 0.5)
    is_fraud = random.random() < adjusted_fraud_prob
    amt = round(random.uniform(500.0, 5000.0), 2) if is_fraud else round(random.uniform(1.0, 1000.0), 2)
    job = random.choice(JOBS)
    city_pop = random.randint(10000, 1000000)
    processed_at_dt = fake.date_time_between(start_date='-1y', end_date='now')
    processed_at = processed_at_dt.isoformat()
    unix_time = int(time.mktime(processed_at_dt.timetuple()))
    hour = processed_at_dt.hour
    day_of_week = processed_at_dt.weekday()
    month = processed_at_dt.month
    is_weekend = 1 if day_of_week >= 5 else 0
    transaction = {
        "merchant": merchant,
        "category": category,
        "amt": amt,
        "gender": gender,
        "city": city,
        "province": province,
        "latitude": latitude,
        "longitude": longitude,
        "city_pop": city_pop,
        "job": job,
        "unix_time": unix_time,
        "merch_latitude": merch_latitude,
        "merch_longitude": merch_longitude,
        "hour": hour,
        "day_of_week": day_of_week,
        "month": month,
        "is_weekend": is_weekend,
       # "is_fraud": is_fraud,
    }
    return transaction

def send_data_to_api():
    url = WEB_APP_URL
    headers = {
        'Content-Type': 'application/json',
    }

    for _ in range(NUM_TRANSACTIONS):
        data = generate_fake_data()
        try:
            response = requests.post(url, json=data, headers=headers, timeout=5)
            response.raise_for_status()
            print(f"Sent data: {json.dumps(data)}")
            print(f"Received response: {response.json()}\n")
        except requests.exceptions.HTTPError as http_err:
            error_response = response.json() if response.headers.get('Content-Type', '').startswith('application/json') else response.text
            print(f"HTTP error occurred: {http_err} - Response: {error_response}\n")
        except requests.exceptions.RequestException as req_err:
            print(f"An error occurred: {req_err}\n")
        time.sleep(DELAY_BETWEEN_REQUESTS)

if __name__ == "__main__":
    send_data_to_api()