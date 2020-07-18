import AccountManager
import json


''' General Entry point for F1TV API'''
__TV_API__='https://f1tv-api.formula1.com/agl/1.0/gbr/en/all_devices/global/'
__OLD_TV_API__='https://f1tv.formula1.com'

''' Parameters for different F1TV API calls'''
__TV_API_PARAMS__ = {"event-occurrence": {"fields_to_expand": "image_urls,sessionoccurrence_urls,sessionoccurrence_urls__image_urls",
                               "fields": "name,self,image_urls,sessionoccurrence_urls,official_name,start_date,end_date,"
                                         "sessionoccurrence_urls__session_name,sessionoccurrence_urls__self,"
                                         "sessionoccurrence_urls__image_urls,sessionoccurrence_urls__start_time,sessionoccurrence_urls__available_for_user,sessionoccurrence_urls__content_urls"},
                     "race-season": {"fields": "year,name,self,eventoccurrence_urls,eventoccurrence_urls__name,eventoccurrence_urls__start_date,"
                                          "eventoccurrence_urls__self,eventoccurrence_urls__image_urls,image_urls",
                                "fields_to_expand": "eventoccurrence_urls,eventoccurrence_urls__image_urls,image_urls"},
                     "session-occurrence": {"fields": "name,self,image_urls,status,channel_urls,start_time,content_urls,session_name",
                                 "fields_to_expand": "channel_urls,image_urls,content_urls,channel_urls__image_urls,content_urls__image_urls,channel_urls__driver_urls,channel_urls__driver_urls__image_urls"},
                     "circuit": {"fields": "name,self,eventoccurrence_urls,eventoccurrence_urls__name,eventoccurrence_urls__start_date,"
                                          "eventoccurrence_urls__self,eventoccurrence_urls__image_urls,eventoccurrence_urls__official_name",
                                "fields_to_expand": "eventoccurrence_urls,eventoccurrence_urls__image_urls"}
                     }



class F1TV_API:
    """ Main API Object - is used to retrieve API information """

    def getFields(self, url):
        for key in __TV_API_PARAMS__:
            if key in url:
                return __TV_API_PARAMS__[key]

    def __init__(self):
        """ Initialize by creating AccountManager object"""
        self.account_manager = AccountManager.AccountManager()

    def login(self, username, password):
        """ Log in with supplied credentials."""
        return self.account_manager.login(username, password)

    def getStream(self, url):
        """ Get stream for supplied viewings item
            This will get the m3u8 url for Content and Channel."""
        complete_url = __OLD_TV_API__ + "/api/viewings/"
        item_dict = {"asset_url" if 'ass' in url else "channel_url": url}

        viewing = self.account_manager.getSession().post(complete_url, data=json.dumps(item_dict))

        if viewing.ok:
            viewing_json = viewing.json()
            if 'chan' in url:
                return viewing_json["tokenised_url"]
            else:
                return viewing_json["objects"][0]["tata"]["tokenised_url"]

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

        if r.ok:
            return r.json()


    def getSeason(self, url):
        """ Get Season object from API by supplying an url"""
        complete_url = __OLD_TV_API__ + url
        r = self.account_manager.getSession().get(complete_url, params=self.getFields(url)) #__TV_API_PARAMS__["season"])

        if r.ok:
            return r.json()

    def getSeasons(self):
        """ Get all season urls that are available at API"""
        complete_url = __OLD_TV_API__ + "/api/race-season/"
        r = self.account_manager.getSession().get(complete_url, params={'order': '-year'})

        if r.ok:
            return r.json()

    def getCircuits(self):
        """ Get all Circuit urls that are available at API"""
        complete_url = __OLD_TV_API__ + "/api/circuit/"
        r = self.account_manager.getSession().get(complete_url, params={"fields": "name,eventoccurrence_urls,self"})

        if r.ok:
            return r.json()

    def getCircuit(self, url):
        """ Get Circuit object from API by supplying an url"""
        complete_url = __OLD_TV_API__ + url
        r = self.account_manager.getSession().get(complete_url, params=__TV_API_PARAMS__["circuit"])

        if r.ok:
            return r.json()
    
    def getF2(self):
        complete_url = __TV_API__+"/api/sets/coll_4440e712d31d42fb95c9a2145ab4dac7"
        r = self.account_manager.getSession().get(complete_url)
        if r.ok:
            return r.json()
    
    def getAnyURL(self, url):
        complete_url = __TV_API__+url
        r = self.account_manager.getSession().get(complete_url)
        if r.ok:
            return r.json()
            
    def getAnyOldURL(self, url):
        complete_url = __OLD_TV_API__+url
        r = self.account_manager.getSession().get(complete_url)
        if r.ok:
            return r.json()
    
    def getSets(self):
        complete_url = __OLD_TV_API__ + "/api/sets/?slug=home"
        r = self.account_manager.getSession().get(complete_url)
        if r.ok:
            rj = r.json()
        content = {}
        for item in rj['objects'][0]['items']:
            itemj = self.account_manager.getSession().get(__OLD_TV_API__+item['content_url']).json()
            if 'title' in list(itemj):
                content[itemj['title']] = item['content_url']
            elif 'name' in list(itemj):
                content[itemj['name']] = item['content_url']
            else:
                content[itemj['UNKNOWN SET: ' + 'uid']] = item['content_url']
        return content
    
    def getSetContent(self, url):
        complete_url = __OLD_TV_API__ + url
        r = self.account_manager.getSession().get(complete_url)
        if r.ok:
            return r.json()
    
    def getEpisode(self, url):
        complete_url = __OLD_TV_API__ + url
        r = self.account_manager.getSession().get(complete_url)
        if r.ok:
            return r.json()
        

    def setLanguage(self, language):
        self.account_manager.session.headers['Accept-Language'] = "{}, en".format(language.upper())
