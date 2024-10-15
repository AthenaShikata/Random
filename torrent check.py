import os
def list_files(startpath):  
    list = ''
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        list = list + str(level) + ('{}{}/'.format(indent, os.path.basename(root))) + '\n'
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            list = list + str(level+1) + ('{}{}'.format(subindent, f)) + '\n'
    list = list + 'end'
    return list
structure = list_files(os.getcwd())
split_structure = structure.splitlines()

tree1 = []
tree2 = []
titletree = []
contentstree = []

for linenum in range(len(split_structure)):
    line = split_structure[linenum]
    if line[0] == '1':
        tree1.append(linenum)
        tree2.append([])
        titletree.append([])
        contentstree.append([])
tree1.append(len(split_structure)-1)

for libnum in range(len(tree1)-1):
    librange = [tree1[libnum],tree1[libnum+1]]
    #print(split_structure[librange[0]],split_structure[librange[1]])
    for linenum in range(librange[0],librange[1]):
        line = split_structure[linenum]
        if line[0] == '2':
            tree2[libnum].append(linenum)
            titletree[libnum].append(line.lstrip('123 '))
            contentstree[libnum].append([])
    if tree2[libnum] != []:
        tree2[libnum].append(librange[1])

for libnum in range(len(tree1)-1):
    if tree2[libnum] != []:
        libfolder = tree2[libnum]
        exportfolder = []
        for titlenum in range(len(libfolder)-1):
            exportfolder.append([])
            titlefolder = libfolder[titlenum]
            titlerange = [libfolder[titlenum],libfolder[titlenum+1]]
            for linenum in range(titlerange[0]+1,titlerange[1]):
                line = split_structure[linenum]
                if line[0] == '3':
                    exportfolder[titlenum].append(line.lstrip('123 '))
            contentstree[libnum] = exportfolder

         
print(tree1)
print()
print(tree2)
print()
print(titletree)
print()
print(contentstree)
print()


notorlistoutput = open('notorlist.txt','w')
torlistoutput = open('torlist.txt','w')
notorlist = ''
torlist = ''


for libnum in range(len(contentstree)):
    lib = contentstree[libnum]
    lib2 = titletree[libnum]
    for titlenum in range(len(lib)):
        title = lib[titlenum] 
        title2 = lib2[titlenum]
        check = 0
        for file in title:
            if file.endswith(".torrent") == True:
                check = 1
        if check == 0:
            notorlist = notorlist + title2 + "\n"
        elif check == 1:
            torlist = torlist + title2 + "\n"

notorlistoutput.write(notorlist)
notorlistoutput.close()

torlistoutput.write(torlist)
torlistoutput.close()