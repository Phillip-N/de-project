import json
import os

def build_kaggle_json():
    username = os.environ['KAGGLE_USER']
    key = os.environ['KAGGLE_KEY']

    kaggle_creds = {
        "username": username,
        "key": key
    }

    with open('/root/.kaggle/kaggle.json', 'w') as fp:
        json.dump(kaggle_creds, fp)
