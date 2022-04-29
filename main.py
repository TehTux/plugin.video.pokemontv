# coding=utf-8
import sys
from datetime import datetime
from urllib.parse import urlencode, parse_qsl
import requests
import xbmcgui
import xbmcplugin


URL = sys.argv[0]
HANDLE = int(sys.argv[1])
VIDEO_API = 'https://www.pokemon.com/api/pokemontv/v2/channels/de/'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36'


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    """
    return '{0}?{1}'.format(URL, urlencode(kwargs))


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    xbmcplugin.setPluginCategory(HANDLE, 'Video Categories')
    xbmcplugin.setContent(HANDLE, 'videos')
    categories = requests.get(VIDEO_API, headers={'USER-AGENT':USER_AGENT}).json()
    for category in categories:
        list_item = xbmcgui.ListItem(label=category['channel_name'])
        list_item.setArt(
            {
                'thumb': category['channel_images']['spotlight_image_2048_1152'],
                'fanart': category['channel_images']['spotlight_image_2048_1152'],
                'poster': category['channel_images']['dashboard_image_1125_1500'],
                'banner':  category['channel_images']['spotlight_image_2732_940'],
                'keyart': category['channel_images']['dashboard_image_1125_1500'],
                'landscape': category['channel_images']['spotlight_image_2048_1152']
            }
        )
        list_item.setInfo('video', {'title': category['channel_name'], 'plot':  category['channel_description']})
        url = get_url(action='listing', category=category['channel_id'])
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, True)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(HANDLE)


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.
    """
    xbmcplugin.setPluginCategory(HANDLE, "Videos")
    xbmcplugin.setContent(HANDLE, 'videos')
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_NONE)
    categories = requests.get(VIDEO_API, headers={'USER-AGENT':USER_AGENT}).json()
    for channel in categories:
        if category == channel['channel_id']:
            videos = channel['media']
            for video in videos:
                list_item = xbmcgui.ListItem(label=video['title'])
                date = datetime.fromtimestamp(video['last_modified'])
                list_item.setInfo('video', {
                    'title': video['title'], 
                    'mediatype': 'video',
                    'year': date.year, 
                    'plot': video['description'],
                    'aired': date.strftime("%Y-%m-%d"),
                    'season': video['season'],
                    'episode': video['episode']
                })
                list_item.setArt({'thumb': video['images']['large']})
                list_item.setProperty('IsPlayable', 'true')
                url = get_url(action='play', video=video['stream_url'])
                xbmcplugin.addDirectoryItem(HANDLE, url, list_item, False)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(HANDLE)


def play_video(path):
    """
    Play a video by the provided path.
    """
    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(HANDLE, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions depending on the provided paramstring
    """
    params = dict(parse_qsl(paramstring))
    if params:
        if params['action'] == 'listing':
            list_videos(params['category'])
        elif params['action'] == 'play':
            play_video(params['video'])
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        list_categories()


if __name__ == '__main__':
    router(sys.argv[2][1:])
