import os
import shutil
from PIL import Image
from subprocess import Popen, PIPE
import re
import xml.etree.ElementTree as ET
import json

'''
HOW TO:
Change directory into desired folder to contain yt-dlp information (refered to as root folder). Put this python program into this folder. Create a document that contains the links to all of the youtube playlists and videos you wish to download. Run the yt-dlp command below with your configurations (it may take several different passes to download everything if youtube blocks you). Move and modify any files that are needed. When every video is downloaded, configure the User Set Variables. This program needs to be run once for each playlist downloaded. When one playlist is done, change the variables and run the next. 


NOTES:
Folder structure for running: {root}/{downloadFolder}/{playlistFolder}/{videos, info.json, subtitles, descriptions, thumbnails}

This program makes copies of all the files downloaded by yt-dlp to preserve a pristine copy of the data in case issues arise.

Many youtube videos use characters that are not allowed for file names. yt-dlp fixes this by converting them to equivalent unicode characters. If you need to identify these files from a list of the regular names, you can use from difflib import SequenceMatcher to test the similarity (I recomend assigning a threshold similarity ~.87 in order to count and for only the highest value match to be selected from the list of matches above the threshold).

If files in the downloaded playlists are out of order and must be changed/downloaded manually, change their playlist id to be one less than the position they should have, and add letters in alphabetical order (abc) to correct the order (ie file - [episode], 53 - [53], 53a - [54], 54 - [55], 55 = [56]).

Program assumes episodes and seasons are in order. Remove unwanted files beforehand. Skip episodes does not remove episodes, it just skips the episode number (ie if skipping 2, files 1,2,3 will become episodes 1,3,4 respectively). Skip seasons does the same. 

Not compatible with yt-dlp jellyfin metadata plugin. Uninstall it and restart jellyfin. The metadata id tag for this plugin is included in .nfo files, but is not necessary or used.

If any metadata is missing, you can edit the .info.json file and manually add it. You can find the missing tags in get_json_metadata() and by looking at other .info.json files. Warning: file size may cause problems for some text editors.

Requires ffmpeg to be installed as a backup to get metadata from video files if info.json fails.

Sponsor block chapter segments are collected as a list variable, but are not used due to lack of knowledge of how to implement them into jellyfin. The segments are encoded into the video file as chapters and are visible in jellyfin, but are not set up to be detected as media segments.

For specials seasons, assign firstSeason = 0. In the .nfo file for each episode, a tag for airsbefore_episode and airsbefore_season are left blank for you to fill in manually. 

To add intermediate episodes (ie E12.5), rename the files to have their playlist ID include the desired decimal (ie 12.5 - ...)

If you are combining multiple playlists into a single series, you need to modify the customYear to reflect the correct value. I suggest running this program regularly for the playlist with the first aired video, then using that year as the customYear for subsequent runs. All backdrop.jpg, poster.jpg,season#-poster.jpg, and tvshow.nfo are added to the jellyfin series folder, but are renamed based on the season (except for the first playlist added). It's up to you to manage these.

If you want to merge two playlists into a single season and sort by date, set orderByDate to True and playlist to 'link1\nlink2'. If these are from different channels, add both authors to author and both channels to channel.

If there is a video that isn't available on youtube or the wayback machine at all and must be downloaded from an alternate source (meaning you can't get it's .info.json either), find its youtube id and add it to the filename with the propper format and create a custom json for it by following the guide below (try to keep the description simple for jellyfin formatting reasons (blank is also acceptable)).
{"idMismatch": "True", "upload_date": "YYYYMMDD", "uploader": "youtubeChannelName", "webpage_url": "linkToVideoDownload", "uploader_url": "linkToChannelURL", "categories": ["youtubeCategories"], "tags":["video","tags"], "description": "description"}


YT-DLP COMMANDS:
Minimum yt-dlp settings for this program (run this command in root folder): 
yt-dlp -o "%(playlist)s/%(playlist_index)s - [%(id)s] - %(title)s.%(ext)s" -P '{path to download folder}' -P "temp:tmp" --embed-chapters --sponsorblock-mark all --write-subs --write-auto-subs --sub-format vtt --write-thumbnail --write-description --write-info-json 
 - .info.json, thumbnail, - mandatory (for full functionality, may work without, but unlikely)
 - description - prefered for better output
 -  subtitles - optional, but prefered
 -  sub format vtt - mandatory for subtitles, assumes vtt format
 - embed chapters, sponsorblock mark - prefered for completeness sake, but unneccessary for this program

My yt-dlp settings (guaranteed to work) (run this command in root folder):
yt-dlp -a '/path/to/listOfPlaylistsAndMissingVideosLinks.txt' --download-archive '/path/to/archive.txt' -o "%(playlist)s/%(playlist_index)s - [%(id)s] - %(title)s.%(ext)s" -P '/path/to/downloadFolder' -P "temp:tmp" -f "bv+ba/b" --embed-thumbnail --embed-metadata --embed-chapters --sponsorblock-mark all --write-subs --write-auto-subs --sub-format vtt --sub-langs "en.*" --audio-quality 0 --cookies-from-browser firefox --write-thumbnail --write-description --write-info-json -r '25M'
To create infinite gmail accounts for youtube cookies, create gmail accounts on your phone in the gmail app, then login thru browser. this bypasses the need for phone number verification


KNOW ISSUES:
Sometimes after moving the files manually to jellyfin, the jellyfin titles are erased and replaced with the season and episode. This likely happens because the folder is in jellyfin not deleted beforehand and jellyfin makes a mistake. If this happens, delete the folder and rerun the program (this is why it only makes copies).

BULK RUN:
To bulk run, follow the template below and add or modify any settings needed. At the end of the script, copy and paste a copy of the template for each playlist you wish to process (Make sure to fill in the template at the top tho)

# BEGIN TEMPLATE -------------

seriestitle = ''
author = ''
channel = ''
playlist = ''
playlistFolder = ''
reverseOrder = False 
firstSeason = 1
startingEpisodeNum = 1
seasons = []
skipEpisodes = []
skipSeasons = []
customYear = ''
moveToJellyfin = True
authorInTitle = True
orderByDate = False


showtitle = check_user_variables()

if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 

if playlist != '': # correct formatting if playlist exists
    playlist = f'\n\n{playlist}'

main()

# END TEMPLATE -------------

'''


# User Set Variables

downloadFolder = '' # folder within current directory that contains the folders for each playlist
fsLibraryFolder = '' # full filesystem path to the jellyfin library folder where you want to store these videos
isDocker = True # Boolean: Is jellyfin being run in a docker container. If True, assumes media folder is named the same in both docker and the main filesystem (ie in docker volumes /path/to/media:/media)
moveToJellyfin = False # Boolean: Automatically move processed files to jellyfin library folder


