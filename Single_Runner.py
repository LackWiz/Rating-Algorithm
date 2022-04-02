import Rating_Algorithm
import setup
print('Enter song ID, separate using comma for multiple songs:')
print("e.g. '25f'   or  'beef, 17cc0'")
songIDs = input()
setup.checkFolderPath()
songIDs = songIDs.replace(" ", "")
songIDs = songIDs.split(",")
print("Would you like to scale the rating by some amount away from scoresaber?")
scaler = input()
try:
    scaler = float(scaler)
except:
    scaler = 1
finally:
    for songID in songIDs:
        print('=============================================')
        folder_path, song_diff = Rating_Algorithm.selectDiff(songID)
        for i, index in enumerate(song_diff):
            print('-----------------------------------------------------------')
            print(song_diff[i])
            throwAway, ratedScore, throwAway, throwAway = Rating_Algorithm.Main(folder_path, song_diff[i], songID)
            print(f'Rated Score: {round(float(ratedScore)*scaler,2)}')
print("Press Enter to Exit")
input()