import os

old_season = 1
new_season = 6

for filename in os.listdir("."):
    if filename.find(f'S{str(old_season).zfill(2)}') != -1:
        title = filename.replace(f'S{str(old_season).zfill(2)}',f'S{str(new_season).zfill(2)}')
        if filename.endswith('.nfo'):
            input = open(filename,'r')
            output = open(title,'w')
            cache = ''
            for line in input:
                line=line.rstrip()
                if line.startswith('  <season>') == True:
                    line = line.replace(str(old_season),str(new_season))
                cache = cache + line + '\n'
            output.write(cache)
            input.close()
            output.close()
            os.remove(filename)
        else:os.rename(filename, title)