seriestitle = '' # the title of the youtube series. leave blank to make the author the only part of the title. cannot contain /
author = '' # the creator of the series (usually the youtuber). cannot contain /
channel = '' # link to the creator's youtube channel;
playlist = '' #link to the playlist these videos come from (not retrieved from metadata because not everything comes from a playlist. if this is the case leave blank)
playlistFolder = '' # copy and paste the name of the playlist folder that was downloaded here (u\ characters are valid and expected)
reverseOrder = False # Boolean: Set True if the playlist is in the wrong order
startingEpisodeNum = 1 # First episode number in season (ie where the program starts counting from)
firstSeason = 1 # starting season (0 will create a specials season)
seasons = [] # first episode of each season (dont use playlist id). assumes episode numbers roll over to next season. leave blank for all one season. if seasons left blank, start at episode one
skipEpisodes = [] # any episode numbers that should be skipped (ie if skipping 2, files 1,2,3 will become episodes 1,3,4 respectively)
skipSeasons = [] # operates exactly the same as skipEpisodes
customYear = '' # default empty string, but both string and int work. when creating a single series from multiple playlists, the year in the series folder name will be incorrect, but can be set here. if left as an empty string, the year will be gathered through metadata. (Tip: Run the earliest released playlist first, then set customYear for following playlists.)
authorInTitle = True # Boolean: Put author in show title
orderByDate = False # Boolean: Change the order of files by episode date instead of file order


downloadFolder = 'youtubedownload' # folder within current directory that contains the folders for each playlist
fsLibraryFolder = '/Wizard/Docker/jellyfin/media/youtube' # full filesystem path to the jellyfin library folder where you want to store these videos
moveToJellyfin = True


seriestitle = 'Space Engineers'
author = 'GetBrocked'
channel = 'https://www.youtube.com/@GetBrocked'
playlist = 'https://www.youtube.com/watch?v=kw6rcey4ytc&list=PLSOiQqYQEf1jkzq-CxPEhYLpPkrekjSua&pp=iAQB'
playlistFolder = 'Space Engineers Season 6 (Sigmarius\u29f8Prequel)'
reverseOrder = False 
firstSeason = 1
seasons = []
skipEpisodes = []
customYear = 2016

# End User Set Variables


def check_user_variables(): # make sure user variables are set correctly
    ErrorTest = []

    if type(downloadFolder) is not str: 
        print(f'TypeError: Variable downloadFolder is not type bool')
        ErrorTest.append('downloadFolder')

    if type(fsLibraryFolder) is not str: 
        print(f'TypeError: Variable fsLibraryFolder is not type str')
        ErrorTest.append('fsLibraryFolder')

    if type(isDocker) is not bool: 
        print(f'TypeError: Variable isDocker is not type bool')
        ErrorTest.append()

    if type(moveToJellyfin) is not bool: 
        print(f'TypeError: Variable moveToJellyfin is not type bool')
        ErrorTest.append('isDocker')

    if type(reverseOrder) is not bool: 
        print(f'TypeError: Variable reverseOrder is not type bool')
        ErrorTest.append('reverseOrder')

    if type(seriestitle) is not str: 
        print(f'TypeError: Variable seriestitle is not type str')
        ErrorTest.append('seriestitle')

    if type(author) is not str: 
        print(f'TypeError: Variable author is not type str')
        ErrorTest.append('author')

    if type(playlistFolder) is not str: 
        print(f'TypeError: Variable playlistFolder is not type str')
        ErrorTest.append('playlistFolder')

    if type(seasons) is not list: 
        print(f'TypeError: Variable seasons is not type list')
        ErrorTest.append('seasons')

    if type(skipEpisodes) is not list: 
        print(f'TypeError: Variable skipEpisodes is not type list')
        ErrorTest.append('skipEpisodes')

    if type(skipSeasons) is not list: 
        print(f'TypeError: Variable skipSeasons is not type list')
        ErrorTest.append('skipSeasons')

    if type(authorInTitle) is not bool: 
        print(f'TypeError: Variable authorInTitle is not type bool')
        ErrorTest.append('authorInTitle')

    
    try: startingEpisodeNumTest = int(startingEpisodeNum)
    except: startingEpisodeNumTest = startingEpisodeNum   
    if type(startingEpisodeNumTest) is not int: 
        print(f'TypeError: Variable startingEpisodeNum is not type int')
        ErrorTest.append('startingEpisodeNum')

    try: firstSeasonTest = int(firstSeason)
    except: firstSeasonTest = firstSeason   
    if type(firstSeasonTest) is not int: 
        print(f'TypeError: Variable firstSeason is not type int')
        ErrorTest.append('firstSeason')

    if type(customYear) is str: 
        if customYear != '':
            try: int(customYear)
            except: 
                print(f'TypeError: Variable customYear is not a valid number')
                ErrorTest.append('customYear')
    elif type(customYear) is not int:
        print(f'TypeError: Variable customYear is not type int or valid str')
        ErrorTest.append('customYear')


    if downloadFolder == '':
        ErrorTest.append('downloadFolder')
        print('ValueError: Variable downloadFolder cannot be empty')
    if fsLibraryFolder == '':
        ErrorTest.append('fsLibraryFolder')
        print('ValueError: Variable fsLibraryFolder cannot be empty')
    if playlistFolder == '':
        ErrorTest.append('playlistFolder')
        print('ValueError: Variable playlistFolder cannot be empty')

    if authorInTitle: # formatting to get correct spacing for showtitle
        if seriestitle == '':
            showtitle = f'{author}'
        else:
            showtitle = f'{author} - {seriestitle}'
        if author == '':
            ErrorTest.append('author')
            print('ValueError: Variable author cannot be empty if authorInTitle is True')
    else: 
        if seriestitle == '': 
            ErrorTest.append('seriestitle')
            print('ValueError: Variable seriestitle cannot be empty if authorInTitle is False')
        else:
            showtitle = f'{seriestitle}'


    if ErrorTest != []: raise TypeError(f'Incorrect variable configuration for {ErrorTest}')

    return showtitle

def copy_and_rename(src_path, dest_path, new_name):
	shutil.copy(src_path, dest_path)
	# Rename the copied file
	shutil.move(f"{dest_path}/{src_path}", f"{dest_path}/{new_name}")

