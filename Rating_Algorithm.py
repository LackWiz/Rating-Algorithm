#Nickname pog sub and follow
from statistics import median
import statistics
import os
import json
import math
import csv
# Get ID ----------------------------------------------------- #
try:
    f = open('bs_path.txt', 'r')
    bs_path = f.read()
    f.close()
except FileNotFoundError:
    print('Enter Beat Saber custom songs folder:')
    bs_path = input()
    f = open('bs_path.txt', 'w')
    dat = f.write(bs_path)
    f.close()

print('Enter song ID:')
song_id = input()
# song_id = "1fe06"  # For Debugging
print('Enter difficulty (like ExpertPlus):')
song_diff = input() + 'Standard.dat'
# song_diff = "ExpertPlusStandard.dat"
# Setup pygame/window ---------------------------------------- #
# mainClock = pygame.time.Clock()
# pygame.mixer.pre_init(44100, -16, 2, 512)
# pygame.init()
# pygame.mixer.set_num_channels(128)
# pygame.display.set_caption('rc_algorithm')
WINDOWWIDTH = 750
WINDOWHEIGHT = 500
# screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)

# Font ------------------------------------------------------- #
# font = pygame.font.SysFont('verdana', 24)

# Text ------------------------------------------------------- #


# def draw_text(text, font, color, surface, x, y):
#     textobj = font.render(text, 1, color)
#     textrect = textobj.get_rect()
#     textrect.topleft = (x, y)
#     screen.blit(textobj, textrect)


# Data ------------------------------------------------------- #
cut_direction_index = [90, 270, 0, 180, 45, 135, 315, 225]

easyAngleMulti = 1  # Multiplyers for different angles
semiMidAngleMulti = 1.1
midAngleMulti = 1.3
hardAngleMulti = 1.5

easySideMulti = 1  # Multiplyers for different positions
semiMidSideMulti = 1.05
midSideMulti = 1.2
hardSideMulti = 1.5

easyVertMulti = 1  # Multiplyers for different positions
semiMidVertMulti = 1.05
midVertMulti = 1.2


angleDiv = 90

staminaPower = 2
patternPower = 2

combinedArrayScale = 4.319

# Minimum precision (how close notes are together) to consider 2 very close notes a slider
sliderPrecision = 1/6
dotSliderPrecision = 1/5

