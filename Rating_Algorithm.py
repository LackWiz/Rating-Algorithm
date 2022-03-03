import statistics
import os
import json
import math
import csv
import MapDownloader
import Variables
import setup
#import tkinter as tk
#from tkinter.filedialog import askdirectory
# tk.Tk().withdraw()

angleDiv = 45

combinedArrayScale = 4.069

# Minimum precision (how close notes are together) to consider 2 very close notes a slider
sliderPrecision = 1/6
dotSliderPrecision = 1/5

swingSpeedS_LB = 32
patternRollingAverage = 128
staminaHistory = 256
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
    def __init__(self, type, cutDirection, bloqPos, startTime, swingTime, mspb):
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
        self.swingSpeedSmoothed = 0
        self.forehand = None
        self.angleDiff = Variables.ANGLE_EASY
        self.posDiff = Variables.SIDE_EASY
        self.angleChangeDiff = 0
        self.stackDiff = 0
        self.stamina = 0
        self.patternDiff = 0
        self.combinedDiff = 0
        self.combinedStamina = 0
        self.combinedSwingSpeedSmoothed = 0
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
                self.posDiff = [Variables.SIDE_SEMI_MID, Variables.SIDE_EASY,
                                Variables.SIDE_SEMI_MID, Variables.SIDE_MID][self.bloqPos[0]]
            elif(not self.forehand):
                self.posDiff = [Variables.SIDE_EASY, Variables.SIDE_SEMI_MID,
                                Variables.SIDE_SEMI_MID, Variables.SIDE_HARD][self.bloqPos[0]]

        elif(self.type == 1):  # Right Hand
            if(self.forehand):
                self.posDiff = [Variables.SIDE_MID, Variables.SIDE_SEMI_MID,
                                Variables.SIDE_EASY, Variables.SIDE_SEMI_MID][self.bloqPos[0]]
            elif(not self.forehand):
                self.posDiff = [Variables.SIDE_HARD, Variables.SIDE_MID,
                                Variables.SIDE_SEMI_MID, Variables.SIDE_EASY][self.bloqPos[0]]

        # Up and Down Diff
        self.posDiff *= [Variables.VERT_EASY, Variables.VERT_SEMI_MID,
                         Variables.VERT_MID][abs(2 * (not self.forehand) - self.bloqPos[1])]

    # TODO: shorten function
    def calcAngleDiff(self):
        if(self.type == 0):  # Left Hand
            if(self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 7, 8]):
                    self.angleDiff = Variables.ANGLE_EASY
                elif(self.cutDirection == 3):
                    self.angleDiff = Variables.ANGLE_SEMI_MID
                elif(self.cutDirection in [5, 6]):
                    self.angleDiff = Variables.ANGLE_MID
                elif(self.cutDirection in [0, 2]):
                    self.angleDiff = Variables.ANGLE_HARD
            elif(not self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 3]):
                    self.angleDiff = Variables.ANGLE_HARD
                elif(self.cutDirection in [5, 6]):
                    self.angleDiff = Variables.ANGLE_MID
                elif(self.cutDirection == 2):
                    self.angleDiff = Variables.ANGLE_SEMI_MID
                elif(self.cutDirection in [0, 4, 8]):
                    self.angleDiff = Variables.ANGLE_EASY
        elif(self.type == 1):  # Right Hand
            if(self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 6, 8]):
                    self.angleDiff = Variables.ANGLE_EASY
                elif(self.cutDirection == 2):
                    self.angleDiff = Variables.ANGLE_SEMI_MID
                elif(self.cutDirection in [4, 7]):
                    self.angleDiff = Variables.ANGLE_MID
                elif(self.cutDirection in [0, 3]):
                    self.angleDiff = Variables.ANGLE_HARD
            elif(not self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 2]):
                    self.angleDiff = Variables.ANGLE_HARD
                elif(self.cutDirection in [4, 7]):
                    self.angleDiff = Variables.ANGLE_MID
                elif(self.cutDirection == 3):
                    self.angleDiff = Variables.ANGLE_SEMI_MID
                elif(self.cutDirection in [0, 5, 8]):
                    self.angleDiff = Variables.ANGLE_EASY

    def calcStackDiff(self):
        if(self.angleChangeDiff >= Variables.ANGLE_MID):
            self.stackDiff = self.numNotes**Variables.NUM_NOTE_HARD_POWER
        else:
            self.stackDiff = self.numNotes**Variables.NUM_NOTE_EASY_POWER


