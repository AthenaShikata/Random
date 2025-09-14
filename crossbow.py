import os
cwd = os.getcwd()

def covert_json(file):
    filename = file[:file.rfind('.')]
    os.rename(file,f'{filename}.json')

def covert_rename(file,template):
    os.rename(file,f'{template}{file}')

def covert_emissive(file,template):
    filename = file[:file.rfind('.')]
    fileext = file[file.rfind('.'):]
    os.rename(file,f'{filename}_e{fileext}')

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
    newText = template.replace('item/enchanted_book/',f'item/enchanted_book/{filename}')
    fileFile = open(file,'w')
    fileCache = fileFile.write(newText)
    fileFile.close()

def edit_file_3(file,template):
    fileFile = open(file,'r')
    fileCache = fileFile.read()
    fileFile.close()
    
    fileCache = fileCache.replace('layer0": "minecraft:item/','layer0": "minecraft:item/enchanted_book/')
    
    fileFile = open(file,'w')
    fileFile.write(fileCache)
    fileFile.close()
    
def newFileFromOldList(file,template):
    filename = file[:file.rfind('.')]
    newtemplate = template.replace('replace',filename)
    fileFile = open(f'{filename}.json','w')
    fileFile.write(newtemplate)
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
        
def book():
    templateFile = open('crossbow.txt','r')
    template = templateFile.read()
    templateFile.close
    crossbow = f'{cwd}/cross/'
    os.chdir(crossbow)
    for file in [file for file in os.listdir('.') if os.path.isfile(file)]:
        edit_file_3(file,template)

def target():
    crossbow = f'{cwd}/cross/'
    os.chdir(crossbow)
    template = 'target_side_'
    for file in [file for file in os.listdir('.') if os.path.isfile(file)]:
        covert_rename(file,template)

def emissive():
    crossbow = f'{cwd}/cross/'
    os.chdir(crossbow)
    template = 'target_side_'
    for file in [file for file in os.listdir('.') if os.path.isfile(file)]:
        covert_emissive(file,template)
        
        
def stew():
    templateFile = open('crossbow.txt','r')
    template = templateFile.read()
    templateFile.close
    crossbow = f'{cwd}/cross/'
    os.chdir(crossbow)
    for file in [file for file in os.listdir('.') if os.path.isfile(file)]:
        newFileFromOldList(file,template)
    
    
def ore():
    crossbow = f'{cwd}/cross/'
    os.chdir(crossbow)
    for folder in [folder for folder in os.listdir('.') if os.path.isdir(folder)]:
        print(folder)
        os.chdir(f'{crossbow}/{folder}')
        for file in [file for file in os.listdir('.') if os.path.isfile(file)]:
            if file.endswith('.properties') and folder.startswith('deepslate'):
                filename = file[:file.rfind('.')]
                fileext = file[file.rfind('.'):]
                fileFile = open(file,'r')
                cache = fileFile.read()
                fileFile.close()
                new = cache.replace(folder,f'{folder}_top')
                fileFile = open(f'{filename}_top{fileext}','w')
                fileFile.write(new)
                fileFile.close
    
def renameOre():
    os.chdir('C:/Users/evanp/Downloads')
    os.rename('New Piskel.png','andesite.png')
    os.rename('New Piskel (1).png','diorite.png')
    os.rename('New Piskel (2).png','dripstone_block.png')
    os.rename('New Piskel (3).png','granite.png')
    os.rename('New Piskel (4).png','tuff.png')
    
renameOre()