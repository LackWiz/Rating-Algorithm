from asyncio.windows_events import NULL
import statistics
import os
import json
import math
import csv
import _BackendFiles.MapDownloader as MapDownloader
import _BackendFiles.Variables as Variables
import _BackendFiles.setup as setup
from collections import deque
#import tkinter as tk
#from tkinter.filedialog import askdirectory
# tk.Tk().withdraw()

# Minimum precision (how close notes are together) to consider 2 very close notes a slider
sliderPrecision = 1/6
dotSliderPrecision = 1/5

cut_direction_index = [90, 270, 0, 180, 45, 135, 315, 225]
DIFFICULTY_ORDER = [
    "ExpertPlusStandard.dat",
    "ExpertPlus.dat",
    "ExpertStandard.dat",
    "Expert.dat",
    "HardStandard.dat",
    "Hard.dat",
    "NormalStandard.dat",
    "Normal.dat",
    "EasyStandard.dat",
    "Easy.dat",
    "ExpertPlusLawless.dat",
    "ExpertLawless.dat",
    "HardLawless.dat",
    "NormalLawless.dat",
    "EasyLawless.dat",
    "ExpertPlusNoArrows.dat",
    "ExpertNoArrows.dat",
    "HardNoArrows.dat",
    "NormalNoArrows.dat",
    "EasyNoArrows.dat",
    "ExpertPlus90Degree.dat",
    "Expert90Degree.dat",
    "Hard90Degree.dat",
    "Normal90Degree.dat",
    "Easy90Degree.dat",
    "90DegreeExpertPlus.dat",
    "90DegreeExpert.dat",
    "90DegreeHard.dat",
    "90DegreeNormal.dat",
    "90DegreeEasy.dat",
    "ExpertPlus360Degree.dat",
    "Expert360Degree.dat",
    "Hard360Degree.dat",
    "Normal360Degree.dat",
    "Easy360Degree.dat",
    "360DegreeExpertPlus.dat",
    "360DegreeExpert.dat",
    "360DegreeHard.dat",
    "360DegreeNormal.dat",
    "360DegreeEasy.dat",
    "ExpertPlusLightshow.dat",
    "ExpertLightshow.dat",
    "HardLightshow.dat",
    "NormalLightshow.dat",
    "EasyLightshow.dat",
    "Lightshow.dat",
    "*.dat"
]

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
        self.angleDiff = Variables.angle_Easy
        self.posDiff = Variables.side_Easy
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

    def setForehand(self, hand, distance):
        self.forehand = hand
        self.calcAngleDiff()
        self.calcPosDiff(distance)

    def calcPosDiff(self, distance = 0):  # Checks if position is easy, medium or difficult based on inhearent position and distance from last note
        try:
            if(self.type == 0):  # Left Hand Side to Side Diff
                # LH centered around 2
                if(self.forehand):
                    self.posDiff = [Variables.side_Semi_Mid, Variables.side_Easy,
                                    Variables.side_Semi_Mid, Variables.side_Mid][self.bloqPos[0]]
                elif(not self.forehand):
                    self.posDiff = [Variables.side_Easy, Variables.side_Semi_Mid,
                                    Variables.side_Semi_Mid, Variables.side_Hard][self.bloqPos[0]]

            elif(self.type == 1):  # Right Hand
                if(self.forehand):
                    self.posDiff = [Variables.side_Mid, Variables.side_Semi_Mid,
                                    Variables.side_Easy, Variables.side_Semi_Mid][self.bloqPos[0]]
                elif(not self.forehand):
                    self.posDiff = [Variables.side_Hard, Variables.side_Mid,
                                    Variables.side_Semi_Mid, Variables.side_Easy][self.bloqPos[0]]

            # Up and Down Diff
            self.posDiff == min(self.posDiff * [Variables.vert_Easy, Variables.vert_Semi_Mid,
                             Variables.vert_Mid][abs(2 * (not self.forehand) - self.bloqPos[1])] * (distance+1)/3, 10)
        except:
            self.posDiff = 1

    # TODO: shorten function
    def calcAngleDiff(self):
        if(self.type == 0):  # Left Hand
            if(self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 7, 8]):
                    self.angleDiff = Variables.angle_Easy
                elif(self.cutDirection == 3):
                    self.angleDiff = Variables.angle_Semi_Mid
                elif(self.cutDirection in [5, 6]):
                    self.angleDiff = Variables.angle_Mid
                elif(self.cutDirection in [0, 2]):
                    self.angleDiff = Variables.angle_Hard
            elif(not self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 3]):
                    self.angleDiff = Variables.angle_Hard
                elif(self.cutDirection in [5, 6]):
                    self.angleDiff = Variables.angle_Mid
                elif(self.cutDirection == 2):
                    self.angleDiff = Variables.angle_Semi_Mid
                elif(self.cutDirection in [0, 4, 8]):
                    self.angleDiff = Variables.angle_Easy
        elif(self.type == 1):  # Right Hand
            if(self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 6, 8]):
                    self.angleDiff = Variables.angle_Easy
                elif(self.cutDirection == 2):
                    self.angleDiff = Variables.angle_Semi_Mid
                elif(self.cutDirection in [4, 7]):
                    self.angleDiff = Variables.angle_Mid
                elif(self.cutDirection in [0, 3]):
                    self.angleDiff = Variables.angle_Hard
            elif(not self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 2]):
                    self.angleDiff = Variables.angle_Hard
                elif(self.cutDirection in [4, 7]):
                    self.angleDiff = Variables.angle_Mid
                elif(self.cutDirection == 3):
                    self.angleDiff = Variables.angle_Semi_Mid
                elif(self.cutDirection in [0, 5, 8]):
                    self.angleDiff = Variables.angle_Easy

    def calcStackDiff(self):
        if(self.angleChangeDiff >= Variables.angle_Mid):
            self.stackDiff = self.numNotes**Variables.stack_Hard_Power
        else:
            self.stackDiff = self.numNotes**Variables.stack_Easy_Power


