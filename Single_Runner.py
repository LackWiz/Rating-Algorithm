import Rating_Algorithm
import setup
print('Enter song ID:')
songID = input()
setup.checkFolderPath()
folder_path, song_diff = Rating_Algorithm.selectDiff(songID)
Rating_Algorithm.Main(folder_path, song_diff, songID)