def get_video_metadata(file): # use ffmpeg to get the date information from video files (backup)
    res = Popen(['ffmpeg', '-i', file, '-hide_banner'],stdout=PIPE,stderr=PIPE)
    none,meta = res.communicate()
    meta_out = meta.decode()
    #print(meta_out)
    try: 
        date = re.search(r'DATE.*', meta_out)
        date = date.group()
        date = date.replace('DATE','').replace('/','').strip(':. \r')
        year = date[0:4]
        date = f'{year}-{date[4:6]}-{date[6:]}'
        return year,date
    except AttributeError:
        try:
            date = re.search(r'date.*', meta_out)
            date = date.group()
            date = date.replace('date','').replace('/','').strip(':. \r')
            year = date[0:4]
            date = f'{year}-{date[4:6]}-{date[6:]}'
            return year,date
        except AttributeError:
            try:
                date = re.search(r'Created on.*', meta_out)
                date = date.group()
                date = date.replace('Created on: ','').replace('/','').strip(':. \r')
                year = date[-4:]
                date = f'{year}-{date[:2]}-{date[2:4]}'
                return year,date
            except AttributeError: raise AttributeError(f'unknown metadata format for file {file}')
        
def get_json_metadata(filename): # use .info.json to get the metadata of the video
    with open(f'{filename}.info.json','r',encoding="utf8") as file:
        data = json.load(file)
        dataClean = json.dumps(data, indent=4)
        
        # critical values. left outside a try/except because if they fail an error should be raised
        date = data['upload_date']
        date = f'{date[:4]}-{date[4:6]}-{date[6:]}'
        year = date[:4]
        uploader = data['uploader']
        video_link = data['webpage_url']
        jsonDescription = data['description']

        try: channel_link = data['uploader_url']
        except: channel_link = data['channel_url']
        
        try: tags = data['tags']
        except: tags = []
        if 'youtube' not in tags: tags.append('youtube')
        if uploader not in tags: tags.append(uploader)
        
        try: genres = data['categories']
        except: genres = []
        if 'youtube' not in genres: genres.append('youtube')
        
        try: sponsor_chapters = data['sponsorblock_chapters'] # unused
        except: sponsor_chapters = []

        try: IDmismatch = bool(data['idMismatch'])
        except: IDmismatch = False
        
        if not IDmismatch:
            videoID = filename[filename.find(' - [')+4:filename.find('] - ')]
            if video_link.find(videoID) == -1: raise NameError(f'Video ID {videoID} in file name does not match video ID in {filename}.info.json. Please resolve.')

    return year, date, uploader, channel_link, video_link, tags, genres, sponsor_chapters, jsonDescription

def get_many_dates(files,ffmpeg): # get list of dates for each video in a season (.info.json primary with ffmpeg backup)
    years = []
    dates = []
    epNum = 0
    for file in files: # get first and last dates
        if file.endswith('.mkv') or file.endswith('.mp4'): #gets a list of all the years these videos were released in an sorts
            fileNum = file[:file.find(' - ')]
            filename = file[:file.rfind('.')]
            if fileNum != epNum: #iterate through episodes, skip files for same episode
                epNum = fileNum
                if fileNum != 0:
                    if os.path.isfile(f'{filename}.info.json'): # primary
                        episodeData = get_json_metadata(filename)
                        yeartemp = episodeData[0]
                        datetemp = episodeData[1]
                    elif ffmpeg == True: # backup
                        yeartemp, datetemp = get_video_metadata(file)
                        print(f'FileNotFoundError: Cannot find info.json file {filename}.info.json. Used ffmpeg to get date metadata')
                    else: raise FileNotFoundError(f'Cannot find info.json file {filename}.info.json and ffmpeg not installed')
                    years.append(yeartemp)
                    dates.append(datetemp)
    firstyear = sorted(years)[0]
    firstdate = sorted(dates)[0]
    lastdate = sorted(dates)[-1]

    return firstyear,firstdate,lastdate


def createSeason(filename,season,showfirstyear,firstyear,firstdate,lastdate,seasonTags,seasonGenres): # creates season.nfo
    if season == 0: seasonFolder = 'Specials'
    else: seasonFolder = f'Season {season}'

    try:
        descriptionFile = open(f'{filename}.description','r')
        description = descriptionFile.read()
        descriptionFile.close()
    except:
        jsonData = get_json_metadata(f'{filename}.info.json')
        description = jsonData[8]

    seasonnfo = ET.Element('season')
    ET.SubElement(seasonnfo,'plot').text = (f'{author} - {channel}{playlist}\n\n\n{description}').rstrip('\n -')
    ET.SubElement(seasonnfo,'outline').text = (f'{author} - {channel}{playlist}\n\n\n{description}').rstrip('\n -')
    ET.SubElement(seasonnfo,'lockdata').text = f'true'  
    ET.SubElement(seasonnfo,'title').text = f'{showtitle}'
    ET.SubElement(seasonnfo,'year').text = f'{firstyear}'
    ET.SubElement(seasonnfo,'premiered').text = f'{firstdate}'
    ET.SubElement(seasonnfo,'releasedata').text = f'{firstdate}'
    ET.SubElement(seasonnfo,'enddate').text = f'{lastdate}'
    for genre in seasonGenres: ET.SubElement(seasonnfo,'genre').text = genre
    for tag in seasonTags: ET.SubElement(seasonnfo,'tag').text = tag
    art = ET.SubElement(seasonnfo, 'art')
    ET.SubElement(art,'poster').text = f'/{jfLibraryFolder}/{showtitle} ({showfirstyear})/season{str(season).zfill(2)}-poster.jpg'
    actor = ET.SubElement(seasonnfo,'actor')
    ET.SubElement(actor,'name').text = f'{author}'
    ET.SubElement(actor,'type').text = f'Actor'
    ET.SubElement(seasonnfo,'seasonnumber').text = f'{season}'

    tree = ET.ElementTree(seasonnfo)
    ET.indent(tree, space="  ", level=0)
    out = open(f"{seasonFolder}/seasonnfo.nfo", 'wb')
    out.write(b'<?xml version="1.0" encoding="UTF-8" standalone = "yes"?>\n')
    tree.write(out, encoding = 'UTF-8', xml_declaration = False)
    out.close()

    if season == 0:
        if os.path.exists(f'season-specials-poster.jpg'):
            os.remove(f'season-specials-poster.jpg')
        shutil.copy2(f'{filename}.jpg', f'season-specials-poster.jpg')
    else: 
        if os.path.exists(f'season{str(season).zfill(2)}-poster.jpg'):
            os.remove(f'season{str(season).zfill(2)}-poster.jpg')
        shutil.copy2(f'{filename}.jpg', f'season{str(season).zfill(2)}-poster.jpg')
    
