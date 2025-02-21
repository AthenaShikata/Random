import os

directory = os.getcwd()
output = open('output.txt','w')
cache = ''

for filename in os.listdir(directory):
    if ((filename != 'output.txt') and (filename != 'text merger.py') and (os.path.isdir(filename) == False)):
        file = open(filename,'r')
        cache = cache + '#' + filename[:-4] + '\n' + file.read().strip() + '\n\n'
        file.close()
print(cache)
output.write(cache)
output.close()