staminaRollingAverage = 128
patternRollingAverage = 128
combinedRollingAverage = 128
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
class BloqStore:
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
        self.forehand = True
        self.angleDiff = easyAngleMulti
        self.angleChangeDiff = 0
        self.posDiff = easySideMulti
        self.stamina = 0
        self.patternDiff = 0
        self.combinedStamina = 0
        self.combinedDiff = 0
        self.combinedDiffSmoothed = 0

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
        self.forehand = True
        self.angleDiff = easyAngleMulti
        self.angleChangeDiff = 0
        self.posDiff = easySideMulti
        self.stamina = 0
        self.patternDiff = 0
        self.combinedDiff = 0

        # Non-negoitables, Up and a select diagonal is backhand
        if self.cutDirection in [0, 4, 5]:  # 4 = NW Left Hand, 5 = NE Right Hand
            if ((self.type == 0) & (self.cutDirection in [0, 4])):
                self.forehand = False
            elif ((self.type == 1) & (self.cutDirection in [0, 5])):
                self.forehand = False
        # Non-negoitables, Down and a select diagonal is forehand
        elif self.cutDirection in [1, 6, 7]:
            # 6 = SE Left Hand, 7 = SW Right Hand
            if ((self.type == 0) & (self.cutDirection in [1, 7])):
                
                self.forehand = True
            elif ((self.type == 1) & (self.cutDirection in [1, 6])):
                
                self.forehand = True
                
        else:
            if type == 0:
                # If it's the first note, assign most likely, correct Forehand/backhand assignment
                self.forehand = cutDirection in [5, 3, 7, 1]
            elif type == 1:
                self.forehand = cutDirection in [6, 4, 2, 1]
        self.calcAngleDiff()

    def addNote(self):
        self.numNotes += 1
        self.swingAngle += 36.87

    def setForehand(self, hand):
        self.forehand = hand
        self.calcAngleDiff()
        self.calcPosDiff()

    def calcPosDiff(self):
        if(self.type == 0):  # Left Hand Side to Side Diff
            if(self.forehand):
                self.posDiff = [semiMidSideMulti, easySideMulti, semiMidSideMulti, midSideMulti][self.bloqPos[0]]
            elif(not self.forehand):
                self.posDiff = [hardSideMulti, midSideMulti, semiMidSideMulti, easySideMulti][self.bloqPos[0]]
            
        elif(self.type == 1):  # Right Hand
            if(self.forehand):
                self.posDiff = [midSideMulti, semiMidSideMulti, easySideMulti, semiMidSideMulti][self.bloqPos[0]]
            elif(not self.forehand):
                self.posDiff = [hardSideMulti, midSideMulti, semiMidSideMulti, easySideMulti][self.bloqPos[0]]
        
        # Up and Down Diff
        if(self.forehand):
            if(self.bloqPos[1] == 0):
                self.posDiff = self.posDiff*easyVertMulti
            elif(self.bloqPos[1] == 1):
                self.posDiff = self.posDiff*semiMidVertMulti
            elif(self.bloqPos[1] == 2):
                self.posDiff = self.posDiff*midVertMulti
        elif(not self.forehand):
            if(self.bloqPos[1] == 0):
                self.posDiff = self.posDiff*midVertMulti
            elif(self.bloqPos[1] == 1):
                self.posDiff = self.posDiff*semiMidVertMulti
            elif(self.bloqPos[1] == 2):
                self.posDiff = self.posDiff*easyVertMulti

    def calcAngleDiff(self):
        if(self.type == 0):  # Left Hand
            if(self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 7, 8]):
                    self.angleDiff = easyAngleMulti
                elif(self.cutDirection == 3):
                    self.angleDiff = semiMidAngleMulti
                elif(self.cutDirection in [5, 6]):
                    self.angleDiff = midAngleMulti
                elif(self.cutDirection in [0, 2]):
                    self.angleDiff = hardAngleMulti
            elif(not self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 3]):
                    self.angleDiff = hardAngleMulti
                elif(self.cutDirection in [5, 6]):
                    self.angleDiff = midAngleMulti
                elif(self.cutDirection == 2):
                    self.angleDiff = semiMidAngleMulti
                elif(self.cutDirection in [0, 4, 8]):
                    self.angleDiff = easyAngleMulti
        elif(self.type == 1):  # Right Hand
            if(self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 6, 8]):
                    self.angleDiff = easyAngleMulti
                elif(self.cutDirection == 2):
                    self.angleDiff = semiMidAngleMulti
                elif(self.cutDirection in [4, 7]):
                    self.angleDiff = midAngleMulti
                elif(self.cutDirection in [0, 3]):
                    self.angleDiff = hardAngleMulti
            elif(not self.forehand):
                # Checks if angle is easy, medium or difficult
                if(self.cutDirection in [1, 2]):
                    self.angleDiff = hardAngleMulti
                elif(self.cutDirection in [4, 7]):
                    self.angleDiff = midAngleMulti
                elif(self.cutDirection == 3):
                    self.angleDiff = semiMidAngleMulti
                elif(self.cutDirection in [0, 5], 8):
                    self.angleDiff = easyAngleMulti
        if(self.angleDiff >= midAngleMulti):    
            self.angleDiff = self.angleDiff*(self.numNotes**(1/3))
        else:
            self.angleDiff = self.angleDiff*(self.numNotes**(1/6))

        


def load_song_dat(path):
    main_path = path
    try:
        with open(main_path) as json_dat:
            dat = json.load(json_dat)
    except FileNotFoundError:
        print("That map doesn't exist! Make sure it's downloaded and you spelt the map name correctly")
        print("Huh maybe it has a weird file name")
        print("This time I won't autocomplete it by adding 'Standard'. you'll need to type out the whole map file name minus .dat")
        print('Enter the exact difficulty file name (like ExpertPlusStandard):')
        song_diff = input()
        main_path = bs_song_path + song_folder + '/' + song_diff + '.dat'
        with open(main_path) as json_dat:
            dat = json.load(json_dat)
        
    return dat