def createShow(filename,firstyear,firstdate,lastdate,showTags,showGenres): # creates tvshow.nfo
    try:
        descriptionFile = open(f'{filename}.description','r')
        description = descriptionFile.read()
        descriptionFile.close()
    except:
        jsonData = get_json_metadata(f'{filename}.info.json')
        description = jsonData[8]

    tvshow = ET.Element('tvshow')
    ET.SubElement(tvshow,'plot').text = (f'{author} - {channel}\n\n\n{description}').rstrip('\n -')
    ET.SubElement(tvshow,'outline').text = (f'{author} - {channel}\n\n\n{description}').rstrip('\n -')
    ET.SubElement(tvshow,'lockdata').text = f'true'
    ET.SubElement(tvshow,'title').text = f'{showtitle}'
    ET.SubElement(tvshow,'year').text = f'{firstyear}'
    ET.SubElement(tvshow,'premiered').text = f'{firstdate}'
    ET.SubElement(tvshow,'releasedata').text = f'{firstdate}'
    ET.SubElement(tvshow,'enddate').text = f'{lastdate}'
    for genre in showGenres: ET.SubElement(tvshow,'genre').text = genre
    for tag in showTags: ET.SubElement(tvshow,'tag').text = tag
    ET.SubElement(tvshow,'studio').text = f'{author}'
    ET.SubElement(tvshow,'studio').text = f'youtube'
    actor = ET.SubElement(tvshow,'actor')
    ET.SubElement(actor,'name').text = f'{author}'
    ET.SubElement(actor,'type').text = f'Actor'
    ET.SubElement(tvshow,'season').text = f'-1'
    ET.SubElement(tvshow,'episode').text = f'-1'
    ET.SubElement(tvshow,'status').text = f'Ended'

    tree = ET.ElementTree(tvshow)
    ET.indent(tree, space="  ", level=0)
    out = open("tvshow.nfo", 'wb')
    out.write(b'<?xml version="1.0" encoding="UTF-8" standalone = "yes"?>\n')
    tree.write(out, encoding = 'UTF-8', xml_declaration = False)
    out.close()

    if os.path.exists('poster.jpg'):
        os.remove('poster.jpg')
    if os.path.exists('backdrop.jpg'):
        os.remove('backdrop.jpg')
    shutil.copy2(f'{filename}.jpg', 'poster.jpg')
    shutil.copy2(f'{filename}.jpg', 'backdrop.jpg')

def createEpisode(title,titleSE,season,firstyear,episode,epfile,ffmpeg): # creates episode.nfo and moves all episode files to propper folder
    if season == 0: seasonFolder = 'Specials'
    else: seasonFolder = f'Season {season}'

    if epfile.endswith('.mkv'):
        copy_and_rename(epfile,f'{os.getcwd()}/{seasonFolder}',f'{titleSE}.mkv') #move and rename mkv video
    elif epfile.endswith('.mp4'): 
        copy_and_rename(epfile,f'{os.getcwd()}/{seasonFolder}',f'{titleSE}.mp4') #move and rename mp4 video

    videoID = title[title.find(' - [')+4:title.find('] - ')]
    if os.path.isfile(f'{title}.info.json'): 
        year,date,episodeUploader,episodeChannel,episodeLink,episodeTags,episodeGenre,episodeSponsorSegments,jsonDescription = get_json_metadata(title)
    elif ffmpeg == True: 
        videoID = title[title.find(' - [')+4:title.find('] - ')]
        year,date = get_video_metadata(epfile)
        episodeUploader = author
        episodeChannel = channel
        episodeLink = f'https://www.youtube.com/watch?v={videoID}'
        episodeTags = ['youtube']
        episodeGenre = ['youtube']
        episodeSponsorSegments = [] # unused
    else: raise FileNotFoundError(f'Cannot find info.json file {title}.info.json and ffmpeg not installed')
    

    try:
        descriptionFile = open(f'{title}.description','r')
        description = descriptionFile.read()
        descriptionFile.close()
    except:
        description = jsonDescription

    cleanTitle = title[title.find('] - ')+4:]

    episodenfo = ET.Element('episodedetails')
    ET.SubElement(episodenfo,'plot').text = (f'{episodeUploader} - {episodeChannel}\n\n{episodeLink}\n\n\n{description}').rstrip('\n -')
    ET.SubElement(episodenfo,'outline').text = (f'{episodeUploader} - {episodeChannel}\n\n{episodeLink}\n\n\n{description}').rstrip('\n -')
    ET.SubElement(episodenfo,'lockdata').text = f'false'
    ET.SubElement(episodenfo,'title').text = f'{cleanTitle}'
    ET.SubElement(episodenfo,'director').text = f'{episodeUploader}'
    ET.SubElement(episodenfo,'year').text = f'{year}'
    ET.SubElement(episodenfo,'sorttitle').text = f'{titleSE}'
    for genre in episodeGenre: ET.SubElement(episodenfo,'genre').text = genre
    for tag in episodeTags: ET.SubElement(episodenfo,'tag').text = tag
    ET.SubElement(episodenfo,'youtubemetadataid').text = f'{videoID}'
    art = ET.SubElement(episodenfo, 'art')
    ET.SubElement(art,'poster').text = f'/{jfLibraryFolder}/{showtitle} ({firstyear})/{seasonFolder}/{titleSE}-thumb.jpg'
    actor = ET.SubElement(episodenfo,'actor')
    ET.SubElement(actor,'name').text = f'{episodeUploader}'
    ET.SubElement(actor,'type').text = f'Actor'
    ET.SubElement(episodenfo,'showtitle').text = f'{showtitle}'
    ET.SubElement(episodenfo,'episode').text = f'{episode}'
    ET.SubElement(episodenfo,'season').text = f'{season}'
    ET.SubElement(episodenfo,'aired').text = f'{date}'

    if season == 0:
        ET.SubElement(episodenfo,'airsbefore_episode').text = f''
        ET.SubElement(episodenfo,'airsbefore_season').text = f''
        ET.SubElement(episodenfo,'displayepisode').text = f'{episode}'
        ET.SubElement(episodenfo,'displayseason').text = f'{season}'

    tree = ET.ElementTree(episodenfo)
    ET.indent(tree, space="  ", level=0)
    out = open(f"{seasonFolder}/{titleSE}.nfo", 'wb')
    out.write(b'<?xml version="1.0" encoding="UTF-8" standalone = "yes"?>\n')
    tree.write(out, encoding = 'UTF-8', xml_declaration = False)
    out.close()


