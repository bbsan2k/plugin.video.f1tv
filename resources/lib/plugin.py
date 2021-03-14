import sys
from urllib.parse import urlencode, parse_qsl, urlparse
import xbmcgui
import xbmcaddon
import xbmcplugin
import xbmc
import xbmcvfs
from resources.lib.F1TVParser.F1TV_Minimal_API import F1TV_API
from datetime import datetime
import time
import requests
import requests_cache
import re
import ast


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

def get_mainpage():

    # mainpage_data = _api_manager.getMainPage()
    # #Check that there are results
    # if "resultObj" in mainpage_data:
    #     #Iterate over front page entries and add them to the menu
    #     for container in mainpage_data['resultObj']['containers']:
    #         label = container['metadata']['label']
    #         target_type = container['actions'][0]['targetType']
    #         uri = container['actions'][0]['uri']
    #         #Create Kodi folder entry
    #         list_item = xbmcgui.ListItem(label=label)
    #         url = get_url(action=target_type, uri=uri, label=label)
    #         xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    #Check for a live event
    live_event = _api_manager.getLiveEvent()
    #There is a live event, add it to the menu
    if live_event:
        list_item = xbmcgui.ListItem(label=f"Live Now - {live_event['metadata']['title']}")
        url = get_url(action="playVideo", content_id=live_event['id'])
        list_item.setProperty('IsPlayable', 'true')
        list_item.setInfo("video", {"title": f"Live Now - {live_event['metadata']['title']}"})
        #Build image url
        image_url = f"https://ott.formula1.com/image-resizer/image/{live_event['metadata']['pictureUrl']}?w=1280&h=720"
        list_item.setArt({'thumb': image_url,
                    'icon': image_url,
                    'fanart': image_url})
        xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    
    #Add Archive To Menu
    list_item = xbmcgui.ListItem(label="Archive")
    url = get_url(action="archive")
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    #Add Shows To Menu
    list_item = xbmcgui.ListItem(label="Shows")
    url = get_url(action="shows")
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    #Add Documentaries to Menu
    list_item = xbmcgui.ListItem(label="Documentaries")
    url = get_url(action="Documentaries")
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def archive():
    archive_page_data = _api_manager.getPage(493)
    for container in archive_page_data["resultObj"]["containers"]:
        #We don't want to grab the hero as it effectively just shows "featured" content
        if container["layout"] != "hero" and len(container["retrieveItems"]["resultObj"]) > 0:
            if container['metadata']['label']:
                list_item = xbmcgui.ListItem(label=container["metadata"]["label"])
            else:
                #If there is no label we need to generate one....
                label = ""
                for sub_item in container['retrieveItems']['resultObj']['containers']:
                    label += f"{sub_item['metadata']['title']}, "
                #Remove the last two characters (trailing comma)
                label = label[:-2]
                list_item = xbmcgui.ListItem(label=label)
            url = get_url(action="archive_block", collection_id=container['retrieveItems']['uriOriginal'].split("/TRAY/EXTCOLLECTION/")[1])
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def archive_block(collection_id):
    archive_years = _api_manager.getPage(f"EXTCOLLECTION/{collection_id}")
    # Build menu for archive block's years
    for year in archive_years["resultObj"]["containers"]:
        try:
            label = str(year['metadata']['season'])
        except KeyError:
            label = str(year['metadata']['title'])
        list_item = xbmcgui.ListItem(label=label)
        try:
            url = get_url(action="archive_year", page_id=year['actions'][0]['uri'].split("ALL/PAGE/")[1].split("/")[0])
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
        except (KeyError, IndexError):
            # If we've hit this it's probably just directly a link to a season review
            url = get_url(action="playVideo", content_id=year['id'])
            list_item.setProperty('IsPlayable', 'true')
            list_item.setInfo("video", {"title": label})
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def archive_year(page_id):
    """Individual years from archive, used by archive_year_block"""
    archive_year_data = _api_manager.getPage(page_id)
    # Build menu for year's different categories
    for container in archive_year_data["resultObj"]["containers"]:
        if len(container["retrieveItems"]["resultObj"]) > 0:
            label = str(container['metadata']['label'])
            list_item = xbmcgui.ListItem(label=label)
            url = get_url(action="archive_category", data=container['retrieveItems']['resultObj']['containers'])
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def archive_category(data):
    #For some reason passing the data through it gets turned into a string, so we need it back to being an array/dict
    data = ast.literal_eval(data)
    for item in data:
        list_item = xbmcgui.ListItem(label=item['metadata']['title'])
        #NEED TO DO THE ADDITIONAL STREAMS CHECKING SHIT
        # list_item.setProperty('IsPlayable', 'true')
        # list_item.setInfo("video", {"title": item['metadata']['title']})
        # url = get_url(action="playVideo", content_id=item['id'])
        # xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
        url = get_url(action="archive_", content_id=item['id'])
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)



