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


# Global variable to signal when we should stop
stop_event = False


def stop(process,type):
    if type == 'keyboard': 
        print("\nKeyboardInterrupt detected. Terminating process...")
        process.terminate()
        print(unavailable) # replace with file
        raise KeyboardInterrupt
    elif type == 'video': 
        print("\nConnectionRefusedError detected. Terminating process...")
        process.terminate()
        print(unavailable) # replace with file
        sys.exit(1)
        sys.exit(1)
    
    print('stuck stop')

def read_stream(stream, output_type, process):
    global stop_event
    global unavailable

    prevLine = ''

    for line in stream:
        if not stop_event:
            # Check if the stop_string is in the output
            if line.find('Video unavailable. This content isn\u2019t available.') != -1:
                print(f"\033[31mSTOP STRING DETECTED: Video unavailable. This content isn\u2019t available.\033[0m")
                stop_event = True  # Signal the threads to stop reading
                stop(process,type='video')
                return  # Exit the function after termination

            # Check if the stop_string is in the output
            if line.find('HTTP Error 429: Too Many Requests') != -1:
                print(f"\033[31mSTOP STRING DETECTED: {'HTTP Error 429: Too Many Requests'}\033[0m")
                stop_event = True  # Signal the threads to stop reading
                autoStop = True
                stop(process,type='video')
                return  # Exit the function after termination
            

            if not stop_event and line.find('Video unavailable') != -1:
                print(line)


            if output_type == 'stdout':
                print(f"\033[32m{line}\033[0m", end='')  # Example: Green for stdout
                sys.stdout.flush()  
            elif output_type == 'stderr':
                print(f"\033[31m{line}\033[0m", end='')  # Example: Red for stderr
                sys.stderr.flush()



            if line.find('[youtube] Extracting URL: '):
                link = line[line.find('[youtube] Extracting URL: '):]

            prevLine = line
        else: 
            print('stuck stream')
            sys.exit(1)


def signal_handler(sig, frame, process):
    global stop_event
    global unavailable
    #print("\nKeyboardInterrupt detected. Terminating process...")
    stop_event = True
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
    # Ensure process finishes
    process.wait()


#command = 'echo test'
#run_command(command, stop_string)

'''def run_command(cmd, stop_string):
    try:
        process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Keep checking output until process completes
        while True:
            # Wait for either stdout or stderr to be ready to read
            rlist, _, _ = select.select([process.stdout, process.stderr], [], [])

            for stream in rlist:
                line = stream.readline()
                if line:
                    sys.stdout.write(line)  # Print output in real-time
                    sys.stdout.flush()
                    # Print the output from either stdout or stderr
                
                    if line.find(stop_string) != False:
                        print(f"\nDetected stop string: '{stop_string}'. Exiting...")
                        process.terminate()  # Terminate the process
                        sys.exit(1)  # Exit the script immediately

            # Check if the process has finished
            if process.poll() is not None and not any([process.stdout, process.stderr]):
                break

        
        # Ensure all remaining output is printed
        stdout, stderr = process.communicate()
        if stdout:
            sys.stdout.write(stdout)
        if stderr:
            sys.stderr.write(stderr)

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Exiting...")
        process.terminate()
        sys.exit(1)'''


'''def run_command(cmd, stop_string):
    try:
        process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Read output line by line
        for line in process.stdout:
            print(line, end="")  # Print output in real-time
            if stop_string in line:
                print(f"\nDetected stop string: '{stop_string}'. Exiting...")
                process.terminate()  # Terminate the process
                sys.exit(1)  # Exit the script immediately

        process.wait()  # Wait for the process to complete

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Exiting...")
        process.terminate()
        sys.exit(1)  # Immediately exit the entire program
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
'''




# Example usage:

for link in linkList:
    if not stop_event:
        command = f'yt-dlp --download-archive "{root}/{archiveFile}" -o "%(playlist)s/%(playlist_index)s - [%(id)s] - %(title)s.%(ext)s" -P "{root}/{downloadFolder}/" -P "temp:tmp" -f "bv+ba/b" --embed-thumbnail --embed-metadata --embed-chapters --sponsorblock-mark all --write-subs --write-auto-subs --sub-format vtt --sub-langs "en.*" --audio-quality 0 --cookies-from-browser firefox --write-thumbnail --write-description --write-info-json -r "25M" {link}'
        #subprocess.call(command,shell=True)
        run_command(command)  # Stops if "Request timeout" appears
        if not stop_event: 
            '''#remove line from sourceFile
            sourceListText = sourceListText.replace(link,'')
            sourceList = open(f'{root}/{sourceFolder}/{sourceFile}','w')
            sourceList.write(sourceListText)
            sourceList.close()

            #erase archive after every playlist
            archive = open(f'{root}/{archiveFile}','w')
            archive.write('')
            archive.close()'''
            pass
print(unavailable)