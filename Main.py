#!/usr/bin/env python2

# ====================================== #
# ===Import all the relevant packages=== #
# ====================================== #

import csv
import numpy as np  # for timing and array operations
import random  # for randomization of trials
import time as ts
import os

import pandas as pd
from psychopy import core, gui, event, logging
from psychopy import visual
from psychopy.tools.filetools import fromFile, toFile  # saving and loading parameter files

import BasicPromptTools  # for loading/presenting prompts and questions
import HelperFunctions
import RatingScales
from HelperFunctions import reverse_string
#from devices import Pathway
from time import time, sleep
from Medoc_control_new import Pathway
import serial
import serial.tools.list_ports as list_ports
from psychopy.iohub import launchHubServer


# from psychopy import visual # visual causes a bug in the guis, so it's declared after all GUIs run.

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?

"""
This function will take event's that happen on psychopy
then convert and return them as unique hex values

List of events:
Break-time:
'break'                  :   16

T2: 20-27
T3: 40-47
T4: 60-67
T5: 80-87
square 1: 0
square 2: +1
square 3: +2
square 4: +3
square 5: +4
heat pulse: +5
rating: +6

more ratings: 90-92
fixation: 95

'Start_Cycle'            :   100-101

"""

print("bef report_event")
# temp - T2/T4/T6/T8
# event_type - square1/square2/square3/square4/square5/heat_pulse/rating/fixation
def report_event(temp, event_type):
    events = {
        'break': hex(16),

        'T2_square1': hex(20),
        'T2_square2': hex(21),
        'T2_square3': hex(22),
        'T2_square4': hex(23),
        'T2_square5': hex(24),
        'T2_heat_pulse': hex(25),
        'T2_PainRatingScale': hex(26),

        'T4_square1': hex(40),
        'T4_square2': hex(41),
        'T4_square3': hex(42),
        'T4_square4': hex(43),
        'T4_square5': hex(44),
        'T4_heat_pulse': hex(45),
        'T4_PainRatingScale': hex(46),

        'T6_square1': hex(60),
        'T6_square2': hex(61),
        'T6_square3': hex(62),
        'T6_square4': hex(63),
        'T6_square5': hex(64),
        'T6_heat_pulse': hex(65),
        'T6_PainRatingScale': hex(66),

        'T8_square1': hex(80),
        'T8_square2': hex(81),
        'T8_square3': hex(82),
        'T8_square4': hex(83),
        'T8_square5': hex(84),
        'T8_heat_pulse': hex(85),
        'T8_PainRatingScale': hex(86),

        'PreVas_rating': hex(90),
        'MidRun_rating': hex(91),
        'PostRun_rating': hex(92),

        'Fixation_cross': hex(95),

        'Start_Cycle': hex(100)
    }

    all_ports = list_ports.comports()
    print(all_ports)

    ser3 = serial.Serial('COM4', 115200, bytesize=serial.EIGHTBITS, timeout=1)
    if ser3.is_open:
        print("connection is open")
    ser3.write("RR".encode())

    ######## Testing the output #######
    ## event sending
    ser3.write(events[event_type].encode())
    core.wait(0.05)
    ser3.write("RR".encode())
    print("closing")
    ser3.close()
    print("closed")

    return events[event_type]

def createPrintLogFile():
    logging.flush()
    with open(filename + '.log', "r", encoding='ascii', errors='ignore') as file:
        items = []
        for line in file:
            row = []
            split = line.split(" ")
            row.append(split[0])
            count = 0
            copy_lines_from = 1
            for i in split[1:]:
                if not i == " ":
                    if count == 1:
                        break

                    row.append(i[1:])
                    count += 1
                copy_lines_from += 1
            b = " ".join(split[copy_lines_from:])
            b = b[1:-1]
            row.append(b)
            items.append(row)

    df2 = pd.DataFrame(items, columns=['Time', 'Level', 'msg'])
    df2.to_csv('logPrints%s.csv' % expInfo['subject'])

INSTRUCTIONS_SLIDES = 36

