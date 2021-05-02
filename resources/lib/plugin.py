

import sys
from urllib.parse import urlencode, parse_qsl, urlparse
import xbmcgui
import xbmcaddon
import xbmcplugin
import xbmc
from datetime import datetime
import time
import requests
import re
from .pyf1tv import PYF1TV

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

_ADDON = xbmcaddon.Addon()
_api = None 

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


def renderPage(items):
    for item in items:
        
        list_item = xbmcgui.ListItem(label=item["name"])

        if "id" in item:
            url = get_url(uri=item["uri"], id=item["id"], target=item["target"], name=item["name"])
        else:
            url = get_url(uri=item["uri"], target=item["target"], name=item["name"])

        folder = True
        if item["target"] == "PLAY":
            folder = False
            list_item.setProperty("IsPlayable", "true")
            list_item.setProperty("MIMEType", "video/MP2T")

        if "image" in item:
            list_item.setArt({"thumb": item["image"]})

        xbmcplugin.addDirectoryItem(_handle, url, list_item, folder)

    
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def play_video(path):
    """
    Play a video by the provided path.
    :param path: str
    :return: None
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
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
        if params['target'] == 'settings':
            _ADDON.openSettings()
        else:
            item = _api.get(params)
            if item:
                log(paramstring)
                if params["target"] == "PLAY":                    
                    play_video(item)
                else:
                    renderPage(item)
            else:
                # If the provided paramstring does not contain a supported action
                # we raise an exception. This helps to catch coding errors,
                # e.g. typos in action names.
                raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        renderMainPage()
        # get_mainpage()
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories

def renderMainPage():

    live = _api.getLive()

    if live:
        list_item = xbmcgui.ListItem(label=live["name"])

        url = get_url(uri=live["uri"], target=live["target"], name=live["name"])
        
        folder = False
        list_item.setProperty("IsPlayable", "true")
        list_item.setProperty("MIMEType", "video/MP2T")

        if "image" in live:
            list_item.setArt({"thumb": live["image"]})

        xbmcplugin.addDirectoryItem(_handle, url, list_item, folder)

    items = _api.getMainpage()
    for item in items:
        
        list_item = xbmcgui.ListItem(label=item["name"])

        if "id" in item:
            url = get_url(uri=item["uri"], id=item["id"], target=item["target"], name=item["name"])
        else:
            url = get_url(uri=item["uri"], target=item["target"], name=item["name"])

        folder = True
        if item["target"] == "PLAY":
            folder = False
            list_item.setProperty("IsPlayable", "true")
            list_item.setProperty("MIMEType", "video/MP2T")

        if "image" in item:
            list_item.setArt({"thumb": item["image"]})

        if "description" in item:
            list_item.setInfo("video", {"plot": item["description"]})

        xbmcplugin.addDirectoryItem(_handle, url, list_item, folder)

    
    list_item = xbmcgui.ListItem(label="Settings")
    xbmcplugin.addDirectoryItem(_handle, get_url(target="settings"), list_item, False)


    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def cacheGetter():
    return None

def cacheSetter(item):
    print(item)

def log(text):
    xbmc.log(text, xbmc.LOGINFO)

def run():
    try:
        global _api
        _api = PYF1TV(username=_ADDON.getSetting("username"), password=_ADDON.getSetting("password"), cacheGetter=cacheGetter, cacheSetter=cacheSetter, log=log)

        xbmc.log(xbmc.getLanguage(format=xbmc.ISO_639_1), xbmc.LOGERROR)
    
    except ValueError as error:

        response = xbmcgui.Dialog().yesno('Login not possible.', error.message, 'Enter Settings?',nolabel='Exit', yeslabel='Settings')
        xbmc.log(error.message, xbmc.LOGERROR)
        if response:
            _ADDON.openSettings()

        exit(1)
    router(sys.argv[2][1:])
