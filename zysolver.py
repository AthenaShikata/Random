import pyautogui
import cv2
import time
import keyboard 
import math
import pyperclip
import threading

def interupt_worker():
    print('thread initiated')
    t = threading.current_thread()
    while not stop_event.is_set():
        if keyboard.is_pressed('esc'): 
            stop_event.set()
            print('KeyboardInterrupt')

def euclidean_distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def click_unique_dots(stop_event):
    # Find all matching locations
    confidence=0.85
    proximity_threshold=45
    matches = list(pyautogui.locateAllOnScreen('ZY-Circle.png', confidence=confidence))
    print(f"Found {len(matches)} potential matches.")

    clicked_positions = []

    for match in matches:
        if not stop_event.is_set():
            center_x, center_y = pyautogui.center(match)
            
            # Check if this dot is close to a previously clicked dot
            too_close = any(
                euclidean_distance((center_x, center_y), prev) < proximity_threshold
                for prev in clicked_positions
            )

            if not too_close:
                pyautogui.moveTo(center_x, center_y)
                pyautogui.click()
                clicked_positions.append((center_x, center_y))
                print(f"Clicked at ({center_x}, {center_y})")
            else:
                print(f"Skipped duplicate at ({center_x}, {center_y})")

def find_unique_buttons(image_path, confidence=0.9, proximity=50):
    raw_matches = list(pyautogui.locateAllOnScreen(image_path, confidence=confidence))
    unique_centers = []

    for match in raw_matches:
        center = pyautogui.center(match)
        if all(euclidean_distance(center, c) > proximity for c in unique_centers):
            unique_centers.append(center)

    print(f"Found {len(unique_centers)} unique matches for {image_path}")
    return unique_centers

def find_nearest_element(button_center, image, confidence):
    answer_boxes = list(pyautogui.locateAllOnScreen(image, confidence=confidence))
    bx, by = button_center

    nearest = None
    min_distance = float('inf')

    for box in answer_boxes:
        ax, ay = pyautogui.center(box)
        if ay < by:  # Must be *above* the button
            dist = abs(by - ay)
            if dist < min_distance:
                nearest = (ax, ay)
                min_distance = dist

    if nearest:
        print(f"Nearest element found at {nearest} (distance {min_distance})")
    else:
        print("No element found above button.")
    return nearest

def find_nearest_show(button_center, image="ZY-Show Answer.png", confidence=0.9):
    shows = list(pyautogui.locateAllOnScreen(image, confidence=confidence))
    bx, by = button_center

    nearest = None
    min_distance = float('inf')

    for show in shows:
        ax, ay = pyautogui.center(show)
        if ay >= by:  # Must be *at or below* the button
            dist = abs(ay - by)
            print(dist)
            if dist < min_distance:
                nearest = (ax, ay)
                min_distance = dist

    if nearest:
        print(f"Nearest show found at {nearest} (distance {min_distance})")
    else:
        print("No show found above button.")
    return nearest

def handle_problem_area(center):
    center = find_nearest_show(center)
    center_x, center_y = center 



    # 1. Click "Show answer"
    pyautogui.moveTo(center_x, center_y)
    
    pyautogui.click(clicks=2)
    
    
    # 2. Move to Answer box (assumed just to the right or slightly below)
    answer_box_pos = find_nearest_element((center_x, center_y),"ZY-Answers.png",0.9)
    answer_box_pos = (answer_box_pos[0] + 0, answer_box_pos[1] + 50)
    pyautogui.moveTo(answer_box_pos)
    pyautogui.click(clicks=3) 
    pyautogui.hotkey('ctrl', 'c')
    
    # 3. Move to input box (assumed above the button)
    input_box_pos = find_nearest_element((center_x, center_y),"ZY-Box.png",0.7)
    #input_box_pos = (center_x - 175, center_y - 60)  # Tune this too
    pyautogui.moveTo(input_box_pos)
    pyautogui.click(clicks=3)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.hotkey('enter')
    check_button_pos = (center_x, center_y+50)
    pyautogui.moveTo(input_box_pos)
    pyautogui.click(3)

    time.sleep(.1)
    #'''
     
def solve_all_problems(stop_event):
    #time.sleep(2)  # Time to switch to browser
    centers  = find_unique_buttons("ZY-Show Answer.png")
    print(f"Found {len(centers)} problems.")
    for center in centers:
        if not stop_event.is_set():
            handle_problem_area(center)

class run_thread(threading.Thread):

    def __init__(self,  *args, **kwargs):
        super(run_thread, self).__init__()
        self._stop_event = threading.Event()
        global stop_event
        stop_event = self._stop_event
        self.run()

    def run(self):
        while not self._stop_event.is_set():
            try:  # used try so that if user pressed other than the given key error will not be shown
                if keyboard.is_pressed(','):  # if key 'q' is pressed 
                    solve_all_problems(self._stop_event)
                elif keyboard.is_pressed('.'):
                    click_unique_dots(self._stop_event)
            except: raise

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()    


def main():
    #time.sleep(5)
    runnerThread = threading.Thread(target=run_thread)
    runnerThread.start()
    interuptThread = threading.Thread(target=interupt_worker)
    interuptThread.start()

    interuptThread.join()
    runnerThread.join()

stop_event = None
main()