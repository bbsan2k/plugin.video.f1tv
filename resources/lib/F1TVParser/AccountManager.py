import requests
import requests_cache
import json
import os
import pyjwt as jwt
import re
import xbmc
import xbmcaddon

#Cache module
try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

from datetime import datetime

# __ACCOUNT_API__='https://api.formula1.com/v1/account/'
# __ACCOUNT_CREATE_SESSION__=__ACCOUNT_API__+'Subscriber/CreateSession'
__ACCOUNT_API__='https://api.formula1.com/v2/account/'
__ACCOUNT_CREATE_SESSION__=__ACCOUNT_API__+'subscriber/authenticate/by-password'

__HEADER_CD_LANGUAGE__='en-GB'
__HEADER_CD_DIST_CHANNEL__='871435e3-2d31-4d4f-9004-96c6a8011656'

__ACCOUNT_SOCIAL_AUTHENTICATE__="https://f1tv.formula1.com/api/social-authenticate/"
__ACCOUNT_IDENTITY_PROVIDER_URL__= "/api/identity-providers/iden_732298a17f9c458890a1877880d140f3/"

class AccountManager:
    def exteractSessionData(self):
        return self.auth_headers['apikey'], self.auth_data['cd-systemid']

    def __requestSessionToken(self):
        login_dict = {
            "DeviceType": 16,
            "DistributionChannel": __HEADER_CD_DIST_CHANNEL__,
            "Language": __HEADER_CD_LANGUAGE__,
            "Login": self.username, 
            "Password": self.password
        }
        r = self.session.post(__ACCOUNT_CREATE_SESSION__, headers=self.auth_headers, json=login_dict)

        if r.ok and 'Fault' not in r.json():
            if r.json()["data"]["subscriptionStatus"] != "active":
                raise ValueError('Subscription is not active.')

            self.session_token = r.json()["data"]["subscriptionToken"]
            xbmc.log(self.session_token, xbmc.LOGINFO)

            # Save the token
            try:
                self.cache.set(f"app://tokens/session/{self.username}", self.session_token)
            except:
                pass
        else:
            raise ValueError('Account Authentication failed.')

    def __requestSocialToken(self):
        dict = {"identity_provider_url": __ACCOUNT_IDENTITY_PROVIDER_URL__, "access_token": self.session_token}

        token_request = self.session.post(__ACCOUNT_SOCIAL_AUTHENTICATE__, data=json.dumps(dict))
        if token_request.ok:
            #self.session.headers["Authorization"] = "JWT " + token_request.json()["token"]

            # Save the token
            try:
                self.cache.set(f"app://tokens/social/{self.username}", token_request.json()["token"])
            except:
                pass



    def __createSession__(self):
        # Try to load a cached token
        try:
            cached_token = self.cache.get(f"app://tokens/session/{self.username}")
            self.session_token = None
            if cached_token is not None:
                cached_token_expiration_time = datetime.fromtimestamp(jwt.decode(cached_token, verify=False)['exp'])

                token_validity_time_remaining = cached_token_expiration_time - datetime.now()

                if token_validity_time_remaining.total_seconds() <= 60 * 60 * 24:
                    self.session_token = None
                else:
                    self.session_token = cached_token
        except Exception as e:
            print("Error loading session from cache")
            print(e)
            self.session_token = None

        if self.session_token is None:
            self.__requestSessionToken()
        else:
            pass
        self.session.headers['ascendontoken'] = self.session_token

    def __createAuthorization__(self):
        if self.session_token is not None:
            # Try to load a cached social token
            try:
                cached_token = self.cache.get(f"app://tokens/social/{self.username}")
                if cached_token is not None:
                    cached_token_expiration_time = datetime.fromtimestamp(jwt.decode(cached_token, verify=False)['exp'])

                    token_validity_time_remaining = cached_token_expiration_time - datetime.now()

                    if token_validity_time_remaining.total_seconds() <= 60 * 60 * 24:
                        self.__requestSocialToken()
                    else:
                        #self.session.headers["Authorization"] = "JWT " + cached_token
                        pass
                else:
                    self.__requestSocialToken()

            except:
                self.__requestSocialToken()

    def __init__(self):
        self.cache = StorageServer.StorageServer("plugin.video.f1tv", 175316)
        self.auth_data = {"cd-systemid": "0"}
        self.session = requests.session()
        #Scrape down the API Key
        f1_account_script_data = self.session.get("https://account.formula1.com/scripts/main.min.js")
        #Extract the apiKey with regex
        api_key = re.findall('apikey: *"(.*?)"', f1_account_script_data.text)[0]
        self.auth_headers = {"Content-Type": "application/json",
                             "apikey": api_key,
                             "CD-DeviceType": '16',
                             "CD-DistributionChannel": __HEADER_CD_DIST_CHANNEL__,
                             'User-Agent': 'RaceControl'}
        #3 second cache for all requests
        requests_cache.install_cache(expire_after=3)
        self.session_token = None

    def getSession(self):
        if self.session_token is None:
            self.__createSession__()
        #if "Authorization" not in self.session.headers:
        #    self.__createAuthorization__()

        return self.session

    def setSessionData(self, apikey, system_id):
        #self.auth_headers['apikey'] = apikey
        #self.auth_data['cd-systemid'] = system_id
        pass

    def login(self, username, password):
        self.username = username
        self.password = password
        return self.getSession()
