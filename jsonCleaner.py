import os
import json
from difflib import SequenceMatcher


for files in os.listdir():
    if files.endswith('.json'):
      with open(files,'r',encoding="utf8") as file:
        data = json.load(file)
        #data = json.loads(str(data))
        dataClean = json.dumps(data, indent=4)
        print(dataClean)
        file.close()
        output = open(files,'w')
        output.write(dataClean)
        output.close()