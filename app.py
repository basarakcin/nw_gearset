from nw_inventory_utils import *
from nw_inventory_scraping import *
from nw_perks import *

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

def create_directory(directory_name):
    try:
        os.mkdir(directory_name)
        print(f"Directory '{directory_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory_name}' already exists.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Replace "build" with the desired directory name if you want a different one.
directory_name = "build"
create_directory(directory_name)

wait_for_active_window("New World")

get_items()
info = scrape_info(1, 10)
for image_file_name, item_info in info.items():
    print(f"{image_file_name}:")
    print(f"  Perks: {item_info['perks']}")
    print(f"  Stats: {item_info['stats']}")
