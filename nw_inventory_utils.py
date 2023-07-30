import os
import sys
import glob
import cv2
import numpy as np
import pyautogui
from screeninfo import get_monitors
import time
from scipy.spatial.distance import pdist, squareform
import pygetwindow as gw


def wait_for_active_window(title):
    while True:
        active_window = pyautogui.getActiveWindow()
        if active_window.title == title:
            break
        time.sleep(0.5)  # Adjust the delay time as needed

    print(f"The active window title is '{title}'.")

def get_all_templates_in_directory(directory):
    return [cv2.imread(os.path.join(directory, filename), 0) 
            for filename in os.listdir(directory) 
            if filename.endswith(".png")]

def get_active_window_monitor(title):
    try:
        active_window = gw.getWindowsWithTitle(title)[0]
    except IndexError:
        print(f"No window with title '{title}' found.")
        return None

    win_x = active_window.left
    win_y = active_window.top

    monitors = get_monitors()
    for i, monitor in enumerate(monitors):
        if win_x >= monitor.x and win_y >= monitor.y and win_x <= monitor.x + monitor.width and win_y <= monitor.y + monitor.height:
            return i  # Return monitor number
    return None

def get_screenshot_of_monitor(monitor_number=0):
    monitor = get_monitors()[monitor_number]
    screenshot = pyautogui.screenshot(region=(
        monitor.x,
        monitor.y,
        monitor.width,
        monitor.height
    ))
    return np.array(screenshot)

def match_template(screenshot, templates):
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    max_vals = [cv2.minMaxLoc(cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED))[1] 
                for template in templates]
    return max(max_vals)

def get_screenshot():
    monitor_number = get_active_window_monitor("New World")
    if monitor_number is None:
        print("New World is not running on any screen. Exiting the program.")
        os._exit(1)
    else:
        screenshot = get_screenshot_of_monitor(monitor_number)
    return screenshot

def get_inventory_screenshot():
    screenshot = get_screenshot()

    if determine_best_template(screenshot) == 'non-tab-gamescreen':
        monitor_number = determine_main_monitor()
        monitor = get_monitors()[monitor_number]
        pyautogui.press('tab')
        time.sleep(1)

        screenshot = get_screenshot()

    return screenshot

def update_templates():
    templates = {}
    for folder in os.listdir('src/templates'):
        folder_path = os.path.join('src/templates', folder)
        if os.path.isdir(folder_path):
            templates[folder] = get_all_templates_in_directory(folder_path)
    return templates

def determine_main_monitor():
    highest_similarity = 0
    main_monitor = 0
    for monitor_number in range(len(get_monitors())):
        screenshot = get_screenshot_of_monitor(monitor_number)
        average_similarity = (match_template(screenshot, templates['gearsets']) + 
                              match_template(screenshot, templates['inventory']) + 
                              match_template(screenshot, templates['non-tab-gamescreen'])) / 3
        if average_similarity > highest_similarity:
            highest_similarity = average_similarity
            main_monitor = monitor_number

    if highest_similarity == 0:
        print("New World is not running on any screen. Exiting the program.")
        sys.exit()
        # exit()

    return main_monitor

def determine_best_template(screenshot):
    similarities = {name: match_template(screenshot, template) for name, template in templates.items()}
    best_match = max(similarities, key=similarities.get)
    print("Best template match: " + best_match)
    return best_match

def create_new_template():
    screenshot = get_screenshot()
    category = determine_best_template(screenshot)

    directory = 'src/templates/' + category

    existing_filenames = os.listdir(directory)
    existing_numbers = [int(filename[:-4]) for filename in existing_filenames if filename.endswith(".png")]
    if existing_numbers:
        next_number = max(existing_numbers) + 1
    else:
        next_number = 1
    new_filename = "{:03}.png".format(next_number)

    cv2.imwrite(os.path.join(directory, new_filename), screenshot)
    global templates
    templates = update_templates()

templates = update_templates()

def eliminate_close_coordinates(coordinates, min_distance):
    coordinates = coordinates.copy()  # Don't modify the input directly
    pairwise_distances = squareform(pdist(coordinates))  # Compute pairwise distances
    indices_to_remove = set()
    for i in range(len(coordinates)):
        if i not in indices_to_remove:
            too_close_indices = np.where(pairwise_distances[i] < min_distance)[0]  # Find nearby points
            indices_to_remove.update(too_close_indices)  # Schedule them for removal
            indices_to_remove.remove(i)  # Keep the current point
    coordinates = [pt for i, pt in enumerate(coordinates) if i not in indices_to_remove]  # Remove the nearby points
    return coordinates

def get_item_positions():
    screenshot = get_inventory_screenshot()
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    # Get all pattern filenames
    pattern_dir = r"src\expertise_pattern"
    pattern_files = glob.glob(os.path.join(pattern_dir, "*.png"))

    # Initialize list of item positions
    item_positions = []

    for pattern_file in pattern_files:
        expertise_pattern = cv2.imread(pattern_file, 0)

        # Perform template matching
        res = cv2.matchTemplate(screenshot_gray, expertise_pattern, cv2.TM_CCOEFF_NORMED)

        # Set a threshold to decide which matches to keep; this may need tuning
        threshold = 0.6

        # Find the locations where the match score exceeds the threshold
        locs = np.where(res >= threshold)

        # Check if there are at least 10 matches
        if len(locs[0]) < 10:
            print(f"Expertise lower than 625 for pattern {pattern_file}...")
            continue

        # For each location where the match was found
        for pt in zip(*locs[::-1]):
            # This is the top-left corner of a match; add the width and height of the template
            # to find the bottom-right corner of the match
            br_corner = (pt[0] + expertise_pattern.shape[1], pt[1] + expertise_pattern.shape[0])

            # Draw a rectangle around the matched area
            cv2.rectangle(screenshot_gray, pt, br_corner, (0,0,255), 2)

            # Define the center of the match area (both horizontally and vertically)
            center_pos = (pt[0] + expertise_pattern.shape[1]//2, pt[1] + expertise_pattern.shape[0]//2)

            # Define the item position: center of match and X pixels to the right (X being the width of the template)
            item_pos = (center_pos[0] + expertise_pattern.shape[1], center_pos[1])
            item_positions.append(item_pos)

    # Eliminate coordinates that are too close
    min_distance = expertise_pattern.shape[0] / 3
    item_positions = eliminate_close_coordinates(item_positions, min_distance)
    return item_positions

def get_items():
    # Get the item positions
    positions = get_item_positions()

    # If no positions were found, return
    if not positions:
        print("No items found.")
        return

    # For each position
    for i, pos in enumerate(positions, start=1):
        # Hover the mouse over the position
        pyautogui.moveTo(pos)
        time.sleep(0.5)
        # Capture a screenshot
        screenshot = pyautogui.screenshot()
        # Save the screenshot as 'itemXX.png' where XX is the position index
        screenshot.save(f'build/item{i:02}.png')
        # Using tabs to bypass the in-game UI bug
        pyautogui.press('tab')
        time.sleep(1)
        pyautogui.press('tab')
    pyautogui.press('tab')



