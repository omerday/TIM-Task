#!/usr/bin/env python2
"""Wrapper for RatingScale objects.."""

from psychopy import core, event, logging#, visual # visual and gui conflict, so don't import it here
import time
from psychopy.iohub.client.keyboard import Keyboard
from psychopy.visual import ratingscale

def ShowVAS(questions_list, options_list, win, io, name='Question', questionDur=float('inf'), isEndedByKeypress=True,
            upKey='right', downKey='left', selectKey='enter',textColor='black',pos=(0.,0.),stepSize=1,hideMouse=True,
            repeatDelay=0.5, scaleTextPos=[0.,0.45], labelYPos=-0.27648, markerSize=0.1, tickHeight=0.0, tickLabelWidth=0.0):
    # import packages
    from psychopy import visual # for ratingScale
    import numpy as np # for tick locations
    from pyglet.window import key # for press-and-hold functionality

    keyboard = io.devices.keyboard

    # set up
    nQuestions = len(questions_list)
    rating = [None]*nQuestions
    decisionTime = [None]*nQuestions
    choiceHistory = [[0]]*nQuestions

    win.color = (217, 217, 217) #'white' # Setting background color to white
    # Rating Scale Loop
    for iQ in range(nQuestions):
        # Make triangle
        markerStim = visual.ShapeStim(win,lineColor=textColor,fillColor=textColor,vertices=((-markerSize/2.,markerSize*np.sqrt(5./4.)),(markerSize/2.,markerSize*np.sqrt(5./4.)),(0,0)),units='norm',closeShape=True,name='triangle');
        
        tickMarks = np.linspace(0,100,len(options_list[iQ])).tolist()
        if tickLabelWidth==0.0: # if default value, determine automatically to fit all tick mark labels
            tickWrapWidth = (tickMarks[1]-tickMarks[0])*0.9/100 # *.9 for extra space, /100 for norm units
        else: # use user-specified value
            tickWrapWidth = tickLabelWidth
        
        ratingScale = ratingscale.RatingScale(win, scale=questions_list[iQ],
            low=0., high=100., markerStart=50., precision=.5, labels=options_list[iQ], tickMarks=tickMarks, tickHeight=tickHeight,
            marker=markerStim, markerColor=textColor, markerExpansion=1, singleClick=False, disappear=False,
            textSize=0.8, textColor=textColor, textFont='Arial Hebrew', showValue=False,
            showAccept=False, acceptKeys=selectKey, acceptPreText='key, click', acceptText='accept?', acceptSize=1.0,
            leftKeys='3', rightKeys='2',  # Dummy keys to avoid double step
            respKeys=(), lineColor=textColor, skipKeys=['q','escape'],
            mouseOnly=False, noMouse=hideMouse, size=2.0, stretch=1.0, pos=pos, minTime=0.4, maxTime=questionDur,
            flipVert=False, depth=0, name='%s%d'%(name,iQ), autoLog=True)
        # Fix text wrapWidth
        for iLabel in range(len(ratingScale.labels)):
            ratingScale.labels[iLabel].wrapWidth = tickWrapWidth
            ratingScale.labels[iLabel].pos  = (ratingScale.labels[iLabel].pos[0],labelYPos)
            ratingScale.labels[iLabel].alignHoriz = 'center'
        # Move main text
        ratingScale.scaleDescription.pos = scaleTextPos

        # Display until time runs out (or key is pressed, if specified)
        win.logOnFlip(level=logging.EXP, msg='Display %s%d'%(name,iQ))
        tStart = time.time()
        accept = False

        while (time.time()-tStart)<questionDur and not accept:
            for event in keyboard.getKeys(etype=Keyboard.KEY_PRESS):
                if event.key == "escape":
                    win.close()
                    core.quit()
                elif event.key == [selectKey, 'space']:
                    accept = True
                    break
                elif event.key in [upKey, downKey]:
                    key_hold = True
                    tPress = time.time()
                    keyPressed = event.key
                    step = stepSize if keyPressed == upKey else -stepSize
                    while key_hold:
                        valPress = ratingScale.markerPlacedAt
                        ratingScale.markerPlacedAt = max(valPress + step, ratingScale.low)
                        ratingScale.markerPlacedAt = min(valPress + step, ratingScale.high)
                        ratingScale.draw()
                        win.flip()
                        for releaseEvent in keyboard.getKeys(etype=Keyboard.KEY_RELEASE):
                            if releaseEvent.key == keyPressed:
                                key_hold = False
                        core.wait(0.05)

            ratingScale.draw()
            win.flip()

        # Log outputs
        rating[iQ] = ratingScale.getRating()
        decisionTime[iQ] = ratingScale.getRT()
        choiceHistory[iQ] = ratingScale.getHistory()

        # if no response, log manually
        if ratingScale.noResponse:
            logging.log(level=logging.DATA,msg='RatingScale %s: (no response) rating=%g'%(ratingScale.name,rating[iQ]))
            logging.log(level=logging.DATA,msg='RatingScale %s: rating RT=%g'%(ratingScale.name,decisionTime[iQ]))
            logging.log(level=logging.DATA,msg='RatingScale %s: history=%s'%(ratingScale.name,choiceHistory[iQ]))

    win.color = (217, 217, 217)
    return rating,decisionTime,choiceHistory
