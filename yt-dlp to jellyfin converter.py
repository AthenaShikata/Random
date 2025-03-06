import os
import shutil
from PIL import Image
from subprocess import Popen, PIPE
import re
import xml.etree.ElementTree as ET

# HOW TO
# NOTE: Must use yt-dlp -o "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s"
# Set manual configurations below for name formatting and metadata
# Navigate current working directory to each playlist folder, then run this script
# In the playlist folder, a tvshow.nof file, a backdrop.jpg file, and a new Season 
#   folder will appear with a copy of all the downloaded files formatted for use in Jellyfin. 
# The last line of output from the script is the name of the parent folder for these
#   new files. In the jellyfin library folder, create a new folder with this name and 
#   move these files into it. 
# If you wish to have multiple seasons of the same show, use the earliest year in the 
#   library folder name and manually add the earliest and latest dates to tvshow.nfo for
#   the releasedate and enddate respectively. 


# Variables Manually Set by User
season = '1' # must be string
seriestitle = 'DSMP & MCYT Animation' # cannot contain /
author = 'SAD-ist' # cannot contain /
channel = 'https://www.youtube.com/@SAD_istfied'
playlist = 'https://youtube.com/playlist?list=PLdbl7RdQ9YJrldoenI9nKPi5lwUegmz7I&si=h_uSr3lU67m7Qtvd'

reverseOrder = False # set true if the playlist is in the wrong order

# Manually Configured Function
def titleExtractor(file,episode):
    fileNum = int(file[:file.find(' - ')])
    #001 - \uff02PUNCH WOOD MAN!\uff02 \uff5c Diamond Dimensions Modded Survival #1 \uff5c Minecraft.mkv

    #title filler in center (use provided ''' to block out whichever is not in use)
    '''
    titleFillerLeft = file.find('Beyond Kerbol') -3 # use these two variables to define the edges of title filler
    titleFillerRight = file.rfind('.') # set these to None if there is nothing to replace
    title = file[(file.find(' - ') + 3):(file.rfind('.'))].replace(file[titleFillerLeft:titleFillerRight],'')
    if titleFillerLeft != None and titleFillerRight != None:title=title.replace(file[titleFillerLeft:titleFillerRight],'')
    #print(file[titleFillerLeft:titleFillerRight])

    '''

    # title in center (use provided ''' to block out whichever is not in use) (define special cases with if statements)
    #'''
    if fileNum == 1: title = 'Dream SMP War - DSMP'
    elif fileNum == 2: title = 'The Fall - DSMP'
    elif fileNum == 3: title = 'Dawn of 16th - DSMP'
    elif fileNum == 4: title = 'Hog Hunt - DSMP'
    elif fileNum == 5: title = 'Ozymandias - DSMP'
    elif fileNum == 6: title = 'Final Waltz - DSMP'
    elif fileNum == 7: title = 'Dream SMP Bloopers - DSMP'
    elif fileNum == 8: title = 'Dre SMP - DSMP'
    elif fileNum == 9: title = 'Dream vs. Technoblade'
    elif fileNum == 10: title = "Sunsprite's Eulogy - Passerine"
    elif fileNum == 11: title = "Who's Who? - Dream Manhunt"
    #'''

    if title.find('/') == True: raise ValueError(f'Show Title {title} cannot contain / characters')

    se = f'S{str(season).zfill(2)}E{str(episode).zfill(file.find(' - '))}'
    titleSE = f'{se} - {title}'
    print(title)
    return title,titleSE



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
    

def createSeason(file,firstyear,firstdate,lastdate,showtitle):
    descriptionFile = open(f'{file[:file.rfind('.')]}.description','r')
    description = descriptionFile.read()
    descriptionFile.close()

    tvshownfo = f'<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n\
    <tvshow>\n\
      <plot>{author}\n{channel}\n\n{description}</plot>\n\
      <outline>{author}\n{channel}\n{description}</outline>\n\
      <lockdata>false</lockdata>\n\
      <title>{showtitle}</title>\n\
      <year>{firstyear}</year>\n\
      <premiered>{firstdate}</premiered>\n\
      <releasedate>{firstdate}/releasedate>\n\
      <enddate>{lastdate}</enddate>\n\
      <genre>youtube</genre>\n\
      <tag>youtube</tag>\n\
      <actor>\n\
        <name>{author}</name>\n\
        <type>Actor</type>\n\
      </actor>\n\
      <season>-1</season>\n\
      <episode>-1</episode>\n\
      <status>Ended</status>\n\
    </tvshow>'
        
    seasonnfo = f'<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n\
    <season>\n\
      <plot>{author}\n{channel}\n{playlist}\n\n{description}</plot>\n\
      <outline>{author}\n{channel}\n{description}</outline>\n\
      <lockdata>false</lockdata>\n\
      <dateadded>2025-02-20 00:00:00</dateadded>\n\
      <title>Season {season}</title>\n\
      <year>{firstyear}</year>\n\
      <premiered>{firstdate}</premiered>\n\
      <releasedate>{firstdate}</releasedate>\n\
      <actor>\n\
        <name>{author}</name>\n\
        <type>Actor</type>\n\
      </actor>\n\
      <seasonnumber>{season}</seasonnumber>'
    
    tvshowNFOfile = open('tvshow.nfo','w')
    tvshowNFOfile.write(tvshownfo)
    tvshowNFOfile.close()

    seasonNFOfile = open(f'Season {season}/season.nfo','w')
    seasonNFOfile.write(seasonnfo)
    seasonNFOfile.close()

    shutil.copy(f'{file[:file.rfind('.')]}.jpg', 'backdrop.jpg')

