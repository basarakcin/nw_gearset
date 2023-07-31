from nw_inventory_utils import *
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
os.mkdir("build")
create_directory(directory_name)

wait_for_active_window("New World")
get_items()
info = scrape_info()
for image_file_name, item_info in info.items():
    print(f"{image_file_name}:")
    print(f"  Perks: {item_info['perks']}")
    print(f"  Stats: {item_info['stats']}")
