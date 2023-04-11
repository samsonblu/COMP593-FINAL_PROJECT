'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''
import requests
import sys

KEY = 'aeKMT7dn7xRECWTcSO6M0LSyK8M7NOAAuQNHyK78'
NASA_URL = 'https://api.nasa.gov/planetary/apod?api_key='
url = NASA_URL + KEY

def main():
    apod_info = get_apod_info(apod_date='2022-01-25')
    get_apod_image_url(apod_info)
    return

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """

    params = {
        'date' : apod_date,
        'thumbs' : True,
    } 

    # Send a get request to the APOD url
    resp_msg = requests.get(url, params=params)

    # Determine whether the GET request was successful
    if resp_msg.ok:
        print('Success.')
        return resp_msg.json()
    else:
        print('Fail.')
        print(f'Status code: {resp_msg.status_code} ({resp_msg.reason})')
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

    # Determine the media type and its corresponding image link
    if apod_info_dict['media_type'] == 'image':
        print(apod_info_dict['hdurl'])
    elif apod_info_dict['media_type'] == 'video':
        print(apod_info_dict['thumbnail_url'])

if __name__ == '__main__':
    main()