# def draw_triangle(surf, point, angle, radius):
#     points = [point, [point[0]+radius*math.cos(math.radians(angle+45)), point[1]+radius*math.sin(math.radians(angle+45))], [
#         point[0]+radius*math.cos(math.radians(angle-45)), point[1]+radius*math.sin(math.radians(angle-45))]]
#     pygame.draw.polygon(surf, (255, 255, 255), points)


def extractBloqData(songNoteArray):

    BloqDataArray: list[Bloq] = []

    for i, block in enumerate(songNoteArray):

        # Checks if the note behind is super close, and treats it as a single swing
        if i != 0 and ((((songNoteArray[i]["_time"] - songNoteArray[i-1]['_time'] <= sliderPrecision) or ((songNoteArray[i]["_time"] - songNoteArray[i-1]['_time'] <= dotSliderPrecision) and songNoteArray[i]["_cutDirection"] == 8)) & (songNoteArray[i]['_cutDirection'] in [songNoteArray[i-1]['_cutDirection'],8]))or(songNoteArray[i]["_time"] - songNoteArray[i-1]['_time'] <= 0.001)):
            # Adds 1 to keep track of how many notes in a single swing
            BloqDataArray[-1].addNote()

        elif i == 0:
            BloqDataArray.append(Bloq(
                block["_type"], block["_cutDirection"],[block["_lineIndex"],block["_lineLayer"]], block["_time"], block["_time"] * mspb))
            BloqDataArray[-1].setForehand(block['_lineLayer'] != 2)

        else:
            BloqDataArray.append(
                Bloq(block["_type"], block["_cutDirection"],[block["_lineIndex"],block["_lineLayer"]], block["_time"], 0))
            if(BloqDataArray[-1].cutDirection not in [0, 1, 4, 5, 6, 7]):
                BloqDataArray[-1].setForehand(not BloqDataArray[-2].forehand)

            # calculates swingTime in ms and Speed and shoves into class for processing later
            BloqDataArray[-1].swingTime = (BloqDataArray[-1].time - #Swing time in ms
                                           BloqDataArray[-2].time)*mspb
            BloqDataArray[-1].swingSpeed = BloqDataArray[-1].swingAngle/BloqDataArray[-1].swingTime #Swing Speed in degrees/ms
            if((BloqDataArray[-1].cutDirection != 8) and (BloqDataArray[-2].cutDirection != 8)):
                BloqDataArray[-1].angleChange = abs(180-abs(cut_direction_index[BloqDataArray[-1].cutDirection]-cut_direction_index[BloqDataArray[-2].cutDirection])) #Calculates Angle Change After parity. e.g. up and down is 0, but up to side is 90
            else:
                BloqDataArray[-1].angleChange = 0
            BloqDataArray[-1].angleChangeTime = BloqDataArray[-1].angleChange/(BloqDataArray[-1].swingTime) #Change in cut angle swing in degrees/millisecond
            BloqDataArray[-1].angleChangeDiff =  1+((max(BloqDataArray[-1].angleChange,45)-45)/angleDiv)**2

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
                    temp += (BloqDataArray[-1*(j+1)].angleDiff*BloqDataArray[-1*(j+1)].posDiff*BloqDataArray[-1*(j+1)].angleChangeDiff)
            # Helps Speed Up the Average Ramp, then does a proper average past staminaRollingAverage/4 and switches to the conventional rolling average after
            if(len(BloqDataArray) < patternRollingAverage/4):
                BloqDataArray[-1].patternDiff = (temp/(patternRollingAverage/4))
            elif(len(BloqDataArray) < patternRollingAverage):
                BloqDataArray[-1].patternDiff = (temp/len(BloqDataArray))
            else:
                BloqDataArray[-1].patternDiff = (temp/patternRollingAverage)
            
            
            # The best way to compound the data to get reasonable results. I have no idea why it works but it does
            # BloqDataArray[-1].combinedDiff = math.sqrt(BloqDataArray[-1].stamina**staminaPower + BloqDataArray[-1].patternDiff**patternPower)*min(math.sqrt(BloqDataArray[-1].stamina**staminaPower),BloqDataArray[-1].patternDiff**patternPower)

    return BloqDataArray


