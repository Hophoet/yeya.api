import os
import pyrebase
from .fake import (
  FIREBASE_API_KEY, 
  FIREBASE_AUTH_DOMAIN, 
  FIREBASE_AUTH_PASSWORD, 
  FIREBASE_AUTH_USERNAME, 
  FIREBASE_DATABASE_URL, 
  FIREBASE_STORAGE_BUCKET
)


# configs
config = {
  "apiKey": FIREBASE_API_KEY,
  "authDomain": FIREBASE_AUTH_DOMAIN,
  "databaseURL": FIREBASE_DATABASE_URL,
  "storageBucket": FIREBASE_STORAGE_BUCKET
}



def get_firebase_objects():
    firebase = pyrebase.initialize_app(config)
    # storage
    storage = firebase.storage()
    # auth user
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password(
      FIREBASE_AUTH_USERNAME,
      FIREBASE_AUTH_PASSWORD
    )
    return (auth, user, storage)

