import os
import re
from difflib import SequenceMatcher

ratioThreshold = .87
downloadFolder = 'youtubedownload'
root = os.getcwd()

completePlaylist = []
incompletePlaylist = []

for playlistFolder in sorted(os.listdir(downloadFolder)):
#for playlistFolder in ['KSP Beyond Kerbol']:

    completeTest = True

    os.chdir(f'{root}/{downloadFolder}/{playlistFolder}')

    files = [f for f in sorted(os.listdir()) if re.match(r'^\d+', f) and ' - ' in f]


    fileNameList = []
    for file in files:
        if file.endswith('.vtt') or file.endswith('.info.json'): 
            fileName = file[:file.rfind('.')]
            fileName = fileName[:fileName.rfind('.')]
        else: 
            fileName = file[:file.rfind('.')]
        fileNameList.append(fileName)

    fileNameList = sorted(set(fileNameList))

    jsonYes = []
    jsonNo = []
    jsonTest = []

    for fileName in fileNameList:
        if os.path.exists(f'{fileName}.info.json'): jsonYes.append(fileName)
        else: 
            jsonNo.append(fileName)
            completeTest = False
    if jsonNo != []: print(f'\n\n{playlistFolder}\n{jsonNo}\n\n')

    if completeTest == True: completePlaylist.append(playlistFolder)
    else: incompletePlaylist.append(playlistFolder)

print(completePlaylist)
print()
print(incompletePlaylist)