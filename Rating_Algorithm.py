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
#song_id = input()
song_id = "1a37c"  # For Debugging
print('Enter difficulty (like ExpertPlusStandard):')
#song_diff = input() + '.dat'
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
    BloqDataArray = []
    for i, block in enumerate(songNoteArray):

        # Checks if the note behind is super close, and treats it as a single swing
        if i != 0 and (songNoteArray[i]["_time"] - songNoteArray[i-1]['_time'] <= 1/8):
            # Adds 1 to keep track of how many notes in a single swing
            BloqDataArray[-1]['numOfBloq'] += 1

        else:
            BloqDataArray.append({"numOfBloq": 1, "cutDirection": 0,
                                "angleNeeded": 0, "swingTime": 0, "Forehand?": True})
            BloqDataArray[n]['cutDirection'] = block['_cutDirection']

            if(BloqDataArray[n]['cutDirection'] == 0):  # Non-negoitables, Up is backhand
                BloqDataArray[n]['Forehand?'] = False

            # Non-negoitables, Down is forehand
            elif(BloqDataArray[n]['cutDirection'] == 1):
                BloqDataArray[n]['Forehand?'] = True

            # Checks if it's the first note in the song and sets forehand as true if it is
            elif((BloqDataArray[n-1]['Forehand?'] == True) & (n-1 >= 0)):
                # If the note has been removed, you can't toggle forehand/backhand
                BloqDataArray[n]['Forehand?'] = False

            elif((BloqDataArray[n-1]['Forehand?'] == False) & (n-1 >= 0)):
                BloqDataArray[n]['Forehand?'] = True

            elif(i-1 == -1):  # Only for First Note Check
                # If it's the first note, assign most likely, correct Forehand/backhand assignment
                if(BloqDataArray[n]['_cutDirection'] in [5, 0, 4, 2]):
                    BloqDataArray[i]['Forehand?'] = False

                # If it's the first note, assign most likely, correct Forehand/backhand assignment
                elif(BloqDataArray[n]['_cutDirection'] in [6, 1, 3, 7]):
                    BloqDataArray[i]['Forehand?'] = True
            n += 1
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
BlockDataLeft = []
BlockDataRight = []


song_info = load_song_dat(bs_song_path + song_folder + '/info.dat')
bpm = song_info['_beatsPerMinute']
mspb = 60*1000/bpm  # milliseconds per beat

for block in song_notes_original:
    if block['_type'] == 0:  # left
        songNoteLeft.append(block.copy())
for block in song_notes_original:
    if block['_type'] == 1:  # right
        songNoteRight.append(block.copy())





# saber length is 1 meter
# distance between top and bottom notes is roughly 1.5m
# distance between side to side notes it roughly 2m
# totalSwingAnglec = 160degrees + numberOfBlocks * RadToDegrees(tan-1(0.75/1))

# Import song dat file
# Filter note dat file into Left and Right Block arrays

# Calculate Block distance into seconds or ms
# Identify stacks/sliders (maybe pauls/poodles) and turn the 2-4 Blocks into a single Block with a large swing angle
# Calculate Block distance into seconds or ms
#
# using 100 degree in, 60 degree out rule to calculate beginning and end points of the saber
#   (change endpoint of current block to)
#
#
# using 1/2 time between last and next block (1/2 time between last and current block + 1/2 time between current and next block), calculate max time for that swing on that block
# using timeForSwing, totalAngleNeeded and 1 meter saber length, calculate saber speed

# List off hard swing angles for both hands


# Each swing entry for left and right hand array should contain
# Block[numberOfBlocks[1 to 4], position[X,Y], angleOfBlock(degree), totalAngleNeeded[160-273.74], timeForSwing(ms), ForeHand?]
# 273.74 = 200 + tan-1(0.75/1)*2 (worst case inverts/quadruple sliders)

# Final difficulty based on Total amount of notes, fastest swings using a rolling average of 4, angle difficulty average for whole map