# Declare primary task parameters.
params = {
    # Declare stimulus and response parameters
    'screenIdx': 0,
    'nTrials': 8,  # number of squares in each block
    'nBlocks': 5,  # number of blocks (aka runs) - need time to move electrode in between
    'painDur': 4,  # time of heat sensation (in seconds)
    'tStartup': 5,  # pause time before starting first stimulus
    # declare prompt and question files
    'skipPrompts': True,  # go right to the task after vas and baseline
    'skipInstructions': False,  # skip instructions slides
    'promptDir': './Text/',  # directory containing prompts and questions files
    'promptFile': './HeatAnticipationPrompts.txt',  # Name of text file containing prompts
    # 'initialpromptFile': 'InitialSafePrompts.txt',  # explain "safe" and "get ready" before the practice - NOT USING THESE SCREENS RIGHT NOW
    'questionFile': './AnxietyScale.txt',  # Name of text file containing Q&As
    'questionDownKey': 'left',  # move slider left
    'questionUpKey': 'right',  # move slider right
    'questionDur': 6.0,
    'vasStepSize': 0.5,  # how far the slider moves with a keypress (increase to move faster)
    'textColor': 'gray',  # black in rgb255 space or gray in rgb space
    'PreVasMsg': reverse_string("כעת נבצע דירוגים"),  # Text shown BEFORE each VAS except the final one
    'introPractice': 'Questions/PracticeRating.txt',  # Name of text file containing practice rating scales
    'moodQuestionFile1': 'Questions/ERVas1RatingScales.txt',
    # Name of text file containing mood Q&As presented before run
    'moodQuestionFile2': 'Questions/ERVasRatingScales.txt',
    # Name of text file containing mood Q&As presented after 3rd block
    'moodQuestionFile3': 'Questions/ERVas4RatingScales.txt',
    # Name of text file containing pain Rating Scale presented after each trial
    'MoodRatingPainFile': 'Questions/MoodRatingPainFile.txt',
    # Name of text file containing mood Q&As presented after run
    'questionSelectKey': 'up',  # select answer for VAS
    'questionSelectAdvances': True,  # will locking in an answer advance past an image rating?
    'vasTextColor': 'black',  # color of text in both VAS types (-1,-1,-1) = black
    'vasMarkerSize': 0.1,  # in norm units (2 = whole screen)
    'vasLabelYDist': 0.1,  # distance below line that VAS label/option text should be, in norm units
    # declare display parameters
    'screenToShow': 1,  # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 50,  # size of cross, in pixels
    'fixCrossPos': [0, 0],  # (x,y) pos of fixation cross displayed before each stimulus (for gaze drift correction)
    'screenColor': (217, 217, 217),  # in rgb255 space: (r,g,b) all between 0 and 255 - light grey
    # parallel port parameters
    'sendPortEvents': False,  # send event markers to biopac computer via parallel port
    'portAddress': 20121,  # 0xE050,  0x0378,  address of parallel port
    'codeBaseline': 144,  # parallel port code for baseline period
    'codeFixation': 143,  # parallel port code for fixation period - safe
    'codeReady': 145,  # parallel port code for Get ready stimulus
    'codeVAS': 142,  # parallel port code for 3 VASs
    'squareDurationMin': 3, # minimum duration for each square
    'squareDurationMax': 6, # maximum duration for each square
    'painRateDuration': 7, # pain rating duration
    'convExcel': 'tempConv.xlsx',  # excel file with temp to binary code mappings
    # 'image1': 'img/image1.png',
    # 'image2': 'img/image2.png',
    # 'image3': 'img/image3.png',
    # 'techInstructionImage1': 'img/techInstructionImage1.png',
    # 'techInstructionImage2': 'img/techInstructionImage2.png',
}

# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #

scriptName = 'TIM.py'
try:  # try to get a previous parameters file
    expInfo = fromFile('%s-lastExpInfo.psydat' % scriptName)
    expInfo['session'] = 1  # automatically increment session number
    expInfo['Gender'] = ["female", "male"]
    expInfo['Language'] = ["Hebrew", "English"]
    expInfo['T2'] = ["34.0", "34.5", "35.0", "35.5","36.0", "36.5", "37.0", "37.5","38.0", "38.5", "39.0", "39.5","40.0", "40.5", "41.0", "41.5",
                     "42.0", "42.5", "43.0", "43.5","44.0", "44.5", "45.0", "45.5","46.0", "46.5", "47.0", "47.5","48.0", "48.5", "49.0", "49.5", "50.0"]
    expInfo['T4'] = ["34.0", "34.5", "35.0", "35.5","36.0", "36.5", "37.0", "37.5","38.0", "38.5", "39.0", "39.5","40.0", "40.5", "41.0", "41.5",
                     "42.0", "42.5", "43.0", "43.5","44.0", "44.5", "45.0", "45.5","46.0", "46.5", "47.0", "47.5","48.0", "48.5", "49.0", "49.5", "50.0"]
    expInfo['T6'] = ["34.0", "34.5", "35.0", "35.5","36.0", "36.5", "37.0", "37.5","38.0", "38.5", "39.0", "39.5","40.0", "40.5", "41.0", "41.5",
                     "42.0", "42.5", "43.0", "43.5","44.0", "44.5", "45.0", "45.5","46.0", "46.5", "47.0", "47.5","48.0", "48.5", "49.0", "49.5", "50.0"]
    expInfo['T8'] = ["34.0", "34.5", "35.0", "35.5","36.0", "36.5", "37.0", "37.5","38.0", "38.5", "39.0", "39.5","40.0", "40.5", "41.0", "41.5",
                     "42.0", "42.5", "43.0", "43.5","44.0", "44.5", "45.0", "45.5","46.0", "46.5", "47.0", "47.5","48.0", "48.5", "49.0", "49.5", "50.0"]
    expInfo['Pain Support'] = True
    expInfo['Skip Instructions'] = False

