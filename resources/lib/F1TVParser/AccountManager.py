import requests
import json
import os
import pyjwt as jwt
import re
import xbmc
import xbmcaddon
from cache import Store

from datetime import datetime

__ACCOUNT_API__='https://api.formula1.com/v1/account/'
__ACCOUNT_CREATE_SESSION__=__ACCOUNT_API__+'Subscriber/CreateSession'

__HEADER_CD_LANGUAGE__='de-DE'

__ACCOUNT_SOCIAL_AUTHENTICATE__="https://f1tv.formula1.com/api/social-authenticate/"
__ACCOUNT_IDENTITY_PROVIDER_URL__= "/api/identity-providers/iden_732298a17f9c458890a1877880d140f3/"

class AccountManager:
    def exteractSessionData(self):
        __SCRIPT_URL__ = 'https://account.formula1.com/scripts/main.min.js'
        r = self.session.get(__SCRIPT_URL__)
        if r.ok:
            in_constants = False
            for line in r.content.splitlines():
                if 'var ENV_CONST' in line:
                    in_constants = True
                    continue
                if in_constants is True:
                    if '};' in line:
                        break
                    else:
                        if 'apikey' in line:
                            m = re.findall('\"apikey\": *\"(.*?)\"', line)
                            self.auth_headers['apikey'] = m[0]
                        elif 'systemId' in line:
                            m = re.findall('\"systemId\": *\"(.*?)\"', line)
                            self.auth_headers['cd-systemid'] = m[0]
            if 'apikey' in r.text:
                m = re.findall('apikey: *\"(.*?)\"', r.text)
                self.auth_headers['apikey'] = m[0]
            if 'systemId' in r.text:
                m = re.findall('systemId: *\"(.*?)\"', r.text)
                self.auth_headers['cd-systemid'] = m[0]
            print(self.auth_headers)

        return self.auth_headers['apikey'], self.auth_headers['cd-systemid']

    def __requestSessionToken(self):
        login_dict = {"Login": self.username, "Password": self.password}
        r = self.session.post(__ACCOUNT_CREATE_SESSION__, headers=self.auth_headers, data=json.dumps(login_dict))

        if r.ok and 'Fault' not in r.json():
            if r.json()["data"]["subscriptionStatus"] != "active":
                raise ValueError('Subscription is not active.')

            self.session_token = r.json()["data"]["subscriptionToken"]

            # Save the token
            try:
                session_token_store = Store("app://tokens/session/{username}".format(username=self.username))
                session_token_store.clear()
                session_token_store.append(self.session_token)
            except:
                pass
        else:
            raise ValueError('Account Authentication failed.')

    def __requestSocialToken(self):
        dict = {"identity_provider_url": __ACCOUNT_IDENTITY_PROVIDER_URL__, "access_token": self.session_token}

        token_request = self.session.post(__ACCOUNT_SOCIAL_AUTHENTICATE__, data=json.dumps(dict))
        if token_request.ok:
            self.session.headers["Authorization"] = "JWT " + token_request.json()["token"]

            # Save the token
            try:
                session_token_store = Store("app://tokens/social/{username}".format(username=self.username))
                session_token_store.clear()
                session_token_store.append(token_request.json()["token"])
            except:
                pass



    def __createSession__(self):
        # Try to load a cached token
        try:
            session_token_store = Store("app://tokens/session/{username}".format(username=self.username))
            session_tokens = session_token_store.retrieve()
            self.session_token = None
            if len(session_tokens):
                for cached_token in session_tokens:
                    cached_token_expiration_time = datetime.fromtimestamp(jwt.decode(cached_token, verify=False)['exp'])

                    token_validity_time_remaining = cached_token_expiration_time - datetime.now()

                    if token_validity_time_remaining.total_seconds() <= 60 * 60 * 24:
                        self.session_token = None
                    else:
                        self.session_token = cached_token
            else:
                self.session_token = None
        except:
            self.session_token = None

        if self.session_token is None:
            self.__requestSessionToken()
        else:
            pass

    def __createAuthorization__(self):
        if self.session_token is not None:
            # Try to load a cached social token
            try:
                social_token_store = Store("app://tokens/social/{username}".format(username=self.username))
                social_tokens = social_token_store.retrieve()
                if len(social_tokens):
                    for cached_token in social_tokens:
                        cached_token_expiration_time = datetime.fromtimestamp(jwt.decode(cached_token, verify=False)['exp'])

                        token_validity_time_remaining = cached_token_expiration_time - datetime.now()

                        if token_validity_time_remaining.total_seconds() <= 60 * 60 * 24:
                            self.__requestSocialToken()
                        else:
                            self.session.headers["Authorization"] = "JWT " + cached_token
                else:
                    self.__requestSocialToken()

            except:
                self.__requestSocialToken()

    def __init__(self):

        self.auth_headers = {"CD-Language": "de-DE",
                             "Content-Type": "application/json"}
        self.session = requests.session()
        self.session_token = None

    def getSession(self):
        if self.session_token is None:
            self.__createSession__()
        if "Authorization" not in self.session.headers:
            self.__createAuthorization__()

        return self.session

    def setSessionData(self, apikey, system_id):
        self.auth_headers['apikey'] = apikey
        self.auth_headers['cd-systemid'] = system_id

    def login(self, username, password):
        self.username = username
        self.password = password
        return self.getSession()
