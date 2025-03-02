files=['01 - test.txt','00 - Dream SMP⧸MCYT Animation.description', '00 - Dream SMP⧸MCYT Animation.jpg', '04 - ＂Hog Hunt＂ ｜ Dream SMP Animation.description', '04 - ＂Hog Hunt＂ ｜ Dream SMP Animation.en-US.vtt', '04 - ＂Hog Hunt＂ ｜ Dream SMP Animation.en-en-US.vtt', '04 - ＂Hog Hunt＂ ｜ Dream SMP Animation.en-en.vtt', '04 - ＂Hog Hunt＂ ｜ Dream SMP Animation.en-fil.vtt', '04 - ＂Hog Hunt＂ ｜ Dream SMP Animation.en-orig.vtt', '04 - ＂Hog Hunt＂ ｜ Dream SMP Animation.en.vtt', '04 - ＂Hog Hunt＂ ｜ Dream SMP Animation.mkv', '04 - ＂Hog Hunt＂ ｜ Dream SMP Animation.webp', '05 - ＂Ozymandias＂ ｜ Dream SMP Animation.description', '05 - ＂Ozymandias＂ ｜ Dream SMP Animation.en-orig.vtt', '05 - ＂Ozymandias＂ ｜ Dream SMP Animation.en.vtt', '05 - ＂Ozymandias＂ ｜ Dream SMP Animation.mkv', '05 - ＂Ozymandias＂ ｜ Dream SMP Animation.webp', '06 - ＂Final Waltz＂ ｜ Dream SMP Animation.description', '06 - ＂Final Waltz＂ ｜ Dream SMP Animation.en-US.vtt', '06 - ＂Final Waltz＂ ｜ Dream SMP Animation.en-en-US.vtt', '06 - ＂Final Waltz＂ ｜ Dream SMP Animation.en-en.vtt', '06 - ＂Final Waltz＂ ｜ Dream SMP Animation.en-ja.vtt', '06 - ＂Final Waltz＂ ｜ Dream SMP Animation.en-orig.vtt', '06 - ＂Final Waltz＂ ｜ Dream SMP Animation.en.vtt', '06 - ＂Final Waltz＂ ｜ Dream SMP Animation.mkv', '06 - ＂Final Waltz＂ ｜ Dream SMP Animation.webp', '08 - Dre SMP.description', '08 - Dre SMP.en.vtt', '08 - Dre SMP.mkv', '08 - Dre SMP.webp', '09 - Dream vs Technoblade Animation.description', '09 - Dream vs Technoblade Animation.mkv', '09 - Dream vs Technoblade Animation.webp', "10 - ＂Sunsprite's Eulogy＂ ｜ Passerine animatic.description", "10 - ＂Sunsprite's Eulogy＂ ｜ Passerine animatic.en-orig.vtt", "10 - ＂Sunsprite's Eulogy＂ ｜ Passerine animatic.en.vtt", "10 - ＂Sunsprite's Eulogy＂ ｜ Passerine animatic.mkv", "10 - ＂Sunsprite's Eulogy＂ ｜ Passerine animatic.webp", "11 - ＂Who's who？＂ ｜ DreamTeam+BBH⧸Muffinteers (Animation).description", "11 - ＂Who's who？＂ ｜ DreamTeam+BBH⧸Muffinteers (Animation).en-orig.vtt", "11 - ＂Who's who？＂ ｜ DreamTeam+BBH⧸Muffinteers (Animation).en.vtt", "11 - ＂Who's who？＂ ｜ DreamTeam+BBH⧸Muffinteers (Animation).mkv", "11 - ＂Who's who？＂ ｜ DreamTeam+BBH⧸Muffinteers (Animation).webp", 'converter.py']











from subprocess import Popen, PIPE
import re
import os
#'''



'''def process_files(file_list, reverse_order):
    # Filter files: must start with a number and contain ' - '
    filtered_files = [f for f in file_list if re.match(r'^\d+', f) and ' - ' in f]
    print(filtered_files)
    # Extract numbers from filenames
    numbered_files = []
    for f in filtered_files:
        match = re.match(r'^(\d+)', f)
        if match:
            num = int(match.group(1))
            if num != 0:  # Ignore files starting with 0
                numbered_files.append((num, f))
    
    # Sort files based on extracted number
    numbered_files.sort(reverse=reverse_order, key=lambda x: x[0])

    # Calculate step size
    numbers = [num for num, _ in numbered_files]
    if len(numbers) > 1:
        step_size = (numbers[-1] - numbers[0])
    else:
        step_size = 1  # Default step size if only one valid file

    # Assign output numbers
    output = {}
    for i, (num, filename) in enumerate(numbered_files):
        output[filename] = round(1 + i * step_size, 2)

    return output'''

reverseOrder = True # set true if the playlist is in the wrong order

epNum = None

files = [f for f in files if re.match(r'^\d+', f) and ' - ' in f]
fileNumList = []
for file in files: 
    if int(file[:file.find(' - ')]) != 0: fileNumList.append(int(file[:file.find(' - ')]))
fileNumList = sorted(set(fileNumList),reverse=reverseOrder)
print(fileNumList)

for file in files:
    #print(file)
    fileNum = int(file[:file.find(' - ')])
    #print(fileNum)
    if fileNum != 0 and fileNum != epNum:
        epNum = fileNum
        #print(epNum)
        if reverseOrder: episode = fileNumList[0] +1 - fileNum
        else: episode = fileNum - fileNumList[0] +1
        #print(episode)
        print(fileNum,episode)


#files = ["3 - FileA.txt", "1 - FileB.txt", "0 - Ignore.txt", "2 - FileC.txt", "random.txt"]
# Example usage