except:  # if not there then use a default set
    expInfo = {
        'subject': '1',
        'session': 1,
        'Gender': 'female',
        'Language': 'Hebrew',
        'T2': '36.0',
        'T4': '41.0',
        'T6': '46.0',
        'T8': '50.0',
        'Pain Support': True,
        'Skip Instructions': False,
    }

# present a dialogue to change select params
dlg = gui.DlgFromDict(expInfo, title=scriptName, order=['subject', 'session', 'Gender', 'Language', 'T2', 'T4', 'T6', 'T8', 'Pain Support', 'Skip Instructions'])
if not dlg.OK:
    core.quit()  # the user hit cancel, so exit

params['painSupport'] = expInfo['Pain Support']
params['skipInstructions'] = expInfo['Skip Instructions']
params['language'] = expInfo['Language']

# save experimental info
toFile('%s-lastExpInfo.psydat' % scriptName, expInfo)  # save params to file for next time

# make a log file to save parameter/event  data
dateStr = ts.strftime("%b_%d_%H%M", ts.localtime())  # add the current time
filename = '%s-%s-%d-%s' % (scriptName, expInfo['subject'], expInfo['session'], dateStr)  # log filename
logging.LogFile((filename + '.log'), level=logging.INFO)  # , mode='w') # w=overwrite
logging.log(level=logging.INFO, msg='---START PARAMETERS---')
logging.log(level=logging.INFO, msg='filename: %s' % filename)
logging.log(level=logging.INFO, msg='subject: %s' % expInfo['subject'])
logging.log(level=logging.INFO, msg='session: %s' % expInfo['session'])
logging.log(level=logging.INFO, msg='T2: %s' % expInfo['T2'])
logging.log(level=logging.INFO, msg='T4: %s' % expInfo['T4'])
logging.log(level=logging.INFO, msg='T6: %s' % expInfo['T6'])
logging.log(level=logging.INFO, msg='T8: %s' % expInfo['T8'])
logging.log(level=logging.INFO, msg='date: %s' % dateStr)
# log everything in the params struct
for key in sorted(params.keys()):  # in alphabetical order
    logging.log(level=logging.INFO, msg='%s: %s' % (key, params[key]))  # log each parameter

logging.log(level=logging.INFO, msg='---END PARAMETERS---')

VAS_file_name = 'subject' + expInfo['subject'] + '_VAS.csv'
# create a csv file to contain VAS data of the 5 questions
csv_file = open(VAS_file_name, mode='a', encoding='ascii', errors='ignore')
# create a csv.writer object
csv_writer = csv.writer(csv_file, delimiter=',')


def write_to_csv(info_to_csv, name_csv_file):
    writer = csv.writer(name_csv_file)
    writer.writerow(info_to_csv)

params['instructionsFolder'] = './instructions/instructions'
if params['language'] == 'english':
    params['instructionsSuffix'] = '_E'
elif expInfo['Gender'] == 'female':
    params['instructionsSuffix'] = '_F'
else:
    params['instructionsSuffix'] = '_M'

# ==================================== #
# == SET UP PARALLEL PORT AND MEDOC == #
# ==================================== #
#
if params['painSupport']:
    if params['sendPortEvents']:
        from psychopy import parallel

        port = parallel.ParallelPort(address=params['portAddress'])
        port.setData(0)  # initialize to all zeros
    else:
        print("Parallel port not used.")


if params['painSupport']:
    # ip and port number from medoc application
    my_pathway = Pathway(ip='192.168.55.80', port_number=20121)
    print("mypathway create")

    # Check status of medoc connection
    # response = my_pathway.status()
    response = my_pathway.sendCommand(0)
    print("send command status was sent")
    print(response)


# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #

# Initializing screen Resolution
# screenRes = [1024, 768] previous one
screenRes = [1920, 1080]

# Initialize deadline for displaying next frame
tNextFlip = [0.0]  # put in a list to make it mutable (weird quirk of python variables)

# create clocks and window
globalClock = core.Clock()  # to keep track of time
win = visual.Window(screenRes, fullscr=False, monitor='testMonitor',
                    screen=params['screenToShow'], units='deg', name='win', color=params['screenColor'],
                    colorSpace='rgb255')
