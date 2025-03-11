import os
import shutil
from PIL import Image
from subprocess import Popen, PIPE
import re
import xml.etree.ElementTree as ET
from datetime import datetime
import json

# HOW TO
# NOTE: Must use yt-dlp -o "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s"
# Set manual configurations below for name formatting and metadata
# If files in the downloaded playlists are out of order and must be changed/downloaded manually, change their playlist id to be one less than the position they should have, and add letters in alphabetical order (abc) to correct the order (ie 53 - [53], 53a - [54], 54 - [55])


# Variables Manually Set by User

downloadFolder = 'youtubedownload'
downloadFolder = 'test'

jellyfinMediaFolder = '/Wizard/Docker/jellyfin/media'
jellyfinLibraryFolder = 'youtube'

startingEpisodeNum = 1 # First episode number in season
reverseOrder = True # Boolean: Set True if the playlist is in the wrong order

firstSeason = 1 # starting season
seasons = [1,72,135] # first episode of each season (dont use playlist number), leave blank for all one season

seriestitle = '' # cannot contain /
author = 'Historia Civilis' # cannot contain /
playlistFolder = 'Chronological Order'

seriestitle = 'DSMP & MCYT Animation'
author = 'SAD-ist'
playlistFolder = 'Dream SMP\u29f8MCYT Animation'

seriestitle = 'Attack of the B Team'
author = 'iBallisticSquid'
playlistFolder = 'iballisticsquid attack of the b team'

seriestitle = 'Crazy Craft 3.0'
author = 'ThnxCya'
playlistFolder = 'Crazy Craft 3.0'
channel = 'https://www.youtube.com/user/ThnxCya'
playlist = 'https://www.youtube.com/watch?v=2lTwWhNKZVA&list=PLMtyT7aZ3NAsQ4s1CqUNPD0fmNWV8swNc&pp=iAQB'
reverseOrder = True # Boolean: Set True if the playlist is in the wrong order
#"""
seriestitle = 'Diamond Dimensions'
author = 'DanTDM'
playlistFolder = 'Diamond Dimensions DanTDM Full Playlist'
channel = 'https://www.youtube.com/@DanTDM'
playlist = 'https://youtube.com/playlist?list=PLe_XjukLHxCfmk_z2YxIJR_4d6qhQJGGx&si=pOtZo0QAYMobBrhT'
reverseOrder = False # Boolean: Set True if the playlist is in the wrong order
#"""






def copy_and_rename(src_path, dest_path, new_name):
	shutil.copy(src_path, dest_path)
	# Rename the copied file
	shutil.move(f"{dest_path}/{src_path}", f"{dest_path}/{new_name}")

def get_metadata(file):
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
    
def get_dates(files):
    years = []
    dates = []
    epNum = 0
    for file in files: # get first and last dates
        playlistID = file.find(' - ')
        if file.endswith('.mkv') or file.endswith('.mp4'): #gets a list of all the years these videos were released in an sorts
            fileNum = file[:playlistID]
            if fileNum != epNum: #iterate through episodes, skip files for same episode
                epNum = fileNum
                if fileNum != 0:
                    yeartemp, datetemp = get_metadata(file)
                    years.append(yeartemp)
                    dates.append(datetemp)
    firstyear = sorted(years)[0]
    firstdate = sorted(dates)[0]
    lastdate = sorted(dates)[-1]

    return firstyear,firstdate,lastdate