def load_song_dat(path):
    with open(path, 'rb') as json_dat:
        dat = json.loads(json_dat.read())
        # dat = json.load(json_dat)
    return dat

def findSongFolder(song_id, isuser):
    bsPath = setup.checkFolderPath()
    song_options = os.listdir(bsPath)
    songFound = False
    for song in song_options:
        if song.startswith(song_id+" "):
            songFolder = song
            songFound = True
            break
    if not songFound:
        # TODO: download from scoresaber if map missing
        if isuser:
            print(song_id + " Not Downloaded or wrong song code!")
            print("Would you like to download this song? (Y/N)")
            if(response := input().capitalize() == "Y"):
                if not (songFolder := MapDownloader.downloadSong(song_id, bsPath)):
                    print(f"Download of {song_id} failed. Exiting...")
                    input()
                    exit()
            else:
                exit()
        else:
            print(f'Downloading Missing song {song_id}')
            if not (songFolder := MapDownloader.downloadSong(song_id, bsPath)):
                print(f"Download of {song_id} failed. Exiting...")
                input()
                exit()
    return songFolder


def findDiffs(bsPath, songFolder):
    difficulties = os.listdir(bsPath + "/" + songFolder)
    difficulties = list(filter(lambda x: x.endswith(
        ".dat") and x.lower() != "info.dat", difficulties))
    try:
        difficulties = sorted(difficulties, key=DIFFICULTY_ORDER.index)
    except ValueError:
        print("Couldn't Sort LOOK AT NUMBERING")
    return difficulties


def selectDiff(song_id, user=True, lock_diff=NULL):
    song_diff = []
    song_id = str(song_id)
    lock_diff = str(lock_diff)
    f = open('_BackendFiles/bs_path.txt', 'r')
    bsPath = f.read()
    f.close

    songFolder = findSongFolder(song_id, isuser=user)

    folder_path = bsPath + songFolder + '/'

    song_info = load_song_dat(folder_path + "Info.dat")
    difficulties = findDiffs(bsPath, songFolder)
    if user:
        print(song_id+" "+song_info['_songName'], end=" ")
        print("Select a difficulty, separate using comma for multiple diffs:")
        print("e.g. 'a'   or  '2,3,4'     or  '1'")
        print("[a] for all diffs")
        for i in range(0, len(difficulties)):
            print(f"[{i + 1}] {difficulties[i]}")
    if lock_diff == '0':
        selectedDiffs = input()  # To enable choice of difficulty
    else:
        selectedDiffs = lock_diff  # To Lock in Some Difficulty
    if selectedDiffs != "a":
        selectedDiffs = selectedDiffs.replace(" ", "")
        selectedDiffs = selectedDiffs.split(",")
        while all(int(flag) <= 0 for (flag) in selectedDiffs) or all(int(flag) > len(difficulties) for (flag) in selectedDiffs):
            print(f"Input not in range 1-{len(difficulties)}, try again")
            selectedDiffs = input()
            selectedDiffs = selectedDiffs.replace(" ", "")
            selectedDiffs = selectedDiffs.split(",")
    else:
        selectedDiffs = []
        for i, index in enumerate(difficulties):
            selectedDiffs.append(i+1)
    for i, index in enumerate(selectedDiffs):
        song_diff.append(difficulties[int(index) - 1])
    if user:
        print(song_diff)
    return folder_path, song_diff

