import os,sys,subprocess,pty,select

root = os.getcwd()
downloadFolder = 'youtubedownload2'
sourceFolder = 'youtubeplaylists'
sourceFile = 'output.txt'
archiveFile = 'autoArchive.txt'

sourceList = open(f'{root}/{sourceFolder}/{sourceFile}','r')
sourceListText = sourceList.read()
sourceList.close()
linkList = [link for link in sourceListText.split('\n') if link.startswith('https://')]

stop_string = "Video unavailable. This content isn't available, try again later."

for link in linkList:
    try:

        command = f'yt-dlp --download-archive "{root}/{archiveFile}" -o "%(playlist)s/%(playlist_index)s - [%(id)s] - %(title)s.%(ext)s" -P "{root}/{downloadFolder}/" -P "temp:tmp" -f "bv+ba/b" --embed-thumbnail --embed-metadata --embed-chapters --sponsorblock-mark all --write-subs --write-auto-subs --sub-format vtt --sub-langs "en.*" --audio-quality 0 --cookies-from-browser firefox --write-thumbnail --write-description --write-info-json -r "25M" {link}'
        
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Read output line by line
        for line in process.stderr:
            print(line, end="")  # Print output in real-time


            if line.find(stop_string) != -1:
                print(f"\nDetected stop string: '{stop_string}'. Exiting...")
                process.terminate()  # Terminate the process
                sys.exit(1)  # Exit the script immediately

        process.wait()  # Wait for the process to complete

        #remove line from sourceFile
        sourceListText = sourceListText.replace(link,'')
        sourceList = open(f'{root}/{sourceFolder}/{sourceFile}','w')
        sourceList.write(sourceListText)
        sourceList.close()

        #erase archive after every playlist
        archive = open(f'{root}/{archiveFile}','w')
        archive.write('')
        archive.close()


    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Exiting...")
        sys.exit(1)  # Immediately exit the entire program
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
    except: raise



print('\ndone\n')



'''     
#[download]  32.0% of  274.67MiB at  507.30KiB/s ETA 06:16

# and ((line.find(f'% of') != -1 ) or (line.find(f'MiB') != -1 ) or (line.find(f'KiB') != -1 ) or (line.find(f'GiB') != -1 ) or (line.find('ETA') != -1))

# and ((prevLine.find(f'% of') != -1 ) or (prevLine.find(f'MiB') != -1 ) or (prevLine.find(f'KiB') != -1 ) or (prevLine.find(f'GiB') != -1 ) or (prevLine.find('ETA') != -1))

            # Output formatting (can be customized)
            if line.startswith('[download]') and ((line.find(f'% of') != -1 ) or (line.find(f'MiB') != -1 ) or (line.find(f'KiB') != -1 ) or (line.find(f'GiB') != -1 ) or (line.find('ETA') != -1)):
                print('linefound')
                if prevLine.startswith('[download]') and ((prevLine.find(f'% of') != -1 ) or (prevLine.find(f'MiB') != -1 ) or (prevLine.find(f'KiB') != -1 ) or (prevLine.find(f'GiB') != -1 ) or (prevLine.find('ETA') != -1)):
                    print('Download Found')
                    if output_type == 'stdout':
                        print(f"\033[32m{line}\033[0m", end='')  # Example: Green for stdout
                        sys.stdout.flush()  
                    elif output_type == 'stderr':
                        print(f"\033[31m{line}\033[0m", end='')  # Example: Red for stderr
                        sys.stderr.flush()
                
                
                
                else:
                    if output_type == 'stdout':
                        print(f"\033[32m{line}\033[0m", end='')  # Example: Green for stdout
                        sys.stdout.flush()  
                    elif output_type == 'stderr':
                        print(f"\033[31m{line}\033[0m", end='')  # Example: Red for stderr
                        sys.stderr.flush()
            else:
                if output_type == 'stdout':
                    print(f"\033[32m{line}\033[0m", end='')  # Example: Green for stdout
                    sys.stdout.flush()  
                elif output_type == 'stderr':
                    print(f"\033[31m{line}\033[0m", end='')  # Example: Red for stderr
                    sys.stderr.flush()

'''


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

