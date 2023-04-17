""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""

import os
import imagelib as image_lib
import inspect
import argparse
import datetime
import sys
import sqlite3
import hashlib
import re
import requests
import urllib
# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None   # Full path of image cache database
api_key = '1bVsvhf8QrkRj4nXgJkDErQvlJYXnANS0US5V8Pw'

def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()    

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    if apod_id != 0:
        image_lib.set_desktop_background_image(apod_info['file_path'])

def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.

    Returns:
        date: APOD date
    """
    # TODO: Complete function body
    # apod_date = date.fromisoformat('2022-12-25')
    # Define command-line arguments
    parser = argparse.ArgumentParser(description='APOD Desktop')
    parser.add_argument('date', nargs='?', default=datetime.date.today().strftime('%Y-%m-%d'),
                    help='APOD date (format: YYYY-MM-DD)')
    args = parser.parse_args()

    # Validate the specified date
    try:
        apod_date = datetime.datetime.strptime(args.date, '%Y-%m-%d').date()
        assert apod_date >= datetime.date(1995, 6, 16)
        assert apod_date <= datetime.date.today()
    except (ValueError, AssertionError):
        print('Error: Invalid APOD date specified.')
        print("Script execution aborted")
        sys.exit(1)


    return apod_date

def get_script_dir():
    """Determines the path of the directory in which this script resides

    Returns:
        str: Full path of the directory in which this script resides
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    return os.path.dirname(script_path)

