import pymongo
from root import get_my_private_ip

client = pymongo.MongoClient('mongodb+srv://admin_rafik:KomZSX3zBmF13ZKa@main-cluster.atvy1.mongodb.net/test')
db = client.video_chat_app
users = db.users
print("Successfully connected to the database ✓")


# For now, this file is list of utility functions for the database

# todo make the name stored in a local file, so that we don't add a new user to the db everytime the same user connects

def signup(name):
    user = {
        'name': name,
        'online': False
    }
    users.insert_one(user)


# todo make sure the user doesn't change the online status of other users (do an ip check before)
def go_online(name, ip):
    users.update_one({'name': name}, {'$set': {'online': True,
                                               'ip': ip}})


# todo make this exclude the current user
def get_online_users():
    return users.find({'online': True, 'ip': {'$ne': get_my_private_ip()}})


def go_offline(name):
    users.update_one({'name': name}, {'$set': {'online': False}})
    # For now, we will delete the user each time
    # todo maybe we can use another method?
    users.remove({'name': name})


def get_user_ip(name):
    return users.find_one({'name': name})['ip']
