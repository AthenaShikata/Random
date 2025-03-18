import os
import re


downloadFolder = 'youtubedownload'



root = os.getcwd()

for playlist in sorted(os.listdir(f'{root}/{downloadFolder}')):
    print(playlist)
    print()
    os.chdir(f'{root}/{downloadFolder}/{playlist}')
    files = [f for f in sorted(os.listdir()) if re.match(r'^\d+', f) and ' - ' in f]
    for file in files:
        if file.find('] - ') != -1 and file.find(' - [') != -1: pass
        else: print(file)
    print()
    print()
