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

os.chdir(f'{root}/{downloadFolder}/Stampylonghead - Terraria (FULL LIST\u29f8COMPLETED)')
for file in os.listdir():
    if file.find(' - ') == 2:
        os.rename(file,f'0{file}')