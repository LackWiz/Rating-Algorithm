import statistics
import os
import json
import math
import csv
import MapDownloader
import Multi
#import tkinter as tk
#from tkinter.filedialog import askdirectory
#tk.Tk().withdraw()

angleDiv = 90

combinedArrayScale = 4.069

# Minimum precision (how close notes are together) to consider 2 very close notes a slider
sliderPrecision = 1/6
dotSliderPrecision = 1/5

staminaRollingAverage = 128
patternRollingAverage = 128
combinedRollingAverage = 128

cut_direction_index = [90, 270, 0, 180, 45, 135, 315, 225]

"""
https://bsmg.wiki/mapping/map-format.html#notes-2
"""

# _cutDirection
#   0 = North,
#   1 = South,
#   2 = West,
#   3 = East,
#   4 = NW,
#   5 = NE,
#   6 = SW,
#   7 = SE,
#   8 = Dot Note

# _lineIndex
#
# 0 = Far Left
# 1 = Center Left
# 2 = Center Right
# 3 = Far Right

# _lineLayer
#
# 0 = Bottom (you)
# 1 = Center
# 2 = Top (me)
# 


# Funcs ------------------------------------------------------ #


class Bloq:
    def __init__(self, type, cutDirection, bloqPos, startTime, swingTime):
        self.numNotes = 1
        self.type = type
        self.cutDirection = cutDirection
        self.angleChange = 0
        self.angleChangeTime = 0
        self.bloqPos = bloqPos
        self.swingAngle = 200
        self.time = startTime
        self.timeMS = self.time * mspb
        self.swingTime = swingTime
        self.swingSpeed = 0
        self.forehand = None
        self.angleDiff = Multi.ANGLE_EASY
        self.posDiff = Multi.SIDE_EASY
        self.angleChangeDiff = 0
        self.stackDiff = 0
        self.stamina = 0
        self.patternDiff = 0
        self.combinedDiff = 0
        self.combinedStamina = 0
        self.combinedDiffSmoothed = 0

        # Code below needs work
        # Non-negoitables, Up and a select diagonal is backhand
        if self.cutDirection in [0, 4, 5]:  # 4 = NW Left Hand, 5 = NE Right Hand
            if ((self.type == 0) & (self.cutDirection in [0, 4])):
                self.forehand = False
            elif ((self.type == 1) & (self.cutDirection in [0, 5])):
                self.forehand = False
            
        # Non-negoitables, Down and a select diagonal is forehand
        elif self.cutDirection in [1, 6, 7]:
            # 6 = SW Right Hand, 7 = SE Left Hand
            if ((self.type == 0) & (self.cutDirection in [1, 7])):
                self.forehand = True
            elif ((self.type == 1) & (self.cutDirection in [1, 6])):
                self.forehand = True
        
        self.calcAngleDiff()
        self.calcPosDiff()

    def addNote(self):
        self.numNotes += 1
        self.swingAngle += 36.87
        self.calcStackDiff()

    def setForehand(self, hand):
        self.forehand = hand
        self.calcAngleDiff()
        self.calcPosDiff()

    def calcPosDiff(self):  # Checks if position is easy, medium or difficult
        if(self.type == 0):  # Left Hand Side to Side Diff
            # LH centered around 2
            if(self.forehand):
                self.posDiff = [Multi.SIDE_SEMI_MID, Multi.SIDE_EASY, Multi.SIDE_SEMI_MID, Multi.SIDE_MID][self.bloqPos[0]]
            elif(not self.forehand):
                self.posDiff = [Multi.SIDE_EASY, Multi.SIDE_SEMI_MID, Multi.SIDE_SEMI_MID, Multi.SIDE_HARD][self.bloqPos[0]]
            
        elif(self.type == 1):  # Right Hand
            if(self.forehand):
                self.posDiff = [Multi.SIDE_MID, Multi.SIDE_SEMI_MID, Multi.SIDE_EASY, Multi.SIDE_SEMI_MID][self.bloqPos[0]]
            elif(not self.forehand):
                self.posDiff = [Multi.SIDE_HARD, Multi.SIDE_MID, Multi.SIDE_SEMI_MID, Multi.SIDE_EASY][self.bloqPos[0]]
        
        # Up and Down Diff
        self.posDiff *= [Multi.VERT_EASY, Multi.VERT_SEMI_MID,Multi.VERT_MID][abs(2 * (not self.forehand) - self.bloqPos[1])]

    # TODO: shorten function
    def calcAngleDiff(self):
        if(self.type == 0):  # Left Hand
            if(self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 7, 8]):
                    self.angleDiff = Multi.ANGLE_EASY
                elif(self.cutDirection == 3):
                    self.angleDiff = Multi.ANGLE_SEMI_MID
                elif(self.cutDirection in [5, 6]):
                    self.angleDiff = Multi.ANGLE_MID
                elif(self.cutDirection in [0, 2]):
                    self.angleDiff = Multi.ANGLE_HARD
            elif(not self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 3]):
                    self.angleDiff = Multi.ANGLE_HARD
                elif(self.cutDirection in [5, 6]):
                    self.angleDiff = Multi.ANGLE_MID
                elif(self.cutDirection == 2):
                    self.angleDiff = Multi.ANGLE_SEMI_MID
                elif(self.cutDirection in [0, 4, 8]):
                    self.angleDiff = Multi.ANGLE_EASY
        elif(self.type == 1):  # Right Hand
            if(self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 6, 8]):
                    self.angleDiff = Multi.ANGLE_EASY
                elif(self.cutDirection == 2):
                    self.angleDiff = Multi.ANGLE_SEMI_MID
                elif(self.cutDirection in [4, 7]):
                    self.angleDiff = Multi.ANGLE_MID
                elif(self.cutDirection in [0, 3]):
                    self.angleDiff = Multi.ANGLE_HARD
            elif(not self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 2]):
                    self.angleDiff = Multi.ANGLE_HARD
                elif(self.cutDirection in [4, 7]):
                    self.angleDiff = Multi.ANGLE_MID
                elif(self.cutDirection == 3):
                    self.angleDiff = Multi.ANGLE_SEMI_MID
                elif(self.cutDirection in [0, 5, 8]):
                    self.angleDiff = Multi.ANGLE_EASY

    def calcStackDiff(self):
        if(self.angleChangeDiff >= Multi.ANGLE_MID):
            self.stackDiff = self.numNotes**Multi.NUM_NOTE_HARD_POWER
        else:
            self.stackDiff = self.numNotes**Multi.NUM_NOTE_EASY_POWER 

        