win.setMouseVisible(False)
# create fixation cross
fCS = params['fixCrossSize']  # size (for brevity)
fCP = params['fixCrossPos']  # position (for brevity)
fixation = visual.TextStim(win, pos=[0, 5], text='SAFE', font='Arial Hebrew', color='skyblue', alignHoriz='center',
                           bold=True, height=3.5)

fixationReady = visual.TextStim(win, pos=[0, 5], text='GET READY', font='Arial Hebrew', color='gray',
                                alignHoriz='center', bold=True, height=3.5, wrapWidth=500)
fixationCross = visual.ShapeStim(win, lineColor='#000000', lineWidth=5.0, vertices=(
    (fCP[0] - fCS / 2, fCP[1]), (fCP[0] + fCS / 2, fCP[1]), (fCP[0], fCP[1]), (fCP[0], fCP[1] + fCS / 2),
    (fCP[0], fCP[1] - fCS / 2)), units='pix', closeShape=False, name='fixCross');
# create text stimuli
message1 = visual.TextStim(win, pos=[0, +.5], wrapWidth=1.5, color='#000000', alignHoriz='center', name='topMsg',
                           text="aaa", units='norm')
message2 = visual.TextStim(win, pos=[0, -.5], wrapWidth=1.5, color='#000000', alignHoriz='center', name='bottomMsg',
                           text="bbb", units='norm')

# load VAS Qs & options
[questions, options, answers] = BasicPromptTools.ParseQuestionFile(params['questionFile'])
print('%d questions loaded from %s' % (len(questions), params['questionFile']))

# get stimulus files

# image slide in instructions to explain color of square
promptImage = 'TIMprompt2.jpg'
stimImage = visual.ImageStim(win, pos=[0, 0], name='ImageStimulus', image=promptImage, units='pix')

color_list = [1, 2, 3, 4, 1, 2, 3, 4]  # 1-white, 2-green, 3-yellow, 4-red, ensure each color is presented twice at random per block
random.shuffle(color_list)

sleepRand = [0, 0.5, 1, 1.5, 2]  # slightly vary onset of heat pain

# for "random" ITI avg 15 sec
painITI = 0
painISI = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5]
random.shuffle(painISI)

# read questions and answers from text files for instructions text, 3 Vass, and practice scale questions
[topPrompts, bottomPrompts] = BasicPromptTools.ParsePromptFile(params['promptDir'] + params['promptFile'])
print('%d prompts loaded from %s' % (len(topPrompts), params['promptFile']))

# PROMPTS FOR EXPLANATION - NOT USING
# [topPrompts1, bottomPrompts1] = BasicPromptTools.ParsePromptFile(params['promptDir'] + "InitialSafePrompts1.txt")
# print('%d prompts loaded from %s' % (len(topPrompts1), "InitialSafePrompts1.txt"))
#
# [topPrompts2, bottomPrompts2] = BasicPromptTools.ParsePromptFile(params['promptDir'] + "InitialSafePrompts2.txt")
# print('%d prompts loaded from %s' % (len(topPrompts2), "InitialSafePrompts2.txt"))
#
# [topPrompts3, bottomPrompts3] = BasicPromptTools.ParsePromptFile(params['promptDir'] + "InitialSafePrompts3.txt")
# print('%d prompts loaded from %s' % (len(topPrompts3), "InitialSafePrompts3.txt"))

[questions_vas1, options_vas1, answers_vas1] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile1'])
print('%d questions loaded from %s' % (len(questions_vas1), params['moodQuestionFile1']))

[questions_vas2, options_vas2, answers_vas2] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile2'])
print('%d questions loaded from %s' % (len(questions_vas2), params['moodQuestionFile2']))

[questions_vas3, options_vas3, answers_vas3] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile3'])
print('%d questions loaded from %s' % (len(questions_vas3), params['moodQuestionFile3']))

[questions_RatingPain, options_RatingPain, answers_RatingPain] = BasicPromptTools.ParseQuestionFile(
    params['MoodRatingPainFile'])
print('%d questions loaded from %s' % (len(questions_vas3), params['moodQuestionFile3']))

[questions_prac, options_prac, answers_prac] = BasicPromptTools.ParseQuestionFile(params['introPractice'])
print('%d questions loaded from %s' % (len(questions_prac), params['introPractice']))

listlist = []

# excel in the folder to convert from Celsius temp to binary code for the medoc machine
excelTemps = pd.read_excel(params['convExcel'])


# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
def AddToFlipTime(tIncrement=1.0):
    tNextFlip[0] += tIncrement


# flip window as soon as possible
def SetFlipTimeToNow():
    tNextFlip[0] = globalClock.getTime()


