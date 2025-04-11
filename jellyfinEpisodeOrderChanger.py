import os

season = 6
# add characters (usually numbers) to the start of the filenames so that python sees them in the correct watch order (automatically removes these)
# ex: 01 S01E04.mkv, 02 S01E01.mkv, 03 S01E02.mkv
# this assumes season and episode come before episode title (ex: S01E01 A New Dawn.mkv)

titles = []

for file in sorted(os.listdir()):
    if file.endswith('.nfo') and not file.startswith('season'):
        fileNum = file[:3]
        title = file[:-4]
        titles.append(title)

print(titles)

for titleNum in range(len(titles)):
    title = titles[titleNum]
    sPos = title.find(f'S{str(season).zfill(2)}E')
    epPos = sPos + 4
    if titleNum+1 > 9: fixedTitle = f'{title[sPos:epPos]}1{str(titleNum-10+1)}{title[epPos+2:]}'
    else: fixedTitle = f'{title[sPos:epPos]}0{str(titleNum+1)}{title[epPos+2:]}'
    print(fixedTitle)
    
    
    for file in os.listdir():
        if file.startswith(title):
            ext = file[file.rfind('.'):]
            if file.endswith('.nfo'):
                input = open(file,'r')
                output = open(f'{fixedTitle}{ext}','w')
                cache = ''
                for line in input:
                    line=line.rstrip()
                    if line.find(file[:file.rfind('.'):]) != -1:
                        line = line.replace(file[:file.rfind('.'):],fixedTitle)
                        print(line)
                    if line.startswith('  <episode>') == True:
                        line = f'{line[:line.find('>')+1:]}{str(titleNum+1)}{line[line.rfind('<'):]}'
                        print(line)
                    cache = cache + line + '\n'
                output.write(cache)
                input.close()
                output.close()
                os.remove(file)
                print()
            else:os.rename(file,f'{fixedTitle}{ext}')

            #os.rename(file,f'{fixedTitle}{ext}')

'''
    if file.endswith('.nfo'):
        fileNum = file[:3]
        title = file[:-4]
        episode = title[title.find('S06E')+4:title.find('S06E')+5]
        for file2 in os.listdir():
            if file2.startswith(fileNum) and not file2.endswith('.nfo'):
                ext = file2[file2.rfind('.'):]
                os.rename(file2,f'{title}{ext}')
        '''