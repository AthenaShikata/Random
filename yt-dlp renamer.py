import os
import glob

downloadFolder = 'youtubedownload'

nameUpdate = open('newnames.txt','r')
cache = nameUpdate.read()
changegsList = cache.split("\n\n")

badFix = []

for playlist in os.listdir(downloadFolder):
    for change in changegsList:
        if change.startswith(playlist):
            print(change)
            print()

            oldName = change.split('\n')[0].strip().replace(f'{playlist}/','')
            newName = change.split('\n')[1].strip().replace(f'{playlist}/','')
            print(oldName)
            print(newName)
            print()

            #oldFiles = glob.glob(f'{downloadFolder}/{playlist}/{oldName[:oldName.rfind('.')]}*')
            oldFiles = os.listdir(f'{downloadFolder}/{playlist}')
            #oldFiles = [file for file in oldFiles if file.startswith(oldName[:oldName.rfind('.')])]
            fixOldFiles = []
            #print(oldFiles)
            oldNameClean = oldName[:oldName.rfind('.')]
            for file in oldFiles:
                if oldNameClean in file:
                    fixOldFiles.append(file)
                else: badFix.append(oldNameClean)
                #print(oldNameClean)
                #print(file)
            print(fixOldFiles)

            #for file in oldFiles:
            #    newFile = f'{newName}{file[file.rfind('.'):]}'
            #    print(newFile)
                
                #try: os.rename(oldFiles,newName)
                #except FileNotFoundError: print(f'FileNotFoundError: The system cannot find the path specified: "{oldName}')
                #except: raise
            print()
            print()
print(badFix)
badFixSort = []



for item in badFix:
    if any(elem in item for elem in ':{}') == True: badFixSort.append(item)
print(badFixSort)

