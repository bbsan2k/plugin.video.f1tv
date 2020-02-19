

import sys
from urllib import urlencode
from urlparse import parse_qsl
from urlparse import urlparse
import xbmcgui
import xbmcaddon
import xbmcplugin
import xbmc
from resources.lib.F1TVParser.F1TV_Minimal_API import F1TV_API
from datetime import datetime
import time
import requests
import re


# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

_api_manager = F1TV_API()
_ADDON = xbmcaddon.Addon()

def fix_string(string_to_fix):
    return u' '.join(string_to_fix).encode('utf-8').strip()

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_seasons():
    season_list = _api_manager.getSeasons()

    return season_list

def get_mainpage():
    list_item = xbmcgui.ListItem(label="List by Season")
    url = get_url(action='list_seasons')

    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label="List by Circuit")
    url = get_url(action='list_circuits')

    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    
    list_item = xbmcgui.ListItem(label="Sets")
    url = get_url(action='sets')
    
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)    

    list_item = xbmcgui.ListItem(label="Settings")
    url = get_url(action='settings')

    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def sets():
    _api_manager.login(_ADDON.getSetting("username"), _ADDON.getSetting("password"))
    
    xbmcplugin.setPluginCategory(_handle, 'Sets')
    xbmcplugin.setContent(_handle, 'videos')
    
    sets = _api_manager.getSets()
    
    # for epi in f2_eps:
        # epi_url = epi['content_url']
        # epi_data = _api_manager.getAnyURL(epi_url)
        # name = epi_data['title']
        # asset = epi_data['items'][0]
        
        # list_item = xbmcgui.ListItem(label=name)
        
        # list_item.setInfo('video', {'title': name,
                                    # 'genre': "Motorsport",
                                    # 'mediatype': 'video'})
        # url = get_url(action='playContent', content_url=asset)
        # list_item.setProperty('IsPlayable', 'true')
        # is_folder = False
        # xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    for key in sets:
        if "/api/sets" in sets[key]:
            #It's a set, lets go.
            #Add set as dir
            list_item = xbmcgui.ListItem(label=key)
            url = get_url(action='setContents', content_url=sets[key])
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
        elif "/api/episodes" in sets[key]:
            #It's an episode.
            epi_data = _api_manager.getEpisode(sets[key])
            name = epi_data['title']
            asset = epi_data['items'][0]
            list_item = xbmcgui.ListItem(label=name)
            list_item.setInfo('video', {'title': name,
                                        'genre': 'Motorsport',
                                        'mediatype': 'video'})
            url = get_url(action='playContent', content_url=asset)
            list_item.setProperty('IsPlayable', 'true')
            is_folder = False
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.endOfDirectory(_handle)

def setContents(content_url):
    _api_manager.login(_ADDON.getSetting("username"), _ADDON.getSetting("password"))
    
    set_content = _api_manager.getSetContent(content_url)
    
    xbmcplugin.setPluginCategory(_handle, set_content['title'])
    xbmcplugin.setContent(_handle, 'videos')
    
    for item in set_content['items']:
        epi_data = _api_manager.getEpisode(item['content_url'])
        name = epi_data['title']
        asset = epi_data['items'][0]
        
        list_item = xbmcgui.ListItem(label=name)
        list_item.setInfo('video', {'title': name,
                                    'genre': 'Motorsport',
                                    'mediatype': 'video'})
        url = get_url(action='playContent', content_url=asset)
        list_item.setProperty('IsPlayable', 'true')
        is_folder = False
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.endOfDirectory(_handle)
    