# TODO: sliding window instead of reactive (for future expansion)


def extractBloqData(songNoteArray, bpm_list: list):

    BloqDataArray: list[Bloq] = []
    t = 0  # To keep track of what bpm to use
    mspb = 60*1000/bpm_list[0]  # Uses ms per beat for all calculations
    for i, block in enumerate(songNoteArray):
        block['_cutDirection'] = min(block['_cutDirection'], 8)
        # Checks if the note behind is super close, and treats it as a single swing
        if i == 0:
            BloqDataArray.append(Bloq(
                block["_type"], block["_cutDirection"], [block["_lineIndex"], block["_lineLayer"]], block["_time"], block["_time"] * mspb, mspb))
            # Forehand if note is not in top section
            BloqDataArray[-1].setForehand(block['_lineLayer'] != 2, 0)

        elif (block["_time"] - songNoteArray[i-1]['_time'] <= (dotSliderPrecision if block["_cutDirection"] == 8 else sliderPrecision)
              and (block['_cutDirection'] in [songNoteArray[i-1]['_cutDirection'], 8])) or ((block["_time"] - songNoteArray[i-1]['_time'] <= 1/32)
                                                                                            or (True if max(block["_cutDirection"], songNoteArray[i-1]['_cutDirection']) == 8 else abs(cut_direction_index[block['_cutDirection']]-cut_direction_index[songNoteArray[i-1]['_cutDirection']]) <= 45) and (block["_time"] - songNoteArray[i-1]['_time'] <= 1/4)):

            # Adds 1 to keep track of how many notes in a single swing
            BloqDataArray[-1].addNote()

        else:
            BloqDataArray.append(
                Bloq(block["_type"], block["_cutDirection"], [block["_lineIndex"], block["_lineLayer"]], block["_time"], 0, mspb))

            # If Left/Right/Dot, just toggle between forehand/backhand
            if BloqDataArray[-1].cutDirection in [2, 3, 8] or BloqDataArray[-1].forehand is None:
                BloqDataArray[-1].setForehand(not BloqDataArray[-2].forehand, math.sqrt((block["_lineIndex"] - songNoteArray[i-1]["_lineIndex"])**2 + (block["_lineLayer"]-songNoteArray[i-1]["_lineLayer"])**2))

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
                1+((max(BloqDataArray[-1].angleChange, 45)-45)/Variables.angle_Div)**Variables.angle_Power, 1.5)
            BloqDataArray[-1].calcStackDiff()
            # calculates swingTime in ms and Speed and shoves into class for processing later
            BloqDataArray[-1].swingTime = (BloqDataArray[-1].time -  # Swing time in ms
                                           BloqDataArray[-2].time)*mspb
            BloqDataArray[-1].swingSpeed = BloqDataArray[-1].swingAngle / \
                BloqDataArray[-1].swingTime  # Swing Speed in degrees/ms

            # Change in cut angle swing in degrees/millisecond
            BloqDataArray[-1].angleChangeTime = BloqDataArray[-1].angleChange / \
                (BloqDataArray[-1].swingTime)

    return BloqDataArray


