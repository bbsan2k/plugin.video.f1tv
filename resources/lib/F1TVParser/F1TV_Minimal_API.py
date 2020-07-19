import AccountManager
import json
import xbmc
import os
import urllib

from cache import Cache, conditional_headers


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

    def callAPI(self, endpoint, method="GET", api_ver=2, params=None, data=None):
        if int(api_ver) == 1:
            complete_url = 'https://f1tv.formula1.com' + endpoint
        elif int(api_ver) == 2:
            complete_url = 'https://f1tv-api.formula1.com/agl/1.0/gbr/en/all_devices/global/' + endpoint
        else:
            xbmc.log("Unable to make an API with invalid API version: {}".format(api_ver), xbmc.LOGERROR)
            return

        if method.upper() == 'GET':
            # Check to see if we've cached the response
            with Cache() as c:
                if params:
                    url_with_parameters = "{complete_url}?{parameters}".format(complete_url=complete_url,
                                                                               parameters=urllib.urlencode(params))
                else:
                    url_with_parameters = complete_url
                cached = c.get(url_with_parameters)
                if cached:
                    # If we have a fresh cached version, return it.
                    if cached["fresh"]:
                        return json.loads(cached["blob"])
                    # otherwise append applicable "If-None-Match"/"If-Modified-Since" headers
                    self.account_manager.getSession().headers.update(conditional_headers(cached))
                # request a new version of the data
                r = self.account_manager.getSession().get(complete_url, params=params, data=data)
                if 200 == r.status_code:
                    # add the new data and headers to the cache
                    c.set(url_with_parameters, r.content, r.headers)
                    return r.json()
                if 304 == r.status_code:
                    # the data hasn't been modified so just touch the cache with the new headers
                    # and return the existing data
                    c.touch(url_with_parameters, r.headers)
                    return json.loads(cached["blob"])


        elif method.upper() == 'POST':
            r = self.account_manager.getSession().post(complete_url, params=params, data=data)
            if r.ok:
                return r.json()
            else:
                return
        else:
            return

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
        item_dict = {"asset_url" if 'ass' in url else "channel_url": url}

        viewing_json = self.callAPI("/api/viewings/", api_ver=1, method='POST', data=json.dumps(item_dict))

        if 'chan' in url:
            return viewing_json["tokenised_url"]
        else:
            return viewing_json["objects"][0]["tata"]["tokenised_url"]

    def getSession(self, url):
        """ Get Session Object from API by supplying an url"""
        session = self.callAPI(url, params=__TV_API_PARAMS__["session-occurrence"])
        return session


    def getEvent(self, url, season = None):
        """ Get Event object from API by supplying an url"""
        event = self.callAPI(url, params=__TV_API_PARAMS__["event-occurrence"])
        return event


    def getSeason(self, url):
        """ Get Season object from API by supplying an url"""
        season = self.callAPI(url, api_ver=1, params=self.getFields(url))
        return season

    def getSeasons(self):
        """ Get all season urls that are available at API"""
        seasons = self.callAPI("/api/race-season/", api_ver=1, params={'order': '-year'})
        return seasons

    def getCircuits(self):
        """ Get all Circuit urls that are available at API"""
        circuits = self.callAPI("/api/circuit/", api_ver=1, params={"fields": "name,eventoccurrence_urls,self"})
        return circuits

    def getCircuit(self, url):
        """ Get Circuit object from API by supplying an url"""
        circuit = self.callAPI(url, api_ver=1, params=__TV_API_PARAMS__["circuit"])
        return circuit
    
    def getF2(self):
        f2 = self.callAPI("/api/sets/coll_4440e712d31d42fb95c9a2145ab4dac7")
        return f2
    
    def getSets(self):
        sets = self.callAPI("/api/sets/?slug=home", api_ver=1)
        content = {}
        for item in sets['objects'][0]['items']:
            item_details = self.callAPI(item['content_url'], api_ver=1)
            if 'title' in list(item_details):
                content[item_details['title']] = item['content_url']
            elif 'name' in list(item_details):
                content[item_details['name']] = item['content_url']
            else:
                content[item_details['UNKNOWN SET: ' + 'uid']] = item['content_url']
        return content

    def setLanguage(self, language):
        self.account_manager.session.headers['Accept-Language'] = "{}, en".format(language.upper())