def combineArray(array1, array2):
    #array1: list[Bloq] = []
    #array2: list[Bloq] = []
    combinedArray: list[BloqStore] = []

    for i in range(0, len(array1)):
        combinedArray.append(BloqStore(array1[i].type, array1[i].cutDirection, array1[i].bloqPos, array1[i].time, array1[i].swingTime))
        combinedArray[-1].timeMS = array1[i].timeMS
        combinedArray[-1].angleDiff = array1[i].angleDiff
        combinedArray[-1].angleChange = array1[i].angleChange
        combinedArray[-1].angleChangeTime = array1[i].angleChangeTime
        combinedArray[-1].combinedDiff = array1[i].combinedDiff
        combinedArray[-1].forehand = array1[i].forehand
        combinedArray[-1].numNotes = array1[i].numNotes
        combinedArray[-1].patternDiff = array1[i].patternDiff
        combinedArray[-1].posDiff = array1[i].posDiff
        combinedArray[-1].stamina = array1[i].stamina
        combinedArray[-1].angleChangeDiff = array1[i].angleChangeDiff
        combinedArray[-1].swingSpeed = array1[i].swingSpeed
    for i in range(0, len(array2)):
        combinedArray.append(BloqStore(array2[i].type, array2[i].cutDirection, array2[i].bloqPos, array2[i].time, array2[i].swingTime))
        combinedArray[-1].timeMS = array2[i].timeMS
        combinedArray[-1].angleDiff = array2[i].angleDiff
        combinedArray[-1].angleChange = array2[i].angleChange
        combinedArray[-1].angleChangeTime = array2[i].angleChangeTime
        combinedArray[-1].combinedDiff = array2[i].combinedDiff
        combinedArray[-1].forehand = array2[i].forehand
        combinedArray[-1].numNotes = array2[i].numNotes
        combinedArray[-1].patternDiff = array2[i].patternDiff
        combinedArray[-1].posDiff = array2[i].posDiff
        combinedArray[-1].stamina = array2[i].stamina
        combinedArray[-1].angleChangeDiff = array2[i].angleChangeDiff
        combinedArray[-1].swingSpeed = array2[i].swingSpeed
    for i in range(1,len(combinedArray)):
        combinedArray[i].combinedStamina = math.sqrt(combinedArray[i].stamina**2 + combinedArray[i-1].stamina**2)
        combinedArray[i].combinedDiff = math.sqrt(combinedArray[i].combinedStamina**staminaPower + combinedArray[i].patternDiff**patternPower) * min(math.sqrt(combinedArray[i].combinedStamina**staminaPower),combinedArray[i].patternDiff**patternPower)
    combinedArray.sort(key=lambda x: x.time)
    temp = len(combinedArray)
    i = 1
    while(i < temp): #Cleans up Duplicate Times
        if(combinedArray[i].time == combinedArray[i-1].time):
            combinedArray[i-1].numNotes += 1
            combinedArray.pop(i)
            temp = len(combinedArray)
            i = i - 1
        i += 1

    
    for i in range(0, len(combinedArray)):
        temp = 0
        for j in range(0, min(combinedRollingAverage,i)): # Uses a rolling average to smooth difficulties between the hands
            temp += combinedArray[i-min(combinedRollingAverage,j)].combinedDiff
        combinedArray[i].combinedDiffSmoothed = combinedArrayScale*temp/min(combinedRollingAverage,i+1) # 6
    
    
    return combinedArray


# Setup ------------------------------------------------------ #
bs_song_path = bs_path
if bs_song_path[-1] not in ['\\', '/']:  # Checks if song path is empty
    bs_song_path += '/'
song_options = os.listdir(bs_song_path)
for song in song_options:
    if song.find(song_id) != -1:
        song_folder = song
        break
try:
    song_folder_contents = os.listdir(bs_song_path + song_folder + '/')
except NameError:
    print("Not Downloaded or wrong song code!")
    print("Press Enter to Exit!")
    input()
    exit()
for song in song_folder_contents:
    if song[-4:] in ['.egg', '.ogg']:
        song_file_name = song
        break

#---------------Where Stuff Happens-----------------------------------------------------------------------------#

# Loads the Full song music file into variable full_music_path
full_music_path = bs_song_path + song_folder + '/' + song_file_name

song_dat = load_song_dat(bs_song_path + song_folder + '/' + song_diff)
song_notes_temp = song_dat['_notes']
song_notes = []

n = 0
for song_note in song_notes_temp:  # Filters Out Left and Right notes from all notes and shoves it into an array
    if song_note['_type'] in [0, 1]:
        song_notes.append([float(song_note['_time']), n, song_note])
        n += 1
