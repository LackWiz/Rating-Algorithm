# Rating-Algorithm
Welcome to the Rating-Algorithm wiki!

umm
1. install python and make sure PATH was selected on installation (on the first page of the intaller)
2. Download and unzip entire repository into a folder of choice
3. Shift+Right click in the working folder containing all the python files and click "Open Powershell Window Here"
4. Run: "*py -m pip install -r requirements.txt*" in powershell. This will download and install any missing modules/libraries
6. run script either Single_Rank.py (single songIDs) or Playlist_Rank.py (playlists)

The bs_path.txt file in _BackendFiles should contain one line: *your install directory*/Beat Saber/Beat Saber_Data/CustomLevels/

It'll spit out an CSV file with all the numbers you can graph in excel in a SpreadSheets and/or BlukResults folder

Errors might appear from 

1. Trying to re-write to a file that you have open
2. Having an older version of Python (this was coded using 3.10.2 so anything newer will work)
3. not have PATH option selected when you installed python, just re-install with that option selected
4. Not having the required modules (just run *py -m pip install -r requirements.txt* if you havn't before)
5. Really Weird Song/Map names
6. Trying to run Mod charts or Mapping extensions. These Maps are not supported (yet)


