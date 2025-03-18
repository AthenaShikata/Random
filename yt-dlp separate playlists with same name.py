import os,json,re,shutil


def copy_and_rename(src_path, dest_path, new_name):
	shutil.copy(src_path, dest_path)
	# Rename the copied file
	shutil.move(f"{dest_path}/{src_path}", f"{dest_path}/{new_name}")

def get_json_metadata(filename): # use .info.json to get the metadata of the video
    with open(f'{filename}.info.json','r',encoding="utf8") as file:
        data = json.load(file)
        dataClean = json.dumps(data, indent=4)
        #print(dataClean)
        # critical values. left outside a try/except because if they fail an error should be raised
        date = data['upload_date']
        year = date[:4]
        uploader = data['uploader']
        video_link = data['webpage_url']
        jsonDescription = data['description']

        try: channel_link = data['uploader_url']
        except: channel_link = data['channel_url']
        
        try: tags = data['tags']
        except: tags = []
        if 'youtube' not in tags: tags.append('youtube')
        
        try: genres = data['categories']
        except: genres = []
        if 'youtube' not in genres: genres.append('youtube')
        
        try: sponsor_chapters = data['sponsorblock_chapters']
        except: sponsor_chapters = []

    return year, date, uploader, channel_link, video_link, tags, genres, sponsor_chapters, jsonDescription



downloadFolder = 'youtubedownload' # folder within current directory that contains the folders for each playlist
playlistFolder = 'Building Time'

os.chdir(f'{os.getcwd()}/{downloadFolder}/{playlistFolder}')

authors = []

for file in sorted(os.listdir()):
    if file.endswith('.info.json') and not file.startswith('00') :
        #print(file)
        filename = file.replace('.info.json','')
        episodeData = get_json_metadata(filename)
        authors.append(episodeData[2])

authors = sorted(set(authors))

for author in authors:
    if os.path.exists(os.path.join(os.getcwd(),f'{playlistFolder} - {author}')):
        shutil.rmtree(os.path.join(os.getcwd(),f'{playlistFolder} - {author}'))
    os.mkdir(f'{playlistFolder} - {author}')



for file in sorted(os.listdir()):
    if file.endswith('.info.json') and not file.startswith('00') :
        filename = file.replace('.info.json','')
        print(filename)
        episodeData = get_json_metadata(filename)
        author = episodeData[2]
        for epfile in os.listdir():
            if epfile.startswith(filename):
                copy_and_rename(epfile,f'{os.getcwd()}/{playlistFolder} - {author}',epfile) #move and rename mp4 video