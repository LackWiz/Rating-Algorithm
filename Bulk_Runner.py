from urllib import response
import Rating_Algorithm
import setup
import os
import csv
import requests
import json

import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfile
tk.Tk().withdraw()



hash_list = []
diff_list = []
queue_list = []
song_diff = []
#-------------------------------Test Variables--------------------------------

#hash_list = ["42CBB3914E8656B85EC26D288D9A5953E3A96CD8","6E1C9B0967F7F48BAEA616DFCEDCED2BEC958A02","955E4674A84881AC57CEA003803F67E207978E89","2FA64C31E675B95FB077D7CB74BC14A5D675A0FC"]
#BulkRunName = "test"


playlist_Path = askopenfile(mode ='r', filetypes =[('Bp Files', '*.bplist'),('JSON Files', '*.json'),('Visual Studio Lists', '*.vslist')])
playlist_Path = playlist_Path.name
# print("Choose a name for Bulk Run (usually playlist name)")
# BulkRunName = input()



#--------------Setup--------------------------
setup.checkFolderPath()

with open(playlist_Path, encoding='utf8') as playlist_json:
    playlistRaw = json.load(playlist_json)
    
BulkRunName = playlistRaw['playlistTitle']
for i, index in enumerate(playlistRaw['songs']):
    hash_list.append(playlistRaw['songs'][i]['hash'])

for i, song in enumerate(hash_list):
    result = requests.get(f"https://api.beatsaver.com/maps/hash/{hash_list[i]}")
    resultJson = json.loads(result.text)
    try:
        song_id = resultJson["id"]
        
        if(hash_list[i].lower() != resultJson["versions"][0]["hash"].lower()):
            print(f"Hash {(resultJson['name'])} From Playlist Entry Doesn't match BeatSaver or is unavaliable")
            print("You seem to have an older version of this song?")
            print("The Results may be different due to possible different local map versus hosted map")
            print("If you just have an old entry but no song, a new version of the song will be downloaded but you'll need to update the playlist manually")
            print("Press Enter to Continue")
            #input()
        folder_path, song_diff = Rating_Algorithm.selectDiff(song_id)
        for i, index in enumerate(song_diff):
            queue_list.append([folder_path, index, song_id])

    except KeyError:
        if(resultJson["error"] == "Not Found"):
            print(f"Song Hash {hash_list[i]} Not Found!")
            print("Song was either deleted or doesn't exist")
            print("Press Enter to Continue")
            #input()

for i, index in enumerate(queue_list):
    diff_list.append(Rating_Algorithm.Main(index[0], index[1], index[2]))

for i, entry in enumerate(diff_list): #List Off all the songs, diffs, and scores
    print(diff_list[i])

#----------------------Export to CSV-----------------------------------------------#

setup.writeToExcel("BulkResults",BulkRunName,["Name", "Weighted/Score", "Median", "Average"],diff_list)

print("Press Enter to Exit")
input()



