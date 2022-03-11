from asyncio.windows_events import NULL
from copy import  deepcopy
from math import ceil
import random
import time
import Rating_Algorithm
import setup
import Variables
import csv
import os
import multiprocessing



class Data: #Class to Hold Training Data and results
    def __init__(self, songID, expectedResults):
        self.songID = songID
        self.expectedResults = expectedResults
        self.results = 0
        self.accuracy = 0
        self.index = 0
    def calcAccuracy(self):
        self.accuracy = self.results/self.expectedResults

class NewValues:    #Class to Hold Data about Average Values at the end of each generation and values for each child in a generation
    def __init__(self, angle_easy, angle_semi_mid, angle_mid, angle_hard, side_easy, side_semi_mid, side_mid, side_hard,
        vert_easy, vert_semi_mid, vert_mid, stack_easy_power, stack_hard_power, stamina_power, pattern_power,
        SSSH, pattern_history, stamin_history, combined_history, angle_div,top1Weight, medianWeight, array_scaling):
        self.generation = 0
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
        self.top1Weight = top1Weight
        self.medianWeight = medianWeight
        self.Accuracy = 0

    def returnList(self):   #Returns all values from the class as a list
        return[
            self.generation,
            self.angle_easy,
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
            self.top1Weight,
            self.medianWeight,
            self.Accuracy]

def rate_func(songID, diff, Vars: NewValues): #Function that gets called for multiprocessing
    Variables.angle_Easy = Vars.angle_easy  #Copies all variables into the Global memory for Rating_Alrogithm
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
    Variables.Top1Weight = Vars.top1Weight
    Variables.MedianWeight = Vars.medianWeight
    Variables.array_Scaling = Vars.array_scaling
    folder_path, song_diff = Rating_Algorithm.selectDiff(songID, False, diff)
    return Rating_Algorithm.Main(folder_path, song_diff[0], songID, False)[1]   #Runs Rating _Algorithm and returns Weighted Result
    
    # print(str(return_Variable[index].results))
if __name__ == "__main__":
    setup.checkFolderPath() #Makes sure bs_path.txt is filled