def load_song_dat(path):
    with open(path, encoding = 'utf8') as json_dat:
        dat = json.load(json_dat)

    return dat


# TODO: sliding window instead of reactive (for future expansion)
def extractBloqData(songNoteArray):

    BloqDataArray: list[Bloq] = []

    for i, block in enumerate(songNoteArray):

        # Checks if the note behind is super close, and treats it as a single swing
        if i == 0:
            BloqDataArray.append(Bloq(
                block["_type"], block["_cutDirection"], [block["_lineIndex"], block["_lineLayer"]], block["_time"], block["_time"] * mspb))
            BloqDataArray[-1].setForehand(block['_lineLayer'] != 2) #Forehand if note is not in top section

        elif (block["_time"] - songNoteArray[i-1]['_time'] <= (dotSliderPrecision if block["_cutDirection"] == 8 else sliderPrecision)
              and (block['_cutDirection'] in [songNoteArray[i-1]['_cutDirection'], 8])) or (block["_time"] - songNoteArray[i-1]['_time'] <= 1/32):

            # Adds 1 to keep track of how many notes in a single swing
            BloqDataArray[-1].addNote()

        else:
            BloqDataArray.append(
                Bloq(block["_type"], block["_cutDirection"], [block["_lineIndex"], block["_lineLayer"]], block["_time"], 0))
            
            if BloqDataArray[-1].cutDirection in [2,3,8] or BloqDataArray[-1].forehand is None: #If Left/Right/Dot, just toggle between forehand/backhand
                BloqDataArray[-1].setForehand(not BloqDataArray[-2].forehand)

            if(BloqDataArray[-1].forehand == BloqDataArray[-2].forehand): #If Hands reset, e.g. bomb resets, bad mapping
                if((BloqDataArray[-1].cutDirection != 8) and (BloqDataArray[-2].cutDirection != 8)):
                    BloqDataArray[-1].angleChange = abs(cut_direction_index[BloqDataArray[-1].cutDirection]-cut_direction_index[BloqDataArray[-2].cutDirection]) #Calculates Angle Change After parity. e.g. up and down is 0, but up to side is 90
            else:
                if((BloqDataArray[-1].cutDirection != 8) and (BloqDataArray[-2].cutDirection != 8)):
                    BloqDataArray[-1].angleChange = abs(180-abs(cut_direction_index[BloqDataArray[-1].cutDirection]-cut_direction_index[BloqDataArray[-2].cutDirection])) #Calculates Angle Change After parity. e.g. up and down is 0, but up to side is 90

            BloqDataArray[-1].angleChangeDiff =  min(1+((max(BloqDataArray[-1].angleChange,45)-45)/angleDiv)**2,2)
            BloqDataArray[-1].calcStackDiff()
            # calculates swingTime in ms and Speed and shoves into class for processing later
            BloqDataArray[-1].swingTime = (BloqDataArray[-1].time - #Swing time in ms
                                           BloqDataArray[-2].time)*mspb
            BloqDataArray[-1].swingSpeed = BloqDataArray[-1].swingAngle/BloqDataArray[-1].swingTime #Swing Speed in degrees/ms
            
            BloqDataArray[-1].angleChangeTime = BloqDataArray[-1].angleChange/(BloqDataArray[-1].swingTime) #Change in cut angle swing in degrees/millisecond
            

            # TODO: move this elsewhere, should be part of processBloqData, not extract
            temp = 0
            # Uses a rolling average to judge stamina
            for j in range(0, staminaRollingAverage):
                if(len(BloqDataArray) >= j+1):
                    temp += (BloqDataArray[-1*(j+1)].swingSpeed)
            # Helps Speed Up the Average Ramp, then does a proper average past staminaRollingAverage/4 and switches to the conventional rolling average after
            if(len(BloqDataArray) < staminaRollingAverage/4):
                BloqDataArray[-1].stamina = (temp/(staminaRollingAverage/4))
            elif(len(BloqDataArray) < staminaRollingAverage):
                BloqDataArray[-1].stamina = (temp/len(BloqDataArray))
            else:
                BloqDataArray[-1].stamina = (temp/staminaRollingAverage)
            temp = 0
            # Uses a rolling average to judge pattern difficulty
            for j in range(0, patternRollingAverage):
                if(len(BloqDataArray) >= j+1):
                    temp += (BloqDataArray[-1*(j+1)].angleDiff*BloqDataArray[-1*(j+1)].posDiff*BloqDataArray[-1*(j+1)].angleChangeDiff*BloqDataArray[-1*(j+1)].stackDiff)
            # Helps Speed Up the Average Ramp, then does a proper average past staminaRollingAverage/4 and switches to the conventional rolling average after
            if(len(BloqDataArray) < patternRollingAverage/4):
                BloqDataArray[-1].patternDiff = (temp /
                                                 (patternRollingAverage/4))
            elif(len(BloqDataArray) < patternRollingAverage):
                BloqDataArray[-1].patternDiff = (temp/len(BloqDataArray))
            else:
                BloqDataArray[-1].patternDiff = (temp/patternRollingAverage)

    return BloqDataArray