song_notes.sort(reverse=True)

song_notes_original = []
for song_note in song_notes_temp:
    if song_note['_type'] in [0, 1]:
        song_notes_original.append(song_note.copy())


songNoteLeft = []
songNoteRight = []


song_info = load_song_dat(bs_song_path + song_folder + '/info.dat')
bpm = song_info['_beatsPerMinute']
mspb = 60*1000/bpm  # milliseconds per beat

for block in song_notes_original:
    if block['_type'] == 0:  # left
        songNoteLeft.append(block.copy())
for block in song_notes_original:
    if block['_type'] == 1:  # right
        songNoteRight.append(block.copy())

BloqDataLeft = extractBloqData(songNoteLeft)
BloqDataRight = extractBloqData(songNoteRight)
combinedArrayRaw = combineArray(BloqDataLeft, BloqDataRight)

excelFileName = os.path.join('Spreadsheets',song_id +" "+ song_info['_songName']+" "+song_diff+ ' export.csv')

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






combinedArray = []
for bloq in combinedArrayRaw:
    combinedArray.append(bloq.combinedDiffSmoothed)


combinedArray.sort(reverse=True)
top_1_percent = sum(combinedArray[:int(len(combinedArray)/100)])/int(len(combinedArray)/100)
# top_5_percent = sum(combinedArray[:int(len(combinedArray)/20)])/int(len(combinedArray)/20)
# top_20_percent = sum(combinedArray[:int(len(combinedArray)/5)])/int(len(combinedArray)/5)
# top_50_percent = sum(combinedArray[:int(len(combinedArray)/2)])/int(len(combinedArray)/2)
# top_70_percent = sum(combinedArray[:int(len(combinedArray)*0.7)])/int(len(combinedArray)*0.7)
median = statistics.median(combinedArray)

final_score = (top_1_percent*7 + median*3)/10

# top_2_percent = top_2_percent*bpm**1.05/300
# top_5_percent = top_5_percent*bpm**1.05/300
# top_20_percent = top_20_percent*bpm**1.05/300
# top_50_percent = top_50_percent*bpm**1.05/300
# top_70_percent = top_70_percent*bpm**1.05/300
# print(top_1_percent,top_5_percent,top_20_percent,top_50_percent,top_70_percent,median)
# print(len(BloqDataLeft))
# final_score = (top_20_percent*2+top_5_percent*3+top_1_percent*4+top_70_percent*3+median)/13
# print(final_score)
# cal_final_score = 1.0299*final_score-0.3284*final_score**2+0.1005*final_score**3-0.009504*final_score**4+0.0002828*final_score**5
# print(cal_final_score)

print(final_score)

print("sucess")

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