def list_seasons():

    _api_manager.login(_ADDON.getSetting("username"), _ADDON.getSetting("password"))

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'Season Overview')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    season_list = _api_manager.getSeasons()['objects']

    for season in season_list:
        season_url = season['self']

        list_item = xbmcgui.ListItem(label=season['name'])

        list_item.setInfo('video', {'title': season['name'],
                                    'genre': "Motorsport",
                                    'mediatype': 'video'})

        url = get_url(action='list_season_events', season=season_url, year=season['name'])

        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_circuits():
    _api_manager.login(_ADDON.getSetting("username"), _ADDON.getSetting("password"))

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'Circuits')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    circuits = _api_manager.getCircuits()['objects']

    for circuit in circuits:
        circuit_url = circuit['self']

        if len(circuit['eventoccurrence_urls']) == 0:
            continue
        list_item = xbmcgui.ListItem(label=circuit['name'])

        xbmc.log(fix_string(circuit['name']), xbmc.LOGNOTICE)
        list_item.setInfo('video', {'title': circuit['name'],
                                    'genre': "Motorsport",
                                    'mediatype': 'video'})

        url = get_url(action='list_circuit_events', circuit=circuit_url, name=fix_string(circuit['name']))

        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_season_events(season_url, year):

    _api_manager.login(_ADDON.getSetting("username"), _ADDON.getSetting("password"))

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'Season ' + str(year))
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    season = _api_manager.getSeason(season_url)

    counter = 1

    for event in season['eventoccurrence_urls']:

        if 'start_date' in event and event['start_date'] is not None:
            try:
                start_date = datetime.strptime(event['start_date'], "%Y-%m-%d")
            except TypeError:
                start_date = datetime(*(time.strptime(event['start_date'], "%Y-%m-%d")[0:6]))
            if start_date > datetime.today():
                continue

        list_item = xbmcgui.ListItem(label="{:02d} {}".format(counter, event['name']))
        thumb = ""
        for image in event['image_urls']:
            if image['type'] == "Thumbnail":
                thumb = image['url']
                break
        # Create a list item with a text label and a thumbnail image.

        list_item.setArt({'thumb': thumb,
                          'icon': thumb,
                          'fanart': thumb})

        list_item.setInfo('video', {'title': event['name'],
                                    'genre': "Motorsport",
                                    'mediatype': 'video'})

        url = get_url(action='list_sessions', event_url=event['self'].replace("/api/",""), event_name=event['name'])

        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

        counter += 1
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_circuit_events(circuit_url, circuit_name):

    _api_manager.login(_ADDON.getSetting("username"), _ADDON.getSetting("password"))

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, circuit_name)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    circuit = _api_manager.getCircuit(circuit_url)

    for event in circuit['eventoccurrence_urls']:

        if 'start_date' in event and event['start_date'] is not None:
            try:
                start_date = datetime.strptime(event['start_date'], "%Y-%m-%d")
            except TypeError:
                start_date = datetime(*(time.strptime(event['start_date'], "%Y-%m-%d")[0:6]))
            if start_date > datetime.today():
                continue

        list_item = xbmcgui.ListItem(label=event['official_name'])
        thumb = ""
        for image in event['image_urls']:
            if image['type'] == "Thumbnail":
                thumb = image['url']
                break
        # Create a list item with a text label and a thumbnail image.

        list_item.setArt({'thumb': thumb,
                          'icon': thumb,
                          'fanart': thumb})

        list_item.setInfo('video', {'title': event['official_name'],
                                    'genre': "Motorsport",
                                    'mediatype': 'video'})

        url = get_url(action='list_sessions', event_url=event['self'], event_name=fix_string(event['official_name']))

        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def list_sessions(event_url, event_name):
    _api_manager.login(_ADDON.getSetting("username"), _ADDON.getSetting("password"))


    xbmc.log("{} - {}".format(event_name, event_url), xbmc.LOGINFO)
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, event_name)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    event = _api_manager.getEvent(event_url)

    for session in event['sessionoccurrence_urls']:

        #if session['available_for_user'] is False and len(session['content_urls']) == 0:
        #    continue

        thumb = ""
        #for image in session['image_urls']:
        #    if image['type'] == "Thumbnail":
        #        thumb = image['url']
        #        break
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=session['name'])
        

        list_item.setArt({'thumb': thumb,
                          'icon': thumb,
                          'fanart': thumb})

        list_item.setInfo('video', {'title': session['name'],
                                    'genre': "Motorsport",
                                    'mediatype': 'video'})

        url = get_url(action='list_content', session_url=session['self'].replace("/api/",""), session_name=session['name'])

        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_content(session_url, session_name):
    _api_manager.login(_ADDON.getSetting("username"), _ADDON.getSetting("password"))

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, session_name)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    session = _api_manager.getSession(session_url)
    print(session)

    for channel in session['channel_urls']:
        

        thumb = ''
        try:
            if len(channel['driver_urls']) > 0:
                for image in channel['driver_urls'][0]['image_urls']:
                    if image['type'] == 'Headshot':
                        thumb = image['url']
                        break
        except:
            pass
        for image in session['image_urls']:
            if image['type'] == 'Thumbnail':
                thumb = image['url']
                break
        # Create a list item with a text label and a thumbnail image.
        channel = _api_manager.getAnyOldURL(channel)
        name = channel['name'] if 'WIF' not in channel['name'] else session['session_name']
        list_item = xbmcgui.ListItem(label=name)

        list_item.setArt({'thumb': thumb,
                          'icon': thumb,
                          'fanart': thumb})

        list_item.setInfo('video', {'title': name,
                                    'genre': "Motorsport",
                                    'mediatype': 'video'})

        url = get_url(action='playContent', content_url=channel['self'])

        list_item.setProperty('IsPlayable', 'true')

        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    for content in session['content_urls']:
        thumb = ''
        for image in content['image_urls']:
            if image['type'] == 'Thumbnail':
                thumb = image['url']
                break
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=content['title'])

        list_item.setArt({'thumb': thumb,
                          'icon': thumb,
                          'fanart': thumb})

        list_item.setInfo('video', {'title': content['title'],
                                    'genre': "Motorsport",
                                    'mediatype': 'video'})

        list_item.setProperty('IsPlayable', 'true')

        if len(content['items']) > 0:
            url = get_url(action='playContent', content_url=content['items'][0])

            is_folder = False
            # Add our item to the Kodi virtual folder listing.
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def getCorrectedM3U8(stream_url):
    r = requests.get(stream_url)
    parts = urlparse(stream_url)

    sub_path = ''
    for component in parts.path.split('/'):
        if 'm3u8' not in component:
            sub_path += component + '/'
    base_url = '{}://{}{}'.format(parts.scheme, parts.netloc, sub_path)

    path = '{}{}'.format(xbmc.translatePath('special://temp'), 'fixed_stream.m3u8')

    out_file = open(path, 'w+')
    if r.ok:
        if 'audio-aacl' in r.content:
            try:
                for line in r.content.splitlines():
                    out_line = ''
                    if line.startswith('#EXT-X-MEDIA:') and 'TYPE=CLOSED-CAPTIONS' not in line:
                        audio_group = re.findall('GROUP-ID=\"(.*?)\"', line)[0]
                        uri = re.findall('URI=\"(.*?)\"', line)[0]
                        corrected_uri= "{}{}".format(base_url, uri) if 'http' not in uri else uri
                        out_line = line.replace(uri, corrected_uri).replace(audio_group, 'AUDIO_1')
                    elif line.startswith('#EXT-X-STREAM-INF:'):
                        audio_group = re.findall('AUDIO=\"(.*?)\"', line)[0]
                        out_line = line.replace(audio_group, 'AUDIO_1')
                    elif not line.startswith('#'):
                        out_line = "{}{}".format(base_url, line) if 'http' not in uri else uri
                    else:
                        out_line = line
                    out_file.write(out_line+'\n')
            except IndexError:
                xbmc.log('Malformatted M3U8')
        else:
            path = stream_url
        xbmc.log(r.content, xbmc.LOGDEBUG)

    out_file.close()

    return path