def list_sets():
    xbmcplugin.setPluginCategory(_handle, 'Sets')
    xbmcplugin.setContent(_handle, 'videos')
    sets = _api_manager.getSets()
    for item in sets:
        if item['content_type']=='content':
            episode = _api_manager.getEpisodeMetadata(episode_uid=item['content_url']['uid'])
            list_episode(episode=episode)
        elif item['content_type']=='set':
            set_metadata=_api_manager.getSetMetadata(set_uid=item['content_url']['uid'])
            list_item = xbmcgui.ListItem(label=set_metadata['title'])
            url = get_url(action='list_set_content', set_uid=item['content_url']['uid'], set_name=set_metadata['title'])
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    #Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def list_set_content(set_uid,set_name):
    xbmcplugin.setPluginCategory(_handle, 'Sets')
    xbmcplugin.setContent(_handle, 'videos')
    set_metadata=_api_manager.getSetMetadata(set_uid=set_uid)
    for set_content in set_metadata['items']:
        episode_uid = set_content['content_url'].split('/')[3]
        episode=_api_manager.getEpisodeMetadata(episode_uid=episode_uid)
        list_episode(episode)
    #Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def list_episode(episode):
    thumb = ''
    for image in episode['image_urls']:
        thumb = image['url']
        break
    # Create a list item with a text label and a thumbnail image.
    list_item = xbmcgui.ListItem(label=episode['title'])

    list_item.setArt({'thumb': thumb,
                    'icon': thumb,
                    'fanart': thumb})

    list_item.setInfo('video', {'title': episode['title'],
                                'genre': "Motorsport",
                                'mediatype': 'video'})

    list_item.setProperty('IsPlayable', 'true')
    episode_slug=episode['slug']
    url = get_url(action='playEpisode', episode_slug=episode_slug)
    xbmcplugin.addDirectoryItem(_handle, url, list_item, False)

def list_seasons():
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'Season Overview')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    season_list = _api_manager.getSeasons()

    for season in season_list:
        season_uid = season['uid']

        list_item = xbmcgui.ListItem(label=str(season['year']))

        list_item.setInfo('video', {'title': str(season['year']),
                                    'genre': "Motorsport",
                                    'mediatype': 'video'})

        url = get_url(action='list_season_events', season=season_uid, year=season['year'])

        is_folder = True
        # Add our item to the Kodi virtual folder listing if the season is not in the future
        if int(season['year']) <= datetime.now().year:
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_circuits():

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


