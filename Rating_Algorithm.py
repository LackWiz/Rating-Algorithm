from cmath import sqrt
from statistics import mean
from pygame.locals import *
from distutils.text_file import TextFile
import pygame
import sys
import random
import time
import os
import json
import math
import csv
from shutil import copyfile
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
print('Enter difficulty (like ExpertPlusStandard):')
# song_diff = input() + '.dat'
song_diff = "ExpertPlusStandard.dat"
# Setup pygame/window ---------------------------------------- #
mainClock = pygame.time.Clock()
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(128)
pygame.display.set_caption('rc_algorithm')
WINDOWWIDTH = 750
WINDOWHEIGHT = 500
screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)

# Font ------------------------------------------------------- #
font = pygame.font.SysFont('verdana', 24)

# Text ------------------------------------------------------- #


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    screen.blit(textobj, textrect)


# Data ------------------------------------------------------- #
cut_direction_index = [90, 270, 0, 180, 45, 135, 315, 225]

easyAngleMulti = 1  # Multiplyers for different angles
semiMidAngleDiff = 1.5
medAngleMulti = 1.75
hardAngleMulti = 2.5

# Minimum precision (how close notes are together) to consider 2 very close notes a slider
sliderPrecision = 1/6
dotSliderPrecision = 1/5

staminaRollingAverage = 64
patternRollingAverage = 32
# CutDirection
#   0 = North,
#   1 = South,
#   2 = West,
#   3 = East,
#   4 = NW,
#   5 = NE,
#   6 = SW,
#   7 = SE,
#   8 = Dot Note

# Funcs ------------------------------------------------------ #


class Bloq:
    def __init__(self, type, cutDirection, startTime, swingTime):
        self.numNotes = 1
        self.type = type
        self.cutDirection = cutDirection
        self.swingAngle = 200
        self.time = startTime
        self.swingTime = swingTime
        self.swingSpeed = 0
        self.forehand = True
        self.angleDiff = 1
        self.stamina = 0
        self.patternDiff = 0
        self.combinedDiff = 0

        # Non-negoitables, Up and a select diagonal is backhand
        if self.cutDirection in [0, 4, 5]:  # 4 = NW Left Hand, 5 = NE Right Hand
            if (self.type is 0 & self.cutDirection in [0, 4]):
                self.forehand = False
            elif (self.type is 1 & self.cutDirection in [0, 5]):
                self.forehand = False
        # Non-negoitables, Down and a select diagonal is forehand
        elif self.cutDirection in [1, 6, 7]:
            # 6 = SE Left Hand, 7 = SW Right Hand
            if (self.type is 0 & self.cutDirection in [1, 7]):
                self.forehand = True
            elif (self.type is 1 & self.cutDirection in [1, 6]):
                self.forehand = True

        else:
            if type is 0:
                # If it's the first note, assign most likely, correct Forehand/backhand assignment
                self.forehand = cutDirection in [5, 3, 7, 1]
            elif type is 1:
                self.forehand = cutDirection in [6, 4, 2, 1]
        self.calcAngleDiff()

    def addNote(self):
        self.numNotes += 1
        self.swingAngle += 36.87

    def setForehand(self, hand):
        self.forehand = hand
        self.calcAngleDiff()

    def calcAngleDiff(self):
        if(self.type == 0):  # Left Hand
            if(self.forehand):
                # Checks is angles are easy, medium or difficult
                if(self.cutDirection in [1, 7]):
                    self.angleDiff = easyAngleMulti
                elif(self.cutDirection is 3):
                    self.angleDiff = semiMidAngleDiff
                elif(self.cutDirection in [5, 6]):
                    self.angleDiff = medAngleMulti
                elif(self.cutDirection in [0, 2, 4]):
                    self.angleDiff = hardAngleMulti
            elif(not self.forehand):
                # Checks is angles are easy, medium or difficult
                if(self.cutDirection in [1, 3]):
                    self.angleDiff = hardAngleMulti
                elif(self.cutDirection in [5, 6]):
                    self.angleDiff = medAngleMulti
                elif(self.cutDirection is 2):
                    self.angleDiff = semiMidAngleDiff
                elif(self.cutDirection in [0, 4]):
                    self.angleDiff = easyAngleMulti
        elif(self.type == 1):  # Right Hand
            if(self.forehand):
                # Checks is angles are easy, medium or difficult
                if(self.cutDirection in [1, 6]):
                    self.angleDiff = easyAngleMulti
                elif(self.cutDirection is 2):
                    self.angleDiff = semiMidAngleDiff
                elif(self.cutDirection in [4, 7]):
                    self.angleDiff = medAngleMulti
                elif(self.cutDirection in [0, 3]):
                    self.angleDiff = hardAngleMulti
            elif(not self.forehand):
                # Checks is angles are easy, medium or difficult
                if(self.cutDirection in [1, 2]):
                    self.angleDiff = hardAngleMulti
                elif(self.cutDirection in [4, 7]):
                    self.angleDiff = medAngleMulti
                elif(self.cutDirection is 3):
                    self.angleDiff = semiMidAngleDiff
                elif(self.cutDirection in [0, 5]):
                    self.angleDiff = easyAngleMulti


