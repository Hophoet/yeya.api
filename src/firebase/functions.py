import uuid
from src.firebase.setup import get_firebase_objects 


def upload(file, old_file_name):
    try:
        auth, user, storage = get_firebase_objects()
        file_name = old_file_name if old_file_name else str(uuid.uuid1())
        store = storage.child(f'users/{file_name}.jpg').put(
            file,
            user['idToken']
        )
        url = storage.child(f'users/{file_name}.jpg').get_url(
            store.get('downloadTokens')
        )
        return (url, file_name)
    except Exception as error:
        raise error
