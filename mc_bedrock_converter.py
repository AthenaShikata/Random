import pyautogui
import keyboard, time
import cv2
from pynput import mouse
import threading
 
# ── Safety settings ────────────────────────────────────────────────────────────
pyautogui.PAUSE = 0.5          # Half-second pause between every PyAutoGUI call
pyautogui.FAILSAFE = True      # Move mouse to top-left corner to abort the script




def convert_world():
    # OPEN WORLD
    pyautogui.click(789, 329)
    pyautogui.click(1312, 357)
    pyautogui.click(2021, 885)
    pyautogui.click(1070, 881)
    pyautogui.click(1827, 961)
    pyautogui.click(1827, 961)


    # SELECT CONVERT
    pyautogui.click(894, 298)
    pyautogui.click(920, 327)
    pyautogui.click(1101, 391)

    # SELECT WORLD
    pyautogui.click(1083, 507)
    pyautogui.moveTo(1564, 496, duration=0.1)
    pyautogui.dragTo(1564, 912, duration=0.2, button='left')

    world_selected = False
    while not world_selected:
        if keyboard.is_pressed('.'):  # if key 'q' is pressed 
            world_selected = True

    #wait for world select

    pyautogui.click(1052, 649)
    pyautogui.click(1052, 683)
    pyautogui.click(1411, 599)
    pyautogui.click(1373, 991)
    
    pyautogui.moveTo(1293, 752, duration=0.1)

while True:
    if keyboard.is_pressed(','):  # if key 'q' is pressed 
        convert_world()
            