def load_song_dat(path):
    with open(path, encoding='utf8') as json_dat:
        dat = json.load(json_dat)

    return dat


# TODO: sliding window instead of reactive (for future expansion)
def extractBloqData(songNoteArray, mspb):

    BloqDataArray: list[Bloq] = []

    for i, block in enumerate(songNoteArray):

        # Checks if the note behind is super close, and treats it as a single swing
        if i == 0:
            BloqDataArray.append(Bloq(
                block["_type"], block["_cutDirection"], [block["_lineIndex"], block["_lineLayer"]], block["_time"], block["_time"] * mspb, mspb))
            # Forehand if note is not in top section
            BloqDataArray[-1].setForehand(block['_lineLayer'] != 2)

        elif (block["_time"] - songNoteArray[i-1]['_time'] <= (dotSliderPrecision if block["_cutDirection"] == 8 else sliderPrecision)
              and (block['_cutDirection'] in [songNoteArray[i-1]['_cutDirection'], 8])) or ((block["_time"] - songNoteArray[i-1]['_time'] <= 1/32) 
              or (True if max(block["_cutDirection"],songNoteArray[i-1]['_cutDirection']) == 8 else abs(cut_direction_index[block['_cutDirection']]-cut_direction_index[songNoteArray[i-1]['_cutDirection']]) <= 45) and (block["_time"] - songNoteArray[i-1]['_time'] <= 1/4)):

            # Adds 1 to keep track of how many notes in a single swing
            BloqDataArray[-1].addNote()

        else:
            BloqDataArray.append(
                Bloq(block["_type"], block["_cutDirection"], [block["_lineIndex"], block["_lineLayer"]], block["_time"], 0, mspb))

            # If Left/Right/Dot, just toggle between forehand/backhand
            if BloqDataArray[-1].cutDirection in [2, 3, 8] or BloqDataArray[-1].forehand is None:
                BloqDataArray[-1].setForehand(not BloqDataArray[-2].forehand)

            # If Hands reset, e.g. bomb resets, bad mapping
            if(BloqDataArray[-1].forehand == BloqDataArray[-2].forehand):
                if((BloqDataArray[-1].cutDirection != 8) and (BloqDataArray[-2].cutDirection != 8)):
                    # Calculates Angle Change After parity. e.g. up and down is 0, but up to side is 90
                    BloqDataArray[-1].angleChange = abs(
                        cut_direction_index[BloqDataArray[-1].cutDirection]-cut_direction_index[BloqDataArray[-2].cutDirection])
            else:
                if((BloqDataArray[-1].cutDirection != 8) and (BloqDataArray[-2].cutDirection != 8)):
                    # Calculates Angle Change After parity. e.g. up and down is 0, but up to side is 90
                    BloqDataArray[-1].angleChange = abs(180-abs(
                        cut_direction_index[BloqDataArray[-1].cutDirection]-cut_direction_index[BloqDataArray[-2].cutDirection]))

            BloqDataArray[-1].angleChangeDiff = min(
                1+((max(BloqDataArray[-1].angleChange, 45)-45)/angleDiv)**2, 1.5)
            BloqDataArray[-1].calcStackDiff()
            # calculates swingTime in ms and Speed and shoves into class for processing later
            BloqDataArray[-1].swingTime = (BloqDataArray[-1].time -  # Swing time in ms
                                           BloqDataArray[-2].time)*mspb
            BloqDataArray[-1].swingSpeed = BloqDataArray[-1].swingAngle / \
                BloqDataArray[-1].swingTime  # Swing Speed in degrees/ms

            # Change in cut angle swing in degrees/millisecond
            BloqDataArray[-1].angleChangeTime = BloqDataArray[-1].angleChange / \
                (BloqDataArray[-1].swingTime)

            # TODO: move this elsewhere, should be part of processBloqData, not extract
            temp = 0
            # Uses a rolling average to asses peak swing speed
            for j in range(1, min(swingSpeedS_LB,len(BloqDataArray)-1)):
                if(len(BloqDataArray) >= j):
                    temp += (BloqDataArray[-1*j].swingSpeed)
            if(len(BloqDataArray) < swingSpeedS_LB):
                BloqDataArray[-1].swingSpeedSmoothed = (temp/len(BloqDataArray))
            else:
                BloqDataArray[-1].swingSpeedSmoothed = (temp/swingSpeedS_LB)
            temp = 0
            # Uses a rolling average to judge pattern difficulty
            for j in range(0, patternRollingAverage):
                if(len(BloqDataArray) >= j+1):
                    temp += (BloqDataArray[-1*(j+1)].angleDiff*BloqDataArray[-1*(j+1)].posDiff *
                             BloqDataArray[-1*(j+1)].angleChangeDiff*BloqDataArray[-1*(j+1)].stackDiff)
            # Helps Speed Up the Average Ramp, then does a proper average past staminaRollingAverage/4 and switches to the conventional rolling average after
            if(len(BloqDataArray) < patternRollingAverage/4):
                BloqDataArray[-1].patternDiff = (temp /
                                                 (patternRollingAverage/4))
            elif(len(BloqDataArray) < patternRollingAverage):
                BloqDataArray[-1].patternDiff = (temp/len(BloqDataArray))
            else:
                BloqDataArray[-1].patternDiff = (temp/patternRollingAverage)

    return BloqDataArray



