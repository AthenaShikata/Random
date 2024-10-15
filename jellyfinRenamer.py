import os
for filename in os.listdir("."):
    if filename.endswith(" (1).mkv"):
        end = filename.find(" (1)")
        title = filename[0:end] + '.mkv'
        os.rename(filename, title)