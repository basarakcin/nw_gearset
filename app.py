# from nw_inventory_utils import *
from nw_inventory_scraping import *

def convert2grayscale(directory = 'src/expertise_pattern'):
    # Get a list of all image files in the directory
    image_files = [filename for filename in os.listdir(directory) if filename.endswith(".png")]

    for filename in image_files:
        # Read the original image in color mode
        image_path = os.path.join(directory, filename)
        original_image = cv2.imread(image_path)

        # Convert the image to grayscale
        grayscale_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

        # Save the grayscale image back to the same filename
        cv2.imwrite(image_path, grayscale_image)

# convert2grayscale()
# os.mkdir("build")

# wait_for_active_window("New World")
# get_items()
# info = scrape_info()
dummy_info = {
    "item01.png": {
        "perks": ["Blessed", "Refreshing Move", "Refreshing Divine Embrace"],
        "stats": {"Focus": 31}
    },
    "item02.png": {
        "perks": ["Keen", "Keen Speed", "Sundering Riposte"],
        "stats": {"Focus": 31}
    },
    "item03.png": {
        "perks": ["Resilient", "Freedom", "Fortifying Sacred Ground"],
        "stats": {"Constitution": 26}
    }
}
info=dummy_info
for image_file_name, item_info in info.items():
    print(f"{image_file_name}:")
    print(f"  Perks: {item_info['perks']}")
    print(f"  Stats: {item_info['stats']}")

username = 'Moar 3ewbs'
write_to_sheet(username, dummy_info)
