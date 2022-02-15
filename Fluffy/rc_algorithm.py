#!/usr/bin/python3.10
# Setup Python ----------------------------------------------- #
import pygame, sys, random, time, os, json, math
from shutil import copyfile
# Get ID ----------------------------------------------------- #
try:
    f = open('bs_path.txt','r')
    bs_path = f.read()
    f.close()
except FileNotFoundError:
    print('Enter Beat Saber custom songs folder:')
    bs_path = input()
    f = open('bs_path.txt','w')
    dat = f.write(bs_path)
    f.close()

print('Enter song ID:')
#song_id = input()
print('Enter difficulty (like ExpertPlus):')
#song_diff = input() + '.dat'
song_id = "1a37c"  # For Debugging
song_diff = "ExpertPlusStandard.dat"

# Setup pygame/window ---------------------------------------- #
mainClock = pygame.time.Clock()
from pygame.locals import *
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(128)
pygame.display.set_caption('rc_algorithm')
WINDOWWIDTH = 750
WINDOWHEIGHT = 500
screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT),0,32)

# Font ------------------------------------------------------- #
font = pygame.font.SysFont('verdana', 10)

# Text ------------------------------------------------------- #
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    screen.blit(textobj, textrect)

# Data ------------------------------------------------------- #
cut_direction_index = [90,270,0,180,45,135,315,225]

# Funcs ------------------------------------------------------ #
def load_song_dat(path):
    main_path = path
    with open(main_path) as json_dat:
        dat = json.load(json_dat)
    return dat

def draw_triangle(surf,point,angle,radius):
    points = [point,[point[0]+radius*math.cos(math.radians(angle+45)),point[1]+radius*math.sin(math.radians(angle+45))],[point[0]+radius*math.cos(math.radians(angle-45)),point[1]+radius*math.sin(math.radians(angle-45))]]
    pygame.draw.polygon(surf,(255,255,255),points)

def get_note_endpoints(note):
    endpoint_spread = 0.5
    pos = [note['_lineIndex']-2,3-(note['_lineLayer']-1.5)] #Gets the X and Y positions of the note
    cut_direction = note['_cutDirection']
    if cut_direction != 8:  
        start_point = [pos[0]+math.cos(math.radians(cut_direction_index[cut_direction]))*endpoint_spread,pos[1]+math.sin(math.radians(cut_direction_index[cut_direction]))*endpoint_spread]
        end_point = [pos[0]+math.cos(math.radians(cut_direction_index[cut_direction]+180))*endpoint_spread,pos[1]+math.sin(math.radians(cut_direction_index[cut_direction]+180))*endpoint_spread]
    else:
        start_point = pos.copy()
        end_point = pos.copy()
    return [start_point,end_point]


