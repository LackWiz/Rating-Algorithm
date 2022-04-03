import requests
import json
import os
import zipfile
import re


def getFilename(cd):
    fname = re.findall('filename="(.+)"', cd)
    return fname[0]


def downloadSong(songID, songsPath):
    s = requests.Session()
    result = s.get(f"https://api.beatsaver.com/maps/id/{songID}")
    resultJson = json.loads(result.text)
    downloadURL = resultJson["versions"][0]["downloadURL"]
    r = requests.get(downloadURL, allow_redirects=True)

    if(r.status_code != 200):
        return False
    f = getFilename(r.headers.get('content-disposition'))
    f = f.replace("?", "_")
    open(f, "wb").write(r.content)

    os.makedirs(songsPath + f[:-4])
    with zipfile.ZipFile(f, 'r') as z:
        z.extractall(songsPath + f[:-4])

    os.remove(f)
    return f[:-4]
