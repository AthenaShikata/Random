import os
import shutil
from PIL import Image
from subprocess import Popen, PIPE
import re
#file = '01 - Interstellar Dreams | Beyond Kerbol #1.description'

# Variables Manually Set by User
season = '1' # must be string
showtitle = ''
author = 'Historia Civilis'
channel = 'https://www.youtube.com/c/HistoriaCivilis'
playlist = 'https://www.youtube.com/watch?v=aq4G-7v-_xI&list=PLODnBH8kenOp7y_w1CWTtSLxGgAU6BR8M'

# manually configured function
def titleExtractor(file,episode):
    titleFillerLeft = file.find('Beyond Kerbol') -3 # use these two variables to define the edges of title filler
    titleFillerRight = file.rfind('.') # set these to None if there is nothing to replace
    title = file[(file.find(' - ') + 3):(file.rfind('.'))].replace(file[titleFillerLeft:titleFillerRight],'')
    if titleFillerLeft != None and titleFillerRight != None:title=title.replace(file[titleFillerLeft:titleFillerRight],'')
    #print(file[titleFillerLeft:titleFillerRight])
    se = f'S{str(season).zfill(2)}E{str(episode).zfill(file.find(' - '))}'
    titleSE = f'{se} - {title}'
    print(title)
    return title,titleSE



#'''

def copy_and_rename(src_path, dest_path, new_name):
	# Copy the file
	shutil.copy(src_path, dest_path)

	# Rename the copied file
	new_path = f"{dest_path}/{new_name}"
	shutil.move(f"{dest_path}/{src_path}", new_path)

def get_metadata(file):
    if file.endswith('.mp4'):
        res = Popen(['ffmpeg', '-i', file, '-hide_banner'],stdout=PIPE,stderr=PIPE)
        none,meta = res.communicate()
        meta_out = meta.decode()
        #---| Take out info
        date = re.search(r'Created on:.*', meta_out)
        date = date.group()
        date = date.replace('Created on: ','')
        date = date[:-2]
        year = date[-4:]
        date = f'{year}-{date[:2]}-{date[3:5]}'
        return year,date
    if file.endswith('.mkv'):
        res = Popen(['ffmpeg', '-i', file, '-hide_banner'],stdout=PIPE,stderr=PIPE)
        none,meta = res.communicate()
        meta_out = meta.decode()
        #---| Take out info
        date = re.search(r'DATE            : .*', meta_out)
        date = date.group()
        date = date.replace('DATE            : ','').rstrip()
        year = date[0:4]
        date = f'{year}-{date[4:6]}-{date[6:]}'
        return year,date
    if file.endswith('.mpeg'):
        return year,date


def createSeason(file,firstyear,firstdate,lastdate):
    descriptionFile = open(f'{file[:file.rfind('.')]}.description','r')
    description = descriptionFile.read()
    descriptionFile.close()

    tvshownfo = f'<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n\
    <tvshow>\n\
      <plot>{author}\n{channel}\n\n{description}</plot>\n\
      <outline>{author}\n{channel}\n{description}</outline>\n\
      <lockdata>true</lockdata>\n\
      <dateadded>2025-02-20 00:00:00</dateadded>\n\
      <title>{author} - {showtitle}</title>\n\
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
      <lockdata>true</lockdata>\n\
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


