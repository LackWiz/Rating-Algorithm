from asyncio.windows_events import NULL
from copy import  deepcopy
import random
import time
import Rating_Algorithm
import setup
import Variables
import csv
import os
import multiprocessing
import datetime


class Data: #Class to Hold Training Data and results
    def __init__(self, songID, expectedResults):
        self.songID = songID
        self.expectedResults = expectedResults
        self.results = 0
        self.accuracy = 0
        self.index = 0

class NewValues:    #Class to Hold Data about Average Values at the end of each generation and values for each child in a generation
    def __init__(self, 
    angle_easy, angle_semi_mid, angle_mid, angle_hard, 
    side_easy, side_semi_mid, side_mid, side_hard,
    vert_easy, vert_semi_mid, vert_mid, 
    angle_Div, 
    stack_easy_power, stack_hard_power, stamina_power, pattern_power,combined_stamina_root_power, combined_Root_Power, combined_min_root_power, angle_Power,
    SSSH, stamina_history, pattern_history, combined_history, stamina_weight, pattern_weight,
    top1Weight, top5Weight, top20Weight, medianWeight, array_scaling):
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

        self.angle_div = angle_Div

        self.stack_easy_power = stack_easy_power
        self.stack_hard_power = stack_hard_power
        self.stamina_power = stamina_power
        self.pattern_power = pattern_power
        self.combined_stamina_root_power = combined_stamina_root_power
        self.combined_root_power = combined_Root_Power
        self.combined_min_rool_power = combined_min_root_power
        self.angle_power = angle_Power

        self.SSSH = SSSH
        self.stamina_history = stamina_history
        self.pattern_history = pattern_history
        self.combined_history = combined_history
        
        self.stamina_weight = stamina_weight
        self.pattern_weight = pattern_weight

        self.top1Weight = top1Weight
        self.top5Weight = top5Weight
        self.top20Weight = top20Weight
        self.medianWeight = medianWeight
        self.array_scaling = array_scaling

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
            self.angle_div,
            self.stack_easy_power,
            self.stack_hard_power,
            self.stamina_power,
            self.pattern_power,
            self.combined_stamina_root_power,
            self.combined_root_power,
            self.combined_min_rool_power,
            self.angle_power,
            self.SSSH,
            self.stamina_history,
            self.pattern_history,
            self.combined_history,
            self.stamina_weight,
            self.pattern_weight,
            self.top1Weight,
            self.top5Weight,
            self.top20Weight,
            self.medianWeight,
            self.array_scaling,
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
    Variables.angle_Div = Vars.angle_div
    Variables.stack_Easy_Power = Vars.stack_easy_power
    Variables.stack_Hard_Power = Vars.stack_hard_power
    Variables.stamina_Power = Vars.stamina_power
    Variables.pattern_Power = Vars.pattern_power
    Variables.combined_stamina_root_power = Vars.combined_stamina_root_power
    Variables.combined_root_power = Vars.combined_root_power
    Variables.combined_min_root_power = Vars.combined_min_rool_power
    Variables.angle_Power = Vars.angle_power
    Variables.swng_Sped_Smoth_History = Vars.SSSH
    Variables.stamina_History = Vars.stamina_history
    Variables.pattern_History = Vars.pattern_history
    Variables.combined_History = Vars.combined_history
    Variables.stamina_Weight = Vars.stamina_weight
    Variables.Top1Weight = Vars.top1Weight
    Variables.Top5Weight = Vars.top5Weight
    Variables.Top20Weight = Vars.top20Weight
    Variables.MedianWeight = Vars.medianWeight
    Variables.array_Scaling = Vars.array_scaling
    folder_path, song_diff = Rating_Algorithm.selectDiff(songID, False, diff)
    return Rating_Algorithm.Main(folder_path, song_diff[0], songID, False)[1]   #Runs Rating _Algorithm and returns Weighted Result
    
