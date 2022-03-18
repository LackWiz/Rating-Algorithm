import Rating_Algorithm
import setup
print('Enter song ID, separate using comma for multiple songs:')
print("e.g. '25f'   or  'beef, 17cc0'")
songIDs = input()
setup.checkFolderPath()
songIDs = songIDs.replace(" ", "")
songIDs = songIDs.split(",")

for songID in songIDs:
    print('=============================================')
    folder_path, song_diff = Rating_Algorithm.selectDiff(songID)
    for i, index in enumerate(song_diff):
        print('-----------------------------------------------------------')
        print(song_diff[i])
        Rating_Algorithm.Main(folder_path, song_diff[i], songID)
print("Press Enter to Exit")
input()