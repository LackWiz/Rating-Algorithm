import Rating_Algorithm
import os
import csv
song_id = ["1", "c32d", "17914", "17cc0"]
diff_list = []
BulkRunName = "test"


# print("Name of Bulk Run")
# BulkRunName = input()

for i, song in enumerate(song_id):
    folder_path, song_diff = Rating_Algorithm.getSongPath(song_id[i])
    diff_list.append(Rating_Algorithm.Main(folder_path, song_diff, song_id[i]))

for i, entery in enumerate(diff_list):
    print(diff_list[i])

excelFileName = os.path.join(f"Bulk Results/{BulkRunName} export.csv")
try:
    f = open(excelFileName, 'w', newline="")
except FileNotFoundError:
    print('Making Bulk Results Folder')
    os.mkdir('Bulk Results')
    f = open(excelFileName, 'w', newline="")
finally:
    writer = csv.writer(f)
    writer.writerow(["Name", "Weighted/Score", "Median", "Average"])
    for diff_i in diff_list:
        writer.writerow(diff_i)
    f.close


print("Press Enter to Exit")
input()



