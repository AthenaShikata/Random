import os,re
reverseOrder = False

downloadFolder = 'youtubedownload'
playlistFolder = 'Space Engineers\uff1a Outlands Season 4'

halfeps = [7,10,13,15,18,22]


os.chdir(f'{os.getcwd()}/{downloadFolder}/{playlistFolder}')

files = [f for f in sorted(os.listdir(),reverse=reverseOrder) if re.match(r'^\d+', f) and ' - ' in f] # get all files and filter out unwanted files (ie everything that wasn't downloaded by yt-dlp)

for file in files:
    for ep in halfeps:
        if file[:file.find(' - ')] == (str(ep)):
            #print(file)
            print(f'{file[:file.find(' - ')]}.5{file[file.find(' - '):]}')
            os.rename(file,f'{file[:file.find(' - ')]}.5{file[file.find(' - '):]}')