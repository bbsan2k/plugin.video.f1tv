import requests
import json
import re

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

        return self.auth_headers['apikey'], self.auth_headers['cd-systemid']

    def __createSession__(self):
        login_dict = {"Login": self.username, "Password": self.password}
        r = self.session.post(__ACCOUNT_CREATE_SESSION__, headers=self.auth_headers, data=json.dumps(login_dict))

        if r.ok and 'Fault' not in r.json():
            if r.json()["data"]["subscriptionStatus"] != "active":
                raise ValueError('Subscription is not active.')

            self.session_token = r.json()["data"]["subscriptionToken"]

        else:
            raise ValueError('Account Authentification failed.')

    def __createAuthorization__(self):
        if self.session_token is not None:
            dict = {"identity_provider_url": __ACCOUNT_IDENTITY_PROVIDER_URL__, "access_token": self.session_token}

            token_request = self.session.post(__ACCOUNT_SOCIAL_AUTHENTICATE__, data=json.dumps(dict))
            if token_request.ok:
                self.session.headers["Authorization"] = "JWT " + token_request.json()["token"]

    def __init__(self, username = None, password = None, token = None):
        self.username = username
        self.password = password
        self.session_token = token
        self.auth_headers = {"CD-Language": "en-GB",
                             "Content-Type": "application/json"}
        self.session = requests.session()

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
        return self.__createSession__()