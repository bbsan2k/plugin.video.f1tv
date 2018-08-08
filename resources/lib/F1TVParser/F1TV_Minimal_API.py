import AccountManager
import json


''' General Entry point for F1TV API'''
__TV_API__='https://f1tv.formula1.com'

''' Parameters for different F1TV API calls'''
__TV_API_PARAMS__ = {"event-occurrence": {"fields_to_expand": "image_urls,sessionoccurrence_urls,sessionoccurrence_urls__image_urls",
                               "fields": "name,self,image_urls,sessionoccurrence_urls,official_name,start_date,end_date,"
                                         "sessionoccurrence_urls__name,sessionoccurrence_urls__self,"
                                         "sessionoccurrence_urls__image_urls,sessionoccurrence_urls__start_time"},
                     "season": {"fields": "year,name,self,eventoccurrence_urls,eventoccurrence_urls__name,eventoccurrence_urls__start_date,"
                                          "eventoccurrence_urls__self,eventoccurrence_urls__image_urls,image_urls",
                                "fields_to_expand": "eventoccurrence_urls,eventoccurrence_urls__image_urls,image_urls"},
                     "session-occurrence": {"fields": "name,self,image_urls,status,channel_urls,start_time,content_urls,session_name",
                                 "fields_to_expand": "channel_urls,image_urls,content_urls,channel_urls__image_urls,content_urls__image_urls,channel_urls__driver_urls,channel_urls__driver_urls__image_urls"},
                     "channel": "",
                     "race_season": {"order": "-year"}}



class F1TV_API:
    """ Main API Object - is used to retrieve API information """

    def __init__(self):
        """ Initialize by creating AccountManager object"""
        self.account_manager = AccountManager.AccountManager()

    def login(self, username, password):
        """ Log in with supplied credentials."""
        return self.account_manager.login(username, password)

    def getStream(self, url):
        """ Get stream for supplied viewings item
            This will get the m3u8 url for Content and Channel."""
        complete_url = __TV_API__ + "/api/viewings/"
        item_dict = {"asset_url" if 'ass' in url else "channel_url": url}

        viewing = self.account_manager.getSession().post(complete_url, data=json.dumps(item_dict))

        if viewing.ok:
            viewing_json = viewing.json()
            if 'chan' in url:
                return viewing.json()["tokenised_url"]
            else:
                return viewing.json()["objects"][0]["tata"]["tokenised_url"]

    def getSession(self, url):
        """ Get Session Object from API by supplying an url"""
        complete_url = __TV_API__ + url
        r = self.account_manager.getSession().get(complete_url, params=__TV_API_PARAMS__["session-occurrence"])

        if r.ok:
            return r.json()

    def getEvent(self, url, season = None):
        """ Get Event object from API by supplying an url"""
        complete_url = __TV_API__ + url
        r = self.account_manager.getSession().get(complete_url, params=__TV_API_PARAMS__["event-occurrence"])

        event = None

        if r.ok:
            return r.json()


    def getSeason(self, url):
        """ Get Season object from API by supplying an url"""
        complete_url = __TV_API__ + url
        r = self.account_manager.getSession().get(complete_url, params=__TV_API_PARAMS__["season"])
        season = None

        if r.ok:
            return r.json()

    def getSeasons(self):
        """ Get all season urls that are available at API"""
        complete_url = __TV_API__ + "/api/race-season/"
        r = self.account_manager.getSession().get(complete_url, params=__TV_API_PARAMS__["race_season"])

        seasons = {}
        if r.ok:
            for season in r.json()["objects"]:
                seasons[season["year"]] = season["self"]

        return seasons

    def setLanguage(self, language):
        self.account_manager.session.headers['Accept-Language'] = "{}, en".format(language.upper())
