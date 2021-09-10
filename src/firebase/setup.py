import os
import pyrebase
from dotenv import load_dotenv

load_dotenv('.env')
class Envs:
    FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
    FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN')
    FIREBASE_AUTH_PASSWORD = os.getenv('FIREBASE_AUTH_PASSWORD')
    FIREBASE_AUTH_USERNAME = os.getenv('FIREBASE_AUTH_USERNAME')
    FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')
    FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')




# configs
config = {
  "apiKey": Envs.FIREBASE_API_KEY,
  "authDomain": Envs.FIREBASE_AUTH_DOMAIN,
  "databaseURL": Envs.FIREBASE_DATABASE_URL,
  "storageBucket": Envs.FIREBASE_STORAGE_BUCKET
}



def get_firebase_objects():
    firebase = pyrebase.initialize_app(config)
    # storage
    storage = firebase.storage()
    # auth user
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password(
      Envs.FIREBASE_AUTH_USERNAME,
      Envs.FIREBASE_AUTH_PASSWORD
    )
    return (auth, user, storage)

