import Rating_Algorithm

print('Enter song ID:')
songID = input()

folder_path, song_diff = Rating_Algorithm.getSongPath(songID)
Rating_Algorithm.Main(folder_path, song_diff, songID)


