import os
import jwt
import json
import getpass
import requests
from pathlib import Path
from datetime import datetime
from valdi.config.settings import Config


class Authenticator:
    def __init__(self):
        self.user_email = None
        self.refresh_token = None
        self._access_token = None
        self.credentials_filepath = Path(__file__).parent.parent.parent / Config.VALDI_CREDENTIALS_FILE
        if os.path.isfile(self.credentials_filepath):
            self._read_credentials()
            if self._is_token_expired(self.refresh_token):
                self._renew_credentials(verbose=True)
            else:
                self._renew_access_token()
        else:
            self._renew_credentials()
        self.user_info = self._get_user_info()

    @property
    def access_token(self):
        if self._is_token_expired(self._access_token):
            self._renew_access_token()
        return self._access_token

    def _get_user_info(self):
        response = requests.get(
            url=f'{Config.VALDI_BASE_URL}/account',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
            }
        )
        response.raise_for_status()
        return json.loads(response.text)

    def _renew_credentials(self, verbose=False):
        if verbose:
            print('Your credentials have expired, you must reauthenticate.')
        hidden_dir = self.credentials_filepath.parent
        os.makedirs(hidden_dir, exist_ok=True)

        self.user_email = input('Account email: ')
        account_pass = getpass.getpass('Password: ')

        response = requests.post(
            url=f'{Config.VALDI_BASE_URL}/account/login',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'email': self.user_email, 'password': account_pass})
        )
        response.raise_for_status()
        json_response = json.loads(response.text)
        self.refresh_token = json_response['refresh_token']
        self._access_token = json_response['access_token']

        with open(self.credentials_filepath, 'w') as f:
            f.write(self.refresh_token)

    def _read_credentials(self):
        with open(self.credentials_filepath, 'r') as f:
            self.refresh_token = f.read()

    def _renew_access_token(self):
        if self._is_token_expired(self.refresh_token):
            self._renew_credentials(verbose=True)
        else:
            response = requests.post(
                url=f'{Config.VALDI_BASE_URL}/account/refresh_token',
                headers={'Content-Type': 'application/json'},
                data=json.dumps({'token': self.refresh_token})
            )
            response.raise_for_status()
            json_response = json.loads(response.text)
            self._access_token = json_response['access_token']

    @staticmethod
    def _is_token_expired(token):
        decoded_token = jwt.decode(token, options={'verify_signature': False})
        token_expiry = datetime.strptime(str(decoded_token['exp']), '%Y%m%d%H%M%S')
        if datetime.utcnow() > token_expiry:
            return True
        else:
            return False