# Uses a rolling average to assess peak swing speed
def processArray(array: list[Bloq]):
    SSS = 0  # Sum of Swing Speed
    qSSS = deque()  # queue
    SPD = 0  # Sum of Pattern Diff
    qSPD = deque()  # queue
    for i in range(0, len(array)):
        if(i >= Variables.swng_Sped_Smoth_History):
            SSS -= qSSS.popleft()
        qSSS.append(array[i].swingSpeed)
        SSS += qSSS[-1]
        array[i].swingSpeedSmoothed = (
            SSS/min(i+1, Variables.swng_Sped_Smoth_History))

        if(i >= Variables.pattern_History):
            SPD -= qSPD.popleft()
        qSPD.append(array[i].angleDiff*array[i].posDiff *
                    array[i].angleChangeDiff*array[i].stackDiff)
        SPD += qSPD[-1]
    # Helps Speed Up the Average Ramp, then does a proper average past patternRollingAverage/4 and switches to the conventional rolling average after
        if(i < Variables.pattern_History/4):
            array[i].patternDiff = (SPD/(Variables.pattern_History/4))
        elif(i < Variables.pattern_History):
            array[i].patternDiff = (SPD/i)
        else:
            array[i].patternDiff = (SPD/Variables.pattern_History)


def combineAndProcessArray(array1, array2):
    processArray(array1)
    processArray(array2)
    combinedArray: list[Bloq] = array1 + array2
    combinedArray.sort(key=lambda x: x.time)  # once combined, sort by time
    for i in range(1, len(combinedArray)):
        combinedArray[i].combinedSwingSpeedSmoothed = (
            combinedArray[i].swingSpeedSmoothed**2 + combinedArray[i-1].swingSpeedSmoothed**2)**(1/Variables.combined_stamina_root_power)
        # TODO Fix Combine function with new variables
        combinedArray[i].combinedDiff = (((Variables.stamina_Weight*combinedArray[i].combinedSwingSpeedSmoothed**Variables.stamina_Power + Variables.pattern_Weight*combinedArray[i].patternDiff**Variables.pattern_Power)/(Variables.stamina_Weight+Variables.pattern_Weight))**(1/Variables.combined_root_power)) * (min(
            combinedArray[i].combinedSwingSpeedSmoothed**Variables.stamina_Power, combinedArray[i].patternDiff**Variables.pattern_Power)**(1/Variables.combined_min_root_power))

    SCA = 0  # Sum of Combined Array
    qCA = deque()
    for i in range(0, len(combinedArray)):
        if(i >= Variables.combined_History):
            SCA -= qCA.popleft()
        qCA.append(combinedArray[i].combinedDiff)
        SCA += qCA[-1]
        combinedArray[i].combinedDiffSmoothed = Variables.array_Scaling * \
            (SCA/min(i+1, Variables.combined_History))

    return combinedArray