# pause everything until stimuli are ready to move on
def WaitForFlipTime():
    while (globalClock.getTime() < tNextFlip[0]):
        keyList = event.getKeys()
        # Check for escape characters
        for key in keyList:
            if key in ['q', 'escape']:
                CoolDown()


color_to_T_dict = {
            1: 'T2',
            2: 'T4',
            3: 'T6',
            4: 'T8'
        }


# main function that takes information to run through each trial
def GrowingSquare(color, block, trial, params):
    import time
    global painITI

    # set color of square
    if color == 1:
        col = 'white'
        colCode = int('FFFFFF', 16)
        colorName = 'White'
    if color == 2:
        col = 'darkseagreen'
        colCode = int('8fbc8f', 16)
        colorName = 'Green'
    elif color == 3:
        col = 'khaki'
        colCode = int('FFFF00', 16)     #colCode = int('F0E68C', 16)
        colorName = 'Yellow'
    elif color == 4:
        col = 'lightcoral'
        colCode = int('D21404', 16)     #colCode = int('F08080', 16)
        colorName = 'Red'
    else:
        col = 'white'
        colCode = int('FFFFFF', 16)
        colorName = 'White'

    trialStart = globalClock.getTime()
    phaseStart = globalClock.getTime()

    # Load pre-defined images of square at different sizes
    squareImages = []
    for i in range(1, 6):
        squareImages.append(visual.ImageStim(win, image=f"Circles2/{color}{colorName}_{i}.JPG", pos=(0, 0)))

    # adjusting squares to fit a 24-inch screen
    for i in range(len(squareImages) - 1):
        squareImages[i].size = (squareImages[i].size[0] * 1.5, squareImages[i].size[1] * 1.4)
    # make last square cover the entire screen
    squareImages[len(squareImages) - 1].size *= 2

    WaitForFlipTime()
    # gray color = during the instructions
    if col != 'gray':
        SetPort(color, 1, block, csv_writer)
    win.flip()

    for i in range(1, 6):
        # Set size of rating scale marker based on current square size
        sizeRatio = squareImages[i-1].size[0] / squareImages[0].size[0]

        squareImages[i-1].draw()
        win.flip()
        print("color " + str(color) + 'i: '+str(i-1))
        # send event to biopac
        report_event(color_to_T_dict[color], color_to_T_dict[color] + '_square' + str(i))

        # Wait for specified duration
        square_duration = random.randint(params['squareDurationMin'], params['squareDurationMax'])
        core.wait(square_duration)

        # get new keys
        newKeys = event.getKeys(keyList=['q', 'escape'], timeStamped=globalClock)
        # check each keypress for escape keys
        if len(newKeys) > 0:
            for thisKey in newKeys:
                if thisKey[0] in ['q', 'escape']:  # escape keys
                    CoolDown()  # exit gracefully

        if col != 'gray':
            BehavFile(globalClock.getTime(), block + 1, trial + 1, color, globalClock.getTime() - trialStart, "square",
                      globalClock.getTime() - phaseStart)

    if col != 'gray':
        # prints current time in seconds
        print(time.time())
        SetPort(color, 2, block, csv_writer)
        # starts a clock object called globalClock that was created using core.Clock()) earlier
        # and records the time at which the clock starts running
        phaseStart = globalClock.getTime()
        #  sets a time at which the next stimulus or event should occur
        tNextFlip[0] = globalClock.getTime() + (params['painDur'])
        # starts a Medoc device connected to the computer running the script
        if params['painSupport']:
            # my_pathway.start()
            print(f"Starting sequence before sleep, line 562, round {round}")
            my_pathway.sendCommand('START')
            print("Sent command start")
            core.wait(0.5)
            my_pathway.sendCommand('TRIGGER')
            print("Sent command trigger")
        # make sure can update rating scale while delaying onset of heat pain
        timer = core.Clock()
        # add a randomized delay to the next event
        timer.add(4 + random.sample(sleepRand, 1)[0])
        while timer.getTime() < 0:
            # rect.draw()
            squareImages[-1].draw()

            win.flip()
            BehavFile(globalClock.getTime(), block + 1, trial + 1, color, globalClock.getTime() - trialStart, "full",
                      globalClock.getTime() - phaseStart, )
            # get new keys
            newKeys = event.getKeys(keyList=['q', 'escape'], timeStamped=globalClock)
            # check each keypress for escape keys
            if len(newKeys) > 0:
                for thisKey in newKeys:
                    if thisKey[0] in ['q', 'escape']:  # escape keys
                        CoolDown()  # exit gracefully
        if params['painSupport']:
            # Trigger the device to start the heat pulse
            # my_pathway.trigger()
            print(f"Starting sequence before sleep, line 589, round {round}")
            my_pathway.sendCommand('START')
            print("Sent command start")
            print(f"Get status results - {my_pathway.sendCommand('GET_STATUS')}")
            # core.wait(0.5)
            # my_pathway.sendCommand('TRIGGER')
            # send event to biopac
            report_event(color_to_T_dict[color], color_to_T_dict[color] + '_heat_pulse')
        # give medoc time to give heat before signalling to stop
        timer = core.Clock()
        timer.add(1)
        # stop the Medoc device from delivering the thermal stimulus.
        if params['painSupport']:
            # response = my_pathway.stop()
            print("Stopping")
            response = my_pathway.sendCommand('STOP')
            core.wait(2)
            #response = my_pathway.sendCommand('STOP')
            stat = my_pathway.sendCommand('GET_STATUS').teststatestr
            while(stat != "IDLE"):
                core.wait(0.5)
                stat = my_pathway.sendCommand('GET_STATUS').teststatestr
                print(f"Get status result = {stat}")
            
        # Flush the key buffer and mouse movements
        event.clearEvents()

    return trialStart, phaseStart


