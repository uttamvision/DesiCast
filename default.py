#!/usr/bin/python3
#
#
# Written by Ksosez, BlueCop
# Released under GPL(v2)

import urllib.request, urllib.parse, urllib.error, cgi, xbmc, xbmcplugin, xbmcaddon, xbmcgui, os, random, re, json
import http.cookiejar
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

## Get the settings

selfAddon = xbmcaddon.Addon(id='plugin.video.DesiCast')
translation = selfAddon.getLocalizedString
defaultimage = 'special://home/addons/plugin.video.DesiCast/icon.png'
defaultfanart = 'special://home/addons/plugin.video.DesiCast/fanart.jpg'
defaultlive = 'special://home/addons/plugin.video.DesiCast/resources/media/new_live.png'
defaultreplay = 'special://home/addons/plugin.video.DesiCast/resources/media/new_replay.png'
defaultupcoming = 'special://home/addons/plugin.video.DesiCast/resources/media/new_upcoming.png'

pluginpath = selfAddon.getAddonInfo('path')
pluginhandle = int(sys.argv[1])

ADDONDATA = xbmc.translatePath('special://profile/addon_data/plugin.video.DesiCast/')
if not os.path.exists(ADDONDATA):
    os.makedirs(ADDONDATA)
USERFILE = os.path.join(ADDONDATA,'userdata.xml')


cj = http.cookiejar.LWPCookieJar()
networkmap = {'n360':'ESPN3','n44':'ESPNPASS'}

channels = '&channel='
channels += 'espnpass'

def CATEGORIES():
    url='http://specpals.com/xml/categories.xml'
    data = get_html(url)
    i = 0
    for cat in ET.XML(data).findall('category'):
        title = cat.get('title')
        img = cat.get('sd_img')
        addDir(title, url, 2, img, i)
        i=i+1
    xbmc.executebuiltin('Container.SetViewMode(%d)' % 500)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def LISTNETWORKS(url,name):
    pass

def LISTSPORTS(url,name,catid):
    data = get_html(url)
    i = 0
    for cat in ET.XML(data).findall('category'):
      if (i==catid):
         for event in cat.findall('categoryLeaf'):
              image = event.get('sd_img')
              title = event.get('title').encode('utf-8')
              url = event.get('feed')
              addDir(title, url, 3, image,0)
      i=i+1
    xbmc.executebuiltin('Container.SetViewMode(%d)' % 500)
    #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def INDEXBYSPORT(url,name):
    INDEX(url,name,bysport=True)

def INDEX(url,name,bysport=False):
    data = get_html(url)
    list_index=1
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    total=len(ET.XML(data).findall('item'))
    xbmc.log("Total: " + str(total))
    for event in ET.XML(data).findall('item'):
        ename = event.findtext('title').encode('utf-8')
        authurl = event.findtext('./media/streamUrl')
        thumb = event.get('sdImg')
        infoLabels = {'title':ename,
                      'tvshowtitle':ename,
                      }
        #authurl=sys.argv[0] + "?url=" + urllib.quote_plus(authurl) + "&mode=" + str(4) + "&name=" + urllib.quote_plus(ename)
        item=xbmcgui.ListItem(ename)
        item.setInfo( type="Video", infoLabels={'title':ename,'plot':ename})
        item.setProperty('IsPlayable', 'true')
        item.setThumbnailImage(thumb)
        addLink(ename, authurl, 4, total,thumb, thumb, infoLabels=infoLabels)
       
        #playlist.add(url=authurl, listitem=item, index=list_index)
        #list_index=list_index+1
    xbmcplugin.setContent(pluginhandle, 'episodes')
    #xbmc.Player().play(playlist)
    xbmc.executebuiltin('Container.SetViewMode(%d)' % 500)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def PLAYESPN3(url):
    PLAY(url,'n360')