def createSeason(filename,season,showfirstyear,firstyear,firstdate,lastdate,showtitle):
    descriptionFile = open(f'{filename}.description','r')
    description = descriptionFile.read()
    descriptionFile.close()

    seasonnfo = ET.Element('season')
    ET.SubElement(seasonnfo,'plot').text = (f'{author}\n{channel}\n{playlist}\n\n{description}').rstrip('\n').rstrip(' ')
    ET.SubElement(seasonnfo,'outline').text = (f'{author}\n{channel}\n{description}').rstrip('\n').rstrip(' ')
    ET.SubElement(seasonnfo,'lockdata').text = f'true'  
    ET.SubElement(seasonnfo,'dateadded').text = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    ET.SubElement(seasonnfo,'title').text = f'{showtitle}'
    ET.SubElement(seasonnfo,'year').text = f'{firstyear}'
    ET.SubElement(seasonnfo,'premiered').text = f'{firstdate}'
    ET.SubElement(seasonnfo,'releasedata').text = f'{firstdate}'
    ET.SubElement(seasonnfo,'enddate').text = f'{lastdate}'
    ET.SubElement(seasonnfo,'genre').text = f'youtube'
    ET.SubElement(seasonnfo,'tag').text = f'youtube'
    art = ET.SubElement(seasonnfo, 'art')
    ET.SubElement(art,'poster').text = f'/media/youtube/{showtitle} ({showfirstyear})/season{str(season).zfill(2)}-poster.jpg'
    actor = ET.SubElement(seasonnfo,'actor')
    ET.SubElement(actor,'name').text = f'{author}'
    ET.SubElement(actor,'type').text = f'Actor'
    ET.SubElement(seasonnfo,'seasonnumber').text = f'{season}'

    tree = ET.ElementTree(seasonnfo)
    ET.indent(tree, space="  ", level=0)
    out = open(f"Season {season}/seasonnfo.nfo", 'wb')
    out.write(b'<?xml version="1.0" encoding="UTF-8" standalone = "yes"?>\n')
    tree.write(out, encoding = 'UTF-8', xml_declaration = False)
    out.close()

    if os.path.exists(f'season{str(season).zfill(2)}-poster.jpg'):
        os.remove(f'season{str(season).zfill(2)}-poster.jpg')
    shutil.copy2(f'{filename}.jpg', f'season{str(season).zfill(2)}-poster.jpg')

def createShow(filename,firstyear,firstdate,lastdate,showtitle):
    descriptionFile = open(f'{filename}.description','r')
    description = descriptionFile.read()
    descriptionFile.close()

    tvshow = ET.Element('tvshow')
    ET.SubElement(tvshow,'plot').text = (f'{author}\n{channel}\n\n{description}').rstrip('\n').rstrip(' ')
    ET.SubElement(tvshow,'outline').text = (f'{author}\n{channel}\n{description}').rstrip('\n').rstrip(' ')
    ET.SubElement(tvshow,'lockdata').text = f'true'
    ET.SubElement(tvshow,'dateadded').text = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    ET.SubElement(tvshow,'title').text = f'{showtitle}'
    ET.SubElement(tvshow,'year').text = f'{firstyear}'
    ET.SubElement(tvshow,'premiered').text = f'{firstdate}'
    ET.SubElement(tvshow,'releasedata').text = f'{firstdate}'
    ET.SubElement(tvshow,'enddate').text = f'{lastdate}'
    ET.SubElement(tvshow,'genre').text = f'youtube'
    ET.SubElement(tvshow,'tag').text = f'youtube'
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

