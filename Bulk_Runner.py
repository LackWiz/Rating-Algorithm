from urllib import response
import Rating_Algorithm
import os
import csv
import requests
import json

import tkinter as tk
from tkinter.filedialog import askdirectory
tk.Tk().withdraw()



#hash_list = []
diff_list = []
song_id_list = []

#Test Variables
#song_id = ["1", "c32d", "17914", "17cc0"]
hash_list = ["42CBB3914E8656B85EC26D288D9A5953E3A96CD8"]
BulkRunName = "test"



# playlist_Path = askdirectory()
# print("Name of Bulk Run")
# BulkRunName = input()

def load_playlist_bplist(path):
    with open(path, encoding='utf8') as json_bplist:
        bplist = json.load(json_bplist)
    return bplist



for i, song in enumerate(hash_list):
    result = requests.get(f"https://api.beatsaver.com/maps/hash/{hash_list[i]}")
    resultJson = json.loads(result.text)
    try:
        song_id = resultJson["id"]
        if(hash_list[i].lower() != resultJson["versions"][0]["hash"].lower()):
            print(f"Hash {hash_list[i]} From Playlist Entry Doesn't match BeatSaver or is unavaliable")
            print("You seem to have an older version of this song?")
            print("The Results may be different due to possible different map versus hosted map")
        folder_path, song_diff = Rating_Algorithm.getSongPath(song_id)
        diff_list.append(Rating_Algorithm.Main(folder_path, song_diff, song_id))
    except KeyError:
        if(resultJson["error"] == "Not Found"):
            print(f"Song Hash {hash_list[i]} Not Found!")
            print("Song was either deleted or doesn't exist")

for i, entery in enumerate(diff_list):
    print(diff_list[i])

excelFileName = os.path.join(f"BulkResults/{BulkRunName} export.csv")
try:
    f = open(excelFileName, 'w', newline="")
except FileNotFoundError:
    print('Making BulkResults Folder')
    os.mkdir('BulkResults')
    f = open(excelFileName, 'w', newline="")
finally:
    writer = csv.writer(f)
    writer.writerow(["Name", "Weighted/Score", "Median", "Average"])
    for diff_i in diff_list:
        writer.writerow(diff_i)
    f.close


print("Press Enter to Exit")
input()



