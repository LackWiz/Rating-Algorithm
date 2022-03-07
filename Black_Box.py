import enum
import Rating_Algorithm
import setup
class Data:
    def __init__(self, songID, expectedResults):
        self.songID = songID
        self.expectedResults = expectedResults
        self.results = 0
        self.accuracy = 0
    def calcAccuracy(self):
        self.accuracy = self.results/self.expectedResults

DataArray: list[Data] = []

DataArray.append(Data("c32d",14))
DataArray.append(Data("170d0",7.5))
DataArray.append(Data("1e4b4",5))



setup.checkFolderPath()

for i, index in enumerate(DataArray):
    folder_path, song_diff = Rating_Algorithm.selectDiff(DataArray[i].songID)
    for j, jndex in enumerate(song_diff):
        print(song_diff[j])
        DataArray[j+i].results = (Rating_Algorithm.Main(folder_path, song_diff[j], DataArray[i].songID))
temp = 0
for i, index in enumerate(DataArray):
    DataArray[i].accuracy = 1-(abs(float(DataArray[i].results[1])-float(DataArray[i].expectedResults))/DataArray[i].expectedResults)
    temp += DataArray[i].accuracy

Accuracy = temp/len(DataArray)
print("Total Accuracy is: " + str(Accuracy))


# print("Press Enter to Exit")
# input()