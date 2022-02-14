from pygame.locals import *
from distutils.text_file import TextFile
import pygame
import sys
import random
import time
import os
import json
import math
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
# song_id = input()
song_id = "1a37c"  # For Debugging
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
font = pygame.font.SysFont('verdana', 10)

# Text ------------------------------------------------------- #


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    screen.blit(textobj, textrect)


# Data ------------------------------------------------------- #
cut_direction_index = [90, 270, 0, 180, 45, 135, 315, 225]

# Funcs ------------------------------------------------------ #


class Bloq:
    def __init__(self, type, cutDirection, startTime, swingTime):
        self.numNotes = 1
        self.type = type
        self.cutDirection = 0
        self.swingAngle = 200
        self.time = startTime
        self.swingTime = swingTime
        self.swingSpeed = 0
        self.forehand = True

        # Non-negoitables, Up is backhand
        if self.cutDirection == 0:
            self.forehand = False

        # Non-negoitables, Down is forehand
        elif self.cutDirection == 1:
            self.forehand = True

        else:
            if type is 0:
                # If it's the first note, assign most likely, correct Forehand/backhand assignment
                self.forehand = cutDirection in [5, 3, 7, 1]
            elif type is 1:
                self.forehand = cutDirection in [6, 4, 2, 1]

    def addNote(self):
        self.numNotes += 1
        self.swingAngle += 36.87

    def setForehand(self, hand):
        self.forehand = hand


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
    n = 0
    BloqDataArray: list[Bloq] = []

    for i, block in enumerate(songNoteArray):

        # Checks if the note behind is super close, and treats it as a single swing
        if i != 0 and (songNoteArray[i]["_time"] - songNoteArray[i-1]['_time'] <= 1/8):
            # Adds 1 to keep track of how many notes in a single swing
            BloqDataArray[-1].addNote()

        elif i == 0:
            BloqDataArray.append(Bloq(block["_type"], block["_cutDirection"], block["_time"], block["_time"] * mspb))
            BloqDataArray[-1].setForehand(block['_lineLayer'] != 2)
            
        else:
            BloqDataArray.append(Bloq(block["_type"], block["_cutDirection"], block["_time"], 0))

            BloqDataArray[-1].swingTime = (BloqDataArray[-1].time -
                                           BloqDataArray[-2].time)*mspb
            BloqDataArray[-1].swingSpeed = BloqDataArray[-1].swingAngle/BloqDataArray[-1].swingTime

    return BloqDataArray


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


# saber length is 1 meter
# distance between top and bottom notes is roughly 1.5m
# distance between side to side notes it roughly 2m
# totalSwingAnglec = 160degrees + numberOfBlocks * RadToDegrees(tan-1(0.75/1))

# Import song dat file
# Filter note dat file into Left and Right Block arrays


# Identify stacks/sliders (maybe pauls/poodles) and turn the 2-4 Blocks into a single Block with a large swing angle ✅
# Calculate Block distance into seconds or ms 73.74 ✅

# using 100 degree in, 60 degree out rule to calculate beginning and end points of the saber✅
#   (change endpoint of current block to)✅
#
#
# using 1/2 time between last and next block (1/2 time between last and current block + 1/2 time between current and next block), calculate max time for that swing on that block ✅
# using swingtime, swingAngle and 1 meter saber length, calculate saber speed ✅

# List off hard swing angles for both hands


# Each swing entry for left and right hand array should contain
# Block[numberOfBlocks[1 to 4], position[X,Y], angleOfBlock(degree), totalAngleNeeded[160-273.74], timeForSwing(ms), ForeHand?]
# 273.74 = 200 + tan-1(0.75/1)*2 (worst case inverts/quadruple sliders)

# Final difficulty based on Total amount of notes, fastest swings using a rolling average of 4, angle difficulty average for whole map
