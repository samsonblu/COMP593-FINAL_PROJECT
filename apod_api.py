'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''
import requests
import sys

KEY = 'aeKMT7dn7xRECWTcSO6M0LSyK8M7NOAAuQNHyK78'
NASA_URL = 'https://api.nasa.gov/planetary/apod'

def main():
    # TODO: Add code to test the functions in this module
    get_apod_info(apod_date='today')
    return

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """

    num_params = len(sys.argv)
    if num_params > 0:
        return sys.argv[1]  
    else:
        print('Error: Missing Date.')

    params = {
        'date': apod_date,
        'thumbs': True,
        'api_key' : 'DEMO_KEY', 
           }
 
    return   

def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.

    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.

    Args:
        apod_info_dict (dict): Dictionary of APOD info from API

    Returns:
        str: APOD image URL
    """

    

    return

if __name__ == '__main__':
    main()