def createEpisode(file,episode,firstyear,showtitle):
    year = 0
    date = 0
    # make the title
    title,titleSE = titleExtractor(file,episode)

    # organize the files
    episodeFiles = [entry for entry in os.listdir('.') if entry.startswith(file[:file.find(' - ')]) and os.path.isfile(entry)]

    for epfile in episodeFiles:
        if epfile.endswith('.mkv'): 
            copy_and_rename(epfile,f'{os.getcwd()}/Season {season}',f'{titleSE}.mkv') #move and rename mkv video
            year,date=get_metadata(f'{file[:file.rfind('.')]}.mkv')
        elif epfile.endswith('.mp4'): 
            copy_and_rename(epfile,f'{os.getcwd()}/Season {season}',f'{titleSE}.mp4') #move and rename mp4 video
            year,date=get_metadata(f'{file[:file.rfind('.')]}.mp4')
        elif epfile.endswith('.jpg'): copy_and_rename(epfile,f'{os.getcwd()}/Season {season}',f'{titleSE}-thumb.jpg') #move and rename thumbnail
        elif epfile.endswith('.vtt'): copy_and_rename(epfile,f'{os.getcwd()}/Season {season}',f'{titleSE}{epfile[epfile.rfind('.',0,-4):]}') #move and rename subtitles
        elif epfile.endswith('.webp'): pass #these files are expected, but handled elsewhere
        elif epfile.endswith('.description'): pass #these files are expected, but handled elsewhere
        else: raise TypeError(f'File found with unexpected extension {epfile[epfile.rfind('.'):]}\n{epfile}')
    
    #create metadata file
    '''descriptionFile = open(f'{file[:file.rfind('.')]}.description','r')
    description = descriptionFile.read()
    descriptionFile.close()

    episodeNFO = f'<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n\
    <episodedetails>\n\
      <plot>{author}\n{channel}\n\n{description}</plot>\n\
      <lockdata>false</lockdata>\n\
      <dateadded>2025-02-20 00:00:00</dateadded>\n\
      <title>{title}</title>\n\
      <director>{author}</director>\n\
      <year>{year}</year>\n\
      <genre>youtube</youtube>\n\
      <art>\n\
        <poster>/media/youtube/{showtitle} ({firstyear})/Season {season}/{titleSE}-thumb.jpg</poster>\n\
      </art>\n\
      <actor>\n\
        <name>{author}</name>\n\
        <type>Actor</type>\n\
      </actor>\n\
      <showtitle>{showtitle}</showtitle>\n\
      <episode>{episode}</episode>\n\
      <season>{season}</season>\n\
      <aired>{date}</aired>\n\
    </episodedetails>'

    episodeNFOfile = open(f'Season {season}/{titleSE}.nfo','w')
    episodeNFOfile.write(episodeNFO)
    episodeNFOfile.close()'''
    

def main():
    if seriestitle == '': #formatting to get correct spacing for showtitle
        showtitle = f'{author}'
    else:
        showtitle = f'{author} - {seriestitle}'
    try : os.mkdir(os.path.join(os.getcwd(),f'Season {season}'))
    except : pass
    if showtitle.find('/') == True: raise ValueError(f'Show Title {showtitle} cannot contain / characters')

    files = [f for f in sorted(os.listdir()) if re.match(r'^\d+', f) and ' - ' in f] # get all files and filter out unwanted files (ie everything that wasn't downloaded by yt-dlp)
    fileNumList = []
    for file in files: 
        if int(file[:file.find(' - ')]) != 0: fileNumList.append(int(file[:file.find(' - ')]))
    fileNumList = sorted(set(fileNumList),reverse=reverseOrder)

    startingNum = None #check for the first filenum of the season
    epNum = None
    episode = 0
    firstyear = None
    firstdate = None
    lastdate = None
    years = []
    dates = []
    
    for file in files: #convert webp images to jpg, but not if it was already converted and get first and last dates
        if file.endswith('.webp'):
            if os.path.isfile(f"{file[:-5]}.jpg") == False:
                thumbnail = Image.open(file).convert("RGB")
                thumbnail.save(f"{file[:-5]}.jpg", "jpeg")
        if file.endswith('.mkv') or file.endswith('.mp4'): #gets a list of all the years these videos were released in an sorts
            fileNum = int(file[:file.find(' - ')])
            if fileNum != epNum: #iterate through episodes, skip files for same episode
                epNum = fileNum
                if fileNum != 0:
                    yeartemp, datetemp = get_metadata(file)
                    years.append(yeartemp)
                    dates.append(datetemp)
    firstyear = sorted(years)[0]
    firstdate = sorted(dates)[0]
    lastdate = sorted(dates)[-1]
    print(f'{showtitle} ({firstyear})')

    for file in files: #iterate through files
        fileNum = int(file[:file.find(' - ')])
        if fileNum != 0 and fileNum != epNum: #iterate through episodes, skip files for same episode and 00 files
            epNum = fileNum
            if reverseOrder: episode = fileNumList[0] +1 - fileNum
            else: episode = fileNum - fileNumList[0] +1
            print(file)
            print(episode)
            createEpisode(file,episode,firstyear,showtitle) #files of an episode, description, subtitles, video, thumbnail

    #createSeason(f'{files[0][:files[0].rfind('.')]}.description',firstyear,firstdate,lastdate,showtitle) # playlist description
    print(f'{showtitle} ({firstyear})')
        

        
main()