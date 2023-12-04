from psychopy import core, event, visual
from psychopy.iohub import launchHubServer
from psychopy.iohub.client.keyboard import Keyboard

def reverse_string(s):
    return s[::-1]

def wait_for_space(window, io):
    """
    Helper method to wait for a Spacebar keypress and keep the window open until then
    :param window:
    :return:
    """
    keyboard = io.devices.keyboard
    while True:
        for event in keyboard.getKeys(etype=Keyboard.KEY_PRESS):
            if event.key == " ":
                return
            if event.key == "escape":
                window.close()
                core.quit()


def wait_for_space_with_replay(window, io):
    """
    Helper method to wait for a Spacebar keypress and keep the window open, or get 'r' keypress for replay of the
     InstructionsEnglish. Returns True if needed to replay.
    :param window:
    :return: True/False if r was pressed
    """
    keyboard = io.devices.keyboard
    while True:
        keys = keyboard.getPresses()
        for event in keys:
            if event.key == 'r' or event.key == 'R':
                return True
            elif event.key == ' ':
                return False
            elif event.key == "escape":
                window.close()
                core.quit()
