from asyncio.windows_events import NULL
from copy import copy, deepcopy
import random
from tkinter import FIRST
import Rating_Algorithm
import setup
import Variables
import csv
import os




class Data:
    def __init__(self, songID, expectedResults):
        self.songID = songID
        self.expectedResults = expectedResults
        self.results = 0
        self.accuracy = 0
    def calcAccuracy(self):
        self.accuracy = self.results/self.expectedResults

class NewValues:
    def __init__(self, angle_easy, angle_semi_mid, angle_mid, angle_hard, side_easy, side_semi_mid, side_mid, side_hard,
        vert_easy, vert_semi_mid, vert_mid, stack_easy_power, stack_hard_power, stamina_power, pattern_power,
        SSSH, pattern_history, stamin_history, combined_history, angle_div, array_scaling):
        self.angle_easy = angle_easy
        self.angle_semi_mid = angle_semi_mid
        self.angle_mid = angle_mid
        self.angle_hard = angle_hard
        self.side_easy = side_easy
        self.side_semi_mid = side_semi_mid
        self.side_mid = side_mid
        self.side_hard = side_hard
        self.vert_easy = vert_easy
        self.vert_semi_mid = vert_semi_mid
        self.vert_mid = vert_mid
        self.stack_easy_power = stack_easy_power
        self.stack_hard_power = stack_hard_power
        self.stamina_power = stamina_power
        self.pattern_power = pattern_power
        self.SSSH = SSSH
        self.pattern_history = pattern_history
        self.stamina_history = stamin_history
        self.combined_history = combined_history
        self.angle_div = angle_div
        self.array_scaling = array_scaling
        self.Accuracy = 0
    # def __deepcopy__():


    def returnList(self):
        return[self.angle_easy,
            self.angle_semi_mid,
            self.angle_mid,
            self.angle_hard,
            self.side_easy,
            self.side_semi_mid,
            self.side_mid,
            self.side_hard,
            self.vert_easy,
            self.vert_semi_mid,
            self.vert_mid,
            self.stack_easy_power,
            self.stack_hard_power,
            self.stamina_power,
            self.pattern_power,
            self.SSSH,
            self.pattern_history,
            self.stamina_history,
            self.combined_history,
            self.angle_div,
            self.array_scaling,
            self.Accuracy]

setup.checkFolderPath()

DataArray: list[Data] = []
DataArray.append(Data("c32d",14)) #Lacks Data
DataArray.append(Data("170d0",7.5))
DataArray.append(Data("1e4b4",5))
DataArray.append(Data("190b4",17))
DataArray.append(Data("1df5b",12.75))
DataArray.append(Data("217a8",11))
DataArray.append(Data("18a92",9.65))
DataArray.append(Data("17cc0",10))
DataArray.append(Data("17ecf",7.5))

DataArray.append(Data("1db9d",13.25)) #Syncs Data
DataArray.append(Data("20540",12.9))
DataArray.append(Data("1f491",12.5))
DataArray.append(Data("18a27",12.4))

DataArray.append(Data("1a2cd",11.95)) #Score Saber Data
DataArray.append(Data("9e5c",11.77))
DataArray.append(Data("16d07",10.08))
DataArray.append(Data("1ace8",10.62))
DataArray.append(Data("1a017",13.22))
DataArray.append(Data("1a209",13.75))
DataArray.append(Data("22639",16))
DataArray.append(Data("20848",14))

Breadth = 1.1
SOIterations: list[NewValues] = []
AverageIteration: list[NewValues] = []
iterations = 25            #Number of gererations
passes = 100               #Number of children per generation
pass_history = 10           #Top picks to average for next generation

