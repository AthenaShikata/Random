import os

for filename in os.listdir("."):
    if filename.startswith('S01') == True:
        title = 'S02' + filename[3:]
        if filename.endswith('.nfo'):
            input = open(filename,'r')
            output = open(title,'w')
            cache = ''
            for line in input:
                line=line.rstrip()
                if line.startswith('  <season>') == True:
                    line = line.replace('1','2')
                cache = cache + line + '\n'
            output.write(cache)
            input.close()
            output.close()
            os.remove(filename)
        else:os.rename(filename, title)