import os
cwd = os.getcwd()

def covert_json(file):
    filename = file[:file.rfind('.')]
    os.rename(file,f'{filename}_broken.properties')

def edit_file_1(file,template):
    fileFile = open(file,'r')
    fileCache = fileFile.read()
    fileFile.close()
    
    line = [line for line in fileCache.split('\n') if line.startswith('texture=textures/')]
    texture = line[0].replace('texture=textures/','')
    newText = template.replace('abc',texture)
    print(newText)
    fileFile = open(file,'w')
    fileCache = fileFile.write(newText)
    fileFile.close()
    
def edit_file_2(file,template):
    filename = file[:file.rfind('.')]
    newText = template.replace('item/elytra/',f'item/elytra/broken_{filename}_icon')
    fileFile = open(file,'w')
    fileCache = fileFile.write(newText)
    fileFile.close()

def edit_file_3(file,template):
    fileFile = open(file,'r')
    fileCache = fileFile.read()
    fileFile.close()
    
    fileCache = fileCache + 'damage=431'
    fileCache = fileCache.replace('_elytra',"_elytra_broken")
    
    fileFile = open(file,'w')
    fileFile.write(fileCache)
    fileFile.close()
    
def crossbow():
    templateFile = open('crossbow.txt','r')
    template = templateFile.read()
    templateFile.close

    cwd = os.getcwd()
    crossbow = f'{cwd}/cross/'
    os.chdir(crossbow)
    encahnt = os.listdir()

    for enchant in os.listdir(crossbow):
        os.chdir(crossbow)
        os.chdir(f'{crossbow}/{enchant}')
        for file in [file for file in os.listdir('.') if os.path.isfile(file)]:
            edit_file_2(file,template)
        for tipped in [folder for folder in os.listdir('.') if os.path.isdir(folder)]:
            os.chdir(f'{crossbow}/{enchant}/{tipped}')
            for file in [file for file in os.listdir('.') if os.path.isfile(file)]:
                edit_file_2(file,template)
            
def elytra():
    templateFile = open('crossbow.txt','r')
    template = templateFile.read()
    templateFile.close
    crossbow = f'{cwd}/cross/'
    os.chdir(crossbow)
    for file in [file for file in os.listdir('.') if os.path.isfile(file)]:
        edit_file_2(file,template)
    for file in [file for file in os.listdir('.') if os.path.isfile(file)]:
        covert_json(file)     
        
        
def elytra2():
    templateFile = open('crossbow.txt','r')
    template = templateFile.read()
    templateFile.close
    crossbow = f'{cwd}/cross/'
    os.chdir(crossbow)
    for file in [file for file in os.listdir('.') if os.path.isfile(file)]:
        edit_file_3(file,template)
    for file in [file for file in os.listdir('.') if os.path.isfile(file)]:
        covert_json(file)

elytra2()