import os
from difflib import SequenceMatcher

ratioThreshold = .87 # configurable value between 0 and 1, comment out the renaming try statement and determine where your threshold lies
if (0 <= ratioThreshold <= 1) == False: raise ValueError(f'Variable ratioThreshold must be between 0 and 1, cannot be {ratioThreshold}')

root = os.getcwd()
downloadFolder = 'youtubedownload'

nameUpdate = open('newnames.txt','r')
cache = nameUpdate.read()
changesList = cache.split("\n\n")
nameUpdate.close()

for playlist in os.listdir(downloadFolder):
    os.chdir(f'{root}/{downloadFolder}/{playlist.replace('/','-')}')

    '''playlistFileLength = 0
    for file in sorted(os.listdir()):
        prevNumber = 0
        
        if int(file[:file.find(' - ')]) != prevNumber and file[file.rfind('.'):] == ('mp4' or 'mkv'):
            prevNumber = int(file[:file.find(' - ')])
            playlistFileLength += 1 
        

        try: 
            playlistFileTest = int(file[:file.find(' - ')]) != prevNumber and file[file.rfind('.'):] == ('mp4' or 'mkv')
            prevNumber = int(file[:file.find(' - ')])
            playlistFileLength += 1 
        except:
            print(f'File does not match format: {file}')

    playlistChangesLength = 0
    for change in changesList:
        if change.startswith(f'{playlist}/') or (playlist.startswith('Dream SMP') and change.startswith('Dream SMP')): 
            playlistChangesLength += 1

    if playlistChangesLength != playlistFileLength: print(f'Playlist mismatch: {playlist} {playlistChangesLength} {playlistFileLength}')

    print()
    print()
'''

    for change in changesList:
        changeTest = False
        videoTest = False

        if change.startswith(f'{playlist}/') or (playlist.startswith('Dream SMP') and change.startswith('Dream SMP')):
            if change.startswith('Dream SMP'): cleanChange = change.replace('Dream SMP/MCYT Animation/','')
            else: cleanChange = change.replace(f'{playlist}/','')
            #print(cleanChange)
            newName = cleanChange.split('\n')[1].strip()
            videoID = newName[newName.find('['):newName.find(']')+1]

            for file in os.listdir():
                if file.endswith('.mp4') or file.endswith('.mkv'): videoTest = True
                if file.startswith(cleanChange[:5]):
                    changeTest = True
                    
                    #print()
            if changeTest == False: print(f'FileNotFoundError: The system cannot find any files for the change \n{change}\n')
            if videoTest == False: print(f'FileNotFoundError: The system cannot find any video files for the change \n{change}\n')
    
    '''print()

    for file in os.listdir():
        if file.endswith('.mp4') or file.endswith('.mkv'):
            changeTest = False
            for change in changesList:
                if change.startswith('Dream SMP'): cleanChange = change.replace('Dream SMP/MCYT Animation/','')
                else: cleanChange = change.replace(f'{playlist}/','')
                oldName = cleanChange.split('\n')[0].strip()
                oldNameClean = oldName[:oldName.rfind('.')]
                filename = file[:file.rfind('.')]
                similarityRatio = SequenceMatcher(None, filename, oldNameClean).ratio()
                #print(similarityRatio)
                if similarityRatio >= ratioThreshold: changeTest = True
            if changeTest == False: print(f'FileNotFoundError: The system cannot find any changes for the video file \n{playlist}/{file}\n')'''

    print()
    print()