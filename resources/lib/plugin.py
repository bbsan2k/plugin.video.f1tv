

import sys
from urllib import urlencode
from urlparse import parse_qsl
import xbmcgui
import xbmcaddon
import xbmcplugin
import xbmc
from resources.lib.F1TVParser.F1TV_Minimal_API import F1TV_API
from datetime import datetime
import time


# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

_api_manager = F1TV_API()
_ADDON = xbmcaddon.Addon()

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


def list_seasons():

    _api_manager.login(_ADDON.getSetting("username"), _ADDON.getSetting("password"))

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'Season Overview')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    season_list = _api_manager.getSeasons()

    for year in reversed(season_list.keys()):
        season_url = season_list[year]
        xbmc.log(str(year), level=xbmc.LOGWARNING)

        list_item = xbmcgui.ListItem(label=str(year))
        # list_item.setArt({'thumb': VIDEOS[category][0]['thumb'],
        #                   'icon': VIDEOS[category][0]['thumb'],
        #                   'fanart': VIDEOS[category][0]['thumb']})

        list_item.setInfo('video', {'title': str(year),
                                    'genre': "Motorsport",
                                    'mediatype': 'video'})

        url = get_url(action='list_events', season=season_url, year=year)

        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_events(season_url, year):
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
        xbmc.log(event['start_date'], xbmc.LOGWARNING)

        try:
            start_date = datetime.strptime(event['start_date'], "%Y-%m-%d")
        except TypeError:
            start_date = datetime(*(time.strptime(event['start_date'], "%Y-%m-%d")[0:6]))

        if start_date > datetime.today():
            continue

        # Create a list item with a text label and a thumbnail image.
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

        url = get_url(action='list_sessions', event_url=event['self'], event_name=event['name'])

        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

        counter += 1
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_sessions(event_url, event_name):
    _api_manager.login(_ADDON.getSetting("username"), _ADDON.getSetting("password"))

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, event_name)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    event = _api_manager.getEvent(event_url)

    for session in event['sessionoccurrence_urls']:
        list_item = xbmcgui.ListItem(label=session['name'])

        thumb = ""
        for image in session['image_urls']:
            if image['type'] == "Thumbnail":
                thumb = image['url']
                break
        # Create a list item with a text label and a thumbnail image.

        list_item.setArt({'thumb': thumb,
                          'icon': thumb,
                          'fanart': thumb})

        list_item.setInfo('video', {'title': session['name'],
                                    'genre': "Motorsport",
                                    'mediatype': 'video'})

        url = get_url(action='list_content', session_url=session['self'], session_name=session['name'])

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

    for channel in session['channel_urls']:

        thumb = ''
        if len(channel['driver_urls']) > 0:
            for image in channel['driver_urls'][0]['image_urls']:
                if image['type'] == 'Headshot':
                    thumb = image['url']
                    break
        else:
            for image in session['image_urls']:
                if image['type'] == 'Thumbnail':
                    thumb = image['url']
                    break
        # Create a list item with a text label and a thumbnail image.
        name = channel['name'] if 'WIF' not in channel['name'] else session['session_name']
        list_item = xbmcgui.ListItem(label=name)

        list_item.setArt({'thumb': thumb,
                          'icon': thumb,
                          'fanart': thumb})

        list_item.setInfo('video', {'title': name,
                                    'genre': "Motorsport",
                                    'mediatype': 'video'})

        url = get_url(action='playContent', content_url=channel['self'])

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
        if len(content['items']) > 0:
            url = get_url(action='playContent', content_url=content['items'][0])

            is_folder = False
            # Add our item to the Kodi virtual folder listing.
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def playContent(content_url):
    _api_manager.login(_ADDON.getSetting("username"), _ADDON.getSetting("password"))

    xbmc.log(content_url, level=xbmc.LOGWARNING)

    stream_url = _api_manager.getStream(content_url)

    xbmc.log(stream_url, level=xbmc.LOGWARNING)

    xbmc.Player().play(stream_url)


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
        if params['action'] == 'list_events':
            # Display the list of videos in a provided category.
            list_events(params['season'], params['year'])
        elif params['action'] == 'list_sessions':
            # Play a video from a provided URL.
            list_sessions(params['event_url'], params['event_name'])
        elif params['action'] == 'list_content':
            # Play a video from a provided URL.
            list_content(params['session_url'], params['session_name'])
        elif params['action'] == 'playContent':
            playContent(params['content_url'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_seasons()


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