def init_apod_cache(parent_dir):
    """Initializes the image cache by:
    - Determining the paths of the image cache directory and database,
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    
    The image cache directory is a subdirectory of the specified parent directory.
    The image cache database is a sqlite database located in the image cache directory.

    Args:
        parent_dir (str): Full path of parent directory    
    """
    global image_cache_dir
    global image_cache_db

    # TODO: Determine the path of the image cache directory
    image_cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')

    print("image cache directory : ",image_cache_dir)    
    # TODO: Create the image cache directory if it does not already exist
    if not os.path.exists(image_cache_dir):
        os.makedirs(image_cache_dir)
        print("Image Cache Directory Created")
    else:
        print("Image Cache Directory already exists.")

    



    # TODO: Determine the path of image cache DB
    image_cache_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
    image_cache_db = os.path.join(image_cache_db, 'apod.db')
    print("image cache database : ",image_cache_db)

    # TODO: Create the DB if it does not already exist
    if not os.path.exists(image_cache_db):
        # os.makedirs(image_cache_db)
        print("Image Cache DB Created")
    else:
        print("image Cache DB already exists.")    
    
    # Connect to the SQLite database and create the table if it doesn't already exist
    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS apod_images
             (id INTEGER PRIMARY KEY, title TEXT, explanation TEXT, file_path TEXT, hash TEXT)''')



# Check if an image with the same SHA-256 hash value already exists in the cache
def hash_file(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
        return hashlib.sha256(data).hexdigest()

   

def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.
     
    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the 
    image cache and the APOD information is added to the image cache DB.

    Args:
        apod_date (date): Date of the APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    """
    print("APOD date:", apod_date.isoformat())
    # TODO: Download the APOD information from the NASA API
    # TODO: Download the APOD image
    # TODO: Check whether the APOD already exists in the image cache
    # TODO: Save the APOD file to the image cache directory
    # TODO: Add the APOD information to the DB
    apod_url = f'https://api.nasa.gov/planetary/apod?api_key={api_key}&date={apod_date.isoformat()}'
    response = requests.get(apod_url)
    apod_data = response.json()
    # print("##########apod_data##########",apod_data)
    if apod_data['media_type'] == 'image':
        # Download the high-definition image file if it doesn't already exist in the cache
        image_url = apod_data['hdurl']
        print("Getting "+ apod_date.isoformat() +" APOD information from NASA...success")
        print("APOD title:",apod_data['title'])
        print("APOD URL:",image_url)
        print("Downloading image from ",image_url,"..success")
        
        image_ext = os.path.splitext(urllib.parse.urlparse(image_url).path)[1]
        image_title = re.sub(r'[^a-zA-Z0-9\s_]+', '', apod_data['title']).strip().replace(' ', '_')
        image_file_name = f'{image_title}{image_ext}'
        image_file_path = os.path.join(image_cache_dir, image_file_name)
        image_hash = hash_file(image_file_path) if os.path.exists(image_file_path) else None
        if not image_hash:
            response = requests.get(image_url)
            with open(image_file_path, 'wb') as f:
                f.write(response.content)
            image_hash = hash_file(image_file_path)
        # Check if the image already exists in the database
        conn = sqlite3.connect(image_cache_db)
        c = conn.cursor()
        print("APOD SHA-256:",image_hash)
        c.execute('SELECT id FROM apod_images WHERE hash=?', (image_hash,))
        existing_image_id = c.fetchone()
        conn.commit()
        # print("existing_image_id::::::::::",existing_image_id)
        if existing_image_id:
            print('Image already exists in cache.')
            return existing_image_id[0]
        else:
            new_Last_Id = add_apod_to_db(apod_data['title'], apod_data['explanation'], image_file_path, image_hash)
            print("APOD image is not already in cache.")
            print("APOD file path:",image_file_path)
            print("Saving image file as ",image_file_path, "...success")
            print("Adding APOD to image cache DB...success")
            return new_Last_Id
    
    # else (apod_data['media_type'] == 'video'):
    else:
         # Download the high-definition image file if it doesn't already exist in the cache
        videos_url = apod_data['url']
        # print("videos_url::::",videos_url)
        # Define the regular expression pattern
        embed_pattern = r'https://www\.youtube\.com/embed/([a-zA-Z0-9_-]+)\?.*'
        
        # Define the replacement pattern for the thumbnail URL
        thumbnail_pattern = r'https://img.youtube.com/vi/\1/0.jpg'

        # Use the re.sub() method to replace the pattern in the input URL with the thumbnail URL
        image_url = re.sub(embed_pattern, thumbnail_pattern, videos_url)

        # print("image_url::::::::::",image_url)
        print("Getting "+ apod_date.isoformat() +" APOD information from NASA...success")
        print("APOD title:",apod_data['title'])
        print("APOD URL:",image_url)
        print("Downloading image from ",image_url,"..success")        
        image_ext = os.path.splitext(urllib.parse.urlparse(image_url).path)[1]
        image_title = re.sub(r'[^a-zA-Z0-9\s_]+', '', apod_data['title']).strip().replace(' ', '_')
        image_file_name = f'{image_title}{image_ext}'
        image_file_path = os.path.join(image_cache_dir, image_file_name)
        image_hash = hash_file(image_file_path) if os.path.exists(image_file_path) else None
        if not image_hash:
            response = requests.get(image_url)
            with open(image_file_path, 'wb') as f:
                f.write(response.content)
            image_hash = hash_file(image_file_path)
        # Check if the image already exists in the database
        conn = sqlite3.connect(image_cache_db)
        c = conn.cursor()
        print("APOD SHA-256:",image_hash)
        c.execute('SELECT id FROM apod_images WHERE hash=?', (image_hash,))
        existing_image_id = c.fetchone()
        conn.commit()
        # print("existing_image_id::::::::::",existing_image_id)
        if existing_image_id:
            print('Image already exists in cache.')
            return existing_image_id[0]
        else:
            new_Last_Id = add_apod_to_db(apod_data['title'], apod_data['explanation'], image_file_path, image_hash)
            print("APOD image is not already in cache.")
            print("APOD file path:",image_file_path)
            print("Saving image file as ",image_file_path, "...success")
            print("Adding APOD to image cache DB...success")
            return new_Last_Id


    return 0


def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: The ID of the newly inserted APOD record, if successful.  Zero, if unsuccessful       
    """
    # TODO: Complete function body
    return 0

def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.

    Args:
        image_sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    # TODO: Complete function body
    return 0

def determine_apod_file_path(image_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache. 
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed

    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '

    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'

    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    # TODO: Complete function body
    return

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
    # TODO: Query DB for image info
    # TODO: Put information into a dictionary
    apod_info = {
        #'title': , 
        #'explanation': ,
        'file_path': 'TBD',
    }
    return apod_info

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache

    Returns:
        list: Titles of all images in the cache
    """
    # TODO: Complete function body
    # NOTE: This function is only needed to support the APOD viewer GUI
    return

if __name__ == '__main__':
    main()