def createEpisode(title,titleSE,season,showtitle,year,firstyear,episode,date):
    descriptionFile = open(f'{title}.description','r')
    description = descriptionFile.read()
    descriptionFile.close()

    cleanTitle = title[title.find('] - ')+4:]
    videoID = title[title.find(' - [')+4:title.find('] - ')]

    episodenfo = ET.Element('episodedetails')
    ET.SubElement(episodenfo,'plot').text = (f'{author}\n{channel}\n\nhttps://www.youtube.com/watch?v={videoID} \n\n{description}').rstrip('\n').rstrip(' ')
    ET.SubElement(episodenfo,'outline').text = (f'{author}\n{channel}\n\nhttps://www.youtube.com/watch?v={videoID} \n\n{description}').rstrip('\n').rstrip(' ')
    ET.SubElement(episodenfo,'lockdata').text = f'true'  
    ET.SubElement(episodenfo,'dateadded').text = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    ET.SubElement(episodenfo,'title').text = f'{cleanTitle}'
    ET.SubElement(episodenfo,'director').text = f'{author}'
    ET.SubElement(episodenfo,'year').text = f'{year}'
    ET.SubElement(episodenfo,'sorttitle') = f'{titleSE}'
    ET.SubElement(episodenfo,'genre').text = f'youtube'
    ET.SubElement(episodenfo,'tag').text = f'youtube'
    ET.SubElement(episodenfo,'youtubemetadataid').text = f'{videoID}'
    art = ET.SubElement(episodenfo, 'art')
    ET.SubElement(art,'poster').text = f'/media/youtube/{showtitle} ({firstyear})//Season {season}/{titleSE}-thumb.jpg'
    actor = ET.SubElement(episodenfo,'actor')
    ET.SubElement(actor,'name').text = f'{author}'
    ET.SubElement(actor,'type').text = f'Actor'
    ET.SubElement(episodenfo,'showtitle').text = f'{showtitle}'
    ET.SubElement(episodenfo,'episode').text = f'{episode}'
    ET.SubElement(episodenfo,'season').text = f'{season}'
    ET.SubElement(episodenfo,'aired').text = f'{date}'

    tree = ET.ElementTree(episodenfo)
    ET.indent(tree, space="  ", level=0)
    out = open(f"Season {season}/{titleSE}.nfo", 'wb')
    out.write(b'<?xml version="1.0" encoding="UTF-8" standalone = "yes"?>\n')
    tree.write(out, encoding = 'UTF-8', xml_declaration = False)
    out.close()


