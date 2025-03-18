import os
import re

files = [f for f in sorted(os.listdir()) if re.match(r'^\d+', f) and ' - ' in f]
for file in sorted(os.listdir()):
    if file.find('] - ') != -1 and file.find(' - [') != -1: # if id
        idlen = file.find('] - ') - file.find(' - [') - 4
        if idlen == 11:
            newname = f'{file[:file.find(' - [')]} - {file[file.find('] - ')+4:]}'
            os.rename(file,newname)
