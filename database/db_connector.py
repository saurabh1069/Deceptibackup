from pymongo import MongoClient

def get_db(uri):
    client = MongoClient(uri)
    db = client['decepticoders']
    return db