# Send parallel port event
def SetPortData(data):
    if params['painSupport'] and params['sendPortEvents']:
        logging.log(level=logging.EXP, msg='set port %s to %d' % (format(params['portAddress'], '#04x'), data))
        port.setData(data)
        print(data)
    else:
        if params['painSupport']:
            print('Port event: %d' % data)


# use color, size, and block to calculate data for SetPortData
def SetPort(color, size, block, csv_writer):
    SetPortData((color - 1) * 6 ** 2 + (size - 1) * 6 + (block))
    if size == 1:
        if color == 1:
            code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['T2']))]
            csv_writer.writerow(["medoc", code.iat[0, 1]])
            logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))
        elif color == 2:
            code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['T4']))]
            csv_writer.writerow(["medoc", code.iat[0, 1]])
            logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))
        elif color == 3:
            code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['T6']))]
            csv_writer.writerow(["medoc", code.iat[0, 1]])
            logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))
        elif color == 4:
            code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['T8']))]
            csv_writer.writerow(["medoc", code.iat[0, 1]])
            logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))

        if params['painSupport']:
            # send command to biopac with parameter matching from excel
            print(f"Selecting TP,  {code.iat[0, 1]}")
            response = my_pathway.sendCommand('SELECT_TP', code.iat[0, 1])
            core.wait(1)
            my_pathway.sendCommand('START')
            # send event to biopac
            report_event(color_to_T_dict[color], color_to_T_dict[color] + '_heat_pulse')

            # Trigger the device to start the heat pulse
            # my_pathway.trigger()

# Handle end of a session


def RunVas(questions, options, io, pos=(0., -0.25), scaleTextPos=[0., 0.25], questionDur=params['questionDur'],
           isEndedByKeypress=params['questionSelectAdvances'], name='Vas'):

    # wait until it's time
    WaitForFlipTime()

    # Show questions and options
    [rating, decisionTime, choiceHistory] = RatingScales.ShowVAS(questions, options, win, questionDur=questionDur,
                                                                 upKey=params['questionUpKey'],
                                                                 downKey=params['questionDownKey'],
                                                                 selectKey=params['questionSelectKey'],
                                                                 isEndedByKeypress=isEndedByKeypress,
                                                                 textColor=params['vasTextColor'], name=name, pos=pos,
                                                                 scaleTextPos=scaleTextPos,
                                                                 labelYPos=pos[1] - params['vasLabelYDist'],
                                                                 markerSize=params['vasMarkerSize'],
                                                                 tickHeight=1, tickLabelWidth=0.9, io=io)

    # write data to CSV file
    csv_writer.writerow([globalClock.getTime(), 'VASRatingScale ' + name + ': (key response) rating=' + str(rating),
                         'rating RT=' + str(decisionTime)])
    # csv_writer.writerow([globalClock.getTime(), 'VASRatingScale ' + name + ': rating RT=' + str(decisionTime)])

    # Update next stim time
    if isEndedByKeypress:
        SetFlipTimeToNow()  # no duration specified, so timing creep isn't an issue
    else:
        AddToFlipTime(
            1)  # I changes that from: AddToFlipTime(questionDur * len(questions))  # add question duration * # of questions
    return choiceHistory


