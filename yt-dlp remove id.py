import os
from difflib import SequenceMatcher

ratioThreshold = .87 # configurable value between 0 and 1, comment out the renaming try statement and determine where your threshold lies
if (0 <= ratioThreshold <= 1) == False: raise ValueError(f'Variable ratioThreshold must be between 0 and 1, cannot be {ratioThreshold}')

root = os.getcwd()
downloadFolder = 'youtubedownload'
downloadFolder = 'test'

nameUpdate = open('newnames.txt','r')
cache = nameUpdate.read()
changesList = cache.split("\n\n")
nameUpdate.close()

def unUnicode(string):
    # \/:*?"  \u29f9 \u29f8 \uff1a \uff0a \uff1f \uff02
    string = str(string)
    string.replace('\u29f9','\\').replace('\u29f8','/').replace('\uff1a',':').replace('\uff0a','*').replace('\uff1f','?').replace('\uff02','"')
    return string

def enUnicode(string):
    string = str(string)
    # \/:*?"  \u29f9 \u29f8 \uff1a \uff0a \uff1f \uff02
    string.replace('\\','\u29f9').replace('/','\u29f8').replace(':','\uff1a').replace('*','\uff0a').replace('?','\uff1f').replace('"','\uff02')
    return string


for playlist in os.listdir(downloadFolder):
    os.chdir(f'{root}/{downloadFolder}/{playlist.replace('/','-')}')
    playlist = unUnicode(playlist)

    for change in changesList:
        changeTest = False
        videoTest = False

        if change.startswith(f'{playlist}/') or (playlist.startswith('Dream SMP') and change.startswith('Dream SMP')):
            if change.startswith('Dream SMP'): cleanChange = change.replace('Dream SMP/MCYT Animation/','')
            else: cleanChange = change.replace(f'{playlist}/','')
            #print(cleanChange)
            oldName = cleanChange.split('\n')[0].strip()
            newName = cleanChange.split('\n')[1].strip()
            if oldName.endswith('.vtt'): 
                oldNameClean = oldName[:oldName.rfind('.')]
                oldNameClean = oldNameClean[:oldNameClean.rfind('.')]
            else: 
                oldNameClean = oldName[:oldName.rfind('.')]
            videoID = newName[newName.find('['):newName.find(']')+1]

            for file in os.listdir():
                if file.find(videoID) != -1:
                    filename = file.replace(f'{videoID} - ','')
                    print(videoID,filename)
                    os.rename(file,filename)
            #print()
            #print()

