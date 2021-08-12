import uuid
from src.firebase.setup import (storage, auth, user)

def upload(file):
    try:
        file_name = str(uuid.uuid1())
        store = storage.child(f'books/{file_name}.jpg').put(
            file,
            user['idToken']
        )
        url = storage.child(f'books/{file_name}.jpg').get_url(
            store.get('downloadTokens')
        )
        return url
    except Exception as error:
        raise error
        print('ERROR', error)