def main():
    os.chdir(f'{root}/{downloadFolder}/{playlistFolder}')

    if seriestitle == '': #formatting to get correct spacing for showtitle
        showtitle = f'{author}'
    else: 
        showtitle = f'{author} - {seriestitle}'


    for seasonPos in range(len(seasons)): # create season folders and remove previously created season folders
        season = firstSeason + seasonPos
        if os.path.exists(os.path.join(os.getcwd(),f'Season {season}')):
            shutil.rmtree(os.path.join(os.getcwd(),f'Season {season}'))
        os.mkdir(os.path.join(os.getcwd(),f'Season {season}'))
        
        
    files = [f for f in sorted(os.listdir(),reverse=reverseOrder) if re.match(r'^\d+', f) and ' - ' in f] # get all files and filter out unwanted files (ie everything that wasn't downloaded by yt-dlp)
    

    seasonPos = 0  # Start at the first index of list1
    nextSeason = seasons[seasonPos]  # Initialize with the first value in list1

    episodeNum = startingEpisodeNum
    seasonIndex = []
    for i in range(len(seasons)):
        seasonIndex.append([])

    for file in files:
        if file.endswith('.webp'): # convert webp images to jpg, but not if it was already converted
            if os.path.isfile(f"{file[:-5]}.jpg") == False:
                thumbnail = Image.open(file).convert("RGB")
                thumbnail.save(f"{file[:-5]}.jpg", "jpeg")
        if file.endswith('.mp4') or file.endswith('mkv'): # organize every video file by season
            season = firstSeason + seasonPos -1
            while seasonPos < len(seasons) - 1 and episodeNum >= nextSeason:
                seasonPos += 1
                nextSeason = seasons[seasonPos]
            if episodeNum == seasons[seasonPos-1]: season = season +1
            if episodeNum < nextSeason:
                seasonIndex[season-1].append(file)
            elif episodeNum >= seasons[-1]:
                season = firstSeason + seasonPos
                seasonIndex[season-1].append(file)
            episodeNum +=1  

    seasonFirstYears = []
    seasonFirstDates = []
    seasonLastDates = []

    for seasonPos in range(len(seasons)): # organize the date metadata of every video file by season
        season = firstSeason + seasonPos
        print(f'Season {season}')
        seasonFiles = seasonIndex[seasonPos]
        seasonFirstYear,seasonFirstDate,seasonLastDate = get_dates(seasonFiles)

        seasonFirstYears.append(seasonFirstYear)
        seasonFirstDates.append(seasonFirstDate)
        seasonLastDates.append(seasonLastDate)

    for seasonPos in range(len(seasons)): # get total show metadata
        firstyear = min(seasonFirstYears)
        firstdate = min(seasonFirstDates)
        lastdate = max(seasonLastDates)

    for seasonPos in range(len(seasons)): # create season.nfo files for all seasons
        season = firstSeason + seasonPos
        madeSeason = False
        for file in files:
            if (file[:file.find(' - ')]).strip('0') == '' and madeSeason == False: 
                fileName = file[:file.rfind('.')]
                createSeason(fileName,season,firstyear,seasonFirstYears[seasonPos],seasonFirstDates[seasonPos],seasonLastDates[seasonPos],showtitle) # playlist description
                madeSeason = True

    for file in files: # create show tvshow.nfo file
        madeShow = False
        if (file[:file.find(' - ')]).strip('0') == '' and madeShow == False: 
            fileName = file[:file.rfind('.')]
            createShow(fileName,firstyear,firstdate,lastdate,showtitle) # show description
            madeShow = True

    print(f'\n{showtitle} ({firstyear})\n') # print the name of the jellyfin show folder


    fileNameList = []
    for seasonPos in range(len(seasonIndex)): # organize all episodes by removing extensions and organizing by season
        fileNameList.append([])
        for file in seasonIndex[seasonPos]: # get all the episode filenames into a list (excluding extensions)
            if (file[:file.find(' - ')]).strip('0') != '': 
                if file.endswith('.vtt'): 
                    fileName = file[:file.rfind('.')]
                    fileName = fileName[:fileName.rfind('.')]
                else: 
                    fileName = file[:file.rfind('.')]
                fileNameList[seasonPos].append(fileName)
    
    for seasonPos in range(len(fileNameList)): # put all episode filenames in order and remove duplicates
        fileNameList[seasonPos] = sorted(set(fileNameList[seasonPos]),reverse=reverseOrder)
        

    episodeNum = startingEpisodeNum
    seasonPos = 0

    for seasonPos in range(len(fileNameList)): # copy and rename all files for each episode to season folder and make .nfo files for each episode
        for title in fileNameList[seasonPos]:
            season = firstSeason + seasonPos

            titleSE = f'S{str(season).zfill(2)}E{str(episodeNum).zfill(sum(c.isdigit() for c in title[:title.find(' - ')]))}{title[title.find(' - '):]}' # add season and episode to the title (with enough padded zeros) and remove playlist id. also removes any letters from playlist id
            print(title)
            print(titleSE)
            print()

            episodeFiles = [episodeFile for episodeFile in os.listdir() if episodeFile.startswith(title)]  
            for epfile in episodeFiles:
                if epfile.endswith('.mkv'): 
                    copy_and_rename(epfile,f'{os.getcwd()}/Season {season}',f'{titleSE}.mkv') #move and rename mkv video
                    year,date=get_metadata(epfile)
                    createEpisode(title,titleSE,season,showtitle,year,firstyear,episodeNum,date) # create episode metadata
                elif epfile.endswith('.mp4'): 
                    copy_and_rename(epfile,f'{os.getcwd()}/Season {season}',f'{titleSE}.mp4') #move and rename mp4 video
                    year,date=get_metadata(epfile)
                    createEpisode(title,titleSE,season,showtitle,year,firstyear,episodeNum,date) # create episode metadata
                elif epfile.endswith('.jpg'): copy_and_rename(epfile,f'{os.getcwd()}/Season {season}',f'{titleSE}-thumb.jpg') #move and rename thumbnail
                elif epfile.endswith('.vtt'): copy_and_rename(epfile,f'{os.getcwd()}/Season {season}',f'{titleSE}{epfile[epfile.rfind('.',0,-4):]}') #move and rename subtitles'''
            episodeNum +=1    


    print(f'\n{showtitle} ({firstyear})\n') # print the name of the jellyfin show folder

root = os.getcwd()
if seasons == []: # if seasons left blank, start at episode one
    seasons = [1] 
main()