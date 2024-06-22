import astropy.units as u
from sunpy.net import Fido, attrs as a
from sunpy.net.hek import HEKClient
from datetime import datetime, timedelta
import os
import requests
from urllib.parse import urlsplit

hek_client = HEKClient()

def datetime_to_url(date_obj):
    # Format the datetime object to the required string format
    date_str = date_obj.strftime("%Y-%m-%d")

    # Construct the URL
    base_url = "https://suntoday.lmsal.com/sdomedia/SunInTime"
    url = f"{base_url}/{date_obj.year}/{date_obj.strftime('%m')}/{date_obj.strftime('%d')}/AIA_DEM_{date_str}.genx"
    return url


def is_flare_ongoing(date):
    start_time = date.replace(hour=22, minute=30, second=0)
    end_time = date.replace(hour=23, minute=39, second=0)
    result = hek_client.search(a.Time(start_time, end_time), a.hek.EventType('FL'))
    return len(result) > 0


def download_file(url, dest_dir):
    # Extract the file name from the URL
    file_name = os.path.basename(urlsplit(url).path)
    # Create the full path by joining the destination directory with the file name
    dest_path = os.path.join(dest_dir, file_name)

    # Send a GET request to the URL
    response = requests.get(url, stream=True)
    # Check if the request was successful
    if response.status_code == 200:
        # Open the destination file in write-binary mode
        with open(dest_path, 'wb') as file:
            # Write the content to the file in chunks
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"File downloaded successfully: {dest_path}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

# Define the time range for the AIA data search
start_date = datetime(2018, 6, 30)
end_date = datetime(2021, 6, 29)

# Generate the list of dates to download AIA data
current_date = start_date
dates_to_download = []

while current_date <= end_date:
    print('is ', current_date, ' ok?')
    if not is_flare_ongoing(current_date):
        print(current_date, ' is okay to download')
        dates_to_download.append(current_date)
    current_date += timedelta(days=1)

url_list = []
for cd in dates_to_download:
    curl = datetime_to_url(cd)
    #download_file(curl, '/Users/walterwei/Downloads/work/fasr_simulation/sun_today_dem')
    download_file(curl, '/Volumes/Media_1t/work/fasr_simulation/suntoday_dem_2018_2021')
    #print(curl, '  downloaded')
    #url_list.append(datetime_to_url(cd))
#print(url_list)