def generate_angle_data(note_data):
    angle_data = []
    last_left = []
    last_right = []
    last_left_angle = 0
    last_right_angle = 0
    difr_x = 0
    difr_y = 0
    difl_x = 0
    difl_y = 0
    l_bonus = 0
    r_bonus = 0
    right_spacing = 9999
    left_spacing = 9999
    l_id = 0
    r_id = 0
    for note in note_data:
        new_l = False
        new_r = False
        if note['_type'] == 0: # left
            new_l = True
            l_id += 1
            if last_left != []:
                left_spacing = note['_time'] - last_left[-1]
                left_spacing = max(0.25,left_spacing)
                new_left = get_note_endpoints(note)[0]
                difl_x = new_left[1]-last_left[1]
                difl_y = new_left[0]-last_left[0]
                angle_1 = math.atan2(difl_x,difl_y) # angle between notes
                if (abs(difl_x) < 0.01) and (abs(difl_y) < 0.01):
                    if (note['_cutDirection'] != 8):
                        angle_1 = math.radians(180+cut_direction_index[note['_cutDirection']]) # if endpoints meet, angle is the angle of the current note
                    else:
                        angle_1 = last_left_angle # don't modify angle if endpoints meet and note is dot
                angle_2 = last_left[2] # angle through previous note - use this to calculate the change in angles
                last_left_angle = angle_1
            last_left = get_note_endpoints(note)[1]
            if (note['_cutDirection'] != 8):
                l_bonus = 1 # account for distance between note enpoints
                if (abs(difl_x) < 0.01) and (abs(difl_y) < 0.01):
                    l_bonus = 2
                last_left.append(math.radians(180+cut_direction_index[note['_cutDirection']]))
            else:
                l_bonus = 0 # no distance between note endpoints on dots
                last_left.append(last_left_angle)
            last_left.append(note['_time'])
        if note['_type'] == 1: # right
            new_r = True
            r_id += 1
            if last_right != []:
                right_spacing = note['_time'] - last_right[-1]
                right_spacing = max(0.35,right_spacing)
                new_right = get_note_endpoints(note)[0]
                difr_x = new_right[1]-last_right[1]
                difr_y = new_right[0]-last_right[0]
                angle_1 = math.atan2(difr_x,difr_y) # angle between notes
                if (abs(difr_x) < 0.01) and (abs(difr_y) < 0.01):
                    if (note['_cutDirection'] != 8):
                        angle_1 = math.radians(180+cut_direction_index[note['_cutDirection']]) # if endpoints meet, angle is the angle of the current note
                    else:
                        angle_1 = last_right_angle # don't modify angle if endpoints meet and note is dot
                angle_2 = last_right[2] # angle through previous note - use this to calculate the change in angles
                last_right_angle = angle_1
            last_right = get_note_endpoints(note)[1]
            if (note['_cutDirection'] != 8):
                r_bonus = 1
                if (abs(difr_x) < 0.01) and (abs(difr_y) < 0.01):
                    r_bonus = 2
                last_right.append(math.radians(180+cut_direction_index[note['_cutDirection']]))
            else:
                r_bonus = 0
                last_right.append(last_right_angle)
            last_right.append(note['_time'])
        angle_data.append([[last_left_angle,math.sqrt(difl_x**2+difl_y**2)+l_bonus,left_spacing,[l_id,new_l]],[last_right_angle,math.sqrt(difr_x**2+difr_y**2)+r_bonus,right_spacing,[r_id,new_r]]])
    return angle_data

def get_recent_diff_data(amount,index,data):
    remaining_left = amount
    remaining_right = amount
    left_history = []
    right_history = []
    n = index
    l_id = -1
    r_id = -1
    while remaining_left > 0:
        if n > 0:
            if data[n][0][-1][1] == True:
                l_id = data[n][0][-1][0]
                left_history.append(score_data(data[n][0]))
                remaining_left -= 1
            else:
                left_history.append(0)
                remaining_left -= 1
        else:
            left_history.append(0)
            remaining_left -= 1
        n -= 1
    n = index
    while remaining_right > 0:
        if n > 0:
            if data[n][1][-1][1] == True:
                r_id = data[n][1][-1][0]
                right_history.append(score_data(data[n][1]))
                remaining_right -= 1
            else:
                right_history.append(0)
                remaining_right -= 1
        else:
            right_history.append(0)
            remaining_right -= 1
        n -= 1
    return left_history, right_history

def score_recent_data(data,threshold): # data is sorted by score - top `threshold` scores are accounted for
    data.sort(reverse=True)
    total = 0
    for i in range(threshold):
        total += data[i]
    return total/threshold

def score_data(data):
    return data[1]**0.9/data[2]
    
# Setup ------------------------------------------------------ #
bs_song_path = bs_path
if bs_song_path[-1] not in ['\\','/']: #Checks if song path is empty
    bs_song_path += '/'
song_options = os.listdir(bs_song_path)
for song in song_options:
    if song.find(song_id) != -1:
        song_folder = song
        break