def load_song_dat(path):
    main_path = path
    with open(main_path) as json_dat:
        dat = json.load(json_dat)
    return dat


def draw_triangle(surf, point, angle, radius):
    points = [point, [point[0]+radius*math.cos(math.radians(angle+45)), point[1]+radius*math.sin(math.radians(angle+45))], [
        point[0]+radius*math.cos(math.radians(angle-45)), point[1]+radius*math.sin(math.radians(angle-45))]]
    pygame.draw.polygon(surf, (255, 255, 255), points)


def extractBloqData(songNoteArray):

    BloqDataArray: list[Bloq] = []

    for i, block in enumerate(songNoteArray):

        # Checks if the note behind is super close, and treats it as a single swing
        if i != 0 and (((songNoteArray[i]["_time"] - songNoteArray[i-1]['_time'] <= sliderPrecision) or ((songNoteArray[i]["_time"] - songNoteArray[i-1]['_time'] <= dotSliderPrecision) and songNoteArray[i]["_cutDirection"] is 8)) & (songNoteArray[i]['_cutDirection'] in [songNoteArray[i-1]['_cutDirection'],8])):
            # Adds 1 to keep track of how many notes in a single swing
            BloqDataArray[-1].addNote()

        elif i == 0:
            BloqDataArray.append(Bloq(
                block["_type"], block["_cutDirection"], block["_time"], block["_time"] * mspb))
            BloqDataArray[-1].setForehand(block['_lineLayer'] != 2)

        else:
            BloqDataArray.append(
                Bloq(block["_type"], block["_cutDirection"], block["_time"], 0))
            if(BloqDataArray[-1].cutDirection not in [0, 1, 4, 5, 6, 7]):
                BloqDataArray[-1].setForehand(not BloqDataArray[-2].forehand)

            # calculates swingTime and Speed and shoves into class for processing later
            BloqDataArray[-1].swingTime = (BloqDataArray[-1].time -
                                           BloqDataArray[-2].time)*mspb
            BloqDataArray[-1].swingSpeed = BloqDataArray[-1].swingAngle / \
                BloqDataArray[-1].swingTime

            temp = 0
            # Uses a rolling average to judge stamina
            for j in range(0, staminaRollingAverage):
                if(len(BloqDataArray) >= j+1):
                    temp += BloqDataArray[-1*(j+1)].swingSpeed
            # Helps Speed Up the Average Ramp, then does a proper average past staminaRollingAverage/4 and switches to the conventional rolling average after
            if(len(BloqDataArray) < staminaRollingAverage/4):
                BloqDataArray[-1].stamina = (temp/(staminaRollingAverage/4))**3
            elif(len(BloqDataArray) < staminaRollingAverage):
                BloqDataArray[-1].stamina = (temp/len(BloqDataArray))**3
            else:
                BloqDataArray[-1].stamina = (temp/staminaRollingAverage)**3
            temp = 0
            # Uses a rolling average to judge pattern difficulty
            for i in range(0, patternRollingAverage):
                if(len(BloqDataArray) >= i+1):
                    temp += BloqDataArray[-1*(i+1)].angleDiff
            BloqDataArray[-1].patternDiff = (temp/patternRollingAverage)**2

            BloqDataArray[-1].combinedDiff = math.sqrt(
                BloqDataArray[-1].stamina**2 + BloqDataArray[-1].patternDiff**2)

    return BloqDataArray


# def combineArray(array1, array2):
#     combinedArray: list[Bloq] = []
#     size = max(len(array1), len(array2))
#     for i in range(0, size):
#         combinedArray.append()


# Setup ------------------------------------------------------ #
bs_song_path = bs_path
if bs_song_path[-1] not in ['\\', '/']:  # Checks if song path is empty
    bs_song_path += '/'
song_options = os.listdir(bs_song_path)
for song in song_options:
    if song.find(song_id) != -1:
        song_folder = song
        break
song_folder_contents = os.listdir(bs_song_path + song_folder + '/')
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

# combinedArray = combineArray(BloqDataLeft, BloqDataRight)

f = open(song_id + ' export.csv', 'w', newline="")
writer = csv.writer(f)
writer.writerow(["_Time", "L Swing Speed degree/ms", "L Angle Diff",
                "L Stamina", "L Pattern Diff", "L CombinedDiff"])
for bloq in BloqDataLeft:
    writer.writerow([bloq.time, bloq.swingSpeed, bloq.angleDiff,
                    bloq.stamina, bloq.patternDiff, bloq.combinedDiff])
f.close()


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
