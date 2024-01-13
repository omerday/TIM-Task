from psychopy import core, event, logging, visual
import time
from psychopy.iohub.client.keyboard import Keyboard
from psychopy.visual import ratingscale

MOOD_RATING_QUESTION_HEBREW = "עד כמה כאב החום?"
MOOD_RATING_QUESTION_ENGLISH = "How painful was the heat?"

MOOD_RATING_ANSWERS_HEBREW = ["בכלל לא", "מאוד"]
MOOD_RATING_ANSWERS_ENGLISH = ["Not at all", "A lot"]

LABELS = ["Anxiety", "Tiredness", "Worry", "Mood", "PainSensitivity"]

QUESTIONS_HEBREW = ["עד כמה אתם מרגישים חרדה או לחץ כרגע?",
                    "עד כמה אתם עייפים?",
                    "עד כמה אתם מודאגים מהחלק הבא?",
                    "איך מצב הרוח שלכם כרגע?",
                    "עד כמה אתם רגישים לכאב?"]
QUESTIONS_ENGLISH = ["How stressed or anxious are you feeling?",
                     "How tired are you?",
                     "How worried are you from the next part?",
                     "How's your mood right now?",
                     "How sensitive are you to pain?"]

ANSWERS_HEBREW = [["כלל לא", "הרבה מאוד"], ["כלל לא", "הרבה מאוד"], ["כלל לא", "הרבה מאוד"], ["רע מאוד", "טוב מאוד"], ["כלל לא", "הרבה מאוד"]]
ANSWERS_ENGLISH = [["Not at all", "A lot"], ["Not at all", "A lot"], ["Not at all", "A lot"], ["Very good", "Very bad"], ["Not at all", "A lot"]]

def run_vas(window: visual.Window, io, params: dict, type:str, duration=float('inf')):
    if type == "PainRating":
        questions = MOOD_RATING_QUESTION_HEBREW if params['language'] == 'Hebrew' else MOOD_RATING_QUESTION_ENGLISH
        answers = MOOD_RATING_ANSWERS_HEBREW if params['language'] == 'Hebrew' else MOOD_RATING_ANSWERS_ENGLISH
    else:
        questions = QUESTIONS_HEBREW if params['language'] == 'Hebrew' else QUESTIONS_ENGLISH
        answers = ANSWERS_HEBREW if params['language'] == 'Hebrew' else ANSWERS_ENGLISH

    keyboard = io.devices.keyboard

    scores = {}

    for i in range(len(questions)):
        scale = ratingscale.RatingScale(window,
                                        labels=[answers[i][0][::-1], answers[i][1][::-1]]
                                            if params['language'] == 'Hebrew' else [answers[i][0],answers[i][1]],
                                        scale=None, choices=None, low=1, high=100, precision=1, tickHeight=0, size=2,
                                        markerStart=50, noMouse=True, leftKeys=1, rightKeys=2,  # Dummy left and right
                                        textSize=0.6, acceptText="לחצו על הרווח"[::-1] if params['language'] == "Hebrew" else "Press Spacebar", showValue=False, showAccept=True,
                                        acceptPreText="לחצו על הרווח"[::-1] if params['language'] == "Hebrew" else "Press Spacebar", acceptSize=1.5,
                                        markerColor="Maroon", acceptKeys=["space"], textColor="Black",
                                        lineColor="Black", disappear=False)
        question_label = visual.TextStim(window, text=questions[i][::-1] if params['language'] == 'Hebrew' else questions[i], height=.12, units='norm', pos=[0, 0.3], wrapWidth=2,
                                   font="Open Sans", color="Black")

        core.wait(0.05)
        keyboard.getKeys()

        end_time = time.time() + duration
        accept = False
        while (duration != float(inf) and time.time() < end_time) or (duration == float(inf) and scale.noResponse and not accept):
            scale.draw()
            question_label.draw()
            window.flip()
            for event in keyboard.getKeys(etype=Keyboard.KEY_PRESS):
                if event.key in ["left", "right"]:
                    key_hold = True
                    step = 1 if event.key == "right" else -1
                    while key_hold:
                        scale.markerPlacedAt = max(scale.markerPlacedAt + step, scale.low)
                        scale.markerPlacedAt = min(scale.markerPlacedAt + step, scale.high)
                        scale.draw()
                        question_label.draw()
                        window.flip()
                        for releaseEvent in keyboard.getKeys(etype=Keyboard.KEY_RELEASE):
                            key_hold = False
                            if releaseEvent.key in [' ', 'space']:
                                accept = True
                            elif releaseEvent.key == 'escape':
                                window.close()
                                core.quit()
                        core.wait(0.03)
                elif event.key in [" ", "space"]:
                    accept = True
                    break
                elif event.key == "escape":
                    window.close()
                    core.quit()
        score = scale.getRating()
        if type == "PainRating":
            return score
        else:
            scores[LABELS[i]] = score
    return scores


def ShowVAS(questions_list, options_list, win, io, name='Question', questionDur=float('inf'), isEndedByKeypress=True, 
            upKey='up', downKey='down', selectKey='enter',textColor='black',pos=(0.,0.),stepSize=1.,hideMouse=True,
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
        end_time = time.time() + questionDur
        accept = False

        print(f"Current time - {time.time()}, VAS should last until {time.time() + questionDur}")

        keyboard.getKeys(etype=Keyboard.KEY_PRESS)
        while time.time() < end_time and not accept:
            for event in keyboard.getKeys(etype=Keyboard.KEY_PRESS):
                if event.key == "escape":
                    win.close()
                    core.quit()
                elif event.key in [selectKey, ' ']:
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
        score = ratingScale.getRating()
        rating[iQ] = score
        decisionTime[iQ] = ratingScale.getRT()
        choiceHistory[iQ] = ratingScale.getHistory()

        # if no response, log manually
        if ratingScale.noResponse:
            logging.log(level=logging.DATA,msg='RatingScale %s: (no response) rating=%g'%(ratingScale.name,rating[iQ]))
            logging.log(level=logging.DATA,msg='RatingScale %s: rating RT=%g'%(ratingScale.name,decisionTime[iQ]))
            logging.log(level=logging.DATA,msg='RatingScale %s: history=%s'%(ratingScale.name,choiceHistory[iQ]))

    win.color = (217, 217, 217)
    return rating, decisionTime, choiceHistory, score