def list_season_events(season_uid, year):

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'Season ' + str(year))
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    season = _api_manager.getSeason(season_uid)
    round_counter = 1

    for event in season:
        event = _api_manager.getEventMetadata(event['uid'])

        if 'start_date' in event and event['start_date'] is not None:
            try:
                start_date = datetime.strptime(event['start_date'], "%Y-%m-%d")
            except TypeError:
                start_date = datetime(*(time.strptime(event['start_date'], "%Y-%m-%d")[0:6]))
            if start_date > datetime.today():
                continue
        if event['name'].strip().endswith('Grand Prix') or event['name'].strip() == 'Indianapolis 500':
            list_item = xbmcgui.ListItem(label="Round {:01d} - {}".format(round_counter, event['name']))
            round_counter += 1
        else:
            list_item = xbmcgui.ListItem(label=event['name'])
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

        url = get_url(action='list_sessions', event_uid=event['uid'], event_name=event['name'])

        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)


    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_circuit_events(circuit_url, circuit_name):

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
        event_uid=event['self'].split('/')[3]
        url = get_url(action='list_sessions', event_uid=event_uid, event_name=event['name'])

        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def list_sessions(event_uid, event_name):
    xbmc.log("{} - {}".format(event_name, event_uid), xbmc.LOGINFO)
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, event_name)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    event = _api_manager.getEvent(event_uid=event_uid)

    for session_url in event['sessionoccurrence_urls']:
        session_uid = session_url.split('/')[3]
        session = _api_manager.getSessionMetadata(session_uid=session_uid)
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

        url = get_url(action='list_session_content', session_uid=session['uid'], session_name=session['name'])

        is_folder = True

        # Add our item to the Kodi virtual folder listing if the item is not upcoming
        if session['status'] != 'upcoming':
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_session_content(session_uid, session_name):

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, session_name)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    session = _api_manager.getSessionMetadata(session_uid=session_uid)

    for channel_url in session['channel_urls']:
        channel_uid = channel_url.split('/')[3]
        # Create a list item with a text label and a thumbnail image.
        channel = _api_manager.getChannelMetadata(channel_uid=channel_uid)
        thumb = ''
        for image in session['image_urls']:
            if image['type'] == 'Thumbnail':
                thumb = image['url']
                break
        try:
            if 'image_urls' in channel['driveroccurrence_urls'][0]:
                for image in channel['driveroccurrence_urls'][0]['image_urls']:
                    if image['image_type'] == 'Headshot':
                        thumb = image['url']
                        break
        except:
            pass
        name = channel['name'] if 'WIF' not in channel['name'] else session['session_name']
        list_item = xbmcgui.ListItem(label=name)

        list_item.setArt({'thumb': thumb,
                          'icon': thumb,
                          'fanart': thumb})

        list_item.setInfo('video', {'title': name,
                                    'genre': "Motorsport",
                                    'mediatype': 'video'})

        url = get_url(action='playChannel', channel_url=channel_url)

        list_item.setProperty('IsPlayable', 'true')

        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    for episode_url in session['content_urls']:
        episode_uid = episode_url.split('/')[3]
        episode = _api_manager.getEpisodeMetadata(episode_uid=episode_uid)
        thumb = ''
        list_episode(episode=episode)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def getCorrectedM3U8(stream_url):
    with requests_cache.disabled():
        r = requests.get(stream_url)
    parts = urlparse(stream_url)

    sub_path = ''
    for component in parts.path.split('/'):
        if 'm3u8' not in component:
            sub_path += component + '/'
    base_url = '{}://{}{}'.format(parts.scheme, parts.netloc, sub_path)

    path = ''
    try:
        path = '{}{}'.format(xbmcvfs.translatePath('special://temp'), 'fixed_stream.m3u8')
    except AttributeError:
        path = '{}{}'.format(xbmc.translatePath('special://temp'), 'fixed_stream.m3u8')

    out_file = open(path, 'w+')
    if r.ok:
        if 'audio-aacl' in r.text:
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
        xbmc.log(r.text, xbmc.LOGDEBUG)

    out_file.close()

    return path

def playVideo(content_id, channel_id=None):
    #Get the M3U8 link
    stream_url = _api_manager.getM3U8(content_id, channel_id)
    #List item stuff
    play_item = xbmcgui.ListItem(path=stream_url)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

def playEpisode(episode_slug):
    extended_episode = _api_manager.getEpisodePlaybackData(slug=episode_slug)
    asset_url = extended_episode['items'][0]['self']
    stream_url = _api_manager.getEpisodeStream(asset_url=asset_url)
    playVideo(stream_url=stream_url)

def playChannel(channel_url):
    stream_url= _api_manager.getChannelStream(channel_url=channel_url)
    playVideo(stream_url=stream_url)

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
        if params['action'] == 'archive':
            # F1TV Page Activity
            archive()
        elif params['action'] == 'archive_block':
            #resultObj based input
            archive_block(params['collection_id'])
        elif params['action'] == 'archive_year':
            archive_year(params['page_id'])
        elif params['action'] == 'archive_category':
            archive_category(params['data'])
        elif params['action'] == 'list_sets':
            list_sets()
        elif params['action'] == 'list_season_events':
            # Display the list of videos in a provided category.
            list_season_events(params['season'], params['year'])
        elif params['action'] == 'list_circuit_events':
            # Display the list of videos in a provided category.
            list_circuit_events(params['circuit'], params['name'])
        elif params['action'] == 'list_sessions':
            # Play a video from a provided URL.
            list_sessions(params['event_uid'], params['event_name'])
        elif params['action'] == 'list_session_content':
            # Play a video from a provided URL.
            list_session_content(params['session_uid'], params['session_name'])
        elif params['action'] == 'list_set_content':
            list_set_content(set_uid=params['set_uid'],set_name=params['set_name'])
        elif params['action'] == 'playEpisode':
            playEpisode(params['episode_slug'])
        elif params['action'] == 'playChannel':
            playChannel(params['channel_url'])
        elif params['action'] == 'playVideo':
            try:
                playVideo(params['content_id'], params['channel_id'])
            except KeyError:
                playVideo(params['content_id'])
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

        response = xbmcgui.Dialog().yesno('Login not possible.', str(error) + 'Enter Settings?',nolabel='Exit', yeslabel='Settings')
        xbmc.log(str(error), xbmc.LOGERROR)
        if response:
            _ADDON.openSettings()

        exit(1)
    router(sys.argv[2][1:])
