from pymongo import MongoClient
from datetime import datetime

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://devxulfiqar:nSISUpLopruL7S8j@mypaperlessoffice.z5g84.mongodb.net/?retryWrites=true&w=majority&appName=mypaperlessoffice"
DB_NAME = "fleet-management"

print("Connecting to MongoDB...")
client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)

# Test connection
try:
    client.server_info()
    print("✓ Connected to MongoDB successfully!")
    
    db = client[DB_NAME]
    
    # Test insert
    fines_collection = db['rta_fines']
    total_collection = db['rta_total']
    
    print(f"Collections in database: {db.list_collection_names()}")
    print(f"Total fines records: {fines_collection.count_documents({})}")
    print(f"Total records in total collection: {total_collection.count_documents({})}")
    
    # Show latest records
    print("\nLatest fines:")
    for fine in fines_collection.find().sort("created_at", -1).limit(5):
        print(f"  - {fine.get('vehicle_info')} | {fine.get('amount')} | {fine.get('date_time')}")
    
    # Show total
    print("\nTotal amount record:")
    total_doc = total_collection.find_one({"type": "total_fines"})
    if total_doc:
        print(f"  Total: {total_doc.get('total_amount')}")
        print(f"  Last updated: {total_doc.get('last_updated')}")
    else:
        print("  No total record found")
    
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    client.close()
    print("\nConnection closed.")