def PLAY(url,videonetwork):
    #data = ReadFile('userdata.htm', ADDONDATA)
    #token = re.compile('sf1%3Ftoken%255B0%255D%3D(.+?)%').findall(data)    
    #xbmc.log('CricketHD:  token: '+token[0])    
    if 'rtmp:' in url or 'rtmpe:' in url :
        url = url.replace("circhd_token","")
    elif 'neotv' in url:
      var = urllib.request.urlopen(url)
      saveUserdata2( url )
      xbmc.log('GET URl:'+url)
      data = ReadFile('userdata2.txt', ADDONDATA)
      url = re.compile('"liveStream":"(.+?)",').findall(data)
      url =    url[0]
      #url=urllib.unquote(url).decode('utf8') 
      url = url.replace('\/', '/')      
      xbmc.log('Neo TV:  url: '+url)
    #elif 'einthusan' in url:
    #  var = urllib.request.urlopen(url)
    #  saveUserdata2( url )
    #  xbmc.log('GET URl:'+url)
    #  data = ReadFile('userdata2.txt', ADDONDATA)
    #  url =    data + "|User-Agent= Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17"  
    #  xbmc.log('Einthusan:  url: '+url)       
    elif 'specpals'in url or '192.168.0.12'in url:
      var = urllib.request.urlopen(url)
      url= var.geturl()
      xbmc.log('PLAY URl:'+url)
    else:   
        url = url+"|User-Agent=Mozilla/5.0 (CrKey armv7l 1.4.15250) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.0 Safari/537.36 yupp_andro_mob"
    item = xbmcgui.ListItem(path=url)
    return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

def getJSON( url):
    response = urllib.request.urlopen(url)
    data = json.load(response)
    url=data["results"]["liveStream"]
    xbmc.log('GET JSON URl:'+url)    
    
def saveUserdata2( url ):
    data1 = get_html2( url)
    SaveFile('userdata2.txt', data1, ADDONDATA)
    soup = BeautifulSoup(data1, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    
def saveUserdata():
    #userdata1 = 'http://crickethd.net/prime/247/sf1.php'
    #data1 = get_html(userdata1)
    #SaveFile('userdata.htm', data1, ADDONDATA)
    #soup = BeautifulSoup(data1, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    checkrights = 'http://broadband.espn.go.com/espn3/auth/espnnetworks/user'

def get_html( url ):
    try:
        xbmc.log('ESPN3:  get_html: '+url)
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17'),('Referer', 'http://einthusan.com')]
        #opener.addheaders = []
        usock = opener.open(url)
        response = usock.read()
        usock.close()
        return response
    except: return False

def get_html2( url ):
    try:
        xbmc.log('ESPN3:  get_html: '+url)
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.10 (maverick) Firefox/3.6.17')]
        #opener.addheaders = []
        usock = opener.open(url)
        response = usock.read()
        usock.close()
        return response
    except: return False

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param

def SaveFile(filename, data, dir):
    path = os.path.join(dir, filename)
    try:
        file = open(path,'w')
    except:
        file = open(path,'w+')
    file.write(data)
    file.close()

def ReadFile(filename, dir):
    path = os.path.join(dir, filename)
    if filename == 'userdata.htm':
        try:
            file = open(path,'r')
        except:
            saveUserdata()
            file = open(path,'r')
    else:
        file = open(path,'r')
    return file.read()

def addLink(name, url, mode, total, iconimage, fanart=False, infoLabels=False):
    u = sys.argv[0] + "?url=" + urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    if not infoLabels:
        infoLabels={"Title": name}
    liz.setInfo(type="Video", infoLabels=infoLabels)
    liz.setProperty('IsPlayable', 'true')
    if not fanart:
        fanart=defaultfanart
    liz.setProperty('fanart_image',fanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz,totalItems=total)
    return ok


def addDir(name, url, mode, iconimage, catid, fanart=False, infoLabels=False):
    u = sys.argv[0] + "?url=" + urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name) + "&catid=" + str(catid)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    if not infoLabels:
        infoLabels={"Title": name}
    liz.setInfo(type="Video", infoLabels=infoLabels)
    if not fanart:
        fanart=defaultfanart
    liz.setProperty('fanart_image',fanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = get_params()
url = None
name = None
mode = None
cookie = None
catid = None


try:
    url = urllib.parse.unquote_plus(params["url"])
except:
    pass
try:
    name = urllib.parse.unquote_plus(params["name"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass
try:
    catid = int(params["catid"])
except:
    pass

xbmc.log("Mode: " + str(mode))
xbmc.log("URL: " + str(url))
xbmc.log("Name: " + str(name))

if mode == None or url == None or len(url) < 1:
    xbmc.log("Generate Main Menu")
    saveUserdata()
    CATEGORIES()
elif mode == 1:
    xbmc.log("Indexing Videos")
    INDEX(url,name)
elif mode == 2:
    xbmc.log("List sports")
    LISTSPORTS(url,name,catid)
elif mode == 3:
    xbmc.log("Index by sport")
    INDEXBYSPORT(url,name)
elif mode == 4:
    PLAYESPN3(url)
elif mode == 5:
    xbmc.log("Upcoming")
    dialog = xbmcgui.Dialog()
    dialog.ok(translation(30035), translation(30036))