def rand_func(Variable, Breadth):
    return random.uniform(Variable-(Variable*(Breadth-1)),Variable*Breadth)

    # print(str(return_Variable[index].results))
if __name__ == "__main__":
    setup.checkFolderPath() #Makes sure bs_path.txt is filled
#=======================================Training Data Template======================================#
    DataArray: list[Data] = []
    #Add data as "DataArray.append('songID', yourStarValue)""
    DataArray.append(Data('c32d',14)) #Lack's Data 
    DataArray.append(Data('170d0',7)) 
    DataArray.append(Data('1e4b4',5)) 
    DataArray.append(Data('169e6',11)) 
    DataArray.append(Data('1df5b',11.5)) 
    DataArray.append(Data('217a8',10.5)) 
    DataArray.append(Data('18a92',9)) 
    DataArray.append(Data('17cc0',9.75))
    DataArray.append(Data('17ecf',7)) 
    DataArray.append(Data('d6a6',9.25))
    DataArray.append(Data('1a37c',12.25))
    DataArray.append(Data('1dc95',11.9))
    DataArray.append(Data('1fa21',9.25))
    DataArray.append(Data('1d5d4',9.75))
    DataArray.append(Data('1dcc5',4))
    DataArray.append(Data('20fa4',9.5))
    DataArray.append(Data('19c66',8.75))

    DataArray.append(Data('1c1f7',17))

    DataArray.append(Data("1a2cd",11.95)) #Score Saber Data
    DataArray.append(Data("9e5c",11.77)) 
    DataArray.append(Data("16d07",10.75)) 
    DataArray.append(Data("1ace8",10.62)) 
    DataArray.append(Data("1a017",13.22)) 
    DataArray.append(Data("1a209",14.25)) 
    DataArray.append(Data('15836',9.5))
    DataArray.append(Data("17914",12.88))
    DataArray.append(Data('7d6c',10.75))

    # DataArray.append(Data("22639",16)) #Unranked from scoresaber discord
    # DataArray.append(Data("20848",14))
    for i in range(0,len(DataArray)):   #Adds an indexing number to each entry in the array
        DataArray[i].index=i
    START_BREADTH = 1.4   #How much, up and down to randomize initial values from Variables.py, not for Scaling Values
    END_BREADTH = 1.3
    WEIGHTEDBREADTH = 1.25   #How much, up and down to randomize initial values from Variables.py, only for Scaling values
    SOGenerations: list[NewValues] = []
    AverageIteration: list[NewValues] = []
    GENERATIONS = 20           #Number of Gererations
    CHILDREN = 10000               #Number of Children per generation
    TOP_PICKS = 100            #Top picks to average for next generation
    PROGRESS_SPLIT = 25        #How often to mark progress in the terminal as a percentage (just a visual)

    maxProcesses = multiprocessing.cpu_count()  #Checks how many cores that are avaliable

    for j in range(0, GENERATIONS):  #Main loop, loops as many times as there are Generatoins
        NewBreadth = START_BREADTH-((START_BREADTH-END_BREADTH)*j/GENERATIONS)#Slowly Reduces randomizing spread after each generation
        progress_threshold = PROGRESS_SPLIT #as a percentage
        ValueArray: list[NewValues] = [] #Initializes/Empties List
        SOGenerations.append(NewValues(NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)) #Adds an entry to the list so it can change numbers
        First = True
        start_time = time.time()    #For measuring time per child
        print(f"Breadth: {round(NewBreadth,5)}")
        for i in range(0, CHILDREN):    #Child loop, Loops as many times as it needs for children to fill array with values to test
            if First:   #First Entry in Value Array is the same as the Top Average of the previous generation
                ValueArray.append(NewValues(
                    Variables.angle_Easy,Variables.angle_Semi_Mid,Variables.angle_Mid,Variables.angle_Hard,
                    Variables.side_Easy,Variables.side_Semi_Mid,Variables.side_Mid,Variables.side_Hard,
                    Variables.vert_Easy,Variables.vert_Semi_Mid,Variables.vert_Mid,
                    Variables.angle_Div,
                    Variables.stack_Easy_Power,Variables.stack_Hard_Power,Variables.stamina_Power,Variables.pattern_Power,Variables.combined_stamina_root_power,Variables.combined_root_power,
                    Variables.combined_min_root_power,Variables.angle_Power,
                    Variables.swng_Sped_Smoth_History,Variables.stamina_History,Variables.pattern_History,Variables.combined_History,
                    Variables.stamina_Weight,Variables.pattern_Weight,Variables.Top1Weight,Variables.Top5Weight,Variables.Top20Weight,Variables.MedianWeight,Variables.array_Scaling))
                First = False
            else: # Assigns Random Values withn the Breadth of the Previous Generations Top Average
                ValueArray.append(NewValues(
                    rand_func(Variables.angle_Easy, NewBreadth),
                    rand_func(Variables.angle_Semi_Mid, NewBreadth),
                    rand_func(Variables.angle_Mid, NewBreadth),
                    rand_func(Variables.angle_Hard, NewBreadth),
                    rand_func(Variables.side_Easy, NewBreadth),
                    rand_func(Variables.side_Semi_Mid, NewBreadth),
                    rand_func(Variables.side_Mid, NewBreadth),
                    rand_func(Variables.side_Hard, NewBreadth),
                    rand_func(Variables.vert_Easy, NewBreadth),
                    rand_func(Variables.vert_Semi_Mid, NewBreadth),
                    rand_func(Variables.vert_Mid, NewBreadth),
                    round(rand_func(Variables.angle_Div, NewBreadth)),
                    rand_func(Variables.stack_Easy_Power, NewBreadth),
                    rand_func(Variables.stack_Hard_Power, NewBreadth),
                    rand_func(Variables.stamina_Power, NewBreadth),
                    rand_func(Variables.pattern_Power, NewBreadth),
                    rand_func(Variables.combined_stamina_root_power, NewBreadth),
                    rand_func(Variables.combined_root_power, NewBreadth),
                    rand_func(Variables.combined_min_root_power, NewBreadth),
                    rand_func(Variables.angle_Power, NewBreadth),
                    round(rand_func(Variables.swng_Sped_Smoth_History, NewBreadth)),
                    round(rand_func(Variables.stamina_History, NewBreadth)),
                    round(rand_func(Variables.pattern_History, NewBreadth)),
                    round(rand_func(Variables.combined_History, NewBreadth)),
                    rand_func(Variables.stamina_Weight, NewBreadth),
                    Variables.pattern_Weight,
                    rand_func(Variables.Top1Weight, WEIGHTEDBREADTH),
                    rand_func(Variables.Top5Weight, WEIGHTEDBREADTH),
                    rand_func(Variables.Top20Weight, WEIGHTEDBREADTH),
                    Variables.MedianWeight,
                    rand_func(Variables.array_Scaling, WEIGHTEDBREADTH),
                ))
            # ValueArray[-1].angle_mid = min(ValueArray[-1].angle_mid,ValueArray[-1].angle_hard)
            # ValueArray[-1].angle_semi_mid = min(ValueArray[-1].angle_semi_mid,ValueArray[-1].angle_mid)
            # ValueArray[-1].angle_easy = min(ValueArray[-1].angle_easy,ValueArray[-1].angle_semi_mid)
            # ValueArray[-1].side_mid = min(ValueArray[-1].side_mid,ValueArray[-1].side_hard)
            # ValueArray[-1].side_semi_mid = min(ValueArray[-1].side_semi_mid,ValueArray[-1].side_mid)
            # ValueArray[-1].side_easy = min(ValueArray[-1].side_easy,ValueArray[-1].side_semi_mid)
            # ValueArray[-1].vert_semi_mid = min(ValueArray[-1].vert_semi_mid,ValueArray[-1].vert_mid)
            # ValueArray[-1].vert_easy = min(ValueArray[-1].vert_easy,ValueArray[-1].vert_semi_mid)
            # ValueArray[-1].stack_easy_power = min(ValueArray[-1].stack_easy_power,ValueArray[-1].stack_hard_power)
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
                        (abs((float(data.results)-data.expectedResults)*8))**0.5,
                        (abs((float(data.results)-data.expectedResults)*8))**8)
                else:
                    data.accuracy = max(
                        (abs((float(data.results)-data.expectedResults)*4))**0.5,
                        (abs((float(data.results)-data.expectedResults)*4))**8)
                temp += data.accuracy
            Vars.Accuracy = temp/len(DataArray) #Averages all accuracies for this Child

            #print(str(round(k/passes*100, 2))+"% Total Accuracy is: " + str(Vars.Accuracy))
            if(round(i/CHILDREN*100,2) >= progress_threshold):  #For Printing Current Generation Progress
                progress_threshold += PROGRESS_SPLIT
                print("\nGeneration "+str(round(i/CHILDREN*100, 2))+"% Done")
            print(*"#", end="", flush=True)

        ValueArray.sort(key=lambda x: x.Accuracy)   #Sorts all Children by their accuracy
        temp = 0
        SOGenerations[0] = NewValues(NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL) #Sum of Generations
        for i in range(0, TOP_PICKS):   #There is a better way to do this but *shrug* Averages Top Picks and Averages them for the next Generation
            SOGenerations[0].angle_easy += ValueArray[i].angle_easy
            SOGenerations[0].angle_semi_mid += ValueArray[i].angle_semi_mid
            SOGenerations[0].angle_mid += ValueArray[i].angle_mid
            SOGenerations[0].angle_hard += ValueArray[i].angle_hard
            SOGenerations[0].side_easy += ValueArray[i].side_easy
            SOGenerations[0].side_semi_mid += ValueArray[i].side_semi_mid
            SOGenerations[0].side_mid += ValueArray[i].side_mid
            SOGenerations[0].side_hard += ValueArray[i].side_hard
            SOGenerations[0].vert_easy += ValueArray[i].vert_easy
            SOGenerations[0].vert_semi_mid += ValueArray[i].vert_semi_mid
            SOGenerations[0].vert_mid += ValueArray[i].vert_mid
            SOGenerations[0].angle_div += ValueArray[i].angle_div
            SOGenerations[0].stack_easy_power += ValueArray[i].stack_easy_power
            SOGenerations[0].stack_hard_power += ValueArray[i].stack_hard_power
            SOGenerations[0].stamina_power += ValueArray[i].stamina_power
            SOGenerations[0].pattern_power += ValueArray[i].pattern_power
            SOGenerations[0].combined_stamina_root_power += ValueArray[i].combined_stamina_root_power
            SOGenerations[0].combined_root_power += ValueArray[i].combined_root_power
            SOGenerations[0].combined_min_rool_power += ValueArray[i].combined_min_rool_power
            SOGenerations[0].angle_power += ValueArray[i].angle_power
            SOGenerations[0].SSSH += ValueArray[i].SSSH
            SOGenerations[0].stamina_history += ValueArray[i].stamina_history
            SOGenerations[0].pattern_history += ValueArray[i].pattern_history
            SOGenerations[0].combined_history += ValueArray[i].combined_history
            SOGenerations[0].stamina_weight += ValueArray[i].stamina_weight
            #pattern weight doesn't change
            SOGenerations[0].top1Weight += ValueArray[i].top1Weight
            SOGenerations[0].top5Weight += ValueArray[i].top5Weight
            SOGenerations[0].top20Weight += ValueArray[i].top20Weight
            #medianWeight doesn't change
            SOGenerations[0].array_scaling += ValueArray[i].array_scaling
            SOGenerations[0].Accuracy += ValueArray[i].Accuracy
        SOGenerations[0].angle_easy = SOGenerations[0].angle_easy/TOP_PICKS
        SOGenerations[0].angle_semi_mid = SOGenerations[0].angle_semi_mid/TOP_PICKS
        SOGenerations[0].angle_mid = SOGenerations[0].angle_mid/TOP_PICKS
        SOGenerations[0].angle_hard = SOGenerations[0].angle_hard/TOP_PICKS
        SOGenerations[0].side_easy = SOGenerations[0].side_easy/TOP_PICKS
        SOGenerations[0].side_semi_mid = SOGenerations[0].side_semi_mid/TOP_PICKS
        SOGenerations[0].side_mid = SOGenerations[0].side_mid/TOP_PICKS
        SOGenerations[0].side_hard = SOGenerations[0].side_hard/TOP_PICKS
        SOGenerations[0].vert_easy = SOGenerations[0].vert_easy/TOP_PICKS
        SOGenerations[0].vert_semi_mid = SOGenerations[0].vert_semi_mid/TOP_PICKS
        SOGenerations[0].vert_mid = SOGenerations[0].vert_mid/TOP_PICKS
        SOGenerations[0].angle_div = SOGenerations[0].angle_div/TOP_PICKS
        SOGenerations[0].stack_easy_power = SOGenerations[0].stack_easy_power/TOP_PICKS
        SOGenerations[0].stack_hard_power = SOGenerations[0].stack_hard_power/TOP_PICKS
        SOGenerations[0].stamina_power = SOGenerations[0].stamina_power/TOP_PICKS
        SOGenerations[0].pattern_power = SOGenerations[0].pattern_power/TOP_PICKS
        SOGenerations[0].combined_stamina_root_power = SOGenerations[0].combined_stamina_root_power/TOP_PICKS
        SOGenerations[0].combined_root_power = SOGenerations[0].combined_root_power/TOP_PICKS
        SOGenerations[0].combined_min_rool_power = SOGenerations[0].combined_min_rool_power/TOP_PICKS
        SOGenerations[0].angle_power = SOGenerations[0].angle_power/TOP_PICKS
        SOGenerations[0].SSSH = SOGenerations[0].SSSH/TOP_PICKS
        SOGenerations[0].stamina_history = SOGenerations[0].stamina_history/TOP_PICKS
        SOGenerations[0].pattern_history = SOGenerations[0].pattern_history/TOP_PICKS
        SOGenerations[0].combined_history = SOGenerations[0].combined_history/TOP_PICKS
        SOGenerations[0].stamina_weight = SOGenerations[0].stamina_weight/TOP_PICKS
        SOGenerations[0].pattern_weight = Variables.pattern_Weight
        SOGenerations[0].top1Weight = SOGenerations[0].top1Weight/TOP_PICKS
        SOGenerations[0].top5Weight = SOGenerations[0].top5Weight/TOP_PICKS
        SOGenerations[0].top20Weight = SOGenerations[0].top20Weight/TOP_PICKS
        SOGenerations[0].medianWeight = Variables.MedianWeight
        SOGenerations[0].array_scaling = SOGenerations[0].array_scaling/TOP_PICKS
        SOGenerations[0].Accuracy = SOGenerations[0].Accuracy/TOP_PICKS
        SOGenerations[0].generation = j+1
        AverageIteration.append(deepcopy(SOGenerations[0]))
        endtime = time.time()
        print(f"\nGeneration: {j+1} Best Accuracy: {round(ValueArray[0].Accuracy,3)}")    #Prints the results from current generation
        print(f"Generation: {j+1} Average Accuracy: {round(AverageIteration[-1].Accuracy,3)}")
        print(f"Average Time per Set of Maps: {round((endtime-start_time)/CHILDREN, 2)}")
        print(f"Estimated Remaining Time: {datetime.timedelta(seconds=round((GENERATIONS-(j+1))*(endtime-start_time),2))}")
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
        Variables.angle_Div = AverageIteration[-1].angle_div
        Variables.stack_Easy_Power = AverageIteration[-1].stack_easy_power
        Variables.stack_Hard_Power = AverageIteration[-1].stack_hard_power
        Variables.stamina_Power = AverageIteration[-1].stamina_power
        Variables.pattern_Power = AverageIteration[-1].pattern_power
        Variables.combined_stamina_root_power = AverageIteration[-1].combined_stamina_root_power
        Variables.combined_root_power = AverageIteration[-1].combined_root_power
        Variables.combined_min_root_power = AverageIteration[-1].combined_min_rool_power
        Variables.angle_Power = AverageIteration[-1].angle_power
        Variables.swng_Sped_Smoth_History = AverageIteration[-1].SSSH
        Variables.stamina_History = AverageIteration[-1].stamina_history
        Variables.pattern_History = AverageIteration[-1].pattern_history
        Variables.combined_History = AverageIteration[-1].combined_history
        Variables.stamina_Weight = AverageIteration[-1].stamina_weight
        #pattern weight doesn't change
        Variables.Top1Weight = AverageIteration[-1].top1Weight
        Variables.Top5Weight = AverageIteration[-1].top5Weight
        Variables.Top20Weight = AverageIteration[-1].top20Weight
        #medient weight doesn't change
        Variables.array_Scaling = AverageIteration[-1].array_scaling
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
        'vert_Easy','vert_Semi_Mid','vert_Mid','angle_Div',
        'stack_Easy_Power','stack_Hard_Power','stamina_Power','pattern_Power','Com_Stam_Root_Power','Com_Root_Power','Com_min_root_power','Angle Power',
        'SSSH','stamina_History','pattern_History','combined_History','stam_weight','pattern_weight','Top 1% Weight','Top 5% Weight','Top 20% Weight','Median Weight','array_scaling','Accuracy']
    
    pyFileName = os.path.join(f"{folderName}/Best Variables.py")
    v = open(pyFileName, "w+")
    v.write(f'angle_Easy = {ValueArray[0].angle_easy}\n')
    v.write(f'angle_Semi_Mid = {ValueArray[0].angle_semi_mid}\n')
    v.write(f'angle_Mid = {ValueArray[0].angle_mid}\n')
    v.write(f'angle_Hard = {ValueArray[0].angle_hard}\n\n')
    v.write(f'side_Easy = {ValueArray[0].side_easy}\n')
    v.write(f'side_Semi_Mid = {ValueArray[0].side_semi_mid}\n')
    v.write(f'side_Mid = {ValueArray[0].side_mid}\n')
    v.write(f'side_Hard = {ValueArray[0].side_hard}\n\n')
    v.write(f'vert_Easy = {ValueArray[0].vert_easy}\n')
    v.write(f'vert_Semi_Mid = {ValueArray[0].vert_semi_mid}\n')
    v.write(f'vert_Mid = {ValueArray[0].vert_mid}\n\n')
    v.write(f'angle_Div = {ValueArray[0].angle_div}\n\n')
    v.write(f'stack_Easy_Power = {ValueArray[0].stack_easy_power}\n')
    v.write(f'stack_Hard_Power = {ValueArray[0].stack_hard_power}\n')
    v.write(f'stamina_Power = {ValueArray[0].stamina_power}\n')
    v.write(f'pattern_Power = {ValueArray[0].pattern_power}\n')
    v.write(f'combined_stamina_root_power = {ValueArray[0].combined_stamina_root_power}\n')
    v.write(f'combined_root_power = {ValueArray[0].combined_root_power}\n')
    v.write(f'combined_min_root_power = {ValueArray[0].combined_min_rool_power}\n')
    v.write(f'angle_Power = {ValueArray[0].angle_power}\n\n')
    v.write(f'swng_Sped_Smoth_History = {ValueArray[0].SSSH}\n')
    v.write(f'stamina_History = {ValueArray[0].stamina_history}\n')
    v.write(f'pattern_History = {ValueArray[0].pattern_history}\n')
    v.write(f'combined_History = {ValueArray[0].combined_history}\n\n')
    v.write(f'stamina_Weight = {ValueArray[0].stamina_weight}\n')
    v.write(f'pattern_Weight = {ValueArray[0].pattern_weight}\n\n')
    v.write(f'Top1Weight = {ValueArray[0].top1Weight}\n')
    v.write(f'Top5Weight = {ValueArray[0].top5Weight}\n')
    v.write(f'Top20Weight = {ValueArray[0].top20Weight}\n')
    v.write(f'MedianWeight = {ValueArray[0].medianWeight}\n')
    v.write(f'array_Scaling = {ValueArray[0].array_scaling}\n')
    v.close()
    
    pyFileName = os.path.join(f"{folderName}/Average Variables.py")
    v = open(pyFileName, "w+")
    v.write(f'angle_Easy = {AverageIteration[-1].angle_easy}\n')
    v.write(f'angle_Semi_Mid = {AverageIteration[-1].angle_semi_mid}\n')
    v.write(f'angle_Mid = {AverageIteration[-1].angle_mid}\n')
    v.write(f'angle_Hard = {AverageIteration[-1].angle_hard}\n\n')
    v.write(f'side_Easy = {AverageIteration[-1].side_easy}\n')
    v.write(f'side_Semi_Mid = {AverageIteration[-1].side_semi_mid}\n')
    v.write(f'side_Mid = {AverageIteration[-1].side_mid}\n')
    v.write(f'side_Hard = {AverageIteration[-1].side_hard}\n\n')
    v.write(f'vert_Easy = {AverageIteration[-1].vert_easy}\n')
    v.write(f'vert_Semi_Mid = {AverageIteration[-1].vert_semi_mid}\n')
    v.write(f'vert_Mid = {AverageIteration[-1].vert_mid}\n\n')
    v.write(f'angle_Div = {AverageIteration[-1].angle_div}\n\n')
    v.write(f'stack_Easy_Power = {AverageIteration[-1].stack_easy_power}\n')
    v.write(f'stack_Hard_Power = {AverageIteration[-1].stack_hard_power}\n')
    v.write(f'stamina_Power = {AverageIteration[-1].stamina_power}\n')
    v.write(f'pattern_Power = {AverageIteration[-1].pattern_power}\n')
    v.write(f'combined_stamina_root_power = {AverageIteration[-1].combined_stamina_root_power}\n')
    v.write(f'combined_root_power = {AverageIteration[-1].combined_root_power}\n')
    v.write(f'combined_min_root_power = {AverageIteration[-1].combined_min_rool_power}\n')
    v.write(f'angle_Power = {AverageIteration[-1].angle_power}\n\n')
    v.write(f'swng_Sped_Smoth_History = {AverageIteration[-1].SSSH}\n')
    v.write(f'stamina_History = {AverageIteration[-1].stamina_history}\n')
    v.write(f'pattern_History = {AverageIteration[-1].pattern_history}\n')
    v.write(f'combined_History = {AverageIteration[-1].combined_history}\n\n')
    v.write(f'stamina_Weight = {AverageIteration[-1].stamina_weight}\n')
    v.write(f'pattern_Weight = {AverageIteration[-1].pattern_weight}\n\n')
    v.write(f'Top1Weight = {AverageIteration[-1].top1Weight}\n')
    v.write(f'Top5Weight = {AverageIteration[-1].top5Weight}\n')
    v.write(f'Top20Weight = {AverageIteration[-1].top20Weight}\n')
    v.write(f'MedianWeight = {AverageIteration[-1].medianWeight}\n')
    v.write(f'array_Scaling = {AverageIteration[-1].array_scaling}\n')
    v.close()

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