def playContent(content_url):
    _api_manager.login(_ADDON.getSetting("username"), _ADDON.getSetting("password"))

    stream_url = _api_manager.getStream(content_url)

    xbmc.log(stream_url, level=xbmc.LOGDEBUG)

    play_item = xbmcgui.ListItem(path=getCorrectedM3U8(stream_url))
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'list_seasons':
            # List all seasons
            list_seasons()
        elif params['action'] == 'list_circuits':
            # List all seasons
            list_circuits()
        elif params['action'] == 'sets':
            sets()
        elif params['action'] == 'setContents':
            setContents(params['content_url'])
        elif params['action'] == 'list_season_events':
            # Display the list of videos in a provided category.
            list_season_events(params['season'], params['year'])
        elif params['action'] == 'list_circuit_events':
            # Display the list of videos in a provided category.
            list_circuit_events(params['circuit'], params['name'])
        elif params['action'] == 'list_sessions':
            # Play a video from a provided URL.
            list_sessions(params['event_url'], params['event_name'])
        elif params['action'] == 'list_content':
            # Play a video from a provided URL.
            list_content(params['session_url'], params['session_name'])
        elif params['action'] == 'playContent':
            playContent(params['content_url'])
        elif params['action'] == 'settings':
            _ADDON.openSettings()
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        get_mainpage()
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories


def run():

    _api_manager.setLanguage(xbmc.getLanguage(format=xbmc.ISO_639_1))

    if _ADDON.getSetting('apikey') == '' or _ADDON.getSetting('system_id') == '':
        apikey, system_id = _api_manager.account_manager.exteractSessionData()
        _ADDON.setSetting('apikey', apikey)
        _ADDON.setSetting('system_id', system_id)
    else:
        _api_manager.account_manager.setSessionData(_ADDON.getSetting('apikey'), _ADDON.getSetting('system_id'))

    try:
        _api_manager.login(_ADDON.getSetting("username"), _ADDON.getSetting("password"))
        xbmc.log(xbmc.getLanguage(format=xbmc.ISO_639_1), xbmc.LOGERROR)
    except ValueError as error:

        response = xbmcgui.Dialog().yesno('Login not possible.', error.message, 'Enter Settings?',nolabel='Exit', yeslabel='Settings')
        xbmc.log(error.message, xbmc.LOGERROR)
        if response:
            _ADDON.openSettings()

        exit(1)
    router(sys.argv[2][1:])