def main():

    if not os.path.isdir(fsLibraryFolder): raise NotADirectoryError(f'Cannot find jellyfin library folder {fsLibraryFolder}. Please create your jellyfin library folder before proceeding or check your spelling :P')

    os.chdir(f'{root}/{downloadFolder}/{playlistFolder}')

    for seasonPos in range(len(seasons)): # create season folders and remove previously created season folders
        season = firstSeason + seasonPos
        if season not in skipSeasons:
            if season == 0: seasonFolder = 'Specials'
            else: seasonFolder = f'Season {season}'
            if os.path.exists(os.path.join(os.getcwd(),seasonFolder)):
                shutil.rmtree(os.path.join(os.getcwd(),seasonFolder))
            os.mkdir(os.path.join(os.getcwd(),seasonFolder))
        
        
    files = [f for f in sorted(os.listdir(),reverse=reverseOrder) if re.match(r'^\d+', f) and ' - ' in f] # get all files and filter out unwanted files (ie everything that wasn't downloaded by yt-dlp)
    otherFiles = [f for f in sorted(os.listdir(),reverse=reverseOrder) if os.path.isfile(f) and not (re.match(r'^\d+', f) and ' - ' in f)] # unwanted files
    
    try: otherFiles.remove('poster.jpg') # remove files created by this script from list of unwanted files
    except:pass
    try: otherFiles.remove('backdrop.jpg')
    except: pass
    try: otherFiles.remove('tvshow.nfo')
    except: pass

    otherFilesTemp = otherFiles # remove season posters
    for file in otherFiles:
        if file.startswith('season') and file.endswith('-poster.jpg'):
            otherFilesTemp.remove(file)
    otherFiles = otherFilesTemp

    ffmpegTest = False
    subtitles = False
    for file in files: # test if ffmpeg is accessible and if any subtitles were downloaded
        if not ffmpegTest:
            if file.endswith('.mkv') or file.endswith('.mp4'):
                try: 
                    res = Popen(['ffmpeg', '-i', file, '-hide_banner'],stdout=PIPE,stderr=PIPE)
                    ffmpeg = True
                except: 
                    ffmpeg = False
                ffmpegTest = True
        if not subtitles:
            if file.endswith('.vtt'): 
                subtitles = True
    if not ffmpeg: print('ffmpeg not detected\n')
    if not subtitles: print('No subtitles detected\n')
    
        
    for file in files:
        if file.endswith('.webp'): # convert webp images to jpg, but not if it was already converted
            if not os.path.isfile(f"{file[:-5]}.jpg"):
                thumbnail = Image.open(file).convert("RGB")
                thumbnail.save(f"{file[:-5]}.jpg", "jpeg")#organize files by date


    if orderByDate:
        fileNameDates = {}
        for file in files:
            if file.endswith('.mp4') or file.endswith('mkv'):
                filename = file[:file.rfind('.')]
                try: 
                    episodeData = get_json_metadata(filename)
                    date = episodeData[1]
                except:
                    year,date = get_video_metadata(file)
                fileNameDates.update({file: date})

        fileNameDates = dict(sorted(fileNameDates.items(), key=lambda item: item[1]))
        orderedFiles = list(fileNameDates.keys())
        if reverseOrder: orderedFiles.reverse()
    elif not orderByDate:
        orderedFiles = files
    orderedFileNames = [file[:file.rfind('.')] for file in orderedFiles]\


    seasonPos = 0  # Start at the first index of list1
    nextSeason = seasons[seasonPos]  # Initialize with the first value in the list

    episodeNum = startingEpisodeNum
    seasonIndex = []
    for i in range(len(seasons)):
        seasonIndex.append([])

    for file in orderedFiles: # organize every video file by season
        if file.endswith('.mp4') or file.endswith('mkv'):
            episodeTest = False
            for reverseSeasonPos in range(len(seasonIndex)-1,-1,-1):
                if not episodeTest and episodeNum >= seasons[reverseSeasonPos]:
                    seasonIndex[reverseSeasonPos].append(file)
                    episodeNum += 1
                    episodeTest = True

    seasonFirstYears = []
    seasonFirstDates = []
    seasonLastDates = []
    seasonTags = []
    seasonGenres = []

    skippedSeasons = 0

    for seasonPos in range(len(seasons)): # organize the date metadata of every video file by season
        season = firstSeason + seasonPos + skippedSeasons
        while season in skipSeasons: 
            season += 1
            skippedSeasons += 1
        if season == 0: seasonFolder = 'Specials'
        else: seasonFolder = f'Season {season}'
        print(seasonFolder)

        seasonTag = []
        seasonGenre = []
        seasonFiles = seasonIndex[seasonPos]
        seasonFirstYear,seasonFirstDate,seasonLastDate = get_many_dates(seasonFiles,ffmpeg)

        for file in seasonFiles:
            filename = file[:file.rfind('.')]
            episodeData = get_json_metadata(filename)
            seasonTag.append(episodeData[5])
            seasonGenre.append(episodeData[6])

        seasonFirstYears.append(seasonFirstYear)
        seasonFirstDates.append(seasonFirstDate)
        seasonLastDates.append(seasonLastDate)
        seasonTags.append(sorted(set([tag for season in seasonTag for tag in season])))
        seasonGenres.append(sorted(set([genre for season in seasonGenre for genre in season])))

    # get total show metadata
    if customYear == '': firstyear = min(seasonFirstYears)
    else: firstyear = int(customYear)
    firstdate = min(seasonFirstDates)
    lastdate = max(seasonLastDates)
    

    skippedSeasons = 0
    for seasonPos in range(len(seasons)): # create season.nfo files for all seasons
        season = firstSeason + seasonPos + skippedSeasons
        while season in skipSeasons: 
            season += 1
            skippedSeasons += 1
        if season == 0: seasonFolder = 'Specials'
        else: seasonFolder = f'Season {season}'
        madeSeason = False
        for file in files:
            if (file[:file.find(' - ')]).strip('0') == '' and not madeSeason: 
                if file.endswith('.info.json'): 
                    filename = file[:-10]
                else: 
                    filename = file[:file.rfind('.')]
                createSeason(filename,season,firstyear,seasonFirstYears[seasonPos],seasonFirstDates[seasonPos],seasonLastDates[seasonPos],seasonTags[seasonPos],seasonGenres[seasonPos]) # playlist description
                madeSeason = True

    madeShow = False
    allTags = sorted(set([tag for season in seasonTags for tag in season]))
    allGenres = sorted(set([genre for season in seasonGenres for genre in season]))

    for file in files: # create show tvshow.nfo file
        if (file[:file.find(' - ')]).strip('0') == '' and not madeShow: 
            if file.endswith('.info.json'): 
                filename = file[:-10]
            else: 
                filename = file[:file.rfind('.')]
            createShow(filename,firstyear,firstdate,lastdate,allTags,allGenres) # show description
            madeShow = True


    print(f'\n{showtitle} ({firstyear})\n') # print the name of the jellyfin show folder
    seriesPath = f'{fsLibraryFolder}/{showtitle} ({firstyear})'
    if os.path.isdir(f'{fsLibraryFolder}/{showtitle} ({firstyear})') and os.listdir(f'{fsLibraryFolder}/{showtitle} ({firstyear})') != []:
            print(f'WARNING: Series folder {showtitle} ({firstyear}) contains files. If this is desired, manually edit the enddate parameter in tvshow.nfo before transfering. Otherwise remove folder and files and rescan the jellyfin library before transfering files (Failing to rescan can cause major issues).\n')


    fileNameList = []
    for seasonPos in range(len(seasonIndex)): # organize all episodes by removing extensions and organizing by season
        fileNameList.append([])
        for file in seasonIndex[seasonPos]: # get all the episode filenames into a list (excluding extensions)
            if (file[:file.find(' - ')]).strip('0') != '': 
                if file.endswith('.vtt') or file.endswith('.info.json'): 
                    filename = file[:file.rfind('.')]
                    filename = filename[:filename.rfind('.')]
                else: 
                    filename = file[:file.rfind('.')]
                fileNameList[seasonPos].append(filename)
    
    for seasonPos in range(len(fileNameList)): # put all episode filenames in order and remove duplicates
        fileNameList[seasonPos] = sorted(set(fileNameList[seasonPos]),reverse=reverseOrder)
                
    if orderByDate:
        for seasonPos in range(len(fileNameList)):
            fileNameList[seasonPos] = sorted(fileNameList[seasonPos], key=lambda x: orderedFileNames.index(x))


    episodeNum = startingEpisodeNum
    MissingIDErrors = []
    MissingFilesErrors = []
    skippedSeasons = 0

    for seasonPos in range(len(fileNameList)): # copy and rename all files for each episode to season folder and make .nfo files for each episode
        for title in fileNameList[seasonPos]:
            season = firstSeason + seasonPos + skippedSeasons
            playlistID = title[title.find(' - '):]
            if playlistID.find('.') != -1: 
                nextEpisode = episodeNum
                episodeNum = f'{episodeNum -1}{title[title.find('.'):title.find(' - ')]}' 


            while season in skipSeasons: 
                season += 1
                skippedSeasons += 1
            if season == 0: seasonFolder = 'Specials'
            else: seasonFolder = f'Season {season}'

            if playlistID.find('.') != -1: 
                if sum(c.isdigit() for c in title[:title.find('.')]) < 2:
                    titleSE = f'S{str(season).zfill(2)}E{str(nextEpisode-1).zfill(2)}{title[title.find('.'):]}' # add season and episode to the title (with enough padded zeros) and remove playlist id. also removes any letters from playlist id
                else:
                    titleSE = f'S{str(season).zfill(2)}E{str(nextEpisode-1).zfill(sum(c.isdigit() for c in title[:title.find('.')]))}{title[title.find('.'):]}' # add season and episode to the title (with enough padded zeros) and remove playlist id. also removes any letters from playlist id

            elif sum(c.isdigit() for c in title[:title.find(' - ')]) < 2:
                titleSE = f'S{str(season).zfill(2)}E{str(episodeNum).zfill(2)}{title[title.find(' - '):]}' # add season and episode to the title (with enough padded zeros) and remove playlist id. also removes any letters from playlist id
            else:
                titleSE = f'S{str(season).zfill(2)}E{str(episodeNum).zfill(sum(c.isdigit() for c in title[:title.find(' - ')]))}{title[title.find(' - '):]}' # add season and episode to the title (with enough padded zeros) and remove playlist id. also removes any letters from playlist id
            
            
            print(title)
            print(titleSE)
            print()
            
            if title.find('] - ') != -1 and title.find(' - [') != -1: # if id exists
                if (title[:title.find(' - ')]).strip('0') != '': # if file isnt playlist
                    if title.find('] - ') - title.find(' - [') - 4 != 11: # if id isnt the right length
                        MissingIDErrors.append(f'Episode {playlistFolder}/{title} does not contain a valid youtube video ID')
            
            if not (os.path.isfile(f'{title}.mkv') or os.path.exists(f'{title}.mkv')):
                MissingFilesErrors.append(f'Cannot find file {playlistFolder}/{title}.mp4 or {playlistFolder}/{title}.mkv')
            if not os.path.isfile(f'{title}.jpg'):
                if os.path.isfile(f'{title}.webp'):
                    MissingFilesErrors.append(f'Cannot find file {playlistFolder}/{title}.jpg, but could find {playlistFolder}/{title}.webp')
                else:
                    MissingFilesErrors.append(f'Cannot find file {playlistFolder}/{title}.jpg or {playlistFolder}/{title}.webp')
            if not os.path.isfile(f'{title}.info.json'):
                MissingFilesErrors.append(f'Cannot find file {playlistFolder}/{title}.info.json')

            pattern = re.compile(rf"^{re.escape(title)}.*{re.escape('.vtt')}$")
            subtitleTest = False
            for filename in os.listdir():
                if not os.path.isfile(os.path.join(os.getcwd(), filename)) and pattern.match(title):
                    subtitleTest = True
            if subtitleTest and subtitles: 
                MissingFilesErrors.append(f'Cannot find subtitle file {playlistFolder}/{title}.*.vtt')
            
            
            # media segments from sponsor block and episode chapters?


            episodeFiles = [episodeFile for episodeFile in os.listdir() if episodeFile.startswith(title)]  
            for epfile in episodeFiles:
                if epfile.endswith('.mkv') or epfile.endswith('.mp4'): 
                    createEpisode(title,titleSE,season,firstyear,episodeNum,epfile,ffmpeg) # create episode metadata
                elif epfile.endswith('.jpg'): copy_and_rename(epfile,f'{os.getcwd()}/{seasonFolder}',f'{titleSE}-thumb.jpg') #move and rename thumbnail
                elif epfile.endswith('.vtt'): copy_and_rename(epfile,f'{os.getcwd()}/{seasonFolder}',f'{titleSE}{epfile[epfile.rfind('.',0,-4):]}') #move and rename subtitles'''
                elif epfile.endswith('.info.json'): copy_and_rename(epfile,f'{os.getcwd()}/{seasonFolder}',f'{titleSE}.info.json')
            
            if playlistID.find('.') != -1: episodeNum = nextEpisode
            else: episodeNum += 1    

            while episodeNum in skipEpisodes:
                episodeNum += 1

    seriesPath = f'{fsLibraryFolder}/{showtitle} ({firstyear})' # move to jellyfin
    skippedSeasons = 0
    if moveToJellyfin: 
        try: os.mkdir(f'{fsLibraryFolder}/{showtitle} ({firstyear})')
        except: pass
        if os.listdir(f'{fsLibraryFolder}/{showtitle} ({firstyear})') != []: # if not empty, don't overwrite files
            shutil.copy2(f'poster.jpg',f'{seriesPath}/poster{season}.jpg')
            shutil.copy2(f'backdrop.jpg',f'{seriesPath}/backdrop{season}.jpg')
            shutil.copy2('tvshow.nfo',f'{seriesPath}/tvshow{season}.nfo')
        else:
            shutil.move('tvshow.nfo',f'{seriesPath}/tvshow.nfo')
            shutil.move('backdrop.jpg',f'{seriesPath}/backdrop.jpg')
            shutil.move('poster.jpg',f'{seriesPath}/poster.jpg')
        for seasonPos in range(len(fileNameList)):
            season = firstSeason + seasonPos + skippedSeasons
            while season in skipSeasons: 
                season += 1
                skippedSeasons += 1
            if season == 0: seasonFolder = 'Specials'
            else: seasonFolder = f'Season {season}'
            shutil.move(f'{seasonFolder}',f'{seriesPath}/{seasonFolder}')
        for file in os.listdir():
            if file.startswith('season') and file.endswith('-poster.jpg'):
                shutil.move(file,f'{seriesPath}/{file}')
    else:
        if os.path.isdir(f'{fsLibraryFolder}/{showtitle} ({firstyear})') and os.listdir(f'{fsLibraryFolder}/{showtitle} ({firstyear})') != []:
            print(f'WARNING: Series folder {showtitle} ({firstyear}) contains files. Please remove them and rescan jellyfin library folder before transfering files (Failing to rescan can cause major issues).\n')
        

    if otherFiles != []:
        print('\nThe following files do not follow the correct naming format for this program and have not been processed. Please correct their naming in order to process them.\n')
        for file in otherFiles: 
            print(file)
        print()

    print(f'\n\n{showtitle} ({firstyear})\n') # print the name of the jellyfin show folder

    if not moveToJellyfin:
        if os.path.isdir(f'{fsLibraryFolder}/{showtitle} ({firstyear})') and os.listdir(f'{fsLibraryFolder}/{showtitle} ({firstyear})') != []:
            print(f'\nWARNING: Series folder {showtitle} ({firstyear}) contains files. Please remove them and rescan jellyfin library folder before transfering files (Failing to rescan can cause major issues).')

