from . import AccountManager
import json
import xbmc
import os
import urllib
import time
from datetime import datetime
import locale

#Cache module
try:
    import StorageServer
except:
    import storageserverdummy as StorageServer



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

__TV_API_ENDPOINTS__ = {
    "home":"home",
    "seasons":"archive-filters/{year}",
    "season":"archive",
    "event":"video-collection/{event_uid}/sessions",
    "event_metadata":"event-occurrence/{event_uid}/",
    "session":"session-occurrence/{session_uid}/archive",
    "channel":"channels/{channel_uid}",
    "episode":"episodes/{episode_uid}",
    "episode_playback":"episodes/{episode_slug}/playback",
    "video-set":"video-set/{set_uid}",
    "viewings":"/api/viewings"
}


class F1TV_API:
    """ Main API Object - is used to retrieve API information """

    def getMainPage(self):
        mainpage_data = self.account_manager.getSession().get(f"{self.f1tvapi}ALL/MENU/F1_TV_Pro_Annual/14")
        if mainpage_data.ok:
            return mainpage_data.json()
    
    def getPage(self, page_id):
        page_data = self.account_manager.getSession().get(f"{self.f1tvapi}ALL/PAGE/{page_id}/F1_TV_Pro_Annual/14")
        if page_data.ok:
            return page_data.json()
    
    def getLiveEvent(self):
        frontpage_url = f"{self.f1tvapi}ALL/PAGE/395/F1_TV_Pro_Monthly/14"
        frontpage_data = self.account_manager.getSession().get(frontpage_url).json()
        for item in frontpage_data["resultObj"]["containers"]:
            for sub_item in item["retrieveItems"]["resultObj"]["containers"]:
                if sub_item["metadata"]["contentSubtype"] == "LIVE":
                    # This is (one of?) the currently live event(s)!
                    return sub_item
                    # menu_items.insert(
                    #     1,
                    #     f"{sub_item['id']} - LIVE EVENT - {sub_item['metadata']['title']}",
                    # )
    
    def getM3U8(self, content_id, channel_id=None):
        url = "https://f1tv.formula1.com/1.0/R/ENG/BIG_SCREEN_HLS/ALL/CONTENT/PLAY"
        params = {
            "contentId": content_id
        }
        if channel_id:
            params["channelId"] = channel_id
        stream_data = self.account_manager.getSession().get(url, params=params).json()
        xbmc.log(str(stream_data), xbmc.LOGINFO)
        return stream_data['resultObj']['url']

    def callAPI(self, endpoint, method="GET", api_ver=2, params=None, data=None):
     #   locale.setlocale(locale.LC_ALL, 'en_US')
        if int(api_ver) == 1:
            complete_url = 'https://f1tv.formula1.com' + endpoint
        elif int(api_ver) == 2:
            #complete_url = 'https://f1tv-api.formula1.com/agl/1.0/deu/en/all_devices/global/' + endpoint
            complete_url = 'https://f1tv-api.formula1.com/agl/1.0/gbr/en/all_devices/global/' + endpoint
        else:
            xbmc.log("Unable to make an API with invalid API version: {}".format(api_ver), xbmc.LOGERROR)
            return

        if method.upper() == 'GET':
            
            if params:
                url_with_parameters = "{complete_url}?{parameters}".format(complete_url=complete_url,
                                                                           parameters=urllib.urlencode(params))
            else:
                url_with_parameters = complete_url
            # request a new version of the data (automatically cached by AccountManager module)
            r = self.account_manager.getSession().get(complete_url, params=params, data=data)
            if 200 == r.status_code:
                # add the new data and headers to the cache
                return r.json()
            if 304 == r.status_code:
                return None


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
        self.cache = StorageServer.StorageServer("plugin.video.f1tv", 175316)
        self.account_manager = AccountManager.AccountManager()
        self.f1tvapi = "https://f1tv.formula1.com/2.0/R/ENG/BIG_SCREEN_HLS/"

    def login(self, username, password):
        """ Log in with supplied credentials."""
        return self.account_manager.login(username, password)

    def getEpisodeStream(self,asset_url):
        """ Get M3U8 URL for Episode """
        post_data = {
            "asset_url":asset_url
        }
        viewing_json = self.callAPI(__TV_API_ENDPOINTS__['viewings'], api_ver=1, method='POST', data=json.dumps(post_data))
        return viewing_json["objects"][0]["tata"]["tokenised_url"]

    def getChannelStream(self,channel_url):
        post_data = {
            "channel_url":channel_url
        }
        viewing_json = self.callAPI(__TV_API_ENDPOINTS__['viewings'], api_ver=1, method='POST', data=json.dumps(post_data))
        return viewing_json["tokenised_url"]

    def getSessionMetadata(self,session_uid):
        """ Get Session Object from API by supplying uid """
        session = self.callAPI(__TV_API_ENDPOINTS__['session'].format(session_uid=session_uid))
        return session

    def getEvent(self, event_uid):
        """ Get Event object from API by supplying event_uid"""
        event = self.callAPI(__TV_API_ENDPOINTS__['event'].format(event_uid=event_uid))
        return event

    # def getLiveEvent(self):
    #     """ Returns event_uid from API"""
    #     elements = self.callAPI("home")['objects'][0]['items']
    #     for element in elements:
    #         if 'set_type_slug' in element['content_url']:
    #             if element['content_url']['set_type_slug'] == 'grand-prix-header':
    #                 return element['content_url']['items'][0]['content_url']['uid']
    #     return None

    def getSetMetadata(self,set_uid):
        """ Return Video-Set Object from API by supplying set_uid """
        return self.callAPI(__TV_API_ENDPOINTS__['video-set'].format(set_uid=set_uid))

    def getSeason(self, year_uid):
        """ Get Season object from API by supplying an url"""
        params={
            "race_season_url":year_uid
        }
        season = self.callAPI(__TV_API_ENDPOINTS__['season'], params=params)
        return season['objects']

    def getChannelMetadata(self,channel_uid):
        """ Get Channel object from API by supplying uid"""
        channel = self.callAPI(__TV_API_ENDPOINTS__['channel'].format(channel_uid=channel_uid))
        return channel

    def getEpisodeMetadata(self,episode_uid):
        """ Get Content object from API by supplying uid"""
        episode = self.callAPI(__TV_API_ENDPOINTS__['episode'].format(episode_uid=episode_uid))
        return episode

    def getEpisodePlaybackData(self,slug):
        """ Get extended content object from API by supplying uid"""
        episode_playback = self.callAPI(__TV_API_ENDPOINTS__['episode_playback'].format(episode_slug=slug))
        return episode_playback['objects'][0]

    def getEventMetadata(self,event_uid):
        """ Get Event object from API by supplying event_uid"""
        event = self.callAPI(__TV_API_ENDPOINTS__['event_metadata'].format(event_uid=event_uid))
        return event

    def getSeasons(self):
        """ Get all season urls that are available at API"""
        #test with macOS
        now = datetime.now()
        current_year = now.year
        seasons = self.callAPI(__TV_API_ENDPOINTS__['seasons'].format(year=current_year+1))
        return seasons['objects']

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
        return self.callAPI(__TV_API_ENDPOINTS__['home'])['objects'][0]['items']

    def setLanguage(self, language):
        self.account_manager.session.headers['Accept-Language'] = "{}, en".format(language.upper())
