import os
import re
#import glob
import fnmatch
import zipfile
import urllib
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
import shutil

__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__cwd__          = __addon__.getAddonInfo('path').decode("utf-8")
__language__     = __addon__.getLocalizedString

SKIN_PATH = os.path.join( xbmc.translatePath("special://home/addons"), xbmc.getSkinDir() )
ADDON_DATA_PATH = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % __addonid__ ).decode("utf-8") )

def main() :
    global ZIP_PATH
    global BACKGROUNDPACKS_REPO
    global INSTALL_PATH
    global download_mode
    modeselect= []
    modeselect.append( __language__(32019) )
    checkDir(os.path.join( ADDON_DATA_PATH))
    dialogSelection = xbmcgui.Dialog()
    download_mode        = dialogSelection.select( __language__(32010), modeselect ) 
    if download_mode == -1 :
        return
    elif download_mode == 0 :
        BACKGROUNDPACKS_REPO = "http://aeon-nox-4-gotham.googlecode.com/svn/trunk/icons/"
        INSTALL_PATH  = os.path.join( SKIN_PATH, "extras" )
        ZIP_PATH = os.path.join( ADDON_DATA_PATH, "ColorIconsNeurosis" )
        DOWNLOAD_BUTTON =  __language__(32029)
    themes = get_local_backgroundpacks()
    themes.append(DOWNLOAD_BUTTON)
    checkDir(ZIP_PATH)	
    dialogThemes = xbmcgui.Dialog()
    index        = dialogThemes.select( __language__(32002), themes ) 
    if index == -1 :
        return
    elif index == len( themes ) - 1 :
        show_remote_themes( BACKGROUNDPACKS_REPO )
    else :
        theme   = themes[ index ]
        install_local_zip( theme )

def log(txt):
    if isinstance (txt,str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonid__, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)
 
def checkDir(path):
    if not xbmcvfs.exists(path):
        xbmcvfs.mkdir(path)
        
def get_local_backgroundpacks( ) :
    themes = []
    if os.path.isdir( ZIP_PATH ) :
        for entry in os.listdir( ZIP_PATH ) :
            if fnmatch.fnmatch(entry, "*.zip") :
                ( name, ext ) = os.path.splitext( entry )
                themes.append( name )
    return themes

def show_remote_themes( BACKGROUNDPACKS_REPO ) :
    file = urllib.urlopen( BACKGROUNDPACKS_REPO )
    html = file.read()
    regexp = re.compile( "<li><a href=\"(.*?)\">(.*?)</a></li>", re.DOTALL )
    items  = regexp.findall( html )
    themes = []
    for item in items :
       if item[1] != ".." :
           ( name, ext ) = os.path.splitext( item[1] )
           themes.append( name )
    if len( themes ) == 0 :
        xbmcgui.Dialog().ok( __addonid__, __language__(32007) )
    else :
        dialogThemes = xbmcgui.Dialog()
        index = dialogThemes.select( __language__(32006), themes )
        if index == -1 :
            return
        theme = themes[ index ]
        dp = xbmcgui.DialogProgress()
        dp.create( __addonid__, __language__(32005), theme )
        remote_theme = os.path.join( BACKGROUNDPACKS_REPO, "%s.zip" % theme )
        local_theme  = os.path.join( ZIP_PATH, "%s.zip" % theme )
        urllib.urlretrieve( remote_theme, local_theme, lambda nb, bs, fs, url=remote_theme : download_progress_hook( nb, bs, fs, local_theme, dp ) )
        dp.close()
        install_local_zip( theme )

def download_progress_hook( numblocks, blocksize, filesize, url=None, dp=None, ratio=1.0 ):
    downloadedsize  = numblocks * blocksize
    percent         = int( downloadedsize * 100 / filesize )
    dp.update( percent )

def install_local_zip( theme ) :
    try :
        DownloadedZip = os.path.join( ZIP_PATH, "%s.zip" % theme )
        zip = zipfile.ZipFile (DownloadedZip, "r")
        zip.extractall(INSTALL_PATH, filter(lambda f: not f.endswith('/'), zip.namelist()))
        zip.close()  
        if download_mode == 8 :
            xbmc.executebuiltin( 'XBMC.UpdateLocalAddons()')
        xbmcgui.Dialog().ok( __addonid__, __language__(32003))
        main()		 
    except :
        xbmcgui.Dialog().ok( __addonid__, __language__(32004))
        main()                            
main()