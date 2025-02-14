import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError
import bcrypt

# MongoDB Connection URI
uri = "mongodb+srv://ahmedsaad22502145:mongodbmaster@cluster0.eak8u.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = MongoClient(uri)
db = client["online_shopping"]

# Create or access the users collection
users_collection: Collection = db["users"]
counters_collection = db["counters"]  # Collection to store auto-increment IDs
# Ensure the email field is unique
users_collection.create_index("email", unique=True)

# Function to get the next sequence number for products
def get_next_sequence(name: str) -> int:
    counter = counters_collection.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,
    )
    return counter["seq"]


# Function to hash passwords
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


# Function to validate passwords
def validate_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# Enum for user roles
USER_ROLE = ["user", "admin"]

# Example users
users = [
    {
        "_id": get_next_sequence("user_id"),
        "first_name": "Ahmed",
        "last_name": "Saad",
        "email": "admin@dsaa.com",
        "hashed_password": hash_password("AdminPass123"),
        "role": "admin"
    },
    {
        "_id": get_next_sequence("user_id"),
        "first_name": "Alaa",
        "last_name": "Abdelkalek",
        "email": "user@dsaa.com",
        "hashed_password": hash_password("UserPass123"),
        "role": "user"
    }
]

# Insert users
for user in users:
    try:
        users_collection.insert_one(user)
        print(f"✅ Inserted user: {user['email']} with ID: {user['_id']}")
    except DuplicateKeyError:
        print(f"⚠️ User with ID {user['_id']} already exists.")

# Verify insertion
print("📝 Users in the database:")
for user in users_collection.find({}, {"_id": 1, "first_name": 1, "last_name": 1, "role": 1}):
    print(user)