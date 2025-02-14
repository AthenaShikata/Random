import os
for filename in os.listdir("."):
    ext = os.path.splitext(filename)[1]
    if os.path.isdir(filename) == True: 
        title = 'Harry Potter ' + filename[16] + ': '
        os.rename(filename, title)