# TODO: misleading function name
def combineArray(array1, array2):
    combinedArray: list[Bloq] = array1 + array2
    
    for i in range(1,len(combinedArray)):
        combinedArray[i].combinedStamina = math.sqrt(combinedArray[i].stamina**2 + combinedArray[i-1].stamina**2)
        combinedArray[i].combinedDiff = math.sqrt(combinedArray[i].combinedStamina**Multi.STAMINA_POWER + combinedArray[i].patternDiff**Multi.PATTERN_POWER) * min(math.sqrt(combinedArray[i].combinedStamina**Multi.STAMINA_POWER),combinedArray[i].patternDiff**Multi.PATTERN_POWER)

    combinedArray.sort(key=lambda x: x.time)

    # TODO: change from n**2 to sliding window
    for i in range(0, len(combinedArray)):
        temp = 0
        for j in range(0, min(combinedRollingAverage,i)): # Uses a rolling average to smooth difficulties between the hands
            temp += combinedArray[i-min(combinedRollingAverage,j)].combinedDiff
        combinedArray[i].combinedDiffSmoothed = combinedArrayScale*temp/min(combinedRollingAverage,i+1) # 6
    
    
    return combinedArray


# Setup ------------------------------------------------------ #
try:
    f = open('bs_path.txt', 'r')
    bsPath = f.read()
except FileNotFoundError:
    print('Enter Beat Saber custom songs folder:')
    # TODO: validate path
    #bsPath = askdirectory()
    bsPath = input()
    if bsPath[-1] not in ['\\', '/']:  # Checks if song path is empty
        bsPath += '/'
    f = open('bs_path.txt', 'w')
    dat = f.write(bsPath)
finally:
    f.close()

