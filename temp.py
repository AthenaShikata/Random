from datetime import datetime
import time
import os

x=0
fileCounter = 0

def otherThing():
    global x
    #print("otherThing x:",x)
    print("otherThing fielCounter:",fileCounter)

def dothing():
    try:
        try:
            for i in range(0,5):
                #global x
                global fileCounter
                print(i)
                #print("doThing x:",x)
                print("doThing fileCounter:",fileCounter)
                otherThing()
                print()
                #x += 1
                fileCounter += 1 
                time.sleep(3)  
            ded = "bob" + 5
            print(int(ded))  
        except KeyboardInterrupt:
            print("\nKEYBOARD INTERUPT")
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            xFile = open('pyScripterror.txt', 'a')
            content = 'Keyboard Interupt: ', dt_string, '\n'
            xFile.write(''.join(content))
            xFile.close()
            return
    except Exception:
        print("TRACEBACK ERROR")
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        xFile = open('pyScripterror.txt', 'a')
        content = 'ERROR: ', dt_string, '\n'
        xFile.write(''.join(content))
        xFile.close()
        dothing()
dothing()
print("COMPLETE :D")