def combineAndProcessArray(array1, array2):
    combinedArray: list[Bloq] = array1 + array2
    combinedArray.sort(key=lambda x: x.time) #once combined, sort by time
    for i in range(1, len(combinedArray)):
        combinedArray[i].combinedSwingSpeedSmoothed = math.sqrt(
            combinedArray[i].swingSpeedSmoothed**2 + combinedArray[i-1].swingSpeedSmoothed**2)
            # TODO Fix Combine function with new variables
        combinedArray[i].combinedDiff = math.sqrt(combinedArray[i].combinedSwingSpeedSmoothed**Variables.STAMINA_POWER + combinedArray[i].patternDiff**Variables.PATTERN_POWER) * min(
            math.sqrt(combinedArray[i].combinedSwingSpeedSmoothed**Variables.STAMINA_POWER), combinedArray[i].patternDiff**Variables.PATTERN_POWER)

    # TODO: change from n**2 to sliding window
    for i in range(0, len(combinedArray)):
        temp = 0
        # Uses a rolling average to smooth difficulties between the hands
        for j in range(0, min(combinedRollingAverage, i)):
            temp += combinedArray[i - min(combinedRollingAverage, j)].combinedDiff
        combinedArray[i].combinedDiffSmoothed = combinedArrayScale * temp/min(combinedRollingAverage, i+1)

    return combinedArray

def askSongID():
    print('Enter song ID:')
    song_id = input()
    return song_id

def findSongFolder(song_id):
    bsPath = setup.checkFolderPath()
    song_options = os.listdir(bsPath)
    songFound = False
    for song in song_options:
        if song.find(song_id) != -1:
            songFolder = song
            songFound = True
            break
    
    if not songFound:
        # TODO: download from scoresaber if map missing
        print(song_id + " Not Downloaded or wrong song code!")
        print("Would you like to download this song? (Y/N)")
        if(response := input().capitalize() == "Y"):
            if not (songFolder := MapDownloader.downloadSong(song_id, bsPath)):
                print(f"Download of {id} failed. Exiting...")
                exit()
        else:
            exit()
    return songFolder

def findDiffs(bsPath, songFolder):
    difficulties = os.listdir(bsPath + "/" + songFolder)
    difficulties = list(filter(lambda x: x.endswith(
        ".dat") and x.lower() != "info.dat", difficulties))
    difficulties = sorted(difficulties,key=Variables.DIFFICULTY_ORDER.index)
    return difficulties

def selectDiff(song_id):
    song_id = str(song_id)
    f = open('bs_path.txt', 'r')
    bsPath = f.read()
    f.close
    
    songFolder = findSongFolder(song_id)

    folder_path = bsPath + songFolder + '/'

    song_info = load_song_dat(folder_path + "Info.dat")
    difficulties = findDiffs(bsPath, songFolder)

    print(song_id+" "+song_info['_songName'], end= " ")
    print("Select a difficulty: ")
    for i in range(0, len(difficulties)):
        print(f"[{i + 1}] {difficulties[i]}")
    while (diff := int(input())) <= 0 or diff > len(difficulties):
        print(f"Input not in range 1-{len(difficulties)}, try again")
    song_diff = difficulties[diff - 1]
    print(song_diff)
    
    return folder_path, song_diff