song_folder_contents = os.listdir(bs_song_path + song_folder + '/')
for song in song_folder_contents:
    if song[-4:] in ['.egg','.ogg']:
        song_file_name = song
        break

full_music_path = bs_song_path + song_folder + '/' + song_file_name #Loads the Full song music file into variable full_music_path

song_dat = load_song_dat(bs_song_path + song_folder + '/' + song_diff)
song_notes_temp = song_dat['_notes']
song_notes = []
n = 0
for song_note in song_notes_temp:       #Filters Out Left and Right notes from all notes and shoves it into an array
    if song_note['_type'] in [0,1]:
        song_notes.append([float(song_note['_time']),n,song_note])
        n += 1
song_notes.sort(reverse=True)

song_notes_original = []
for song_note in song_notes_temp:   
    if song_note['_type'] in [0,1]:
        song_notes_original.append(song_note.copy())

stack = [0,[]] # time, contents
n = 0
for song_note in song_notes_original:
    if song_note['_type'] == 0: # left
        if song_note['_time'] != stack[0]:
            if len(stack[1]) > 1: #Checks if notes are stacked
                total_x = 0
                total_y = 0
                for note in stack[1]:
                    total_x += song_notes_original[note]['_lineIndex']
                    total_y += song_notes_original[note]['_lineLayer']
                total_x /= len(stack[1])
                total_y /= len(stack[1])
                for note in stack[1]:
                    song_notes_original[note]['_cutDirection'] = 8
                    song_notes_original[note]['_lineIndex'] = total_x
                    song_notes_original[note]['_lineLayer'] = total_y
            stack[0] = song_note['_time']
            stack[1] = [n]
        else:
            stack[1].append(n)
    n += 1
# twas lazy and copy-pasted
stack = [0,[]] # time, contents
n = 0
for song_note in song_notes_original:
    if song_note['_type'] == 1: # right
        if song_note['_time'] != stack[0]:
            if len(stack[1]) > 1:
                total_x = 0
                total_y = 0
                for note in stack[1]:
                    total_x += song_notes_original[note]['_lineIndex']
                    total_y += song_notes_original[note]['_lineLayer']
                total_x /= len(stack[1])
                total_y /= len(stack[1])
                for note in stack[1]:
                    song_notes_original[note]['_cutDirection'] = 8
                    song_notes_original[note]['_lineIndex'] = total_x
                    song_notes_original[note]['_lineLayer'] = total_y
            stack[0] = song_note['_time']
            stack[1] = [n]
        else:
            stack[1].append(n)
    n += 1

song_info = load_song_dat(bs_song_path + song_folder + '/info.dat')

bpm = song_info['_beatsPerMinute']
bpms = bpm/60/1000

#boop_sfx = pygame.mixer.Sound('boop.wav')
sounds_played = 0

song_angles = generate_angle_data(song_notes_original)

left_score_map = []
right_score_map = []
lstam_score_map = []
rstam_score_map = []
stam_portion = int(len(song_angles)/50 + 40)
for n in range(len(song_angles)):
    right_score_map.append(score_recent_data(get_recent_diff_data(7,n,song_angles.copy())[1],5))
    left_score_map.append(score_recent_data(get_recent_diff_data(7,n,song_angles.copy())[0],5)) # take last 9 notes and average top 4
    rstam_score_map.append(score_recent_data(get_recent_diff_data(stam_portion,n,song_angles.copy())[1],stam_portion))
    lstam_score_map.append(score_recent_data(get_recent_diff_data(stam_portion,n,song_angles.copy())[0],stam_portion))

def zero_scores(data):
    for n in range(len(data)):
        try:
            if data[-n-1] == data[-n-2]:
                data[-n-1] = 0
        except IndexError:
            pass

def ghost_scores(data):
    for n in range(len(data)):
        try:
            if data[n+1] == 0:
                data[n+1] = data[n] * 0.8
        except IndexError:
            pass