def RunMoodVas(questions, options, io, name='MoodVas'):
    # Wait until it's time
    WaitForFlipTime()

    SetPortData(params['codeBaseline'])
    # display pre-VAS prompt
    if not params['skipPrompts']:
        if expInfo['gender'] == 'female':
            BasicPromptTools.RunPrompts([params['PreVasMsg']], [reverse_string("לחצי על כל מקש כדי להמשיך")], win, message1,
                                    message2)
        else:
            BasicPromptTools.RunPrompts([params['PreVasMsg']], [reverse_string("לחץ על כל מקש כדי להמשיך")], win, message1,
                                    message2)

    # Display this VAS
    for i in range(len(questions)):
        question = [questions[i]]
        option = [options[i]]
        imgName = question[0].replace(' ', '_')
        imgName = imgName.replace('?', '')
        imgName = imgName.replace('\n', '')
        if name == 'PainRatingScale':
            RunVas(question, option, questionDur=params['painRateDuration'], isEndedByKeypress=False, name=name, io=io)
        else:
            RunVas(question, option, questionDur=float("inf"), isEndedByKeypress=True, name=name, io=io)
        
        # VAS_history = RunVas(question, option, questionDur=float("inf"), isEndedByKeypress=True, name=name)
        # csv_writer.writerow([globalClock.getTime(), 'VASRatingScale ' + name + ': choiceHistory=' + str(VAS_history)])

    BasicPromptTools.RunPrompts([], [reverse_string("מנוחה קצרה")], win, message1, message2)
    tNextFlip[0] = globalClock.getTime()

    # wait until it's time to show screen
    WaitForFlipTime()
    # show screen and update next flip time
    win.flip()
    AddToFlipTime(1)


def CoolDown():
    # Stop drawing ratingScale (if it exists)
    try:
        fixationCross.autoDraw = False
    except:
        print('fixation cross does not exist.')

    df = pd.DataFrame(listlist,
                      columns=['Absolute Time', 'Block', 'Trial', 'Color', 'Trial Time', 'Phase', 'Phase Time'])
    df.to_csv('avgFile%s.csv' % expInfo['subject'])

    message1.setText(reverse_string("הגענו לסוף הניסוי. תודה על ההשתתפות!"))
    if expInfo['gender'] == 'female':
        message2.setText(reverse_string("לחצי על אסקייפ כדי לסיים"))
    else:    
        message2.setText(reverse_string("לחץ על אסקייפ כדי לסיים"))
    win.logOnFlip(level=logging.EXP, msg='Display TheEnd')

    message1.setFont('Arial Hebrew')
    message2.setFont('Arial Hebrew')
    message1.draw()
    message2.draw()
    win.flip()

    thisKey = event.waitKeys(keyList=['q', 'escape'])

    # convert the log file into csv file
    createPrintLogFile()

    # exit
    core.quit()


# handle transition between blocks
def BetweenBlock(params):
    while (globalClock.getTime() < tNextFlip[0]):
        win.flip()  # to update ratingScale
    # stop autoDraw
    AddToFlipTime(1)
    tNextFlip[0] = globalClock.getTime() + 1.0

    # COMMENTED OUT NEED TO PRESS SPACE BEFORE PROCEEDING TO NEXT SLIDE
    message1.setText(reverse_string("הסתיים הבלוק הנוכחי"))
    message2.setText(reverse_string("לחץ על מקש הרווח כדי להתקדם"))
    win.logOnFlip(level=logging.EXP, msg='BetweenBlock')
    #
    message1.setFont('Arial Hebrew')
    message2.setFont('Arial Hebrew')
    message1.draw()
    message2.draw()
    win.flip()
    #
    thisKey = event.waitKeys(keyList=['space'])  # use space bar to avoid accidental advancing
    if thisKey:
       tNextFlip[0] = globalClock.getTime() + 2.0


def BehavFile(absTime, block, trial, color, trialTime, phase, phaseTime):
    list = [absTime, block, trial, color, trialTime, phase, phaseTime]
    listlist.append(list)


# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #

io = launchHubServer()
# log the start of the and set up
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')

# Creates an empty numpy array for the number of trials specified in the experiment parameters.
tStimVec = np.zeros(params['nTrials'])

# Creates an empty list for storing average ratings across trials
avgArray = []

