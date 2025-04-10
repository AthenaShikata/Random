import os

sourceFolder = 'youtubeplaylists'
outputFile = 'output.txt'
root = os.getcwd()
output = open(f'{root}/{sourceFolder}/{outputFile}','w')
cache = ''

for filename in sorted(os.listdir(f'{root}/{sourceFolder}')):
    if ((filename != 'output.txt') and (filename != 'text merger.py') and (not os.path.isdir(f'{root}/{sourceFolder}/{filename}'))):
        file = open(f'{root}/{sourceFolder}/{filename}','r')
        cache = cache + '#' + filename[:-4] + '\n' + file.read().strip() + '\n\n'
        file.close()
print(cache)
output.write(cache)
output.close()