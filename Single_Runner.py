import Rating_Algorithm
import setup
print('Enter song ID:')
songID = input()
setup.checkFolderPath()
folder_path, song_diff = Rating_Algorithm.selectDiff(songID)
for i, index in enumerate(song_diff):
    print(song_diff[i])
    Rating_Algorithm.Main(folder_path, song_diff[i], songID)
print("Press Enter to Exit")
input()