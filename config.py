import os

# MongoDB URI (can be overridden with environment variable)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
