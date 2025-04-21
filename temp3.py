import os
import pty
import subprocess
import sys
import fcntl
import select
import signal
import threading
import time

root = os.getcwd()
downloadFolder = 'youtubedownload2'
sourceFolder = 'youtubeplaylists'
sourceFile = 'output.txt'
archiveFile = 'autoArchive.txt'
unavailableFile = 'unavailable.txt'

sourceList = open(f'{root}/{sourceFolder}/{sourceFile}','r')
sourceListText = sourceList.read()
sourceList.close()
linkList = [link for link in sourceListText.split('\n') if link.startswith('https://')]

#print(linkList)

unavailable = []
lastLink = ''

# Global variable to signal when we should stop
stop_event = False

def writeUnavailable(unavailable):
    print('wrtingunknown')
    file = open(unavailableFile,'r')
    cache = file.read()
    file.close()
    for line in unavailable:
        if cache.find(line) == -1:
            cache = f'{cache.rstrip(' \n')}\n{line}\n'
    file = open(unavailableFile,'w')
    file.write(cache)
    print(cache)
    file.close()
    print('finished writing')


def stop(process,type):
    print('stopped')
    if type == 'keyboard': 
        print("\nKeyboardInterrupt detected. Terminating process...")
        process.terminate()
        writeUnavailable(unavailable)
        raise KeyboardInterrupt
    elif type == 'video': 
        print("\nConnectionRefusedError detected. Terminating process...")
        process.terminate()
        writeUnavailable(unavailable)
        raise ConnectionRefusedError
    

def read_stream(stream, output_type, process):
    global stop_event
    global unavailable
    global lastLink

    prevLine = ''

    for line in stream:
        if not stop_event:
            # Check if the stop_string is in the output
            if line.find('Video unavailable. This content isn\u2019t available.') != -1:
                print(f"\033[31mSTOP STRING DETECTED: Video unavailable. This content isn\u2019t available.\033[0m")
                stop_event = True  # Signal the threads to stop reading
                stop(process,type='video')
                print('detect 1')
                return  # Exit the function after termination

            # Check if the stop_string is in the output
            if line.find('HTTP Error 429: Too Many Requests') != -1:
                print(f"\033[31mSTOP STRING DETECTED: {'HTTP Error 429: Too Many Requests'}\033[0m")
                stop_event = True  # Signal the threads to stop reading
                autoStop = True
                stop(process,type='video')
                print('detecct 2')
                return  # Exit the function after termination
            

            '''if not stop_event and line.find('Video unavailable') != -1:
                unavailable.append(f'{lastLink} - {line.rstrip(' \n')}\n')
                print('unavailable found')'''

            if output_type == 'stdout':
                print(f"\033[32m{line}\033[0m", end='')  # Example: Green for stdout
                sys.stdout.flush()  
            elif output_type == 'stderr':
                print(f"\033[31m{line}\033[0m", end='')  # Example: Red for stderr
                sys.stderr.flush()



            if line.find('[youtube] Extracting URL: ') != -1:
                lastLink = line[line.find('[youtube] Extracting URL: ') + 26:]
                print(lastLink)

            prevLine = line
        else: 
            print('stuck stream')
            #sys.exit(1)
            return


def signal_handler(sig, frame, process):
    global stop_event
    global unavailable
    stop_event = True
    print('signaled')
    stop(process,type='keyboard')

def run_command(command):
    global stop_event
    global unavailable

    # Start the subprocess
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, preexec_fn=os.setsid)

    # Register the signal handler for KeyboardInterrupt (Ctrl+C)
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, process))

    # Start separate threads to read stdout and stderr
    stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, 'stdout', process))
    stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, 'stderr', process))

    # Start the threads
    stdout_thread.start()
    stderr_thread.start()

    # Wait for both threads to finish or process to terminate
    stdout_thread.join()
    stderr_thread.join()
    print('joined')
    # Ensure process finishes
    process.wait()
    print('waited')



# Example usage:

try: 
    file = open(unavailableFile,'w')
    file.write('')
    file.close()
except FileExistsError: pass
except: raise

for link in linkList:
    if not stop_event:
        command = f'yt-dlp --download-archive "{root}/{archiveFile}" -o "%(playlist)s/%(playlist_index)s - [%(id)s] - %(title)s.%(ext)s" -P "{root}/{downloadFolder}/" -P "temp:tmp" -f "bv+ba/b" --embed-thumbnail --embed-metadata --embed-chapters --sponsorblock-mark all --write-subs --write-auto-subs --sub-format vtt --sub-langs "en.*" --audio-quality 0 --cookies-from-browser firefox --write-thumbnail --write-description --write-info-json -r "25M" {link}'
        #command = f'yt-dlp --download-archive "{root}/{archiveFile}" -o "%(playlist)s/%(playlist_index)s - [%(id)s] - %(title)s.%(ext)s" -P "{root}/{downloadFolder}/" -P "temp:tmp" -f "bv+ba/b" --embed-thumbnail --embed-metadata --embed-chapters --sponsorblock-mark all --write-subs --write-auto-subs --sub-format vtt --sub-langs "en.*" --audio-quality 0 --cookies-from-browser firefox --write-thumbnail --write-description --write-info-json -r "25M" https://www.youtube.com/watch?v=zkcq22D3aXM&list=PLSOiQqYQEf1jLoZyGczPUBTVi-aPp3XnT&pp=iAQB'

        #subprocess.call(command,shell=True)
        run_command(command)  # Stops if "Request timeout" appears
        if not stop_event: 
            print('run ended')
            '''#remove line from sourceFile
            sourceListText = sourceListText.replace(link,'')
            sourceList = open(f'{root}/{sourceFolder}/{sourceFile}','w')
            sourceList.write(sourceListText)
            sourceList.close()

            #erase archive after every playlist
            archive = open(f'{root}/{archiveFile}','w')
            archive.write('')
            archive.close()'''

writeUnavailable(unavailable)