#possible overlapping hashes bug
print('Enter song ID:')
song_id = input()

song_options = os.listdir(bsPath)
songFound = False
for song in song_options:
    if song.find(song_id) != -1:
        songFolder = song
        songFound = True
        break

if not songFound:
    # TODO: download from scoresaber if map missing
    print("Not Downloaded or wrong song code!")
    print("Would you like to download this song? (Y/N)")
    if(response := input().capitalize() == "Y"):
        if not (songFolder := MapDownloader.downloadSong(song_id, bsPath)):
            print(f"Download of {id} failed. Exiting...")
            exit()
    else:
        exit()

difficulties = os.listdir(bsPath + "/" + songFolder)
difficulties = list(filter(lambda x : x.endswith(".dat") and x != "Info.dat", difficulties))

print("Select a difficulty: ")
for i in range(0, len(difficulties)):
    print(f"[{i + 1}] {difficulties[i]}")

while (diff := int(input())) <= 0 or diff > len(difficulties):
    print(f"Input not in range 1-{len(difficulties)}, try again")

song_diff = difficulties[diff - 1] 

#---------------Where Stuff Happens-----------------------------------------------------------------------------#

song_dat = load_song_dat(bsPath + songFolder + '/' + song_diff)
song_info = load_song_dat(bsPath + songFolder + "/Info.dat")

bpm = song_info['_beatsPerMinute']
mspb = 60*1000/bpm  # milliseconds per beat

# remove the bombs
song_notes = list(filter(lambda x: x['_type'] in [0, 1], song_dat['_notes']))

# split into red and blue notes
songNoteLeft = [block for block in song_notes if block['_type'] == 0]
songNoteRight = [block for block in song_notes if block['_type'] == 1]

BloqDataLeft = extractBloqData(songNoteLeft)
BloqDataRight = extractBloqData(songNoteRight)
combinedArrayRaw = combineArray(BloqDataLeft, BloqDataRight)

# export results to spreadsheet
excelFileName = os.path.join(
    f"Spreadsheets/{song_id} {song_info['_songName']} {song_diff} export.csv")

try:
    f = open(excelFileName, 'w', newline="")
except FileNotFoundError:
    print('Making Spreadsheets Folder')
    os.mkdir('Spreadsheets')
    f = open(excelFileName, 'w', newline="")
    
finally:
    writer = csv.writer(f)
    writer.writerow(["TimeMS","Beat","Type","Forehand","numNotes", "SwingSpeed", "Angle Diff", "AngleChangeDiff","Pos Diff",
                    "C Stamina", "C Pattern Diff", "C CombinedDiff", "C SmoothedDiff"])
    for bloq in combinedArrayRaw:
        writer.writerow([bloq.timeMS, bloq.time,  bloq.type, bloq.forehand, bloq.numNotes, bloq.swingSpeed, bloq.angleDiff, bloq.angleChangeDiff, bloq.posDiff,
                        bloq.combinedStamina, bloq.patternDiff, bloq.combinedDiff, bloq.combinedDiffSmoothed])
    f.close()


combinedArray = [bloq.combinedDiffSmoothed for bloq in combinedArrayRaw]

combinedArray.sort(reverse=True)
top_1_percent = sum(combinedArray[:int(len(combinedArray)/100)])/int(len(combinedArray)/100)

median = statistics.median(combinedArray)
final_score = (top_1_percent*7 + median*3)/10

print(final_score)
print("Press Enter to Exit!")
input()

# saber length is 1 meter
# distance between top and bottom notes is roughly 1.5m
# distance between side to side notes it roughly 2m
# totalSwingAnglec = 200degrees + numberOfBlocks * RadToDegrees(tan-1(0.75/1))

# Import song dat file✅
# Filter note dat file into Left and Right Block arrays✅
# Identify stacks/sliders (maybe pauls/poodles) and turn the 2-4 Blocks into a single Block with a large swing angle ✅
# Calculate Block distance into seconds or ms 73.74 ✅
# using 100 degree in, 60 degree out rule to calculate beginning and end points of the saber✅
# using swingtime, swingAngle and 1 meter saber length, calculate saber speed ✅
# List off hard swing angles for both hands + Appended angle diff to class✅

# Each swing entry for left and right hand array should contain
# Block[numberOfBlocks[1 to 4], cutDirection, totalAngleNeeded[160-273.74], timeForSwing(ms), ForeHand?]✅

# Final difficulty based on Total amount of notes, fastest swings using a rolling average of 4, angle difficulty average for whole map ✅