root = os.getcwd()
    
if isDocker: # correct path formatting 
    fsLibraryFolderTemp = fsLibraryFolder.rstrip('/').rstrip('\\') 
    fsLibraryPath = re.split(r'[\\/]',fsLibraryFolderTemp)
    jfLibraryFolder = f'{fsLibraryPath[-2]}/{fsLibraryPath[-1]}'
else: 
    jfLibraryFolder = fsLibraryFolder


showtitle = check_user_variables()

if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 

if playlist != '': # correct formatting if playlist exists
    playlist = f'\n\n{playlist}'

main()

# end of normal program

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------

'''
seriestitle = "Stampy's Lovely World"
author = 'Stampylonghead'
channel = 'https://www.youtube.com/user/stampylonghead'
playlist = 'https://youtube.com/playlist?list=PL1Zu9lv9TlTiCilIiI4E9ry-BDnUc91nB&si=32qzjvvby5PcfcWD'
playlistFolder = "Stampy's Lovely World (All in order)"
reverseOrder = False 
firstSeason = 1
startingEpisodeNum = 1
seasons = []
skipEpisodes = []
customYear = ''




#---------------------------------------------------------------------------------------------


showtitle = check_user_variables()

if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 

if playlist != '': # correct formatting if playlist exists
    playlist = f'\n\n{playlist}'

main()


#---------------------------------------------------------------------------------------------







#---------------------------------------------------------------------------------------------


showtitle = check_user_variables()

if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 

if playlist != '': # correct formatting if playlist exists
    playlist = f'\n\n{playlist}'

main()


#---------------------------------------------------------------------------------------------
'''