zero_scores(left_score_map)
zero_scores(right_score_map)
zero_scores(rstam_score_map)
zero_scores(lstam_score_map)

ghost_scores(left_score_map)
ghost_scores(right_score_map)
ghost_scores(rstam_score_map)
ghost_scores(lstam_score_map)

combined_scores = []
for val in range(len(left_score_map)):
    combined_scores.append(((left_score_map[val]+lstam_score_map[val]*0.3)**2+(right_score_map[val]+rstam_score_map[val]*0.3)**2)**(1/2))
combined_scores.sort(reverse=True)
top_2_percent = sum(combined_scores[:int(len(combined_scores)/50)])/int(len(combined_scores)/50)
top_5_percent = sum(combined_scores[:int(len(combined_scores)/20)])/int(len(combined_scores)/20)
top_20_percent = sum(combined_scores[:int(len(combined_scores)/5)])/int(len(combined_scores)/5)
top_50_percent = sum(combined_scores[:int(len(combined_scores)/2)])/int(len(combined_scores)/2)
top_70_percent = sum(combined_scores[:int(len(combined_scores)*0.7)])/int(len(combined_scores)*0.7)
median = combined_scores[int(len(combined_scores)/2)]

top_2_percent = top_2_percent*bpm**1.05/300
top_5_percent = top_5_percent*bpm**1.05/300
top_20_percent = top_20_percent*bpm**1.05/300
top_50_percent = top_50_percent*bpm**1.05/300
top_70_percent = top_70_percent*bpm**1.05/300

#print(top_2_percent,top_5_percent,top_20_percent,top_50_percent,top_70_percent,median)
#print(len(left_score_map))
final_score = (top_20_percent*2+top_5_percent*3+top_2_percent*4+top_70_percent*3+median)/13
print(final_score)

music = pygame.mixer.Sound(full_music_path)
music.play()
#pygame.mixer.music.play(0)
start_time = time.time()

last_angles = [[0,0,999],[0,0,999]]

peak_left_diff = 0
peak_right_diff = 0
left_ghost_val = 0
right_ghost_val = 0

peak_lstam_diff = 0
peak_rstam_diff = 0
lstam_ghost_val = 0
rstam_ghost_val = 0

score_sum_ghost_val = 0
score_sum_peak = 0

