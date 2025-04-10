import os
import shutil

def copy_and_rename(src_path, dest_path):
	# Copy the file
	shutil.copy(src_path, dest_path)

	# Rename the copied file
	new_path = f"{dest_path}/{src_path}"
	shutil.move(f"{dest_path}/{src_path}", new_path)

for filename in os.listdir("."):
    if filename.endswith('.mkv') == True:
        title = filename[40:-11] +' ('+filename[-9:-5]+')'
        os.mkdir(title)
        copy_and_rename(filename, title)