seriestitle = 'Space Engineers'
author = 'GetBrocked'
channel = 'https://www.youtube.com/@GetBrocked'
playlist = 'https://www.youtube.com/watch?v=wZ07FUVead0&list=PLSOiQqYQEf1gc7x_m12F_DZVoUaOxEnFX&pp=iAQB'
playlistFolder = 'Space Engineers 7 (Sigmarius\u29f8Prequel)'
reverseOrder = False 
firstSeason = 2
seasons = []
skipEpisodes = []
customYear = 2016



#---------------------------------------------------------------------------------------------


showtitle = check_user_variables()

if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 

if playlist != '': # correct formatting if playlist exists
    playlist = f'\n\n{playlist}'

main()


#---------------------------------------------------------------------------------------------





seriestitle = 'Space Engineers'
author = 'GetBrocked'
channel = 'https://www.youtube.com/@GetBrocked'
playlist = 'https://www.youtube.com/watch?v=wZ07FUVead0&list=PLSOiQqYQEf1gc7x_m12F_DZVoUaOxEnFX&pp=iAQB'
playlistFolder = 'Space Engineers Season 8 (Sigmarius\u29f8Prequel)'
reverseOrder = False 
firstSeason = 3
seasons = []
skipEpisodes = []
customYear = 2016



#---------------------------------------------------------------------------------------------


showtitle = check_user_variables()

if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 

if playlist != '': # correct formatting if playlist exists
    playlist = f'\n\n{playlist}'

main()


#---------------------------------------------------------------------------------------------






seriestitle = 'Space Engineers'
author = 'GetBrocked'
channel = 'https://www.youtube.com/@GetBrocked'
playlistFolder = 'Space Engineers Season 2 (Into the Fray)'
playlist = 'https://www.youtube.com/watch?v=8tZW7JTZWKc&list=PLSOiQqYQEf1gAxJENyxvrigbUfjawQLVs&pp=iAQB'
reverseOrder = False 
firstSeason = 5
seasons = []
skipEpisodes = []
customYear = 2016


