import re 
import cv2
import string
from PIL import Image
import pytesseract
import numpy as np
from nw_perks import *

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_item_description(image_path):
    # Open image file with OpenCV
    img = cv2.imread(image_path)
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Perform OCR to get the bounding boxes of all text in the image
    d = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

    # Initialize y-coordinate of the top of the "Requirement: Level 60" text
    y_top_requirement = None
    x_left_requirement = None
    x_right_requirement = None

    # Iterate over all detected text
    for i in range(len(d["text"])):
        if i >= len(d["text"]) - 2:  # If we're near the end of the array, break to avoid index out of range error
            break
        # Concatenate current token and the next two tokens
        combined_text = " ".join([d["text"][i], d["text"][i+1], d["text"][i+2]])
        # If "Requirement: Level 60" is found
        if "Requirement: Level 60" in combined_text:
            # Get the top y-coordinate of the bounding box of the text
            y_top_requirement = d["top"][i]
            # Get the left and right x-coordinate of the bounding box of the text
            x_left_requirement = d["left"][i] - 10
            x_right_requirement = d["left"][i] + 3*d["width"][i] + 30
            break

    if y_top_requirement is not None and x_left_requirement is not None and x_right_requirement is not None:
        # Crop the image to this area
        cropped_image = Image.fromarray(img[:y_top_requirement, x_left_requirement:x_right_requirement])
        # Use Tesseract to extract the text from the cropped image
        text = pytesseract.image_to_string(cropped_image)
        return text
    else:
        print("Could not find 'Requirement: Level 60' in the image.")
        return None

def extract_perk_names(text):
    perk_names = []

    # Split the text into lines
    lines = text.split('\n')

    # Iterate over each line
    for line in lines:
        # Find the colon in the line
        colon_index = line.find(':')
        # If a colon is found
        if colon_index != -1:
            # Get the text before the colon
            perk_name = line[:colon_index]
            # Strip any non-alphabetic characters from the beginning of the perk name
            perk_name = re.sub("^[^a-zA-Z]*", "", perk_name)
            perk_names.append(perk_name)

    return perk_names

def extract_item_stats(text):
    # The regex pattern for item stats: a '+' sign, followed by one or two digits, a space, and then the stat name
    pattern = r'\+(\d{1,2})\s([a-zA-Z]+)'

    # Find all matches in the text
    matches = re.findall(pattern, text)

    # Convert each match to a dictionary with the stat name as the key and the number as the value
    item_stats = {match[1]: int(match[0]) for match in matches}

    return item_stats

def scrape_info(start, end):
    result = {}
    # Iterate over each image
    for i in range(start, end+1):
        # Add leading zero if number is less than 10 for proper file formatting
        num_str = str(i).zfill(2)
        
        # Generate the image file path
        image_file_name = f"item{num_str}.png"
        image_path = f"build/{image_file_name}"

        # Extract the item description
        text = extract_item_description(image_path)
        if text is None:
            print(f"Could not extract information from {image_path}")
            continue

        # Extract the perk names
        perks = extract_perk_names(text)
        print(f"Perks in {image_path}: {perks}")

        for perk in perks:
            cleaned_perk = perk.translate(str.maketrans('', '', string.punctuation)).strip().lower()
            matches = [gen_perk for gen_perk in generated_perks if gen_perk.lower() in cleaned_perk]
            
            if matches:
                # Sort the matches by length, descending, and take the first one
                longest_match = sorted(matches, key=len, reverse=True)[0]
                matched_perks.append(longest_match)
        
        print(f"Perks: {matched_perks}")
        
        # Extract the stats
        stats = extract_item_stats(text)
        print(f"Stats in {image_path}: {stats}")

        # Store the information in a dictionary with the image file name as the key
        result[image_file_name] = {"perks": perks, "stats": stats}

    return result
