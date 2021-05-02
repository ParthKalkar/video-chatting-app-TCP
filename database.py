import pymongo

client = pymongo.MongoClient('mongodb+srv://admin_rafik:KomZSX3zBmF13ZKa@main-cluster.atvy1.mongodb.net/test')
db = client.video_chat_app
users = db.users



