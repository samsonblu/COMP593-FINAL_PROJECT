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
from datetime import *
from datetime import date
import os
import image_lib
import inspect
import apod_api
import sys
import sqlite3
import apod_api
import hashlib
import re

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

    # Determine if an argument was given, exit otherwise

    if len(sys.argv) == 1:
        apod_date = date.today()
        return apod_date

    if len(sys.argv) >= 3:
        print('Error too many parameters.')
        exit()
    
    # Determine if argument given is in correct format
    if len(sys.argv) == 2:
        try: 
            apod_date = date.fromisoformat(sys.argv[1])
        except ValueError:
            print(f'Error incorrect format. Please provide a date in YYYY-MM-DD format.')
            exit()

    # Determine whether date is in correct date range

    if apod_date < date(1995,6,16):
        print('Error out of date range. Please provide a date within 1995-06-16 and Today.')
        exit()
    
    elif apod_date > date.today():
        print('Error out of date range. Please provide a date within 1995-06-16 and Today.')
        exit()

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

    # Determine the path of the image cache directory
    
    image_cache_dir = os.path.join(parent_dir, 'image_cache')
    print(f'Image cache directory: {image_cache_dir}')

    # Create the image cache directory if it does not already exist

    if not os.path.isdir(image_cache_dir):
        os.makedirs(image_cache_dir)
        print('Image cache directory created')

    else:
        print('Image cache directory already exists!')

    # Determine the path of image cache DB

    image_cache_db = os.path.join(image_cache_dir, 'image_cache.db')
    print(f'Image cache database: {image_cache_db}')

    # Create the DB if it does not already exist

    if not os.path.isfile(image_cache_db):
        con = sqlite3.connect(image_cache_db)
        cur = con.cursor()

        create_apod_tbl_query = """
        CREATE TABLE IF NOT EXISTS apod_images
        (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            explanation TEXT,
            file_path TEXT NOT NULL,
            hash TEXT
        );
        """

        cur.execute(create_apod_tbl_query)
        con.commit()
        con.close()

        print('Image cache database created')
    else: 
        print('Image cache database already exists!')

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

    print("APOD date:", apod_date)
    # Download the APOD information from the NASA API

    print(f'Getting {apod_date} APOD information from NASA...', end=' ')
    apod_info = apod_api.get_apod_info(apod_date)
    title = apod_info['title']
    url = apod_api.get_apod_image_url(apod_info)
    explanation = apod_info['explanation']

    print(f"APOD title: {title}")

    print(f"APOD URL: {url}")

    # Download the APOD image and get the hash
    
    file_content = image_lib.download_image(url)
    sha256 = hashlib.sha256(file_content).hexdigest()
    print(f'SHA-256: {sha256}')

    # Check whether the APOD already exists in the image cache

    check_sha256 = get_apod_id_from_db(sha256)

    if check_sha256 != 0:
       print('APOD image is already in cache.') 
       return check_sha256
    
    elif check_sha256 ==0:
        print('APOD image not already in cache.')
        file_path = determine_apod_file_path(title, url)
        
        # Save the APOD file to the image cache directory
        image_lib.save_image_file(file_content, file_path)
        populate_table = add_apod_to_db(title, explanation, file_path, sha256)
        return populate_table
    
    # Add the APOD information to the DB
    else:
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
    print('Adding the APOD image to database...', end=' ')

    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()

    add_apod_tbl_query = """
        INSERT INTO apod_images
        (
            title,
            explanation,
            file_path,
            hash
        )
        VALUES (?, ?, ?, ?);
    """

    apod_val = (
        title,
        explanation,
        file_path,
        sha256
    )

    cur.execute(add_apod_tbl_query, apod_val)
    con.commit()
    con.close()

    # Determine if the query returns an ID

    created_id = cur.lastrowid
    if created_id > 0:
        print('Success.')
        return created_id
    else:
        print('Fail.')
        return 0

def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.

    Args:
        image_sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """

    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()

    apod_tbl_query = f"""
        SELECT id FROM apod_images
        WHERE hash ='{image_sha256}'
    """

    cur.execute(apod_tbl_query)

    query_result = cur.fetchall()
    con.close()

    # Access the first object of the tuple and the first object of the list in the query result. 

    if query_result:
        image_id = query_result[0][0]
        return image_id
    else:
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
    
    # Find the extension of the image URL

    regex = re.search(r'\.\w+$', image_url)
    file_ext = regex.group()
    apod_title = re.sub(r'\s+', '_', image_title)

    # Remove any non words from the title

    clean_title = re.sub(r'[^\w\d_]', '', apod_title)

    # Build the file path of the image

    file_name = clean_title + file_ext

    file_path = os.path.join(image_cache_dir, file_name)

    return file_path

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
    #  Query DB for image info

    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    add_image_query = f"""
    SELECT title, explanation, file_path FROM apod_images
    WHERE id = '{image_id}'
    """
    cur.execute(add_image_query)
    query_result = cur.fetchone()
    con.close()

    #  Put information into a dictionary

    apod_info = {
        'title': query_result[0], 
        'explanation': query_result[1],
        'file_path': query_result[2]
    }
    return apod_info

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache

    Returns:
        list: Titles of all images in the cache
    """
    
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()

    get_title_query = """
        SELECT title FROM apod_images
    """
    cur.execute(get_title_query)
    query_results = cur.fetchall
    con.close()
    
    # Iterate over titles in the query

    title_results = [q for t in query_results for q in t]
    
    # NOTE: This function is only needed to support the APOD viewer GUI
    return title_results

if __name__ == '__main__':
    main()