def createEpisode(file,episode,firstyear):
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
        elif epfile.endswith('.webp'): pass
        elif epfile.endswith('.description'): pass
        else: raise TypeError(f'File found with unexpected extension {epfile[epfile.rfind('.'):]}\n{epfile}')
    
    #create metadata file
    descriptionFile = open(f'{file[:file.rfind('.')]}.description','r')
    description = descriptionFile.read()
    descriptionFile.close()

    episodeNFO = f'<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n\
    <episodedetails>\n\
      <plot>{author}\n{channel}\n\n{description}</plot>\n\
      <lockdata>true</lockdata>\n\
      <dateadded>2025-02-20 00:00:00</dateadded>\n\
      <title>{title}</title>\n\
      <director>{author}</director>\n\
      <year>{year}</year>\n\
      <genre>youtube</youtube>\n\
      <art>\n\
        <poster>/media/youtube/{author} - {showtitle} ({firstyear})/Season {season}/{titleSE}-thumb.jpg</poster>\n\
      </art>\n\
      <actor>\n\
        <name>{author}</name>\n\
        <type>Actor</type>\n\
      </actor>\n\
      <showtitle>{author} - {showtitle}</showtitle>\n\
      <episode>{episode}</episode>\n\
      <season>{season}</season>\n\
      <aired>{date}</aired>\n\
    </episodedetails>'
    '''
      <fileinfo>\n\
        <streamdetails>\n\
        <video>\n\
          <codec>{videocodec}</codec>\n\
          <micodec>{videocodec}</micodec>\n\
          <bitrate>{videobitrate}</bitrate>\n\
          <width>{videowidth}</width>\n\
          <height>{videoheight}</height>\n\
          <aspect>{videoaspectratio}</aspect>\n\
          <aspectratio>{videoaspectratio}</aspectratio>\n\
          <framerate>{videoframerate}</framerate>\n\
          <language>eng</language>\n\
          <scantype>{videoscantype}</scantype>\n\
          <default>True</default>\n\
          <forced>False</forced>\n\
          <duration>{videodurationminutes}</duration>\n\
          <durationinseconds>{videodurationseconds}</durationinseconds>\n\
        </video>\n\
        <audio>\n\
          <codec>{audiocodec}</codec>\n\
          <micodec>{audiocodec}</micodec>\n\
          <bitrate>{audiobitrate}</bitrate>\n\
          <language>eng</language>\n\
          <scantype>progressive</scantype>\n\
          <channels>{channels}</channels>\n\
          <samplingrate>{samplingrate}</samplingrate>\n\
          <default>True</default>\n\
          <forced>False</forced>\n\
        </audio>\n\
        <subtitle>\n\
          <codec>{subtitlecodec}</codec>\n\
          <micodec>{subtitlecodec}</micodec>\n\
          <width>{subtitlewidth}</width>\n\
          <height>{subtitleheight}</height>\n\
          <language>eng</language>\n\
          <scantype>progressive</scantype>\n\
          <default>False</default>\n\
          <forced>False</forced>\n\
        </subtitle>\n\
        </streamdetails>\n\
      </fileinfo>\n\
    </episodedetails>
    '''

    episodeNFOfile = open(f'Season {season}/{titleSE}.nfo','w')
    episodeNFOfile.write(episodeNFO)
    episodeNFOfile.close()
    

def main():    
    files = sorted(os.listdir())
    startingNum = None #check for the first filenum of the season
    epNum = None
    episode = 1
    firstyear = None
    firstdate = None
    lastdate = None
    years = []
    dates = []
    try : os.mkdir(os.path.join(os.getcwd(),f'Season {season}'))
    except : pass
    for file in files: #convert webp images to jpg, but not if it was already converted and get first and last dates
        if file.endswith('.webp'):
            if os.path.isfile(f"{file[:-5]}.jpg") == False:
                thumbnail = Image.open(file).convert("RGB")
                thumbnail.save(f"{file[:-5]}.jpg", "jpeg")
        if os.path.isfile(file) and file.endswith('.py') == False and file.endswith('.nfo') == False and (file.endswith('.mkv') or file.endswith('.mp4') or file.endswith('.mpeg')):
            fileNum = int(file[:file.find(' - ')])
            if fileNum != 0:
                yeartemp, datetemp = get_metadata(file)
                years.append(yeartemp)
                dates.append(datetemp)
    yearssort = sorted(years)
    datessort = sorted(dates)
    firstyear = yearssort[0]
    firstdate = datessort[0]
    lastdate = datessort[-1]
    print(f'{author} - {showtitle} ({firstyear})')
    for file in files: #iterate through files
        if os.path.isfile(file) and file.endswith('.py') == False and file.endswith('.nfo') == False:
            fileNum = int(file[:file.find(' - ')])
            if fileNum != epNum: #iterate through episodes, skip files for same episode
                epNum = fileNum
                if fileNum != 0 and startingNum == None: startingNum = fileNum -1 #define the first episode in a season's filenum -1 (basically the offset of episodes from filenums)
                if fileNum != 0: #files of an episode, description, subtitles, video, thumbnail
                    if startingNum + episode != fileNum: raise TypeError(f'ERROR E{episode}F{fileNum}\n{file}')
                    print(file)
                    createEpisode(file,episode,firstyear)
                    episode += 1
    playlistfile = files[0]
    createSeason(f'{playlistfile[:playlistfile.rfind('.')]}.description',firstyear,firstdate,lastdate) # playlist description
    print(f'{author} - {showtitle} ({firstyear})')
        

        
main()

#'''