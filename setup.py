import os
import MapDownloader
def checkFolderPath():
    try:
        f = open('bs_path.txt', 'r')
        bsPath = f.read()
    except FileNotFoundError:
        print('Enter Beat Saber custom songs folder:')
        # TODO: validate path
        #bsPath = askdirectory()
        bsPath = input()
        if bsPath[-1] not in ['\\', '/']:  # Checks if song path is empty
            bsPath += '/'
        f = open('bs_path.txt', 'w')
        dat = f.write(bsPath)
    finally:
        f.close()
    return bsPath