for j in range(0, iterations):
    ValueArray: list[NewValues] = []
    SOIterations.append(NewValues(NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL))   #Sum of Iterations
    First = True
    for i in range(0, passes):
        if First:
            ValueArray.append(NewValues(Variables.angle_Easy,Variables.angle_Semi_Mid,Variables.angle_Mid,Variables.angle_Hard,
                Variables.side_Easy,Variables.side_Semi_Mid,Variables.side_Mid,Variables.side_Hard,
                Variables.vert_Easy,Variables.vert_Semi_Mid,Variables.vert_Mid,Variables.stack_Easy_Power,Variables.stack_Hard_Power,
                Variables.stamina_Power,Variables.pattern_Power,Variables.swng_Sped_Smoth_History,Variables.pattern_History,
                Variables.stamina_History,Variables.combined_History,Variables.angle_Div, Variables.array_Scaling))
            First = False
        else:
            ValueArray.append(NewValues(
                random.uniform(Variables.angle_Easy/Breadth,Variables.angle_Easy*Breadth),
                random.uniform(Variables.angle_Semi_Mid/Breadth,Variables.angle_Semi_Mid*Breadth),
                random.uniform(Variables.angle_Mid/Breadth,Variables.angle_Mid*Breadth),
                random.uniform(Variables.angle_Hard/Breadth,Variables.angle_Hard*Breadth),
                random.uniform(Variables.side_Easy/Breadth,Variables.side_Easy*Breadth),
                random.uniform(Variables.side_Semi_Mid/Breadth,Variables.side_Semi_Mid*Breadth),
                random.uniform(Variables.side_Mid/Breadth,Variables.side_Mid*Breadth),
                random.uniform(Variables.side_Hard/Breadth,Variables.side_Hard*Breadth),
                random.uniform(Variables.vert_Easy/Breadth,Variables.vert_Easy*Breadth),
                random.uniform(Variables.vert_Semi_Mid/Breadth,Variables.vert_Semi_Mid*Breadth),
                random.uniform(Variables.vert_Mid/Breadth,Variables.vert_Mid*Breadth),
                random.uniform(Variables.stack_Easy_Power/Breadth,Variables.stack_Easy_Power*Breadth),
                random.uniform(Variables.stack_Hard_Power/Breadth,Variables.stack_Hard_Power*Breadth),
                random.uniform(Variables.stamina_Power/Breadth,Variables.stamina_Power*Breadth),
                random.uniform(Variables.pattern_Power/Breadth,Variables.pattern_Power*Breadth),
                round(random.uniform(Variables.swng_Sped_Smoth_History/Breadth,Variables.swng_Sped_Smoth_History*Breadth)),
                round(random.uniform(Variables.pattern_History/Breadth,Variables.pattern_History*Breadth)),
                round(random.uniform(Variables.stamina_History/Breadth,Variables.stamina_History*Breadth)),
                round(random.uniform(Variables.combined_History/Breadth,Variables.combined_History*Breadth)),
                random.uniform(Variables.angle_Div/Breadth,Variables.angle_Div*Breadth),
                random.uniform(Variables.array_Scaling/Breadth,Variables.array_Scaling*Breadth)
            ))
    First = True
    for Vars in ValueArray:
        
        Variables.angle_Easy = Vars.angle_easy
        Variables.angle_Semi_Mid = Vars.angle_semi_mid
        Variables.angle_Mid = Vars.angle_mid
        Variables.angle_Hard = Vars.angle_hard
        Variables.side_Easy = Vars.side_easy
        Variables.side_Semi_Mid = Vars.side_semi_mid
        Variables.side_Mid = Vars.side_mid
        Variables.side_Hard = Vars.side_hard
        Variables.vert_Easy = Vars.vert_easy
        Variables.vert_Semi_Mid = Vars.vert_semi_mid
        Variables.vert_Mid = Vars.vert_mid
        Variables.stack_Easy_Power = Vars.stack_easy_power
        Variables.stack_Hard_Power = Vars.stack_hard_power
        Variables.stamina_Power = Vars.stamina_power
        Variables.pattern_Power = Vars.pattern_power
        Variables.swng_Sped_Smoth_History = Vars.SSSH
        Variables.pattern_History = Vars.pattern_history
        Variables.stamina_History = Vars.stamina_history
        Variables.combined_History = Vars.combined_history
        Variables.angle_Div = Vars.angle_div
        Variables.array_Scaling = Vars.array_scaling
        
        for Data in DataArray:
            folder_path, song_diff = Rating_Algorithm.selectDiff(Data.songID, False, 1)
            Data.results = (Rating_Algorithm.Main(folder_path, song_diff[0], Data.songID, False))
        temp = 0
        for i, index in enumerate(DataArray):
            DataArray[i].accuracy = (abs(float(DataArray[i].results[1])-DataArray[i].expectedResults)/DataArray[i].expectedResults)**2
            temp += DataArray[i].accuracy
        Vars.Accuracy = temp/len(DataArray)
        print("Total Accuracy is: " + str(Vars.Accuracy))
    ValueArray.sort(key=lambda x: x.Accuracy)
    
    temp = 0
    SOIterations[0] = NewValues(NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)
    for i in range(0, pass_history):
        SOIterations[0].angle_easy += ValueArray[i].angle_easy
        SOIterations[0].angle_semi_mid += ValueArray[i].angle_semi_mid
        SOIterations[0].angle_mid += ValueArray[i].angle_mid
        SOIterations[0].angle_hard += ValueArray[i].angle_hard
        SOIterations[0].side_easy += ValueArray[i].side_easy
        SOIterations[0].side_semi_mid += ValueArray[i].side_semi_mid
        SOIterations[0].side_mid += ValueArray[i].side_mid
        SOIterations[0].side_hard += ValueArray[i].side_hard
        SOIterations[0].vert_easy += ValueArray[i].vert_easy
        SOIterations[0].vert_semi_mid += ValueArray[i].vert_semi_mid
        SOIterations[0].vert_mid += ValueArray[i].vert_mid
        SOIterations[0].stack_easy_power += ValueArray[i].stack_easy_power
        SOIterations[0].stack_hard_power += ValueArray[i].stack_hard_power
        SOIterations[0].stamina_power += ValueArray[i].stamina_power
        SOIterations[0].pattern_power += ValueArray[i].pattern_power
        SOIterations[0].SSSH += ValueArray[i].SSSH
        SOIterations[0].pattern_history += ValueArray[i].pattern_history
        SOIterations[0].stamina_history += ValueArray[i].stamina_history
        SOIterations[0].combined_history += ValueArray[i].combined_history
        SOIterations[0].angle_div += ValueArray[i].angle_div
        SOIterations[0].array_scaling += ValueArray[i].array_scaling
        SOIterations[0].Accuracy += ValueArray[i].Accuracy
    SOIterations[0].angle_easy = SOIterations[0].angle_easy/pass_history
    SOIterations[0].angle_semi_mid = SOIterations[0].angle_semi_mid/pass_history
    SOIterations[0].angle_mid = SOIterations[0].angle_mid/pass_history
    SOIterations[0].angle_hard = SOIterations[0].angle_hard/pass_history
    SOIterations[0].side_easy = SOIterations[0].side_easy/pass_history
    SOIterations[0].side_semi_mid = SOIterations[0].side_semi_mid/pass_history
    SOIterations[0].side_mid = SOIterations[0].side_mid/pass_history
    SOIterations[0].side_hard = SOIterations[0].side_hard/pass_history
    SOIterations[0].vert_easy = SOIterations[0].vert_easy/pass_history
    SOIterations[0].vert_semi_mid = SOIterations[0].vert_semi_mid/pass_history
    SOIterations[0].vert_mid = SOIterations[0].vert_mid/pass_history
    SOIterations[0].stack_easy_power = SOIterations[0].stack_easy_power/pass_history
    SOIterations[0].stack_hard_power = SOIterations[0].stack_hard_power/pass_history
    SOIterations[0].stamina_power = SOIterations[0].stamina_power/pass_history
    SOIterations[0].pattern_power = SOIterations[0].pattern_power/pass_history
    SOIterations[0].SSSH = SOIterations[0].SSSH/pass_history
    SOIterations[0].pattern_history = SOIterations[0].pattern_history/pass_history
    SOIterations[0].stamina_history = SOIterations[0].stamina_history/pass_history
    SOIterations[0].combined_history = SOIterations[0].combined_history/pass_history
    SOIterations[0].angle_div = SOIterations[0].angle_div/pass_history
    SOIterations[0].array_scaling = SOIterations[0].array_scaling/pass_history
    SOIterations[0].Accuracy = SOIterations[0].Accuracy/pass_history
    
    AverageIteration.append(deepcopy(SOIterations[0]))
    
    print("Iteration: " + str(j) +" Best Accuracy: "+ str(ValueArray[0].Accuracy))
    print("Iteration: " + str(j) +" Average Accuracy: "+ str(AverageIteration[-1].Accuracy))
    Variables.angle_Easy = AverageIteration[-1].angle_easy
    Variables.angle_Semi_Mid = AverageIteration[-1].angle_semi_mid
    Variables.angle_Mid = AverageIteration[-1].angle_mid
    Variables.angle_Hard = AverageIteration[-1].angle_hard
    Variables.side_Easy = AverageIteration[-1].side_easy
    Variables.side_Semi_Mid = AverageIteration[-1].side_semi_mid
    Variables.side_Mid = AverageIteration[-1].side_mid
    Variables.side_Hard = AverageIteration[-1].side_hard
    Variables.vert_Easy = AverageIteration[-1].vert_easy
    Variables.vert_Semi_Mid = AverageIteration[-1].vert_semi_mid
    Variables.vert_Mid = AverageIteration[-1].vert_mid
    Variables.stack_Easy_Power = AverageIteration[-1].stack_easy_power
    Variables.stack_Hard_Power = AverageIteration[-1].stack_hard_power
    Variables.stamina_Power = AverageIteration[-1].stamina_power
    Variables.pattern_Power = AverageIteration[-1].pattern_power
    Variables.swng_Sped_Smoth_History = AverageIteration[-1].SSSH
    Variables.pattern_History = AverageIteration[-1].pattern_history
    Variables.stamina_History = AverageIteration[-1].stamina_history
    Variables.combined_History = AverageIteration[-1].combined_history
    Variables.angle_Div = AverageIteration[-1].angle_div
    Variables.array_Scaling = AverageIteration[-1].array_scaling

folderName = "MachineLearning"
fileName = "Results"
headerList = ["angle_Easy","angle_Semi_Mid","angle_Mid","angle_Hard",'side_Easy','side_Semi_Mid','side_Mid','side_Hard',
    'vert_Easy','vert_Semi_Mid','vert_Mid','stack_Easy_Power','stack_Hard_Power','stamina_Power','pattern_Power',
    'SSSH','pattern_History','stamina_History','combined_History','angle_Div','array_scaling','Accuracy']

excelFileName = os.path.join(f"{folderName}/{fileName} export.csv")
try:
    x = open(excelFileName, 'w', newline="", encoding='utf8')
except FileNotFoundError:
    print(f'Making {folderName} Folder')
    os.mkdir(folderName)
    x = open(excelFileName, 'w', newline="")
finally:
    writer = csv.writer(x)
    writer.writerow(headerList)
    for i in range(0, len(AverageIteration)):
        writer.writerow(AverageIteration[i].returnList())
    x.close()





#setup.writeSingleToExcel("MachineLearning","Results",[""],ValueArray[0])









print("Press Enter to Exit")
input()