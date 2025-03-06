import os
from difflib import SequenceMatcher

ratioThreshold = .87 # configurable value between 0 and 1, comment out the renaming try statement and determine where your threshold lies
if (0 <= ratioThreshold <= 1) == False: raise ValueError(f'Variable ratioThreshold must be between 0 and 1, cannot be {ratioThreshold}')

root = os.getcwd()
downloadFolder = 'youtubedownload'
#downloadFolder = 'test'

nameUpdate = open(f'{root}/newnames.txt','r')
cache = nameUpdate.read()
cache = cache.rstrip('\n')
changesList = cache.split("\n\n")
nameUpdate.close()

nameUpdate = open(f'{root}/archive.txt','r')
cache = nameUpdate.read()
idSourceList = cache.split("\n")
nameUpdate.close()

def unUnicode(string):
    # \/:*?"  \u29f9 \u29f8 \uff1a \uff0a \uff1f \uff02
    string = str(string)
    string.replace('\u29f9','\\').replace('\u29f8','/').replace('\uff1a',':').replace('\uff0a','*').replace('\uff1f','?').replace('\uff02','"')
    return string

for playlist in sorted(os.listdir(f'{root}/{downloadFolder}')):
    origPlaylist = playlist
    os.chdir(f'{root}/{downloadFolder}/{playlist}')

    emptyTest = True
    for file in os.listdir(): 
        if os.path.isfile(file) == True: emptyTest = False
    if emptyTest == True: continue
    
    playlist = unUnicode(playlist)
    print(playlist)

    changePlaylistList = []
    changePlaylistListSimilarity = []

    for line in idSourceList:
        id = line.replace(f'youtube ','')
        videoID = f'[{id}]'
        for change in changesList:
            if change.find(id) != -1:
                newNameSplit = change.split('\n')[1].strip()
                changePlaylist = newNameSplit[:newNameSplit.rfind('/',0,newNameSplit.find(id))]
                newName = newNameSplit[newNameSplit.rfind('/',0,newNameSplit.find(id))+1:]
                
                similarityRatioPlaylist = SequenceMatcher(None, changePlaylist, playlist).ratio()
                if similarityRatioPlaylist >= ratioThreshold:
                    changePlaylistList.append(changePlaylist)
                    changePlaylistListSimilarity.append(similarityRatioPlaylist)
                    #print(changePlaylist)
                    #print(similarityRatioPlaylist)
    #print(changePlaylistListSimilarity)
    bestPlaylistID = changePlaylistListSimilarity.index(max(changePlaylistListSimilarity))
    bestPlaylist = changePlaylistList[bestPlaylistID]
    print(bestPlaylist)
    print(max(changePlaylistListSimilarity))
    print()

    for change in changesList:
        if change.startswith(f'{bestPlaylist}/'):
            changeTest = False
            videoTest = False
            cleanChange = change.replace(f'{bestPlaylist}/','')
            #print(cleanChange)
            oldName = cleanChange.split('\n')[0].strip()
            newName = cleanChange.split('\n')[1].strip()
            if oldName.endswith('.vtt'): 
                oldNameClean = oldName[:oldName.rfind('.')]
                oldNameClean = oldNameClean[:oldNameClean.rfind('.')]
            else: 
                oldNameClean = oldName[:oldName.rfind('.')]
            videoID = newName[newName.find('['):newName.find(']')+1]

            for file in sorted(os.listdir()):
                if file.endswith('.mp4') or file.endswith('.mkv'): videoTest = True
                if file.startswith(cleanChange[:5]):
                    changeTest = True
                    if file.find(videoID) == -1:
                        if file.endswith('.vtt'): 
                            filename = file[:file.rfind('.')]
                            filename = filename[:filename.rfind('.')]
                        else:
                            filename = file[:file.rfind('.')]
                        similarityRatio = SequenceMatcher(None, filename, oldNameClean).ratio()
                        if similarityRatio >= ratioThreshold:
                            newFile = f'{file[:file.find(' - ')]} - {videoID}{file[file.find(' - '):]}'
                            #print(newFile)

                            # renaming try statement
                            #'''
                            try: os.rename(file,newFile) 
                            except FileNotFoundError: raise FileNotFoundError(f'FileNotFoundError: The system cannot find the path specified: "{root}/{downloadFolder}/{bestPlaylist}/{file}"')
                            except: raise
                            #'''

                        #print()
            if changeTest == False: print(f'FileNotFoundError: The system cannot find any files for the change \n{change}\n')
            if videoTest == False: print(f'FileNotFoundError: The system cannot find any video files for the change \n{change}\n')
    #print()
    #print()