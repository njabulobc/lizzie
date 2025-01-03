import pandas as pd
import numpy as np
from faker import Faker
import random
import time
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Parameters
NUM_RECORDS = 17432      # Total number of transactions to generate
FRAUD_PROB = 0.03        # Probability of a transaction being fraudulent

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
    'Chinhoyi', 'Kwekwe', 'Marondera', 'Chivhu', 'Zvishavane', 
    'Kariba', 'Shurugwi', 'Karoi', 'Beit Bridge', 'Mhangura',
    'Hwange', "Vic Falls", 'Lupane'
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

def create_merchant_category_mapping(merchants, categories):
    """
    Create a mapping of merchants to product categories.
    
    Args:
        merchants (list): List of merchant names
        categories (list): List of product categories
    
    Returns:
        dict: A dictionary mapping merchants to categories
    """
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
    """
    Create a mapping of cities to provinces.
    
    Args:
        cities (list): List of city names
        provinces (list): List of province names
    
    Returns:
        dict: A dictionary mapping cities to provinces
    """
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

# Function to generate random latitude and longitude within Zimbabwe
def random_lat_long():
    # Zimbabwe approximate latitude: -21 to -15
    # Zimbabwe approximate longitude: 25 to 35
    latitude = round(random.uniform(-21.0, -15.0), 6)
    longitude = round(random.uniform(25.0, 35.0), 6)
    return latitude, longitude

# Function to generate unix timestamp within the last year
def random_unix_time():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    random_date = fake.date_time_between(start_date=start_date, end_date=end_date)
    return int(time.mktime(random_date.timetuple())), random_date

# Lists to store generated data
data = {
    'merchant': [],
    'category': [],
    'amt': [],
    'gender': [],
    'city': [],
    'province': [],
    'latitude': [],
    'longitude': [],
    'city_pop': [],
    'job': [],
    'unix_time': [],
    'merch_latitude': [],
    'merch_longitude': [],
    'processed_at': [],
    'is_fraud': []
}

for _ in range(NUM_RECORDS):
    # Determine if the transaction is fraudulent
    is_fraud = np.random.rand() < FRAUD_PROB
    
    # Generate merchant and category using the predefined mapping
    merchant = random.choice(MERCHANTS)
    category = MERCHANT_CATEGORIES[merchant]
    
    # Generate amount
    if is_fraud:
        amt = round(random.uniform(500.0, 5000.0), 2)  # Higher amounts for fraud
    else:
        amt = round(random.uniform(1.0, 1000.0), 2)
    
    # Gender
    gender = random.choice(GENDERS)
    
    # City and province using the predefined mapping
    city = random.choice(CITIES)
    province = CITY_PROVINCES[city]
    
    # Latitude and longitude for the transaction
    latitude, longitude = random_lat_long()
    
    # City population
    city_pop = random.randint(10000, 1000000)
    
    # Job
    job = random.choice(JOBS)
    
    # Unix time and processed_at
    unix_time, processed_at = random_unix_time()
    
    # Merchant's latitude and longitude
    merch_latitude, merch_longitude = random_lat_long()
    
    # Append to data
    data['merchant'].append(merchant)
    data['category'].append(category)
    data['amt'].append(amt)
    data['gender'].append(gender)
    data['city'].append(city)
    data['province'].append(province)
    data['latitude'].append(latitude)
    data['longitude'].append(longitude)
    data['city_pop'].append(city_pop)
    data['job'].append(job)
    data['unix_time'].append(unix_time)
    data['merch_latitude'].append(merch_latitude)
    data['merch_longitude'].append(merch_longitude)
    data['processed_at'].append(processed_at)
    data['is_fraud'].append(is_fraud)

# Create DataFrame
df = pd.DataFrame(data)

# Optional: Shuffle the dataset
df = df.sample(frac=1).reset_index(drop=True)

# Save to CSV
df.to_csv('zwg_credit_card_fraud_dataset.csv', index=False)

print(f"Dataset generated with {NUM_RECORDS} records.")
print(f"Fraudulent transactions: {df['is_fraud'].sum()} ({(df['is_fraud'].mean() * 100):.2f}%)")
print("Dataset saved to 'zwg_credit_card_fraud_dataset.csv'.")