#---------------------------------------------------------------------------------------------


showtitle = check_user_variables()

if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 

if playlist != '': # correct formatting if playlist exists
    playlist = f'\n\n{playlist}'

main()


#---------------------------------------------------------------------------------------------





seriestitle = 'Space Engineers'
author = 'GetBrocked'
channel = 'https://www.youtube.com/@GetBrocked'
playlist = 'https://www.youtube.com/watch?v=Bq7xYyj93eg&list=PLSOiQqYQEf1h6_vShUY38ST-XEBH6qSYb&pp=iAQB'
playlistFolder = 'Space Engineers Season 3 (Osiris)'
reverseOrder = False 
firstSeason = 6
seasons = []
skipEpisodes = []
customYear = 2016


#---------------------------------------------------------------------------------------------


showtitle = check_user_variables()

if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 

if playlist != '': # correct formatting if playlist exists
    playlist = f'\n\n{playlist}'

main()


#---------------------------------------------------------------------------------------------




seriestitle = 'Space Engineers'
author = 'GetBrocked'
channel = 'https://www.youtube.com/@GetBrocked'
playlist = 'https://www.youtube.com/watch?v=Bq7xYyj93eg&list=PLSOiQqYQEf1h6_vShUY38ST-XEBH6qSYb&pp=iAQB'
playlistFolder = 'Space Engineers Season 4 (Osiris)'
reverseOrder = False 
firstSeason = 7
seasons = []
skipEpisodes = []
customYear = 2016




#---------------------------------------------------------------------------------------------


showtitle = check_user_variables()

if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 

if playlist != '': # correct formatting if playlist exists
    playlist = f'\n\n{playlist}'

main()


#---------------------------------------------------------------------------------------------



seriestitle = 'Space Engineers'
author = 'GetBrocked'
channel = 'https://www.youtube.com/@GetBrocked'
playlist = 'https://www.youtube.com/watch?v=DxnE6UyEqkA&list=PLSOiQqYQEf1g7expr8xBre_DyMKoA7lRg&pp=iAQB'
playlistFolder = 'Space Engineers Season 5 (Osiris)'
reverseOrder = False 
firstSeason = 8
seasons = []
skipEpisodes = []
customYear = 2016




#---------------------------------------------------------------------------------------------


showtitle = check_user_variables()

if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 

if playlist != '': # correct formatting if playlist exists
    playlist = f'\n\n{playlist}'

main()


#---------------------------------------------------------------------------------------------




seriestitle = 'Space Engineers'
author = 'GetBrocked'
channel = 'https://www.youtube.com/@GetBrocked'
playlist = ''
playlistFolder = 'Space Engineers Specials'
reverseOrder = False 
firstSeason = 0
seasons = []
skipEpisodes = []
customYear = 2016



#---------------------------------------------------------------------------------------------


showtitle = check_user_variables()

if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 

if playlist != '': # correct formatting if playlist exists
    playlist = f'\n\n{playlist}'

main()


#---------------------------------------------------------------------------------------------




seriestitle = 'Space Engineers: Outlands'
author = 'GetBrocked'
channel = 'https://www.youtube.com/@GetBrocked'
playlist = 'https://www.youtube.com/watch?v=JqWK7rS8u3Q&list=PLSOiQqYQEf1hJA80Y6m1PcGeCjqLJFCjp&pp=iAQB'
playlistFolder = 'Space Engineers\uff1a Outlands  Season 1'
reverseOrder = False 
firstSeason = 1
seasons = []
skipEpisodes = []
customYear = 2021



#---------------------------------------------------------------------------------------------


showtitle = check_user_variables()

if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 

if playlist != '': # correct formatting if playlist exists
    playlist = f'\n\n{playlist}'

main()


#---------------------------------------------------------------------------------------------




seriestitle = 'Space Engineers: Outlands'
author = 'GetBrocked'
channel = 'https://www.youtube.com/@GetBrocked'
playlist = 'https://www.youtube.com/watch?v=JqWK7rS8u3Q&list=PLSOiQqYQEf1hJA80Y6m1PcGeCjqLJFCjp&pp=iAQB'
playlistFolder = 'Space Engineers\uff1a Outlands Season 2'
reverseOrder = False 
firstSeason = 2
seasons = []
skipEpisodes = []
customYear = 2021



#---------------------------------------------------------------------------------------------


showtitle = check_user_variables()

if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 

if playlist != '': # correct formatting if playlist exists
    playlist = f'\n\n{playlist}'

main()


#---------------------------------------------------------------------------------------------




seriestitle = 'Space Engineers: Outlands'
author = 'GetBrocked'
channel = 'https://www.youtube.com/@GetBrocked'
playlist = 'https://www.youtube.com/watch?v=JqWK7rS8u3Q&list=PLSOiQqYQEf1hJA80Y6m1PcGeCjqLJFCjp&pp=iAQB'
playlistFolder = 'Space Engineers\uff1a Outlands Season 3'
reverseOrder = False 
firstSeason = 3
seasons = []
skipEpisodes = []
customYear = 2021



#---------------------------------------------------------------------------------------------




seriestitle = 'Space Engineers: Outlands'
author = 'GetBrocked'
channel = 'https://www.youtube.com/@GetBrocked'
playlist = 'https://www.youtube.com/watch?v=JqWK7rS8u3Q&list=PLSOiQqYQEf1hJA80Y6m1PcGeCjqLJFCjp&pp=iAQB'
playlistFolder = 'Space Engineers\uff1a Outlands Season 4'
reverseOrder = False 
firstSeason = 4
seasons = []
skipEpisodes = []
customYear = 2021


#---------------------------------------------------------------------------------------------


showtitle = check_user_variables()

if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 

if playlist != '': # correct formatting if playlist exists
    playlist = f'\n\n{playlist}'

main()


#---------------------------------------------------------------------------------------------



seriestitle = 'Space Engineers: Outlands'
author = 'GetBrocked'
channel = 'https://www.youtube.com/@GetBrocked'
playlist = 'https://youtube.com/playlist?list=PLSOiQqYQEf1gTVDlZKRZUc3ZQXqD06hhB&si=WYe2JVn4FgzvO23u'
playlistFolder = 'Outlands Stories'
reverseOrder = True 
firstSeason = 0
seasons = []
skipEpisodes = []
customYear = 2021
orderByDate = True





#---------------------------------------------------------------------------------------------


showtitle = check_user_variables()

if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 

if playlist != '': # correct formatting if playlist exists
    playlist = f'\n\n{playlist}'

main()


#---------------------------------------------------------------------------------------------