def Main(folder_path, song_diff, song_id, user=True):
    song_id = str(song_id)
    song_dat = load_song_dat(folder_path + song_diff)
    song_info = load_song_dat(folder_path + "Info.dat")
    bpm = song_info['_beatsPerMinute']

    # Keep only the notes
    try:
        song_notes = list(
            filter(lambda x: x['_type'] in [0, 1], song_dat['_notes']))
    except:
        song_notes = []
        if user:
            print("No _note data found: Cannot Deal with 3.0.0 maps")
    try:
        song_bpm_list = list(song_dat['_customData']['_BPMChanges'])
        song_bpm_list.insert(0, bpm)  # Put Initial BPM at front of List
        if user:
            print("Found BPM changes")
    except:
        song_bpm_list = [bpm]
        if user:
            print("No BPM changes")
    # split into red and blue notes
    songNoteLeft = [block for block in song_notes if block['_type'] == 0]
    songNoteRight = [block for block in song_notes if block['_type'] == 1]

    BloqDataLeft = extractBloqData(songNoteLeft, song_bpm_list)
    BloqDataRight = extractBloqData(songNoteRight, song_bpm_list)
    combinedArrayRaw = combineAndProcessArray(BloqDataLeft, BloqDataRight)

    SmoothDiff = [bloq.combinedDiffSmoothed for bloq in combinedArrayRaw]

    SmoothDiff.sort(reverse=True)
    Failed = False
    try:
        top_1_percent = sum(
            SmoothDiff[:int(len(SmoothDiff)/100)])/(len(SmoothDiff)/100)
    except ZeroDivisionError:
        top_1_percent = "Cannot Divide by Zero"
        Failed = True
    try:
        top_5_percent = sum(
            SmoothDiff[:int(len(SmoothDiff)/100)])/(len(SmoothDiff)/100)
    except ZeroDivisionError:
        top_5_percent = "Cannot Divide by Zero"
        Failed = True
    try:
        top_20_percent = sum(
            SmoothDiff[:int(len(SmoothDiff)/100)])/(len(SmoothDiff)/100)
    except ZeroDivisionError:
        top_20_percent = "Cannot Divide by Zero"
        Failed = True
    try:
        median = statistics.median(SmoothDiff)
        average = statistics.mean(SmoothDiff)
    except statistics.StatisticsError:
        median = "No Data"
        average = "No Data"
        Failed = True
    if not Failed:
        final_score = (top_1_percent*Variables.Top1Weight + top_5_percent*Variables.Top5Weight + top_20_percent*Variables.Top20Weight + median *
                       Variables.MedianWeight)/(Variables.Top1Weight+Variables.Top5Weight+Variables.Top20Weight+Variables.MedianWeight)
    else:
        final_score = "No Score Can Be Made"
    # export results to spreadsheet
    if user:
        excelFileName = os.path.join(
            f"Spreadsheets/{song_id} {song_info['_songName'].replace('/', '')} {song_diff} export.csv")
        excelFileName = excelFileName.replace("*", "")
        excelFileName = excelFileName.replace("\\", "")
        excelFileName = excelFileName.replace(">", "")
        excelFileName = excelFileName.replace("<", "")
        excelFileName = excelFileName.replace("|", "")
        excelFileName = excelFileName.replace(":", "")
        excelFileName = excelFileName.replace("?", "")
        excelFileName = excelFileName.replace('"', "")
        try:
            f = open(excelFileName, 'w', newline="", encoding='utf-8')
        except FileNotFoundError:
            print('Making Spreadsheets Folder')
            os.mkdir('Spreadsheets')
            f = open(excelFileName, 'w', newline="", encoding='utf-8')
        finally:
            writer = csv.writer(f)
            writer.writerow(["TimeMS", "Beat", "Type", "Forehand", "numNotes", "SwingSpeed", "SmoothSpeed", "Angle Diff", "AngleChangeDiff", "Pos Diff",
                            "Stamina", "Pattern Diff", "CombinedDiff", "SmoothedDiff", "", "Rated Score", "Median", "Average"])
            try:
                writer.writerow(["", "", "", statistics.mean([bloq.forehand for bloq in combinedArrayRaw]),
                                 statistics.mean(
                                     [bloq.numNotes for bloq in combinedArrayRaw]),
                                 statistics.mean(
                                     [bloq.swingSpeed for bloq in combinedArrayRaw]),
                                 statistics.mean(
                                     [bloq.swingSpeedSmoothed for bloq in combinedArrayRaw]),
                                 statistics.mean(
                                     [bloq.angleDiff for bloq in combinedArrayRaw]),
                                 statistics.mean(
                                     [bloq.angleChangeDiff for bloq in combinedArrayRaw]),
                                 statistics.mean(
                                     [bloq.posDiff for bloq in combinedArrayRaw]),
                                 statistics.mean(
                                     [bloq.combinedStamina for bloq in combinedArrayRaw]),
                                 statistics.mean(
                                     [bloq.patternDiff for bloq in combinedArrayRaw]),
                                 statistics.mean(
                                     [bloq.combinedDiff for bloq in combinedArrayRaw]),
                                 statistics.mean(
                                     [bloq.combinedDiffSmoothed for bloq in combinedArrayRaw]),
                                 "",
                                 final_score, median, average])
            except statistics.StatisticsError:
                writer.writerow(["Failed to get averages"])
            finally:
                for bloq in combinedArrayRaw:
                    writer.writerow([bloq.timeMS, bloq.time,  bloq.type, bloq.forehand, bloq.numNotes, bloq.swingSpeed, bloq.swingSpeedSmoothed, bloq.angleDiff, bloq.angleChangeDiff, bloq.posDiff,
                                    bloq.combinedStamina, bloq.patternDiff, bloq.combinedDiff, bloq.combinedDiffSmoothed])
            f.close()
        final_score = str(final_score)
        median = str(median)
        average = str(average)
        #print(song_id+" "+song_info['_songName']+" "+song_diff)
        #print("Rated Score:" + final_score)
        #print("Median:" + median)
        #print("Average: " + average)

    return song_id+" "+song_info['_songName']+" "+song_diff, final_score, median, average


# Setup ------------------------------------------------------ #


# possible overlapping hashes bug