def Main(folder_path, song_diff, song_id):
    song_id = str(song_id)
    song_dat = load_song_dat(folder_path + song_diff)
    song_info = load_song_dat(folder_path + "Info.dat")

    bpm = song_info['_beatsPerMinute']
    mspb = 60*1000/bpm  # milliseconds per beat

    # remove the bombs
    song_notes = list(filter(lambda x: x['_type'] in [0, 1], song_dat['_notes']))

    # split into red and blue notes
    songNoteLeft = [block for block in song_notes if block['_type'] == 0]
    songNoteRight = [block for block in song_notes if block['_type'] == 1]

    BloqDataLeft = extractBloqData(songNoteLeft,mspb)
    BloqDataRight = extractBloqData(songNoteRight,mspb)
    combinedArrayRaw = combineAndProcessArray(BloqDataLeft, BloqDataRight)

    SmoothDiff = [bloq.combinedDiffSmoothed for bloq in combinedArrayRaw]

    SmoothDiff.sort(reverse=True)
    top_1_percent = sum(
        SmoothDiff[:int(len(SmoothDiff)/100)])/int(len(SmoothDiff)/100)

    median = statistics.median(SmoothDiff)
    average = statistics.mean(SmoothDiff)
    final_score = (top_1_percent*7 + median*3)/10

    # export results to spreadsheet
    excelFileName = os.path.join(
        f"Spreadsheets/{song_id} {song_info['_songName']} {song_diff} export.csv")
    excelFileName.replace("*", "")
    try:
        f = open(excelFileName, 'w', newline="")
    except FileNotFoundError:
        print('Making Spreadsheets Folder')
        os.mkdir('Spreadsheets')
        f = open(excelFileName, 'w', newline="")


    finally:
        writer = csv.writer(f)
        writer.writerow(["TimeMS", "Beat", "Type", "Forehand", "numNotes", "SwingSpeed","SmoothSpeed", "Angle Diff", "AngleChangeDiff", "Pos Diff",
                        "Stamina", "Pattern Diff", "CombinedDiff", "SmoothedDiff","","Weighted","Median","Average"])
        writer.writerow(["","","",statistics.mean([bloq.forehand for bloq in combinedArrayRaw]),
            statistics.mean([bloq.numNotes for bloq in combinedArrayRaw]),
            statistics.mean([bloq.swingSpeed for bloq in combinedArrayRaw]),
            statistics.mean([bloq.swingSpeedSmoothed for bloq in combinedArrayRaw]),
            statistics.mean([bloq.angleDiff for bloq in combinedArrayRaw]),
            statistics.mean([bloq.angleChangeDiff for bloq in combinedArrayRaw]),
            statistics.mean([bloq.posDiff for bloq in combinedArrayRaw]),
            statistics.mean([bloq.combinedStamina for bloq in combinedArrayRaw]),
            statistics.mean([bloq.patternDiff for bloq in combinedArrayRaw]),
            statistics.mean([bloq.combinedDiff for bloq in combinedArrayRaw]),
            statistics.mean([bloq.combinedDiffSmoothed for bloq in combinedArrayRaw]),
            "",
            final_score,median,average])
        for bloq in combinedArrayRaw:
            writer.writerow([bloq.timeMS, bloq.time,  bloq.type, bloq.forehand, bloq.numNotes, bloq.swingSpeed,bloq.swingSpeedSmoothed, bloq.angleDiff, bloq.angleChangeDiff, bloq.posDiff,
                            bloq.combinedStamina, bloq.patternDiff, bloq.combinedDiff, bloq.combinedDiffSmoothed])
        f.close()
    final_score = str(final_score)
    median = str(median)
    average = str(average)
    #print(song_id+" "+song_info['_songName']+" "+song_diff)
    print("Weighted Score:" + final_score)
    print("Median:" + median)
    print("Average: " + average)
    
    return song_id+" "+song_info['_songName']+" "+song_diff, final_score, median, average




# Setup ------------------------------------------------------ #


# possible overlapping hashes bug