#=======================================Training Data Template======================================#
    DataArray: list[Data] = []
    #Add data as "DataArray.append('songID', yourStarValue)""
    DataArray.append(Data("c32d",14)) #Lacks Data 
    DataArray.append(Data("170d0",7.5)) 
    DataArray.append(Data("1e4b4",5)) 
    # DataArray.append(Data("190b4",17)) 
    DataArray.append(Data("1df5b",12)) 
    DataArray.append(Data("217a8",10.25)) 
    DataArray.append(Data("18a92",9.25)) 
    DataArray.append(Data("17cc0",10))
    DataArray.append(Data("17ecf",7)) 
    DataArray.append(Data('1cb5f', 10.5))
    DataArray.append(Data('d6a6', 9.25))

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
    DataArray.append(Data('15836',9.5))
    DataArray.append(Data('9deb',8))
    DataArray.append(Data("17914",12.88))
    DataArray.append(Data('7d6c', 10.75))

    DataArray.append(Data("22639",16)) #Unranked from scoresaber discord
    # DataArray.append(Data("20848",14))
    for i in range(0,len(DataArray)):   #Adds an indexing number to each entry in the array
        DataArray[i].index=i
    BREADTH = 1.2   #How much, up and down to randomize initial values from Variables.py, not for Scaling Values
    WEIGHTEDBRANCH = 1.05   #How much, up and down to randomize initial values from Variables.py, only for Scaling values
    SOIterations: list[NewValues] = []
    AverageIteration: list[NewValues] = []
    GENERATIONS = 100           #Number of Gererations
    CHILDREN = 720               #Number of Children per generation
    TOP_PICKS = 20           #Top picks to average for next generation
    PROGRESS_SPLIT = 25        #How often to mark progress in the terminal (just a visual)

    maxProcesses = multiprocessing.cpu_count()  #Checks how many cores that are avaliable

    for j in range(0, GENERATIONS):  #Main loop, loops as many times as there are Generatoins
        NewBreadth = BREADTH-((BREADTH-1)*j/GENERATIONS)#Slowly Reduces randomizing spread after each generation
        progress_threshold = PROGRESS_SPLIT #as a percentage
        ValueArray: list[NewValues] = [] #Initializes/Empties List
        SOIterations.append(NewValues(NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)) #Adds an entry to the list so it can change numbers
        First = True
        start_time = time.time()    #For measuring time per child
        print("Breadth: " + str(NewBreadth))
        for i in range(0, CHILDREN):    #Child loop, Loops as many times as it needs for children to fill array with values to test
            if First:   #First Entry in Value Array is the same as the Top Average of the previous generation
                ValueArray.append(NewValues(Variables.angle_Easy,Variables.angle_Semi_Mid,Variables.angle_Mid,Variables.angle_Hard,
                    Variables.side_Easy,Variables.side_Semi_Mid,Variables.side_Mid,Variables.side_Hard,
                    Variables.vert_Easy,Variables.vert_Semi_Mid,Variables.vert_Mid,Variables.stack_Easy_Power,Variables.stack_Hard_Power,
                    Variables.stamina_Power,Variables.pattern_Power,Variables.swng_Sped_Smoth_History,Variables.pattern_History,
                    Variables.stamina_History,Variables.combined_History,Variables.angle_Div,Variables.Top1Weight,Variables.MedianWeight,Variables.array_Scaling))
                First = False
            else: # Assigns Random Values withn the Breadth of the Previous Generations Top Average
                ValueArray.append(NewValues(
                    random.uniform(Variables.angle_Easy/NewBreadth,Variables.angle_Easy*NewBreadth),
                    random.uniform(Variables.angle_Semi_Mid/NewBreadth,Variables.angle_Semi_Mid*NewBreadth),
                    random.uniform(Variables.angle_Mid/NewBreadth,Variables.angle_Mid*NewBreadth),
                    random.uniform(Variables.angle_Hard/NewBreadth,Variables.angle_Hard*NewBreadth),
                    random.uniform(Variables.side_Easy/NewBreadth,Variables.side_Easy*NewBreadth),
                    random.uniform(Variables.side_Semi_Mid/NewBreadth,Variables.side_Semi_Mid*NewBreadth),
                    random.uniform(Variables.side_Mid/NewBreadth,Variables.side_Mid*NewBreadth),
                    random.uniform(Variables.side_Hard/NewBreadth,Variables.side_Hard*NewBreadth),
                    random.uniform(Variables.vert_Easy/NewBreadth,Variables.vert_Easy*NewBreadth),
                    random.uniform(Variables.vert_Semi_Mid/NewBreadth,Variables.vert_Semi_Mid*NewBreadth),
                    random.uniform(Variables.vert_Mid/NewBreadth,Variables.vert_Mid*NewBreadth),
                    random.uniform(Variables.stack_Easy_Power/NewBreadth,Variables.stack_Easy_Power*NewBreadth),
                    random.uniform(Variables.stack_Hard_Power/NewBreadth,Variables.stack_Hard_Power*NewBreadth),
                    random.uniform(Variables.stamina_Power/NewBreadth,Variables.stamina_Power*NewBreadth),
                    random.uniform(Variables.pattern_Power/NewBreadth,Variables.pattern_Power*NewBreadth),
                    round(random.uniform(Variables.swng_Sped_Smoth_History/NewBreadth,Variables.swng_Sped_Smoth_History*NewBreadth)),
                    round(random.uniform(Variables.pattern_History/NewBreadth,Variables.pattern_History*NewBreadth)),
                    round(random.uniform(Variables.stamina_History/NewBreadth,Variables.stamina_History*NewBreadth)),
                    round(random.uniform(Variables.combined_History/NewBreadth,Variables.combined_History*NewBreadth)),
                    random.uniform(Variables.angle_Div/NewBreadth,Variables.angle_Div*NewBreadth),
                    random.uniform(Variables.Top1Weight/WEIGHTEDBRANCH,Variables.Top1Weight*WEIGHTEDBRANCH),
                    random.uniform(Variables.MedianWeight/WEIGHTEDBRANCH,Variables.MedianWeight*WEIGHTEDBRANCH),
                    random.uniform(Variables.array_Scaling/WEIGHTEDBRANCH,Variables.array_Scaling*WEIGHTEDBRANCH) 
                ))
        First = True
        for i, Vars in enumerate(ValueArray): #Main Child Loop, Goes through every entry in the ValueArray to test every combination of values in the array
            results = []
            processes = []
            input_param_list = []
            for a, data in enumerate(DataArray):    #Makes a parameter list to pass for multiprocessing
                input_param_list.append((data.songID, 1, Vars))
                
            with multiprocessing.Pool(maxProcesses) as p:   #Spawns child processes to utilize multi-core cpus
                results = p.starmap(rate_func, input_param_list)    #Returns result into results list

            for a, data in enumerate(DataArray):    #Copies results from multiprocessing into the DataArray
                data.results = results[a]
                # Data.results = rate_func(Data.songID, 1)
            temp = 0
            for data in DataArray:  #Accuracy Calculation, Based on a piecewise function to prevent single map outliers
                if data.songID == 'c32d':   #Extra weight for c32d if it exists, you can replace with map of choice or change 'c32d' to whatever song you'd like
                    data.accuracy = max(
                        (abs(float(data.results)-data.expectedResults)*28/data.expectedResults)**0.5,
                        (abs((float(data.results)-data.expectedResults)*28/data.expectedResults))**8)
                else:
                    data.accuracy = max(
                        (abs(float(data.results)-data.expectedResults)*28/data.expectedResults)**0.75,
                        (abs((float(data.results)-data.expectedResults)*28/data.expectedResults))**4)
                temp += data.accuracy
            Vars.Accuracy = temp/len(DataArray) #Averages all accuracies for this Child

            #print(str(round(k/passes*100, 2))+"% Total Accuracy is: " + str(Vars.Accuracy))
            if(round(i/CHILDREN*100,2) >= progress_threshold):  #For Printing Current Generation Progress
                progress_threshold += PROGRESS_SPLIT
                print("\nGeneration "+str(round(i/CHILDREN*100, 2))+"% Done")
            print(*"#", end="", flush=True)

        ValueArray.sort(key=lambda x: x.Accuracy)   #Sorts all Children by their accuracy
        temp = 0
        SOIterations[0] = NewValues(NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)
        for i in range(0, TOP_PICKS):   #There is a better way to do this but *shrug* Averages Top Picks and Averages them for the next Generation
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
            SOIterations[0].top1Weight += ValueArray[i].top1Weight
            SOIterations[0].medianWeight += ValueArray[i].medianWeight
            SOIterations[0].Accuracy += ValueArray[i].Accuracy
        SOIterations[0].angle_easy = SOIterations[0].angle_easy/TOP_PICKS
        SOIterations[0].angle_semi_mid = SOIterations[0].angle_semi_mid/TOP_PICKS
        SOIterations[0].angle_mid = SOIterations[0].angle_mid/TOP_PICKS
        SOIterations[0].angle_hard = SOIterations[0].angle_hard/TOP_PICKS
        SOIterations[0].side_easy = SOIterations[0].side_easy/TOP_PICKS
        SOIterations[0].side_semi_mid = SOIterations[0].side_semi_mid/TOP_PICKS
        SOIterations[0].side_mid = SOIterations[0].side_mid/TOP_PICKS
        SOIterations[0].side_hard = SOIterations[0].side_hard/TOP_PICKS
        SOIterations[0].vert_easy = SOIterations[0].vert_easy/TOP_PICKS
        SOIterations[0].vert_semi_mid = SOIterations[0].vert_semi_mid/TOP_PICKS
        SOIterations[0].vert_mid = SOIterations[0].vert_mid/TOP_PICKS
        SOIterations[0].stack_easy_power = SOIterations[0].stack_easy_power/TOP_PICKS
        SOIterations[0].stack_hard_power = SOIterations[0].stack_hard_power/TOP_PICKS
        SOIterations[0].stamina_power = SOIterations[0].stamina_power/TOP_PICKS
        SOIterations[0].pattern_power = SOIterations[0].pattern_power/TOP_PICKS
        SOIterations[0].SSSH = SOIterations[0].SSSH/TOP_PICKS
        SOIterations[0].pattern_history = SOIterations[0].pattern_history/TOP_PICKS
        SOIterations[0].stamina_history = SOIterations[0].stamina_history/TOP_PICKS
        SOIterations[0].combined_history = SOIterations[0].combined_history/TOP_PICKS
        SOIterations[0].angle_div = SOIterations[0].angle_div/TOP_PICKS
        SOIterations[0].array_scaling = SOIterations[0].array_scaling/TOP_PICKS
        SOIterations[0].top1Weight = SOIterations[0].top1Weight/TOP_PICKS
        SOIterations[0].medianWeight = SOIterations[0].medianWeight/TOP_PICKS
        SOIterations[0].Accuracy = SOIterations[0].Accuracy/TOP_PICKS
        SOIterations[0].generation = j+1
        AverageIteration.append(deepcopy(SOIterations[0]))
        endtime = time.time()
        print("\nIteration: " + str(j) +" Best Accuracy: "+ str(ValueArray[0].Accuracy))    #Prints the results from current generation
        print(f"Iteration: {str(j)} Average Accuracy: {str(AverageIteration[-1].Accuracy)}")
        print(f"Average Time per Set of Maps: {(endtime-start_time)/CHILDREN}")
        Variables.angle_Easy = AverageIteration[-1].angle_easy  #Assigns New Values for Next Generation
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
        Variables.Top1Weight = AverageIteration[-1].top1Weight
        Variables.MedianWeight = AverageIteration[-1].medianWeight
    finalMapAcc: list = []
    for data in DataArray:  #Gathering Data about the Full run
        folder_path, song_diff = Rating_Algorithm.selectDiff(data.songID, False, 1)
        mapReturn = Rating_Algorithm.Main(folder_path, song_diff[0], data.songID, False)[1]
        finalMapAcc.append([data.songID,data.expectedResults,mapReturn,mapReturn-data.expectedResults])


    #Excel shannagins
    folderName = "MachineLearning"
    fileName = "Results"
    accHeaderList = ['songID','Expected Acc','Results','Difference']
    headerList = ['Generation','angle_Easy','angle_Semi_Mid','angle_Mid','angle_Hard','side_Easy','side_Semi_Mid','side_Mid','side_Hard',
        'vert_Easy','vert_Semi_Mid','vert_Mid','stack_Easy_Power','stack_Hard_Power','stamina_Power','pattern_Power',
        'SSSH','pattern_History','stamina_History','combined_History','angle_Div','array_scaling','Top 1% Weight','Median Weight','Accuracy']

    excelFileName = os.path.join(f"{folderName}/{fileName} export.csv")
    try:
        x = open(excelFileName, 'w', newline="", encoding='utf8')
    except FileNotFoundError:
        print(f'Making {folderName} Folder')
        os.mkdir(folderName)
        x = open(excelFileName, 'w', newline="")
    finally:
        writer = csv.writer(x)
        writer.writerow(accHeaderList)
        writer.writerows(finalMapAcc)
        writer.writerow(headerList)
        for i in range(0, len(AverageIteration)):
            writer.writerow(AverageIteration[i].returnList())
        x.close()





#setup.writeSingleToExcel("MachineLearning","Results",[""],ValueArray[0])









    print("Press Enter to Exit")
    input()