"""
pygame.mixer.music.load(full_music_path)
pygame.mixer.music.play(0)

last_angles = [[0, 0, 999], [0, 0, 999]]
bpms = bpm/60/1000
start_time = time.time()
currNoteNum = 0
# Loop ------------------------------------------------------- #
while True:
    # Background --------------------------------------------- #
    screen.fill((0, 0, 0))
    # Render ------------------------------------------------- #
    time_progress = (time.time()-start_time)*1000*bpms
    n = 0
    for note in song_notes:
        note = note[2]
        note_num = len(song_notes)-n-1
        if note['_type'] in [0, 1]:
            if (note['_time'] > time_progress-(150*bpms)) and (note['_time'] < time_progress+(1000*bpms)):
                note_x = note['_lineIndex']-2
                note_y = 3-(note['_lineLayer']-1.5)
                age = time_progress+(1000*bpms)-note['_time']
                size = age*12.5
                pos_x = 270+note_x*(6+size)
                pos_y = 80+note_y*(6+size)
                if note['_type'] == 0:
                    color = (255, 0, 0)
                if note['_type'] == 1:
                    color = (0, 0, 255)
                if note['_time'] > time_progress:
                    surf = pygame.Surface((int(size), int(size)))
                    surf.set_alpha(150)
                    surf.fill(color)
                    screen.blit(surf, (pos_x-int(size/2), pos_y-int(size/2)))
                    if note['_cutDirection'] != 8:
                        draw_triangle(screen, [pos_x, pos_y], cut_direction_index[note['_cutDirection']], int(
                            size/(2*math.sqrt(2))))
                    else:
                        pygame.draw.circle(screen, (255, 255, 255), [
                                           int(pos_x), int(pos_y)], int(size/6))
                else:
                    if currNoteNum <= note_num:
                        #last_angles = song_angles[currNoteNum+1]
                        currNoteNum += 1
                        # boop_sfx.play()
                    alt_size = int(size+(age-(1000*bpms))*150)
                    surf_1 = pygame.Surface((alt_size, alt_size))
                    surf_2 = pygame.Surface((alt_size-4, alt_size-4))
                    surf_1.fill(color)
                    surf_1.blit(surf_2, (2, 2))
                    surf_1.set_colorkey((0, 0, 0))
                    surf_1.set_alpha(255-(age-(1000*bpms))/(150*bpms)*255)
                    screen.blit(
                        surf_1, (pos_x-int(alt_size/2), pos_y-int(alt_size/2)))
        n += 1
    # UI ----------------------------------------------------- #
    progress_ms = pygame.mixer.music.get_pos()
    progress_s = round(progress_ms/1000, 2)
    draw_text(str(progress_s), font, (255, 255, 255), screen, 2, 2)

    difficulty_r = (last_angles[1][1])**1.25/last_angles[1][2]
    difficulty_l = (last_angles[0][1])**1.25/last_angles[0][2]

    pygame.draw.line(screen, (255, 0, 0), [100, 400], [100+math.cos(last_angles[0][0])*15*(
        last_angles[0][1]+1), 400+math.sin(last_angles[0][0])*15*(last_angles[0][1]+1)], 3)
    pygame.draw.circle(screen, (255, 0, 0), [100, 400], 7)
    pygame.draw.circle(screen, (155, 0, 0), [100, 400], int(
        15*(last_angles[0][1]+1))+1, 2)
    pygame.draw.circle(screen, (255, 255, 255), [
                       100, 400], int(15*difficulty_l)+2, 2)
    pygame.draw.line(screen, (0, 0, 255), [400, 400], [400+math.cos(last_angles[1][0])*15*(
        last_angles[1][1]+1), 400+math.sin(last_angles[1][0])*15*(last_angles[1][1]+1)], 3)
    pygame.draw.circle(screen, (0, 0, 255), [400, 400], 7)
    pygame.draw.circle(screen, (0, 0, 155), [400, 400], int(
        15*(last_angles[1][1]+1))+1, 2)
    pygame.draw.circle(screen, (255, 255, 255), [
                       400, 400], int(15*difficulty_r)+2, 2)

    left_difficulty_average = 0
    right_difficulty_average = 0
    lstam_difficulty_average = 0
    rstam_difficulty_average = 0

    # left_score_map[currNoteNum]
    # right_score_map[currNoteNum]
    # lstam_score_map[currNoteNum]
    # rstam_score_map[currNoteNum]
    # peak_lstam_diff = max(peak_lstam_diff,lstam_difficulty_average)
    # peak_rstam_diff = max(peak_rstam_diff,rstam_difficulty_average)
    # peak_left_diff = max(peak_left_diff,left_difficulty_average)
    # peak_right_diff = max(peak_right_diff,right_difficulty_average)
    # lstam_ghost_val -= 0.01
    # rstam_ghost_val -= 0.01
    # left_ghost_val -= 0.05
    # right_ghost_val -= 0.05
    # left_ghost_val = max(left_ghost_val,left_difficulty_average)
    # right_ghost_val = max(right_ghost_val,right_difficulty_average)
    # lstam_ghost_val = max(lstam_ghost_val,lstam_difficulty_average)
    # rstam_ghost_val = max(rstam_ghost_val,rstam_difficulty_average)

    # score_sum = ((left_ghost_val+lstam_ghost_val)**3 + (right_ghost_val+rstam_ghost_val)**3)**(1/3)

    # score_sum_ghost_val -= 0.01
    # score_sum_ghost_val = max(score_sum,score_sum_ghost_val)

    # score_sum_peak = max(score_sum_peak,score_sum)

    # sum_ghost_rect = pygame.Rect(WINDOWWIDTH-145,WINDOWHEIGHT-7-score_sum_ghost_val*15,20,score_sum_ghost_val*15+2)
    # sum_rect = pygame.Rect(WINDOWWIDTH-145,WINDOWHEIGHT-7-score_sum*15,20,score_sum*15+2)
    # pygame.draw.rect(screen,(0,100,0),sum_ghost_rect)
    # pygame.draw.rect(screen,(0,255,0),sum_rect)
    # pygame.draw.line(screen,(255,255,255),[WINDOWWIDTH-145,WINDOWHEIGHT-8-score_sum_peak*15],[WINDOWWIDTH-125,WINDOWHEIGHT-8-score_sum_peak*15],2)

    # # ghost vals
    # lg_rect = pygame.Rect(WINDOWWIDTH-100,WINDOWHEIGHT-7-left_ghost_val*15,20,left_ghost_val*15+2)
    # rg_rect = pygame.Rect(WINDOWWIDTH-75,WINDOWHEIGHT-7-right_ghost_val*15,20,right_ghost_val*15+2)
    # pygame.draw.rect(screen,(100,0,0),lg_rect)
    # pygame.draw.rect(screen,(0,0,100),rg_rect)
    # lstamg_rect = pygame.Rect(WINDOWWIDTH-50,WINDOWHEIGHT-7-lstam_ghost_val*15,20,lstam_ghost_val*15+2)
    # rstamg_rect = pygame.Rect(WINDOWWIDTH-25,WINDOWHEIGHT-7-rstam_ghost_val*15,20,rstam_ghost_val*15+2)
    # pygame.draw.rect(screen,(100,25,0),lstamg_rect)
    # pygame.draw.rect(screen,(0,25,100),rstamg_rect)
    # # realtime vals
    # l_rect = pygame.Rect(WINDOWWIDTH-100,WINDOWHEIGHT-7-left_difficulty_average*15,20,left_difficulty_average*15+2)
    # r_rect = pygame.Rect(WINDOWWIDTH-75,WINDOWHEIGHT-7-right_difficulty_average*15,20,right_difficulty_average*15+2)
    # pygame.draw.rect(screen,(255,0,0),l_rect)
    # pygame.draw.rect(screen,(0,0,255),r_rect)
    # lstam_rect = pygame.Rect(WINDOWWIDTH-50,WINDOWHEIGHT-7-lstam_difficulty_average*15,20,lstam_difficulty_average*15+2)
    # rstam_rect = pygame.Rect(WINDOWWIDTH-25,WINDOWHEIGHT-7-rstam_difficulty_average*15,20,rstam_difficulty_average*15+2)
    # pygame.draw.rect(screen,(255,50,0),lstam_rect)
    # pygame.draw.rect(screen,(0,50,255),rstam_rect)
    # for i in range(26):
    #     pygame.draw.line(screen,(255,255,255),[WINDOWWIDTH-120,WINDOWHEIGHT-5-i*15],[WINDOWWIDTH-102,WINDOWHEIGHT-5-i*15],2)
    #     draw_text(str(i), font, (255,255,255), screen, WINDOWWIDTH-120, WINDOWHEIGHT-19-i*15)
    # pygame.draw.line(screen,(255,255,255),[WINDOWWIDTH-100,WINDOWHEIGHT-8-peak_left_diff*15],[WINDOWWIDTH-80,WINDOWHEIGHT-8-peak_left_diff*15],2)
    # pygame.draw.line(screen,(255,255,255),[WINDOWWIDTH-75,WINDOWHEIGHT-8-peak_right_diff*15],[WINDOWWIDTH-55,WINDOWHEIGHT-8-peak_right_diff*15],2)
    # pygame.draw.line(screen,(255,255,255),[WINDOWWIDTH-50,WINDOWHEIGHT-8-peak_lstam_diff*15],[WINDOWWIDTH-30,WINDOWHEIGHT-8-peak_lstam_diff*15],2)
    # pygame.draw.line(screen,(255,255,255),[WINDOWWIDTH-25,WINDOWHEIGHT-8-peak_rstam_diff*15],[WINDOWWIDTH-5,WINDOWHEIGHT-8-peak_rstam_diff*15],2)
    # Buttons ------------------------------------------------ #
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
    # Update ------------------------------------------------- #
    pygame.display.update()
    mainClock.tick(60)
"""

print("Press Enter to Exit!")
input()
exit()