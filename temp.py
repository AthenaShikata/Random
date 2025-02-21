from subprocess import Popen, PIPE
import re
import os
#'''
#file = 'Allergic to thots.mp4'
#file = '01 - Interstellar Dreams ｜ Beyond Kerbol #1.mkv'
file = '11 - youtube video #wTQsFnwWQZ4.mkv'
file = 'Ep78 For Those Who Stand Beside Us.mpeg'

if file.endswith('.mp4'):
    res = Popen(['ffmpeg', '-i', file, '-hide_banner'],stdout=PIPE,stderr=PIPE)
    none,meta = res.communicate()
    meta_out = meta.decode()
    #---| Take out info
    date = re.search(r'Created on:.*', meta_out)
    date = date.group()
    date = date.replace('Created on: ','')
    date = date[:-2]
    year = date[-4:]
    date = f'{year}-{date[:2]}-{date[3:5]}'
    print(year,date)
if file.endswith('.mkv'):
    res = Popen(['ffmpeg', '-i', file, '-hide_banner'],stdout=PIPE,stderr=PIPE)
    none,meta = res.communicate()
    meta_out = meta.decode()
    #---| Take out info
    date = re.search(r'DATE            : .*', meta_out)
    date = date.group()
    date = date.replace('DATE            : ','').rstrip()
    year = date[0:4]
    date = f'{year}-{date[4:6]}-{date[6:]}'
    print(year,date)
if file.endswith('.mpeg'):
    res = Popen(['ffmpeg', '-i', file, '-hide_banner'],stdout=PIPE,stderr=PIPE)
    none,meta = res.communicate()
    meta_out = meta.decode()
    print(meta_out)
    print(year,date)
#'''