# Starts a for loop that iterates over each block of the experiment.
for block in range(0, params['nBlocks']):
    if block == 0:  # If it's the first block, runs a mood VAS rating task and displays some prompts to the participant.
        again = True
        while again:
            again = False
            if params['skipInstructions'] == False:
                image = visual.ImageStim(win, image=f"{params['instructionsFolder']}{params['instructionsSuffix']}_1.jpeg", pos=(0, 0), units='pix', size=screenRes)
                image.draw()
                win.flip()
                HelperFunctions.wait_for_space(win, io)
                WaitForFlipTime()
                SetPortData(params['codeVAS'])
                RunMoodVas(questions_vas1, options_vas1, name='PreVAS', io=io)
                if params['painSupport']:
                    report_event('PreVAS', 'PreVas_rating')
                # RunPrompts() We don't use "Run Prompts", but give instructions as text
                # Present each slide and wait for spacebar input to advance to the next slide
                for i in range(2, INSTRUCTIONS_SLIDES + 1):
                    image.image = f"{params['instructionsFolder']}{params['instructionsSuffix']}_{i}.jpeg"
                    image.size = screenRes
                    image.draw()
                    win.flip()
                    if i == INSTRUCTIONS_SLIDES:
                        again = HelperFunctions.wait_for_space_with_replay(win, io)
                    else:
                        HelperFunctions.wait_for_space(win, io)

    if block == 2:  # If it's the second block, stops drawing the anxiety slider and fixation cross, runs a mood VAS rating task, displays some prompts, and sets the next stimulus presentation time to 4-6 seconds in the future.
        print("got to block 2 if statement")
        fixation.autoDraw = False

        # Run VAS after 2nd block
        RunMoodVas(questions_vas2, options_vas2, name='MidRun', io=io)
        report_event('MidRun', 'MidRun_rating')

        # Rest slide
        message1.setText(reverse_string("מנוחה קצרה"))
        message1.setFont('Arial Hebrew')
        message1.draw()
        win.flip()

        timer = core.Clock()
        timer.add(random.randint(1, 2))
        while timer.getTime() < 0:
            win.flip()

        tNextFlip[0] = globalClock.getTime() + random.randint(1, 2)

        # BasicPromptTools.RunPrompts(["Thank you for your responses."], ["Press the space bar to continue."], win,message1, message2)
        # thisKey = event.waitKeys(keyList=['space'])  # use space bar to avoid accidental advancing
        # if thisKey:
        #     tNextFlip[0] = globalClock.getTime() + random.randint(4, 6)

    # wait before first stimulus
    fixationCross.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    win.flip()  # Flip the window to display the fixation cross
    core.wait(1)  # Change to that: random.randint(4, 6)
    report_event('Fixation', 'Fixation_cross')

    # wait until it's time to show screen
    WaitForFlipTime()
    # show screen and update next flip time
    win.flip()
    AddToFlipTime(1)

    win.callOnFlip(SetPortData,
                   data=params['codeBaseline'])  # Calls a function to set the port data to the baseline code.

    # Waits for 2 seconds before displaying the first stimulus.
    while (globalClock.getTime() < tNextFlip[0] + 2):
        win.flip()  # to update ratingScale

    arrayLength = 1
    painITI = 0

    ############################################

    # Starts a loop to present each trial.
    for trial in range(params['nTrials']):
        color = color_list[trial]  # Selects the color for this trial.

        # write in csv block number, trial number and color
        # csv_writer.writerow("block number:"+block,"trial number:"+trial, "color:"+color)
        """
        # call function to write data to the file
        write_to_csv(['block:'+str(block), 'trial:'+str(trial), 'color:'+str(color)], VAS_file_name)
        """
        with open(VAS_file_name, 'a', newline='') as csv_file:
            write_to_csv(['block:' + str(block), 'trial:' + str(trial), 'color:' + str(color)], csv_file)

        # Calls the GrowingSquare function to present the stimulus, and records the start time and phase start time.
        trialStart, phaseStart = GrowingSquare(color, block, trial, params)
        win.flip()  # Flips the screen and waits for 2 seconds.
        core.wait(1)

        # Sets the next stimulus presentation time.
        tNextFlip[0] = globalClock.getTime() + (painISI[painITI])
        painITI += 1
        RunMoodVas(questions_RatingPain, options_RatingPain, name='PainRatingScale', io=io)
        report_event(color_to_T_dict[color], color_to_T_dict[color] + '_PainRatingScale')
        WaitForFlipTime()
        tNextFlip[0] = globalClock.getTime() + random.randint(8, 12)

    ### THE FIXATION "SAFE" AND "GET READY" WAS DELETED FROM HERE ###

    ############################################

    # Randomize order of colors for next block (if there is a next block, meaning we are not in the end)
    if block < (params['nBlocks'] - 1):
        BetweenBlock(params)  # betweenblock message
        random.shuffle(color_list)
        random.shuffle(painISI)
    logging.log(level=logging.EXP,
                msg='==== END BLOCK %d/%d ====' % (block + 1, params['nBlocks']))  # Logs the end of the block.

    # finish recording
    # if block == 2 or block == 5:
    if block == 2 or block == (params['nBlocks'] - 1):
        print("I got to the last if statement")

WaitForFlipTime()  # This waits for the next screen refresh.

RunMoodVas(questions_vas3, options_vas3, name='PostRun', io=io)  # This displays a mood VAS after the experiment is completed.
report_event('PostRun', 'PostRun_rating')

WaitForFlipTime()  # This waits for the next screen refresh.

# Log end of experiment
logging.log(level=logging.EXP, msg='--- END EXPERIMENT ---')

# clean-up & exit experiment

CoolDown()