# Loop ------------------------------------------------------- #
while True:
    # Background --------------------------------------------- #
    screen.fill((0,0,0))
    # Render ------------------------------------------------- #
    time_progress = (time.time()-start_time)*1000*bpms
    n = 0
    for note in song_notes:
        note = note[2]
        note_num = len(song_notes)-n-1
        if note['_type'] in [0,1]:
            if (note['_time'] > time_progress-(150*bpms)) and (note['_time'] < time_progress+(1000*bpms)):
                note_x = note['_lineIndex']-2
                note_y = 3-(note['_lineLayer']-1.5)
                age = time_progress+(1000*bpms)-note['_time']
                size = age*12.5
                pos_x = 270+note_x*(6+size)
                pos_y = 80+note_y*(6+size)
                if note['_type'] == 0:
                    color = (255,0,0)
                if note['_type'] == 1:
                    color = (0,0,255)
                if note['_time'] > time_progress:
                    surf = pygame.Surface((int(size),int(size)))
                    surf.set_alpha(150)
                    surf.fill(color)
                    screen.blit(surf,(pos_x-int(size/2),pos_y-int(size/2)))
                    if note['_cutDirection'] != 8:
                        draw_triangle(screen,[pos_x,pos_y],cut_direction_index[note['_cutDirection']],int(size/(2*math.sqrt(2))))
                    else:
                        pygame.draw.circle(screen,(255,255,255),[int(pos_x),int(pos_y)],int(size/6))
                else:
                    if sounds_played <= note_num:
                        #last_angles = song_angles[sounds_played+1]
                        sounds_played += 1
                        #boop_sfx.play()
                    alt_size = int(size+(age-(1000*bpms))*150)
                    surf_1 = pygame.Surface((alt_size,alt_size))
                    surf_2 = pygame.Surface((alt_size-4,alt_size-4))
                    surf_1.fill(color)
                    surf_1.blit(surf_2,(2,2))
                    surf_1.set_colorkey((0,0,0))
                    surf_1.set_alpha(255-(age-(1000*bpms))/(150*bpms)*255)
                    screen.blit(surf_1,(pos_x-int(alt_size/2),pos_y-int(alt_size/2)))
        n += 1
    # UI ----------------------------------------------------- #
    progress_ms = pygame.mixer.music.get_pos()
    progress_s = progress_ms/1000
    progress_s = int(progress_s)
    draw_text(str(progress_s), font, (255,255,255), screen, 2, 2)

    difficulty_r = (last_angles[1][1])**1.25/last_angles[1][2]
    difficulty_l = (last_angles[0][1])**1.25/last_angles[0][2]

    pygame.draw.line(screen,(255,0,0),[100,400],[100+math.cos(last_angles[0][0])*15*(last_angles[0][1]+1),400+math.sin(last_angles[0][0])*15*(last_angles[0][1]+1)],3)
    pygame.draw.circle(screen,(255,0,0),[100,400],7)
    pygame.draw.circle(screen,(155,0,0),[100,400],int(15*(last_angles[0][1]+1))+1,2)
    pygame.draw.circle(screen,(255,255,255),[100,400],int(15*difficulty_l)+2,2)
    pygame.draw.line(screen,(0,0,255),[400,400],[400+math.cos(last_angles[1][0])*15*(last_angles[1][1]+1),400+math.sin(last_angles[1][0])*15*(last_angles[1][1]+1)],3)
    pygame.draw.circle(screen,(0,0,255),[400,400],7)
    pygame.draw.circle(screen,(0,0,155),[400,400],int(15*(last_angles[1][1]+1))+1,2)
    pygame.draw.circle(screen,(255,255,255),[400,400],int(15*difficulty_r)+2,2)

    left_difficulty_average = left_score_map[sounds_played]
    right_difficulty_average = right_score_map[sounds_played]
    lstam_difficulty_average = lstam_score_map[sounds_played]
    rstam_difficulty_average = rstam_score_map[sounds_played]

    peak_lstam_diff = max(peak_lstam_diff,lstam_difficulty_average)
    peak_rstam_diff = max(peak_rstam_diff,rstam_difficulty_average)
    peak_left_diff = max(peak_left_diff,left_difficulty_average)
    peak_right_diff = max(peak_right_diff,right_difficulty_average)
    lstam_ghost_val -= 0.01
    rstam_ghost_val -= 0.01
    left_ghost_val -= 0.05
    right_ghost_val -= 0.05
    left_ghost_val = max(left_ghost_val,left_difficulty_average)
    right_ghost_val = max(right_ghost_val,right_difficulty_average)
    lstam_ghost_val = max(lstam_ghost_val,lstam_difficulty_average)
    rstam_ghost_val = max(rstam_ghost_val,rstam_difficulty_average)

    score_sum = ((left_ghost_val+lstam_ghost_val)**3 + (right_ghost_val+rstam_ghost_val)**3)**(1/3)

    score_sum_ghost_val -= 0.01
    score_sum_ghost_val = max(score_sum,score_sum_ghost_val)

    score_sum_peak = max(score_sum_peak,score_sum)

    sum_ghost_rect = pygame.Rect(WINDOWWIDTH-145,WINDOWHEIGHT-7-score_sum_ghost_val*15,20,score_sum_ghost_val*15+2)
    sum_rect = pygame.Rect(WINDOWWIDTH-145,WINDOWHEIGHT-7-score_sum*15,20,score_sum*15+2)
    pygame.draw.rect(screen,(0,100,0),sum_ghost_rect)
    pygame.draw.rect(screen,(0,255,0),sum_rect)
    pygame.draw.line(screen,(255,255,255),[WINDOWWIDTH-145,WINDOWHEIGHT-8-score_sum_peak*15],[WINDOWWIDTH-125,WINDOWHEIGHT-8-score_sum_peak*15],2)
    
    # ghost vals
    lg_rect = pygame.Rect(WINDOWWIDTH-100,WINDOWHEIGHT-7-left_ghost_val*15,20,left_ghost_val*15+2)
    rg_rect = pygame.Rect(WINDOWWIDTH-75,WINDOWHEIGHT-7-right_ghost_val*15,20,right_ghost_val*15+2)
    pygame.draw.rect(screen,(100,0,0),lg_rect)
    pygame.draw.rect(screen,(0,0,100),rg_rect)
    lstamg_rect = pygame.Rect(WINDOWWIDTH-50,WINDOWHEIGHT-7-lstam_ghost_val*15,20,lstam_ghost_val*15+2)
    rstamg_rect = pygame.Rect(WINDOWWIDTH-25,WINDOWHEIGHT-7-rstam_ghost_val*15,20,rstam_ghost_val*15+2)
    pygame.draw.rect(screen,(100,25,0),lstamg_rect)
    pygame.draw.rect(screen,(0,25,100),rstamg_rect)
    # realtime vals
    l_rect = pygame.Rect(WINDOWWIDTH-100,WINDOWHEIGHT-7-left_difficulty_average*15,20,left_difficulty_average*15+2)
    r_rect = pygame.Rect(WINDOWWIDTH-75,WINDOWHEIGHT-7-right_difficulty_average*15,20,right_difficulty_average*15+2)
    pygame.draw.rect(screen,(255,0,0),l_rect)
    pygame.draw.rect(screen,(0,0,255),r_rect)
    lstam_rect = pygame.Rect(WINDOWWIDTH-50,WINDOWHEIGHT-7-lstam_difficulty_average*15,20,lstam_difficulty_average*15+2)
    rstam_rect = pygame.Rect(WINDOWWIDTH-25,WINDOWHEIGHT-7-rstam_difficulty_average*15,20,rstam_difficulty_average*15+2)
    pygame.draw.rect(screen,(255,50,0),lstam_rect)
    pygame.draw.rect(screen,(0,50,255),rstam_rect)
    for i in range(26):
        pygame.draw.line(screen,(255,255,255),[WINDOWWIDTH-120,WINDOWHEIGHT-5-i*15],[WINDOWWIDTH-102,WINDOWHEIGHT-5-i*15],2)
        draw_text(str(i), font, (255,255,255), screen, WINDOWWIDTH-120, WINDOWHEIGHT-19-i*15)
    pygame.draw.line(screen,(255,255,255),[WINDOWWIDTH-100,WINDOWHEIGHT-8-peak_left_diff*15],[WINDOWWIDTH-80,WINDOWHEIGHT-8-peak_left_diff*15],2)
    pygame.draw.line(screen,(255,255,255),[WINDOWWIDTH-75,WINDOWHEIGHT-8-peak_right_diff*15],[WINDOWWIDTH-55,WINDOWHEIGHT-8-peak_right_diff*15],2)
    pygame.draw.line(screen,(255,255,255),[WINDOWWIDTH-50,WINDOWHEIGHT-8-peak_lstam_diff*15],[WINDOWWIDTH-30,WINDOWHEIGHT-8-peak_lstam_diff*15],2)
    pygame.draw.line(screen,(255,255,255),[WINDOWWIDTH-25,WINDOWHEIGHT-8-peak_rstam_diff*15],[WINDOWWIDTH-5,WINDOWHEIGHT-8-peak_rstam_diff*15],2)
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
